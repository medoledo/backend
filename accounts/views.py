from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, BasePermission
from .serializers import (
    TeacherProfileSerializer, 
    StudentProfileSerializer,
    UserSerializer,
    CenterSerializer
)
from .models import (
    User, 
    StudentProfile, 
    TeacherProfile, 
    AssistantProfile, 
    Subject, 
    Grade, 
    Center,
    Payment
)
from django.db.models import Q
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from .permissions import  IsTeacher , IsStudent , IsAssistant , IsAdmin

# Composite Permission Classes
class IsTeacherOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['teacher', 'admin']

class IsTeacherOrAssistant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['teacher', 'assistant']

class IsTeacherAssistantOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['teacher', 'assistant', 'admin']

class IsAssistantOrAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['assistant', 'admin']

# Authentication Views
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# Dashboard Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def admin_dashboard(request):
    if request.user.role != 'admin':
        return Response({'detail': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
    
    stats = {
        'teachers_count': TeacherProfile.objects.count(),
        'students_count': StudentProfile.objects.count(),
        'assistants_count': AssistantProfile.objects.count(),
        'recent_payments': list(Payment.objects.all().order_by('-date')[:5].values('teacher__full_name', 'amount', 'date'))
    }
    return Response(stats, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsTeacher])
def teacher_dashboard(request):
    teacher = request.user.teacher_profile
    stats = {
        'students_count': StudentProfile.objects.filter(teacher=teacher).count(),
        'assistants_count': AssistantProfile.objects.filter(teacher=teacher).count(),
        'centers': list(Center.objects.filter(teacher=teacher).values('id', 'name')),
        'pending_approvals': StudentProfile.objects.filter(teacher=teacher, is_approved=False).count()
    }
    return Response(stats, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsStudent])
def student_dashboard(request):
    student = request.user.student_profile
    data = {
        'profile': StudentProfileSerializer(student).data,
        'recent_attendance': list(student.attendance_records.order_by('-date')[:5].values('date', 'attended')),
    }
    return Response(data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAssistant])
def assistant_dashboard(request):
    assistant = request.user.assistant_profile
    stats = {
        'teacher': assistant.teacher.full_name,
        'students_count': StudentProfile.objects.filter(teacher=assistant.teacher).count(),
        'centers': list(Center.objects.filter(teacher=assistant.teacher).values('id', 'name'))
    }
    return Response(stats, status=status.HTTP_200_OK)

# Student Management
@api_view(['POST'])
@permission_classes([IsTeacherOrAdmin])
def create_student(request):
    # 1. Create User
    user_data = {
        'username': request.data.get('username'),
        'password': request.data.get('password'),
        'email': request.data.get('email', ''),
        'role': 'student'
    }
    
    user_serializer = UserSerializer(data=user_data)
    if not user_serializer.is_valid():
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = user_serializer.save()
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # 2. Determine Teacher
    try:
        if request.user.role == 'teacher':
            teacher = request.user.teacher_profile
        else:
            if 'teacher' not in request.data:
                user.delete()
                return Response({'error': 'Teacher ID required for admin'}, status=400)
            teacher = TeacherProfile.objects.get(id=request.data['teacher'])
    except TeacherProfile.DoesNotExist:
        user.delete()
        return Response({'error': 'Invalid teacher ID'}, status=400)

    # 3. Prepare Profile Data
    profile_data = {
        'full_name': request.data.get('full_name'),
        'phone_number': request.data.get('phone_number'),
        'parent_number': request.data.get('parent_number'),
        'gender': request.data.get('gender'),
        'grade': request.data.get('grade'),
        'center': request.data.get('center')
    }

    # 4. Validate and Create Student Profile
    serializer = StudentProfileSerializer(
        data=profile_data,
        context={'request': request, 'teacher': teacher}
    )
    
    if serializer.is_valid():
        try:
            # Explicitly set user and teacher relationships
            student = serializer.save(
                user=user,
                teacher=teacher
            )
            return Response(StudentProfileSerializer(student).data, status=201)
        except Exception as e:
            user.delete()
            return Response({'error': str(e)}, status=400)
    
    # Cleanup if validation fails
    user.delete()
    return Response(serializer.errors, status=400)
    
    
@api_view(['POST'])
@permission_classes([IsAdmin])
def approve_student(request, student_id):
    try:
        student = StudentProfile.objects.get(id=student_id)
        student.is_approved = True
        student.save()
        return Response({'detail': 'Student approved'}, status=status.HTTP_200_OK)
    except StudentProfile.DoesNotExist:
        return Response({'detail': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsTeacherAssistantOrAdmin])
def list_students(request):
    # Base queryset
    if request.user.role == 'admin':
        queryset = StudentProfile.objects.all()
    else:
        # For teachers and assistants, get their associated teacher
        teacher = (
            request.user.teacher_profile 
            if request.user.role == 'teacher' 
            else request.user.assistant_profile.teacher
        )
        queryset = StudentProfile.objects.filter(teacher=teacher)

    # Apply filters for all roles
    search_query = request.GET.get('search')
    center_id = request.GET.get('center_id')
    grade_id = request.GET.get('grade_id')

    if search_query:
        queryset = queryset.filter(
            Q(full_name__icontains=search_query) |
            Q(phone_number__icontains=search_query) |
            Q(parent_number__icontains=search_query)
        )

    if center_id:
        queryset = queryset.filter(center_id=center_id)

    if grade_id:
        queryset = queryset.filter(grade_id=grade_id)

    serializer = StudentProfileSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsTeacherAssistantOrAdmin])
def student_detail(request, pk):
    # Get student with permission check
    try:
        if request.user.role == 'admin':
            student = StudentProfile.objects.get(pk=pk)
        elif request.user.role == 'teacher':
            student = StudentProfile.objects.get(pk=pk, teacher=request.user.teacher_profile)
        else:  # assistant
            student = StudentProfile.objects.get(pk=pk, teacher=request.user.assistant_profile.teacher)
    except StudentProfile.DoesNotExist:
        return Response({'detail': 'Student not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = StudentProfileSerializer(student)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = StudentProfileSerializer(student, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete associated user account too
        user = student.user
        student.delete()
        user.delete()
        return Response({'detail': 'Student deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# Teacher Management
@api_view(['POST'])
@permission_classes([IsAdmin])
def create_teacher_profile(request):
    # 1. Create User
    user_data = {
        'username': request.data.get('username'),
        'password': request.data.get('password'),
        'email': request.data.get('email', ''),
        'role': 'teacher'
    }
    
    user_serializer = UserSerializer(data=user_data)
    if not user_serializer.is_valid():
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = user_serializer.save()
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # 2. Create Teacher Profile
    profile_data = {
        'full_name': request.data.get('full_name'),
        'phone_number': request.data.get('phone_number'),
        'gender': request.data.get('gender'),
        'subject': request.data.get('subject'),
        'grades': request.data.get('grades', [])
    }

    # 3. Validate and Create Profile
    serializer = TeacherProfileSerializer(
        data=profile_data,
        context={'request': request}
    )
    
    if serializer.is_valid():
        try:
            # Explicitly set the user relationship
            teacher = serializer.save(user=user)
            return Response({
                'user': UserSerializer(user).data,
                'profile': TeacherProfileSerializer(teacher).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            user.delete()
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    # Cleanup if validation fails
    user.delete()
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsTeacherOrAdmin])
def my_teacher_profile(request):
    try:
        profile = request.user.teacher_profile
        serializer = TeacherProfileSerializer(profile)
        return Response(serializer.data)
    except TeacherProfile.DoesNotExist:
        return Response({'detail': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAdmin])
def list_teachers(request):
    teachers = TeacherProfile.objects.all()
    serializer = TeacherProfileSerializer(teachers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdmin])
def teacher_detail(request, pk):
    try:
        teacher = TeacherProfile.objects.get(pk=pk)
    except TeacherProfile.DoesNotExist:
        return Response({'detail': 'Teacher not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TeacherProfileSerializer(teacher)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = TeacherProfileSerializer(teacher, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        # Delete associated user account too
        user = teacher.user
        teacher.delete()
        user.delete()
        return Response({'detail': 'Teacher deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# Assistant Management
@api_view(['POST'])
@permission_classes([IsTeacherOrAdmin])
def create_assistant(request):
    teacher = request.user.teacher_profile if request.user.role == 'teacher' else TeacherProfile.objects.get(pk=request.data.get('teacher_id'))
    
    # Create User account first
    user_data = {
        'username': request.data.get('username'),
        'password': request.data.get('password'),
        'email': request.data.get('email', ''),
        'role': 'assistant'
    }
    
    user_serializer = UserSerializer(data=user_data)
    if not user_serializer.is_valid():
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = user_serializer.save()
    
    # Create AssistantProfile
    profile_data = {
        'user': user.id,
        'teacher': teacher.id,
        'full_name': request.data.get('full_name'),
        'phone_number': request.data.get('phone_number'),
        'gender': request.data.get('gender')
    }
    
    try:
        AssistantProfile.objects.create(
            user=user,
            teacher=teacher,
            full_name=profile_data['full_name'],
            phone_number=profile_data['phone_number'],
            gender=profile_data['gender']
        )
        return Response({'message': 'Assistant created successfully'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        user.delete()
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsTeacherOrAdmin])
def view_assistants(request):
    if request.user.role == 'teacher':
        assistants = AssistantProfile.objects.filter(teacher=request.user.teacher_profile)
    else:  # admin
        teacher_id = request.query_params.get('teacher_id')
        if teacher_id:
            assistants = AssistantProfile.objects.filter(teacher_id=teacher_id)
        else:
            assistants = AssistantProfile.objects.all()
    
    data = [{
        'id': a.id,
        'username': a.user.username,
        'full_name': a.full_name,
        'phone_number': a.phone_number,
        'gender': a.gender,
        'teacher': a.teacher.full_name
    } for a in assistants]
    
    return Response(data, status=status.HTTP_200_OK)

@api_view(['PATCH'])
@permission_classes([IsTeacherOrAdmin])
def update_assistant(request, assistant_id):
    try:
        if request.user.role == 'teacher':
            assistant = AssistantProfile.objects.get(id=assistant_id, teacher=request.user.teacher_profile)
        else:  # admin
            assistant = AssistantProfile.objects.get(id=assistant_id)
    except AssistantProfile.DoesNotExist:
        return Response({'error': 'Assistant not found'}, status=status.HTTP_404_NOT_FOUND)

    data = request.data
    allowed_fields = ['full_name', 'phone_number', 'gender']
    updates = {k: data[k] for k in allowed_fields if k in data}
    
    for field, value in updates.items():
        setattr(assistant, field, value)
    
    assistant.save()
    return Response({'message': 'Assistant updated successfully'}, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsTeacherOrAdmin])
def delete_assistant(request, assistant_id):
    try:
        if request.user.role == 'teacher':
            assistant = AssistantProfile.objects.get(id=assistant_id, teacher=request.user.teacher_profile)
        else:  # admin
            assistant = AssistantProfile.objects.get(id=assistant_id)
    except AssistantProfile.DoesNotExist:
        return Response({'error': 'Assistant not found'}, status=status.HTTP_404_NOT_FOUND)

    user = assistant.user
    assistant.delete()
    user.delete()
    return Response({'message': 'Assistant deleted successfully'}, status=status.HTTP_204_NO_CONTENT)

# Center Management
@api_view(['POST'])
@permission_classes([IsTeacherOrAdmin])
def create_center(request):
    if request.user.role == 'teacher':
        request.data['teacher'] = request.user.teacher_profile.id
    
    serializer = CenterSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_centers(request):
    if request.user.role == 'admin':
        centers = Center.objects.all()
    elif request.user.role == 'teacher':
        centers = Center.objects.filter(teacher=request.user.teacher_profile)
    elif request.user.role == 'assistant':
        centers = Center.objects.filter(teacher=request.user.assistant_profile.teacher)
    else:  # student
        centers = Center.objects.filter(id=request.user.student_profile.center_id)
    
    serializer = CenterSerializer(centers, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


from rest_framework import generics, filters
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404
from .models import Attendance
from .serializers import AttendanceSerializer
from accounts.models import StudentProfile, Center
from accounts.serializers import StudentProfileSerializer
from accounts.permissions import IsTeacher, IsAssistant

class AttendanceCreateView(generics.CreateAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsTeacher | IsAssistant]

    def perform_create(self, serializer):
        user = self.request.user
        student_id = self.request.data.get('student')
        
        # Get student and verify ownership
        student = get_object_or_404(StudentProfile, id=student_id)
        teacher = self._get_teacher(user)
        
        if student.teacher != teacher:
            raise PermissionDenied("You can only add attendance for your own students.")
        
        serializer.save(submitted_by=user)

    def _get_teacher(self, user):
        if user.role == 'teacher':
            return user.teacher_profile
        elif user.role == 'assistant':
            return user.assistant_profile.teacher
        raise PermissionDenied()

class AttendanceUpdateView(generics.UpdateAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsTeacher | IsAssistant]

    def get_queryset(self):
        teacher = self._get_teacher(self.request.user)
        return Attendance.objects.filter(student__teacher=teacher)

    def _get_teacher(self, user):
        if user.role == 'teacher':
            return user.teacher_profile
        elif user.role == 'assistant':
            return user.assistant_profile.teacher
        raise PermissionDenied()

class AttendanceDeleteView(generics.DestroyAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsTeacher | IsAssistant]

    def get_queryset(self):
        teacher = self._get_teacher(self.request.user)
        return Attendance.objects.filter(student__teacher=teacher)

    def _get_teacher(self, user):
        if user.role == 'teacher':
            return user.teacher_profile
        elif user.role == 'assistant':
            return user.assistant_profile.teacher
        raise PermissionDenied()

class StudentSearchListView(generics.ListAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [IsTeacher | IsAssistant]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['full_name', 'user__username']

    def get_queryset(self):
        teacher = self._get_teacher(self.request.user)
        queryset = StudentProfile.objects.filter(teacher=teacher)

        # Validate center belongs to teacher
        if center_id := self.request.query_params.get('center'):
            if not Center.objects.filter(id=center_id, teacher=teacher).exists():
                raise ValidationError("Invalid center ID")
            queryset = queryset.filter(center_id=center_id)

        if grade_id := self.request.query_params.get('grade'):
            queryset = queryset.filter(grade_id=grade_id)

        return queryset

    def _get_teacher(self, user):
        if user.role == 'teacher':
            return user.teacher_profile
        elif user.role == 'assistant':
            return user.assistant_profile.teacher
        raise PermissionDenied()

class AttendanceListView(generics.ListAPIView):
    serializer_class = AttendanceSerializer
    permission_classes = [IsTeacher | IsAssistant]

    def get_queryset(self):
        teacher = self._get_teacher(self.request.user)
        queryset = Attendance.objects.filter(student__teacher=teacher)

        if student_id := self.request.query_params.get('student'):
            queryset = queryset.filter(student_id=student_id)

        if date := self.request.query_params.get('date'):
            queryset = queryset.filter(date=date)

        return queryset

    def _get_teacher(self, user):
        if user.role == 'teacher':
            return user.teacher_profile
        elif user.role == 'assistant':
            return user.assistant_profile.teacher
        raise PermissionDenied()
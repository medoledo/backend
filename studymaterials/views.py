from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import StudyWeek, StudyMaterial
from .serializers import StudyWeekSerializer, StudyMaterialSerializer
from accounts.permissions import IsTeacher, IsAssistant

class IsTeacherOrAssistant(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['teacher', 'assistant']

class StudyWeekViewSet(viewsets.ModelViewSet):
    serializer_class = StudyWeekSerializer
    permission_classes = [IsTeacherOrAssistant]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            return StudyWeek.objects.filter(teacher=user.teacher_profile)
        elif user.role == 'assistant':
            return StudyWeek.objects.filter(teacher=user.assistant_profile.teacher)
        return StudyWeek.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        if user.role == 'teacher':
            serializer.save(teacher=user.teacher_profile)
        else:
            serializer.save(teacher=user.assistant_profile.teacher)

class StudyMaterialViewSet(viewsets.ModelViewSet):
    serializer_class = StudyMaterialSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == 'teacher':
            return StudyMaterial.objects.filter(teacher=user.teacher_profile)
        elif user.role == 'assistant':
            return StudyMaterial.objects.filter(teacher=user.assistant_profile.teacher)
        elif user.role == 'student':
            student = user.student_profile
            return StudyMaterial.objects.filter(
                teacher=student.teacher,
                grade=student.grade
            )
        return StudyMaterial.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        teacher = user.teacher_profile if user.role == 'teacher' else user.assistant_profile.teacher
        
        # Validate grade assignment in serializer
        serializer.save(teacher=teacher)

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsTeacherOrAssistant()]
        return [permissions.IsAuthenticated()]
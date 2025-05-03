from rest_framework import generics, permissions, filters
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404
from .models import Test, TestScore
from .serializers import TestScoreSerializer
from accounts.models import StudentProfile, Center
from accounts.permissions import IsTeacher, IsAssistant

def get_current_teacher(user):
    """Helper to get teacher profile for both teachers and assistants"""
    if user.role == 'teacher':
        return user.teacher_profile
    elif user.role == 'assistant':
        return user.assistant_profile.teacher
    raise PermissionDenied("Invalid user role")

class TestScoreCreateView(generics.CreateAPIView):
    serializer_class = TestScoreSerializer
    permission_classes = [permissions.IsAuthenticated & (IsTeacher | IsAssistant)]

    def perform_create(self, serializer):
        teacher = get_current_teacher(self.request.user)
        student = get_object_or_404(StudentProfile, id=self.request.data.get('student'))
        
        # Verify student belongs to teacher
        if student.teacher != teacher:
            raise PermissionDenied("You can only assign scores to your own students")

        # Validate test belongs to teacher
        test = get_object_or_404(Test, id=self.request.data.get('test'))
        if test.created_by != teacher:
            raise PermissionDenied("Invalid test ID")

        # Validate center/grade if provided
        if (center_id := self.request.data.get('center')) and student.center_id != center_id:
            raise ValidationError("Student is not in this center")
        if (grade_id := self.request.data.get('grade')) and student.grade_id != grade_id:
            raise ValidationError("Student is not in this grade")

        serializer.save(test=test, student=student, created_by=self.request.user)

class TestScoreUpdateView(generics.UpdateAPIView):
    serializer_class = TestScoreSerializer
    permission_classes = [permissions.IsAuthenticated & (IsTeacher | IsAssistant)]

    def get_queryset(self):
        teacher = get_current_teacher(self.request.user)
        return TestScore.objects.filter(
            student__teacher=teacher,
            test__created_by=teacher  # Ensure test also belongs to teacher
        )

    def perform_update(self, serializer):
        # Additional validation during updates
        student = serializer.validated_data.get('student')
        if student and student.teacher != get_current_teacher(self.request.user):
            raise PermissionDenied("Cannot change student ownership")
        serializer.save()

class TestScoreDeleteView(generics.DestroyAPIView):
    serializer_class = TestScoreSerializer
    permission_classes = [permissions.IsAuthenticated & (IsTeacher | IsAssistant)]

    def get_queryset(self):
        teacher = get_current_teacher(self.request.user)
        return TestScore.objects.filter(
            student__teacher=teacher,
            test__created_by=teacher
        )

class TestScoreSearchView(generics.ListAPIView):
    serializer_class = TestScoreSerializer
    permission_classes = [permissions.IsAuthenticated & (IsTeacher | IsAssistant)]
    filter_backends = [filters.SearchFilter]
    search_fields = ['student__full_name', 'student__user__username']

    def get_queryset(self):
        teacher = get_current_teacher(self.request.user)
        queryset = TestScore.objects.filter(
            student__teacher=teacher,
            test__created_by=teacher
        )

        # Validate test belongs to teacher
        if test_id := self.request.query_params.get('test'):
            if not Test.objects.filter(id=test_id, created_by=teacher).exists():
                raise ValidationError("Invalid test ID")
            queryset = queryset.filter(test_id=test_id)

        # Validate center belongs to teacher
        if center_id := self.request.query_params.get('center'):
            if not Center.objects.filter(id=center_id, teacher=teacher).exists():
                raise ValidationError("Invalid center ID")
            queryset = queryset.filter(student__center_id=center_id)

        if grade_id := self.request.query_params.get('grade'):
            queryset = queryset.filter(student__grade_id=grade_id)

        return queryset
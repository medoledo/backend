from rest_framework import serializers
from .models import Test, TestScore
from accounts.models import TeacherProfile, StudentProfile

class TestSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.full_name', read_only=True)

    class Meta:
        model = Test
        fields = ['id', 'name', 'teacher', 'teacher_name', 'date', 'description']
        read_only_fields = ['teacher']

class TestScoreSerializer(serializers.ModelSerializer):
    test_name = serializers.CharField(source='test.name', read_only=True)
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    student_username = serializers.CharField(source='student.user.username', read_only=True)

    class Meta:
        model = TestScore
        fields = ['id', 'test', 'student', 'test_name', 'student_name', 'student_username', 'score', 'date_taken']
        read_only_fields = ['student', 'test']

from rest_framework import serializers
from .models import Attendance

class AttendanceSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    phone_number = serializers.CharField(source='student.phone_number', read_only=True)
    parent_number = serializers.CharField(source='student.parent_number', read_only=True)
    submitted_by = serializers.CharField(source='submitted_by.username', read_only=True)

    class Meta:
        model = Attendance
        fields = [
            'id',
            'student',
            'student_name',
            'phone_number',
            'parent_number',
            'attended',
            'homework',
            'date',
            'submitted_by',
        ]

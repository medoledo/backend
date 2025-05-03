from rest_framework import serializers
from .models import User, TeacherProfile, StudentProfile, Center
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

# User serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role']


# Teacher profile serializer
class TeacherProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherProfile
        fields = '__all__'
        read_only_fields = ['user']  # Keep user read-only

    def create(self, validated_data):
        # Handle many-to-many relationship for grades
        grades = validated_data.pop('grades', [])
        teacher = TeacherProfile.objects.create(**validated_data)
        teacher.grades.set(grades)
        return teacher


# Center serializer (read-only teacher)
class CenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Center
        fields = ['id', 'name', 'teacher']
        read_only_fields = ['teacher']


# Student profile serializer with center validation
# accounts/serializers.py
class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = '__all__'
        read_only_fields = ['user', 'teacher', 'is_approved']

    def validate_center(self, value):
        request = self.context.get('request')
        teacher = self.context.get('teacher')
        
        if value and value.teacher != teacher:
            raise serializers.ValidationError("Center does not belong to the specified teacher")
        return value
# Custom token serializer with role in claims
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        return data

from rest_framework import serializers
from .models import StudyWeek, StudyMaterial

class StudyMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyMaterial
        fields = ['id', 'teacher', 'week', 'grade', 'title', 'material_type', 
                 'file', 'text_content', 'external_url']
        read_only_fields = ['teacher']

    def validate(self, attrs):
        request = self.context.get('request')
        grade = attrs.get('grade')
        
        if request.user.role == 'teacher':
            teacher = request.user.teacher_profile
        elif request.user.role == 'assistant':
            teacher = request.user.assistant_profile.teacher
        else:
            raise serializers.ValidationError("Invalid content creator role")

        if not teacher.grades.filter(id=grade.id).exists():
            raise serializers.ValidationError(
                f"Teacher is not assigned to grade {grade.name}"
            )

        return attrs

class StudyWeekSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudyWeek
        fields = ['id', 'teacher', 'title', 'description']
        read_only_fields = ['teacher']

    def validate(self, attrs):
        # If validating grades in StudyWeek
        if 'grade' in attrs:  
            teacher = self._get_teacher(self.context['request'].user)
            if not teacher.grades.filter(id=attrs['grade'].id).exists():
                raise serializers.ValidationError("Invalid grade assignment")
        return attrs
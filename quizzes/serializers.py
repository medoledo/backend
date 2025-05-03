from rest_framework import serializers
from .models import Quiz, Question, Choice, QuizSubmission, Answer
from accounts.models import StudentProfile, TeacherProfile

# Quiz Serializer
class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'description', 'time_limit_minutes', 'created_by', 'grade', 'created_at', 'is_published', 'total_marks']
# Question Serializer
class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'quiz', 'question_type', 'text', 'image', 'marks', 'order']

# Choice Serializer
class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'question', 'text', 'is_correct', 'order']

# Quiz Submission Serializer
class QuizSubmissionSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all())
    quiz = serializers.PrimaryKeyRelatedField(queryset=Quiz.objects.all())
    
    class Meta:
        model = QuizSubmission
        fields = ['id', 'quiz', 'student', 'submitted_at', 'score', 'is_completed']

# Answer Serializer
class AnswerSerializer(serializers.ModelSerializer):
    selected_choices = serializers.PrimaryKeyRelatedField(queryset=Choice.objects.all(), many=True)
    class Meta:
        model = Answer
        fields = ['id', 'submission', 'question', 'selected_choices', 'is_correct', 'marks_obtained']

# Serializer to handle the specific data return for a student's submission
class StudentSubmissionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    class Meta:
        model = QuizSubmission
        fields = ['id', 'quiz', 'student', 'submitted_at', 'score', 'is_completed', 'answers']

# quizzes/serializers.py
class TeacherChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'

class StudentChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text']

class StudentQuestionSerializer(serializers.ModelSerializer):
    choices = StudentChoiceSerializer(many=True)
    
    class Meta:
        model = Question
        fields = ['id', 'text', 'image', 'choices']

class TeacherQuestionSerializer(serializers.ModelSerializer):
    choices = TeacherChoiceSerializer(many=True)
    
    class Meta:
        model = Question
        fields = '__all__'
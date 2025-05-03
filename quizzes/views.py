from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Quiz, Question, Choice, QuizSubmission
from .serializers import (
    QuizSerializer,
    QuestionSerializer,
    ChoiceSerializer,
    QuizSubmissionSerializer
)
from accounts.permissions import IsAdmin, IsTeacher, IsAssistant, IsStudent
from accounts.models import Grade
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

# Helper function to get current teacher
def get_current_teacher(user):
    if user.role == 'teacher':
        return user.teacher_profile
    elif user.role == 'assistant':
        return user.assistant_profile.teacher
    raise PermissionDenied("Invalid user role")

# Composite Permissions
class IsTeacherOrAssistant(BasePermission):
    def has_permission(self, request, view):
        return IsTeacher().has_permission(request, view) or \
               IsAssistant().has_permission(request, view)

class IsTeacherOrAssistantOrStudent(BasePermission):
    def has_permission(self, request, view):
        return IsTeacher().has_permission(request, view) or \
               IsAssistant().has_permission(request, view) or \
               IsStudent().has_permission(request, view)

# Quizzes Views
class QuizListView(APIView):
    permission_classes = [IsTeacherOrAssistantOrStudent]

    def get(self, request):
        user = request.user
        if user.role == 'student':
            student = user.student_profile
            quizzes = Quiz.objects.filter(
                created_by=student.teacher,
                grade=student.grade
            )
        else:
            teacher = get_current_teacher(user)
            quizzes = Quiz.objects.filter(created_by=teacher)
        
        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data)

class QuizDetailView(APIView):
    permission_classes = [IsTeacherOrAssistantOrStudent]

    def get(self, request, pk):
        quiz = get_object_or_404(Quiz, pk=pk)
        user = request.user

        if user.role == 'student':
            student = user.student_profile
            if quiz.created_by != student.teacher or quiz.grade != student.grade:
                return Response(
                    {"detail": "Not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
        else:
            teacher = get_current_teacher(user)
            if quiz.created_by != teacher:
                return Response(
                    {"detail": "Not found"}, 
                    status=status.HTTP_404_NOT_FOUND
                )

        serializer = QuizSerializer(quiz)
        return Response(serializer.data)

class QuizCreateView(APIView):
    permission_classes = [IsTeacherOrAssistant]

    def post(self, request):
        serializer = QuizSerializer(data=request.data)
        if serializer.is_valid():
            teacher = get_current_teacher(request.user)
            grade = get_object_or_404(Grade, pk=request.data.get('grade'))
            
            serializer.save(created_by=teacher, grade=grade)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuizUpdateView(APIView):
    permission_classes = [IsTeacherOrAssistant]

    def put(self, request, pk):
        teacher = get_current_teacher(request.user)
        quiz = get_object_or_404(Quiz, pk=pk, created_by=teacher)
        
        serializer = QuizSerializer(quiz, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuizDeleteView(APIView):
    permission_classes = [IsTeacherOrAssistant]

    def delete(self, request, pk):
        teacher = get_current_teacher(request.user)
        quiz = get_object_or_404(Quiz, pk=pk, created_by=teacher)
        quiz.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Questions Views
class QuestionCreateView(APIView):
    permission_classes = [IsTeacherOrAssistant]

    def post(self, request):
        teacher = get_current_teacher(request.user)
        quiz = get_object_or_404(Quiz, pk=request.data.get('quiz'), created_by=teacher)
        
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionUpdateView(APIView):
    permission_classes = [IsTeacherOrAssistant]

    def put(self, request, pk):
        teacher = get_current_teacher(request.user)
        question = get_object_or_404(Question, pk=pk, quiz__created_by=teacher)
        
        serializer = QuestionSerializer(question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QuestionDeleteView(APIView):
    permission_classes = [IsTeacherOrAssistant]

    def delete(self, request, pk):
        teacher = get_current_teacher(request.user)
        question = get_object_or_404(Question, pk=pk, quiz__created_by=teacher)
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Choices Views
class ChoiceCreateView(APIView):
    permission_classes = [IsTeacherOrAssistant]

    def post(self, request):
        teacher = get_current_teacher(request.user)
        question = get_object_or_404(
            Question, 
            pk=request.data.get('question'), 
            quiz__created_by=teacher
        )
        
        serializer = ChoiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChoiceUpdateView(APIView):
    permission_classes = [IsTeacherOrAssistant]

    def put(self, request, pk):
        teacher = get_current_teacher(request.user)
        choice = get_object_or_404(
            Choice, 
            pk=pk, 
            question__quiz__created_by=teacher
        )
        
        serializer = ChoiceSerializer(choice, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChoiceDeleteView(APIView):
    permission_classes = [IsTeacherOrAssistant]

    def delete(self, request, pk):
        teacher = get_current_teacher(request.user)
        choice = get_object_or_404(
            Choice, 
            pk=pk, 
            question__quiz__created_by=teacher
        )
        choice.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Submissions Views
class SubmitQuizView(APIView):
    permission_classes = [IsStudent]

    def post(self, request, quiz_id):
        student = request.user.student_profile
        quiz = get_object_or_404(
            Quiz, 
            pk=quiz_id,
            created_by=student.teacher,
            grade=student.grade
        )
        
        submission, created = QuizSubmission.objects.get_or_create(
            quiz=quiz,
            student=student
        )
        submission.is_completed = True
        submission.save()
        return Response({"message": "Quiz submitted successfully"})

class SubmissionListView(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        student = request.user.student_profile
        submissions = QuizSubmission.objects.filter(student=student)
        serializer = QuizSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

class TeacherAssistantSubmissionListView(APIView):
    permission_classes = [IsTeacherOrAssistant]

    def get(self, request, quiz_id):
        teacher = get_current_teacher(request.user)
        quiz = get_object_or_404(Quiz, pk=quiz_id, created_by=teacher)
        submissions = QuizSubmission.objects.filter(quiz=quiz)
        serializer = QuizSubmissionSerializer(submissions, many=True)
        return Response(serializer.data)

class GradeSubmissionView(APIView):
    permission_classes = [IsTeacherOrAssistant]

    def post(self, request, submission_id):
        teacher = get_current_teacher(request.user)
        submission = get_object_or_404(
            QuizSubmission, 
            pk=submission_id, 
            quiz__created_by=teacher
        )
        
        score = request.data.get('score')
        if score is not None:
            submission.score = score
            submission.save()
            return Response({"message": "Submission graded successfully"})
        return Response({"error": "Score is required"}, status=status.HTTP_400_BAD_REQUEST)
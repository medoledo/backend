from django.urls import path
from .views import (
    QuizListView,
    QuizDetailView,
    QuizCreateView,
    QuizUpdateView,
    QuizDeleteView,
    QuestionCreateView,
    QuestionUpdateView,
    QuestionDeleteView,
    ChoiceCreateView,
    ChoiceUpdateView,
    ChoiceDeleteView,
    SubmitQuizView,
    SubmissionListView,
    TeacherAssistantSubmissionListView,
    GradeSubmissionView
)

urlpatterns = [
    # Quizzes
    path('quizzes/', QuizListView.as_view(), name='quiz-list'),
    path('quizzes/create/', QuizCreateView.as_view(), name='quiz-create'),
    path('quizzes/<int:pk>/', QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/<int:pk>/update/', QuizUpdateView.as_view(), name='quiz-update'),
    path('quizzes/<int:pk>/delete/', QuizDeleteView.as_view(), name='quiz-delete'),
    
    # Quiz-specific Questions
    path('quizzes/<int:quiz_id>/questions/create/', QuestionCreateView.as_view(), name='question-create'),
    path('questions/<int:pk>/update/', QuestionUpdateView.as_view(), name='question-update'),
    path('questions/<int:pk>/delete/', QuestionDeleteView.as_view(), name='question-delete'),
    
    # Question-specific Choices
    path('questions/<int:question_id>/choices/create/', ChoiceCreateView.as_view(), name='choice-create'),
    path('choices/<int:pk>/update/', ChoiceUpdateView.as_view(), name='choice-update'),
    path('choices/<int:pk>/delete/', ChoiceDeleteView.as_view(), name='choice-delete'),
    
    # Submissions
    path('quizzes/<int:quiz_id>/submit/', SubmitQuizView.as_view(), name='quiz-submit'),
    path('submissions/', SubmissionListView.as_view(), name='submission-list'),
    path('quizzes/<int:quiz_id>/submissions/', TeacherAssistantSubmissionListView.as_view(), name='quiz-submissions'),
    path('submissions/<int:submission_id>/grade/', GradeSubmissionView.as_view(), name='grade-submission'),
]
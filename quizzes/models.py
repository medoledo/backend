from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from accounts.models import TeacherProfile, StudentProfile , Grade

# Quiz Model
class Quiz(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    time_limit_minutes = models.PositiveIntegerField(default=60)
    created_by = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=False)
    total_marks = models.PositiveIntegerField(default=0)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)  # Add this line

    def __str__(self):
        return self.title

    def get_user_submission(self, student):
        try:
            return self.submissions.get(student=student)
        except QuizSubmission.DoesNotExist:
            return None

# Question Model (Only MCQ)
class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=10, choices=[('mcq', 'Multiple Choice')], default='mcq')
    text = models.TextField()
    image = models.ImageField(upload_to='quiz_images/', blank=True, null=True)
    marks = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.quiz.title} - Q{self.order}"

# Choice Model
class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=200)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.question.text[:50]} - {self.text[:20]}"

# Quiz Submission
class QuizSubmission(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(default=0)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('quiz', 'student')

    def __str__(self):
        return f"{self.student.user.username} - {self.quiz.title}"

# Answer Model
class Answer(models.Model):
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choices = models.ManyToManyField(Choice, blank=True)
    is_correct = models.BooleanField(default=False)
    marks_obtained = models.FloatField(default=0)

    def __str__(self):
        return f"Answer to {self.question.text[:50]}"

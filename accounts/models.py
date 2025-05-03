from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# Gender Choices
GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
)

# User model
class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('assistant', 'Assistant'),
        ('student', 'Student'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"

# Subject model
class Subject(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# Grade model
class Grade(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

# Teacher profile
class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    grades = models.ManyToManyField('Grade', related_name='teachers')

    def __str__(self):
        return f"Teacher: {self.full_name} (Subject: {self.subject.name if self.subject else 'No subject'})"

# Center model — now scoped to each teacher
class Center(models.Model):
    name = models.CharField(max_length=100)
    teacher = models.ForeignKey('TeacherProfile', on_delete=models.CASCADE, related_name='centers')

    class Meta:
        unique_together = ('name', 'teacher')  # Ensures private center list per teacher

    def __str__(self):
        return f"{self.name} ({self.teacher.full_name})"

# Assistant profile
class AssistantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='assistant_profile')
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='assistants')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    def __str__(self):
        return f"Assistant: {self.full_name} (Teacher: {self.teacher.full_name})"

# Student profile
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='students')
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    parent_number = models.CharField(max_length=15)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True)
    center = models.ForeignKey(Center, on_delete=models.SET_NULL, null=True)
    is_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Student: {self.full_name} (Teacher: {self.teacher.full_name})"

# Payment model for teacher payment history
class Payment(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)

    def __str__(self):
        return f"{self.teacher.full_name} paid {self.amount} on {self.date}"

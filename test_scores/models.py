from django.db import models
from accounts.models import User, TeacherProfile, StudentProfile
from django.utils import timezone

class Test(models.Model):
    name = models.CharField(max_length=255)
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='tests')
    date = models.DateField(default=timezone.now)
    description = models.TextField()

    def __str__(self):
        return f"{self.name} - {self.teacher.user.username} - {self.date}"


class TestScore(models.Model):
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='scores')
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='test_scores')
    score = models.FloatField()
    date_taken = models.DateField(default=timezone.now)

    def __str__(self):
        return f"Test: {self.test.name}, Student: {self.student.full_name}, Score: {self.score}"


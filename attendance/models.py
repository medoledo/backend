from django.db import models
from django.utils import timezone
from accounts.models import StudentProfile, User  # adjust if app name differs

class Attendance(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_records')
    attended = models.BooleanField(default=False)
    homework = models.BooleanField(default=False)
    date = models.DateField(default=timezone.now)
    submitted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='submitted_attendance')

    def __str__(self):
        return f"{self.student.full_name} - {self.date} - {'Present' if self.attended else 'Absent'}"

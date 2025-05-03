from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import TeacherProfile , Grade  # reference to your existing model

class StudyWeek(models.Model):
    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='study_weeks')  # NEW
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.teacher.full_name})"

class StudyMaterial(models.Model):
    MATERIAL_TYPES = (
        ('pdf', 'PDF'),
        ('video', 'Video'),
        ('image', 'Image'),
        ('text', 'Text'),
        ('link', 'External Link'),
    )

    teacher = models.ForeignKey(TeacherProfile, on_delete=models.CASCADE, related_name='materials')  # NEW
    week = models.ForeignKey(StudyWeek, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=100)
    material_type = models.CharField(max_length=10, choices=MATERIAL_TYPES)
    file = models.FileField(upload_to='study_materials/', blank=True, null=True)
    text_content = models.TextField(blank=True)
    external_url = models.URLField(blank=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)  # Add this line

    def __str__(self):
        return f"{self.title} ({self.material_type}) - {self.teacher.full_name}"

    def clean(self):
        if not any([self.file, self.text_content, self.external_url]):
            raise ValidationError("At least one of file, text content, or external URL must be provided")

        if self.material_type == 'pdf' and not self.file:
            raise ValidationError("PDF materials must have a file uploaded")
        if self.material_type == 'video' and not (self.file or self.external_url):
            raise ValidationError("Video materials must have either a file or external URL")
        if self.material_type == 'image' and not self.file:
            raise ValidationError("Image materials must have a file uploaded")
        if self.material_type == 'text' and not self.text_content:
            raise ValidationError("Text materials must have text content")
        if self.material_type == 'link' and not self.external_url:
            raise ValidationError("Link materials must have an external URL")

    def get_absolute_url(self):
        if self.file:
            return self.file.url
        if self.external_url:
            return self.external_url
        return '#'

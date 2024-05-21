from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_photo = models.ImageField(upload_to='profile_photos', blank=True, null=True)

    def __str__(self):
        return self.user.username

class Case(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    ]

    filed_by = models.ForeignKey(User, related_name='filed_cases', on_delete=models.CASCADE)
    case_against = models.ForeignKey(User, related_name='cases_against', on_delete=models.CASCADE)
    details = models.TextField()
    document = models.FileField(upload_to='case_documents/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ongoing')
    verdict = models.TextField(blank=True, null=True)

    def clean(self):
        if self.status == 'completed' and not self.verdict:
            raise ValidationError('A verdict is required when the status is completed.')

    def __str__(self):
        return f"Case {self.id} filed by {self.filed_by.username} against {self.case_against.username}"

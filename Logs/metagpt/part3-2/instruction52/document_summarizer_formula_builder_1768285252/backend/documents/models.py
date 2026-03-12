from django.db import models
from django.conf import settings

class Document(models.Model):
    FILE_TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('docx', 'Word'),
        ('txt', 'Plain Text'),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    file_name = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    upload_time = models.DateTimeField(auto_now_add=True)
    summary = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.file_name} ({self.owner.username})"
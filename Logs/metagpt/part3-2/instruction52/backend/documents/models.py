from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Document(models.Model):
    document_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=20)  # e.g., 'pdf', 'docx', 'txt'
    uploaded_at = models.DateTimeField(default=timezone.now)
    content = models.TextField(blank=True)  # Parsed text content

    def parse(self):
        """
        Returns the parsed content of the document.
        Assumes content is already parsed and stored.
        """
        return self.content

    def __str__(self):
        return f"{self.filename} ({self.file_type}) uploaded by {self.user.username}"
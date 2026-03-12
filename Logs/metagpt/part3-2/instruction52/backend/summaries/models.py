from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from documents.models import Document

User = get_user_model()

class Summary(models.Model):
    summary_id = models.AutoField(primary_key=True)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='summaries')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='summaries')
    summary_text = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)

    def generate(self, document: Document) -> str:
        """
        Generates a concise summary for the given document.
        This is a stub for the actual NLP-based summarization logic.
        """
        # In production, replace this with actual NLP summarization logic.
        # For now, return the first 500 characters as a 'summary'.
        if document.content:
            return document.content[:500]
        return ""

    def __str__(self):
        return f"Summary for {self.document.filename} by {self.user.username}"
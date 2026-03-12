from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            'document_id',
            'user',
            'filename',
            'file_type',
            'uploaded_at',
            'content',
        ]
        read_only_fields = ['document_id', 'uploaded_at', 'content']
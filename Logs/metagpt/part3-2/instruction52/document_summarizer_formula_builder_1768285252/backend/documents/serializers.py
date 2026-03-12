from rest_framework import serializers
from .models import Document

class DocumentSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Document
        fields = [
            'id',
            'owner',
            'owner_username',
            'file_name',
            'file_type',
            'upload_time',
            'summary',
            'content',
        ]
        read_only_fields = ['id', 'owner', 'upload_time', 'summary', 'content']
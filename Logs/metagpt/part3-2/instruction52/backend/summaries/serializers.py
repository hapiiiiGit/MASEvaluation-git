from rest_framework import serializers
from .models import Summary

class SummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Summary
        fields = [
            'summary_id',
            'document',
            'user',
            'summary_text',
            'created_at',
        ]
        read_only_fields = ['summary_id', 'created_at', 'summary_text']
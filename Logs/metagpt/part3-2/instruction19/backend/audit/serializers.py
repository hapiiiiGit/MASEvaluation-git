from rest_framework import serializers
from .models import AuditLog
from users.serializers import UserSerializer

class AuditLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = AuditLog
        fields = [
            'id',
            'user',
            'action',
            'object_type',
            'object_id',
            'timestamp',
            'details',
        ]
        read_only_fields = ['id', 'user', 'timestamp']
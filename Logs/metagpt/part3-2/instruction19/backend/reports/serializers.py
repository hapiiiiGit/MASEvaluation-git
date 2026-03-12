from rest_framework import serializers
from .models import FinancialReport
from users.serializers import UserSerializer

class FinancialReportSerializer(serializers.ModelSerializer):
    generated_by = UserSerializer(read_only=True)

    class Meta:
        model = FinancialReport
        fields = [
            'id',
            'type',
            'parameters',
            'generated_by',
            'generated_at',
            'data',
        ]
        read_only_fields = ['id', 'generated_by', 'generated_at', 'data']
from rest_framework import serializers
from .models import Formula, FormulaResult

class FormulaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Formula
        fields = [
            'formula_id',
            'user',
            'name',
            'expression',
            'created_at',
        ]
        read_only_fields = ['formula_id', 'created_at']

class FormulaResultSerializer(serializers.ModelSerializer):
    formula = FormulaSerializer(read_only=True)
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = FormulaResult
        fields = [
            'result_id',
            'formula',
            'user',
            'input_data',
            'result',
            'created_at',
        ]
        read_only_fields = ['result_id', 'created_at', 'result']
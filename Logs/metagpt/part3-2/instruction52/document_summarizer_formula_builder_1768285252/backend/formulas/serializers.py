from rest_framework import serializers
from .models import Formula
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class FormulaSerializer(serializers.ModelSerializer):
    owner_username = serializers.ReadOnlyField(source='owner.username')
    shared_with = UserSerializer(many=True, read_only=True)
    shared_with_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Formula
        fields = [
            'id',
            'owner',
            'owner_username',
            'name',
            'expression',
            'variables',
            'created_at',
            'shared_with',
            'shared_with_ids',
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'owner_username', 'shared_with']

    def create(self, validated_data):
        shared_with_ids = validated_data.pop('shared_with_ids', [])
        formula = Formula.objects.create(**validated_data)
        if shared_with_ids:
            formula.shared_with.set(shared_with_ids)
        return formula

    def update(self, instance, validated_data):
        shared_with_ids = validated_data.pop('shared_with_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if shared_with_ids is not None:
            instance.shared_with.set(shared_with_ids)
        return instance
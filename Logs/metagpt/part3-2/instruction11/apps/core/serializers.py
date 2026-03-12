from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import CoreData

User = get_user_model()

class CoreDataSerializer(serializers.ModelSerializer):
    owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)

    class Meta:
        model = CoreData
        fields = ['id', 'owner', 'data_field', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'owner']

    def create(self, validated_data):
        request = self.context.get('request')
        user = request.user if request and request.user.is_authenticated else None
        if user is None:
            raise serializers.ValidationError("Authenticated user required to create CoreData.")
        validated_data['owner'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # Prevent changing owner
        validated_data.pop('owner', None)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['owner'] = instance.owner.username if instance.owner else None
        return rep
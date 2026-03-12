from rest_framework import serializers
from .models import User
from events.models import Session, Event

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = ['id', 'title', 'description', 'start_time', 'end_time', 'room', 'resources']

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'title', 'event_type', 'start_date', 'end_date', 'location', 'category']

class UserSerializer(serializers.ModelSerializer):
    sessions = SessionSerializer(many=True, read_only=True)
    managed_events = EventSerializer(many=True, read_only=True)
    registered_events = EventSerializer(many=True, read_only=True)
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'role', 'full_name', 'bio', 'profile_picture',
            'organization', 'contact_number', 'linkedin_url', 'website_url',
            'expertise', 'sessions', 'managed_events', 'registered_events'
        ]
        read_only_fields = ['sessions', 'managed_events', 'registered_events']

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'role', 'full_name', 'bio', 'profile_picture',
            'organization', 'contact_number', 'linkedin_url', 'website_url', 'expertise'
        ]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            'full_name', 'bio', 'profile_picture', 'organization', 'contact_number',
            'linkedin_url', 'website_url', 'expertise'
        ]
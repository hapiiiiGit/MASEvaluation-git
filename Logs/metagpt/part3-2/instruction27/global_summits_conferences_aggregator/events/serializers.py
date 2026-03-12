from rest_framework import serializers
from .models import Event, Summit, Conference, Session
from users.models import User

class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'role', 'profile_picture']

class SessionSerializer(serializers.ModelSerializer):
    speakers = UserShortSerializer(many=True, read_only=True)

    class Meta:
        model = Session
        fields = [
            'id', 'title', 'description', 'start_time', 'end_time',
            'speakers', 'room', 'resources'
        ]

class SummitSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())

    class Meta:
        model = Summit
        fields = [
            'id', 'event', 'theme', 'sponsors', 'website'
        ]

class ConferenceSerializer(serializers.ModelSerializer):
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())

    class Meta:
        model = Conference
        fields = [
            'id', 'event', 'tracks', 'sponsors', 'website'
        ]

class EventSerializer(serializers.ModelSerializer):
    organizers = UserShortSerializer(many=True, read_only=True)
    delegates = UserShortSerializer(many=True, read_only=True)
    speakers = UserShortSerializer(many=True, read_only=True)
    sessions = SessionSerializer(many=True, read_only=True)
    summit_details = SummitSerializer(read_only=True)
    conference_details = ConferenceSerializer(read_only=True)
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Event
        fields = [
            'id', 'title', 'description', 'event_type', 'start_date', 'end_date',
            'location', 'address', 'image', 'category', 'is_featured',
            'organizers', 'delegates', 'speakers', 'sessions',
            'summit_details', 'conference_details', 'created_at', 'updated_at'
        ]

class EventCreateUpdateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = Event
        fields = [
            'title', 'description', 'event_type', 'start_date', 'end_date',
            'location', 'address', 'image', 'category', 'is_featured'
        ]
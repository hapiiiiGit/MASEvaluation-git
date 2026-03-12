from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Event, Summit, Conference, Session
from .serializers import (
    EventSerializer,
    EventCreateUpdateSerializer,
    SummitSerializer,
    ConferenceSerializer,
    SessionSerializer
)
from users.models import User
from users.serializers import UserShortSerializer
from django.shortcuts import get_object_or_404

class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint for event CRUD operations, listing, and detail views.
    """
    queryset = Event.objects.all().select_related().prefetch_related('organizers', 'delegates', 'speakers', 'sessions')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return EventCreateUpdateSerializer
        return EventSerializer

    def perform_create(self, serializer):
        event = serializer.save()
        # Automatically add the creator as an organizer if role is organizer
        if self.request.user.role == 'organizer':
            event.organizers.add(self.request.user)
        event.save()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def register_delegate(self, request, pk=None):
        """
        Register the current user as a delegate for the event.
        """
        event = self.get_object()
        user = request.user
        if user.role != 'delegate':
            return Response({"detail": "Only delegates can register for events."}, status=status.HTTP_403_FORBIDDEN)
        event.delegates.add(user)
        event.save()
        return Response({"detail": "Registered successfully."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def add_speaker(self, request, pk=None):
        """
        Add a speaker to the event.
        """
        event = self.get_object()
        speaker_id = request.data.get('speaker_id')
        speaker = get_object_or_404(User, id=speaker_id, role='speaker')
        event.speakers.add(speaker)
        event.save()
        return Response({"detail": f"Speaker {speaker.full_name} added."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def sessions(self, request, pk=None):
        """
        List all sessions for the event.
        """
        event = self.get_object()
        sessions = event.sessions.all()
        serializer = SessionSerializer(sessions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def speakers(self, request, pk=None):
        """
        List all speakers for the event.
        """
        event = self.get_object()
        speakers = event.speakers.all()
        serializer = UserShortSerializer(speakers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def delegates(self, request, pk=None):
        """
        List all delegates for the event.
        """
        event = self.get_object()
        delegates = event.delegates.all()
        serializer = UserShortSerializer(delegates, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def organizers(self, request, pk=None):
        """
        List all organizers for the event.
        """
        event = self.get_object()
        organizers = event.organizers.all()
        serializer = UserShortSerializer(organizers, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def summit_details(self, request, pk=None):
        """
        Get summit details for the event if available.
        """
        event = self.get_object()
        if hasattr(event, 'summit_details'):
            serializer = SummitSerializer(event.summit_details)
            return Response(serializer.data)
        return Response({"detail": "No summit details available."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'], permission_classes=[permissions.AllowAny])
    def conference_details(self, request, pk=None):
        """
        Get conference details for the event if available.
        """
        event = self.get_object()
        if hasattr(event, 'conference_details'):
            serializer = ConferenceSerializer(event.conference_details)
            return Response(serializer.data)
        return Response({"detail": "No conference details available."}, status=status.HTTP_404_NOT_FOUND)


class SummitViewSet(viewsets.ModelViewSet):
    """
    API endpoint for summit CRUD operations.
    """
    queryset = Summit.objects.all().select_related('event')
    serializer_class = SummitSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ConferenceViewSet(viewsets.ModelViewSet):
    """
    API endpoint for conference CRUD operations.
    """
    queryset = Conference.objects.all().select_related('event')
    serializer_class = ConferenceSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class SessionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for session CRUD operations.
    """
    queryset = Session.objects.all().select_related('event').prefetch_related('speakers')
    serializer_class = SessionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        session = serializer.save()
        # Optionally, add the creator as a speaker if role is speaker
        if self.request.user.role == 'speaker':
            session.speakers.add(self.request.user)
        session.save()
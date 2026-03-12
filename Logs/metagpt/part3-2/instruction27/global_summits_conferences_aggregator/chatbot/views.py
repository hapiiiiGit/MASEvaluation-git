from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import ChatSession, ChatMessage, UserInteraction
from .serializers import (
    ChatSessionSerializer,
    ChatMessageSerializer,
    UserInteractionSerializer,
    ChatSessionCreateSerializer,
    ChatMessageCreateSerializer,
    UserInteractionCreateSerializer,
)
from .openai_integration import get_ai_response
from events.models import Event
from users.models import User
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone

class ChatSessionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for chat session management.
    """
    queryset = ChatSession.objects.all().select_related('user', 'event')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ChatSessionCreateSerializer
        return ChatSessionSerializer

    def perform_create(self, serializer):
        session = serializer.save(user=self.request.user)
        session.is_active = True
        session.started_at = timezone.now()
        session.save()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def end(self, request, pk=None):
        """
        End a chat session.
        """
        session = self.get_object()
        if session.user != request.user and not request.user.is_superuser:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        session.is_active = False
        session.ended_at = timezone.now()
        session.save()
        return Response({"detail": "Chat session ended."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def messages(self, request, pk=None):
        """
        List all messages in the chat session.
        """
        session = self.get_object()
        messages = session.messages.all()
        serializer = ChatMessageSerializer(messages, many=True)
        return Response(serializer.data)

class ChatMessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint for chat message management.
    """
    queryset = ChatMessage.objects.all().select_related('session')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ChatMessageCreateSerializer
        return ChatMessageSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        message = serializer.save()
        session = message.session
        # If sender is user, get AI response and create bot message
        if message.sender == 'user':
            ai_response = get_ai_response(message.message, session)
            ChatMessage.objects.create(
                session=session,
                sender='bot',
                message=ai_response,
                timestamp=timezone.now(),
                is_escalated=False
            )
        message.timestamp = timezone.now()
        message.save()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def escalate(self, request, pk=None):
        """
        Escalate a chat message to human support.
        """
        message = self.get_object()
        if message.sender != 'user':
            return Response({"detail": "Only user messages can be escalated."}, status=status.HTTP_400_BAD_REQUEST)
        message.is_escalated = True
        message.save()
        # Optionally, notify admin/support here
        return Response({"detail": "Message escalated to human support."}, status=status.HTTP_200_OK)

class UserInteractionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for tracking user interactions with the chatbot.
    """
    queryset = UserInteraction.objects.all().select_related('user', 'event')
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserInteractionCreateSerializer
        return UserInteractionSerializer

    def perform_create(self, serializer):
        interaction = serializer.save(user=self.request.user)
        interaction.timestamp = timezone.now()
        interaction.save()
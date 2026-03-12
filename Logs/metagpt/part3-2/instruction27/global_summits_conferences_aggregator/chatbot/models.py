from django.db import models
from django.conf import settings
from events.models import Event

class ChatSession(models.Model):
    """
    Represents a chat session between a user and the AI chatbot.
    Optionally linked to an event for contextual support.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chat_sessions'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"ChatSession #{self.id} - {self.user.username}"

    class Meta:
        verbose_name = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'
        ordering = ['-started_at']


class ChatMessage(models.Model):
    """
    Stores individual messages exchanged in a chat session.
    """
    SENDER_CHOICES = (
        ('user', 'User'),
        ('bot', 'Bot'),
        ('admin', 'Admin'),
    )

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_escalated = models.BooleanField(default=False)  # If escalated to human support

    def __str__(self):
        return f"Message from {self.get_sender_display()} in Session #{self.session.id}"

    class Meta:
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        ordering = ['timestamp']


class UserInteraction(models.Model):
    """
    Tracks user interactions with the chatbot for analytics and personalization.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chatbot_interactions'
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='chatbot_interactions'
    )
    interaction_type = models.CharField(
        max_length=50,
        help_text="Type of interaction (e.g., FAQ, recommendation, support, escalation)"
    )
    detail = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField(default=True)

    def __str__(self):
        return f"Interaction: {self.interaction_type} by {self.user.username}"

    class Meta:
        verbose_name = 'User Interaction'
        verbose_name_plural = 'User Interactions'
        ordering = ['-timestamp']
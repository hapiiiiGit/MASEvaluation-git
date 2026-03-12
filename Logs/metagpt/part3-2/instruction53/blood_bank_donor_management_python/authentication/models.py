from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """
    Extends Django's AbstractUser to support authentication and access control.
    Additional fields can be added here if needed for registration or profile.
    """
    # You can add more fields if needed for registration/profile
    # For now, we use the default AbstractUser fields

    def __str__(self):
        return f"{self.username} ({self.email})"

class PasswordResetToken(models.Model):
    """
    Stores password reset tokens for users.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Password reset token for {self.user.username} ({'used' if self.is_used else 'active'})"
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Extends Django's built-in User model to allow for future profile fields and relationships.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
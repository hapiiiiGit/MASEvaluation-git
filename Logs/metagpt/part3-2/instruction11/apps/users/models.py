from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Additional fields can be added here if needed.
    """
    # All fields from AbstractUser are included (username, email, password, etc.)
    # See: https://docs.djangoproject.com/en/4.2/ref/contrib/auth/#user-model

    # Example: add extra fields here if required
    # phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username

class Profile(models.Model):
    """
    Profile model with a one-to-one relationship to User.
    Stores additional user information.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(blank=True, default='')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
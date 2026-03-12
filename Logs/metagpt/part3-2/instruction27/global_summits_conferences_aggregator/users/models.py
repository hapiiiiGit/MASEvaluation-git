from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('delegate', 'Delegate'),
        ('organizer', 'Organizer'),
        ('speaker', 'Speaker'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    # Common profile fields
    full_name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    organization = models.CharField(max_length=255, blank=True)
    contact_number = models.CharField(max_length=30, blank=True)
    linkedin_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)

    # Speaker-specific fields
    expertise = models.CharField(max_length=255, blank=True)
    sessions = models.ManyToManyField('events.Session', blank=True, related_name='speakers')

    # Organizer-specific fields
    managed_events = models.ManyToManyField('events.Event', blank=True, related_name='organizers')

    # Delegate-specific fields
    registered_events = models.ManyToManyField('events.Event', blank=True, related_name='delegates')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
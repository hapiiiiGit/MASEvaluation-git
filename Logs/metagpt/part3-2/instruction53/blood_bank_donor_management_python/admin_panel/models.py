from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class AdminUser(AbstractUser):
    """
    Extends Django's AbstractUser to add role and is_active fields.
    """
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('staff', 'Staff'),
        ('superadmin', 'Super Administrator'),
    ]
    role = models.CharField(max_length=32, choices=ROLE_CHOICES, default='staff')
    is_active = models.BooleanField(default=True)

    def set_role(self, role: str):
        if role in dict(self.ROLE_CHOICES):
            self.role = role
            self.save()

    def __str__(self):
        return f"{self.username} ({self.role})"

class AuditLog(models.Model):
    """
    Stores audit logs for admin actions.
    """
    ACTION_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('view', 'View'),
        ('export', 'Export'),
        ('other', 'Other'),
    ]
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(AdminUser, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=32, choices=ACTION_CHOICES)
    description = models.TextField(blank=True)
    timestamp = models.DateTimeField(default=timezone.now)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        user_str = self.user.username if self.user else "Unknown"
        return f"{self.action} by {user_str} at {self.timestamp}"
from django.db import models
from django.utils import timezone

class Donor(models.Model):
    BLOOD_TYPE_CHOICES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]

    id = models.CharField(max_length=64, primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    location = models.CharField(max_length=255)
    contact_info = models.CharField(max_length=255)
    last_donation = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def register(self, data: dict):
        """
        Register a new donor using the provided data dictionary.
        Returns the created Donor instance.
        """
        donor = Donor.objects.create(
            id=data.get('id'),
            name=data.get('name'),
            blood_type=data.get('blood_type'),
            location=data.get('location'),
            contact_info=data.get('contact_info'),
            last_donation=data.get('last_donation', None),
            is_active=data.get('is_active', True)
        )
        return donor

    def update_info(self, data: dict):
        """
        Update donor information using the provided data dictionary.
        """
        self.name = data.get('name', self.name)
        self.blood_type = data.get('blood_type', self.blood_type)
        self.location = data.get('location', self.location)
        self.contact_info = data.get('contact_info', self.contact_info)
        self.last_donation = data.get('last_donation', self.last_donation)
        self.is_active = data.get('is_active', self.is_active)
        self.save()

    def __str__(self):
        return f"{self.name} ({self.blood_type}) - {self.location}"
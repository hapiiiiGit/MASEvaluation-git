from django.db import models
from django.conf import settings

class Event(models.Model):
    EVENT_TYPE_CHOICES = (
        ('summit', 'Summit'),
        ('conference', 'Conference'),
        ('workshop', 'Workshop'),
        ('webinar', 'Webinar'),
        ('other', 'Other'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    category = models.CharField(max_length=100, blank=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    organizers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='organized_events',
        limit_choices_to={'role': 'organizer'},
        blank=True
    )
    delegates = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='attended_events',
        limit_choices_to={'role': 'delegate'},
        blank=True
    )
    speakers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='speaking_events',
        limit_choices_to={'role': 'speaker'},
        blank=True
    )

    def __str__(self):
        return f"{self.title} ({self.get_event_type_display()})"

    class Meta:
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-start_date']


class Session(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    speakers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='sessions_speaking',
        limit_choices_to={'role': 'speaker'},
        blank=True
    )
    room = models.CharField(max_length=100, blank=True)
    resources = models.TextField(blank=True)

    def __str__(self):
        return f"{self.title} ({self.event.title})"

    class Meta:
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'
        ordering = ['start_time']


class Summit(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='summit_details')
    theme = models.CharField(max_length=255, blank=True)
    sponsors = models.TextField(blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return f"Summit: {self.event.title}"

    class Meta:
        verbose_name = 'Summit'
        verbose_name_plural = 'Summits'


class Conference(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='conference_details')
    tracks = models.TextField(blank=True)
    sponsors = models.TextField(blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return f"Conference: {self.event.title}"

    class Meta:
        verbose_name = 'Conference'
        verbose_name_plural = 'Conferences'
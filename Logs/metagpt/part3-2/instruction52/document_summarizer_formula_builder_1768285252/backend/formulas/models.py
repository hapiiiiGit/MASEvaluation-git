from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField

class Formula(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='formulas'
    )
    name = models.CharField(max_length=255)
    expression = models.TextField(help_text="Mathematical expression, e.g., 'a + b * c'")
    variables = JSONField(
        default=dict,
        blank=True,
        help_text="Dictionary of variable names and descriptions, e.g., {'a': 'Revenue', 'b': 'Cost'}"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    shared_with = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='shared_formulas',
        blank=True
    )

    def __str__(self):
        return f"{self.name} ({self.owner.username})"
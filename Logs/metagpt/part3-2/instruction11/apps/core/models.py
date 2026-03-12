from django.db import models
from django.conf import settings

class CoreData(models.Model):
    """
    CoreData model representing a generic data entity owned by a user.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coredata'
    )
    data_field = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CoreData(id={self.id}, owner={self.owner.username}, data_field={self.data_field})"
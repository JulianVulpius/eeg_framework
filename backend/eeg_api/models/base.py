from django.db import models
from django.conf import settings

class AuditBaseModel(models.Model):
    """
    An abstract base class that provides self-updating 
    'created' and 'changed' audit fields.
    """
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="%(class)s_created"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name="%(class)s_changed"
    )
    changed_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
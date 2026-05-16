from django.db import models
from .base import AuditBaseModel

class ComponentType(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="e.g., 'Text Input Field'")
    # Matches the exact frontend string to render the correct .vue file
    identifier = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'ComponentType'

    def __str__(self):
        return f"{self.name} ({self.identifier})"

class ComponentCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'ComponentCategory'

    def __str__(self):
        return self.name

class Component(AuditBaseModel):
    category = models.ForeignKey(ComponentCategory, on_delete=models.PROTECT, null=True, blank=True)
    component_type = models.ForeignKey(ComponentType, on_delete=models.PROTECT)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    parameter = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'Component'

    def __str__(self):
        return f"{self.name} [{self.component_type.identifier}]"
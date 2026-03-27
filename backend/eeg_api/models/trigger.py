from django.db import models
from .base import AuditBaseModel

class TriggerDefinition(models.Model):
    name = models.CharField(max_length=100)
    
    trigger_character = models.CharField(max_length=50)

    class Meta:
        db_table = 'TriggerDefinition'

    def __str__(self):
        return f"{self.name} ({self.trigger_character})"

class TriggerGroupCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'TriggerGroupCategory'

    def __str__(self):
        return self.name

class TriggerGroup(AuditBaseModel):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(TriggerGroupCategory, on_delete=models.PROTECT, null=True, blank=True)
    
    triggers = models.ManyToManyField(
        TriggerDefinition,
        through='TriggerGroupDefinition',
        related_name='trigger_groups'
    )

    class Meta:
        db_table = 'TriggerGroup'

    def __str__(self):
        return self.name


class TriggerGroupDefinition(models.Model):
    group = models.ForeignKey(TriggerGroup, on_delete=models.CASCADE)
    definition = models.ForeignKey(TriggerDefinition, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('group', 'definition')
        db_table = 'TriggerGroup_TriggerDefinition'

    def __str__(self):
        return f"{self.group.name} -> {self.definition.name}"


class TriggerPair(models.Model):
    name = models.CharField(max_length=100)
    
    # We must provide distinct related_names since both point to the same target table
    start_trigger = models.ForeignKey(
        TriggerDefinition, 
        on_delete=models.PROTECT, 
        related_name='pair_starts'
    )
    end_trigger = models.ForeignKey(
        TriggerDefinition, 
        on_delete=models.PROTECT, 
        related_name='pair_ends'
    )

    class Meta:
        db_table = 'TriggerPair'

    def __str__(self):
        return f"{self.name}: {self.start_trigger.name} -> {self.end_trigger.name}"

class TriggerHotkeyMapping(AuditBaseModel):
    group = models.ForeignKey(TriggerGroup, on_delete=models.CASCADE, related_name='hotkey_mappings')
    
    definition = models.ForeignKey(TriggerDefinition, on_delete=models.CASCADE)
    key_code = models.CharField(max_length=50)

    class Meta:
        db_table = 'TriggerHotkeyMapping'
        # Prevent the same key from being used twice in the same group
        unique_together = ('group', 'key_code')

    def __str__(self):
        return f"{self.group.name}: {self.key_code} -> {self.definition.name}"
from django.db import models
from django.conf import settings
from .ui import Event, PageGroup
from .subject import SubjectProfile
from .device import DeviceModel

class EventRole(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='roles')
    name = models.CharField(max_length=100)
    
    # stores permission flags for later use
    permissions = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = 'EventRole'
        unique_together = ('event', 'name')

    def __str__(self):
        return f"{self.name} ({self.event.name})"

class EventGroupPageGroup(models.Model):
    event_group = models.ForeignKey('EventGroup', on_delete=models.CASCADE)
    page_group = models.ForeignKey(PageGroup, on_delete=models.CASCADE)

    class Meta:
        db_table = 'EventGroup_PageGroup'
        unique_together = ('event_group', 'page_group')

    def __str__(self):
        return f"{self.event_group.name} -> {self.page_group.name}"

class EventGroup(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    
    page_groups = models.ManyToManyField(
        PageGroup, 
        through='EventGroupPageGroup',
        related_name='event_groups', 
        blank=True
    )

    class Meta:
        db_table = 'EventGroup'
        unique_together = ('event', 'name')

    def __str__(self):
        return f"{self.name} ({self.event.name})"

class EventSubjectAssignment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='subject_assignments')
    subject = models.ForeignKey(SubjectProfile, on_delete=models.CASCADE, related_name='event_assignments')
    group = models.ForeignKey(EventGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='subjects')

    class Meta:
        db_table = 'EventSubjectAssignment'
        unique_together = ('event', 'subject', 'group')

    def __str__(self):
        group_name = self.group.name if self.group else "unassigned"
        return f"{self.subject.identifier} -> {group_name} @ {self.event.name}"

class EventStaffAssignment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_roles')
    role = models.ForeignKey(EventRole, on_delete=models.CASCADE, related_name='assignments')
    event_group = models.ForeignKey(EventGroup, on_delete=models.CASCADE, null=True, blank=True, related_name='staff')

    class Meta:
        db_table = 'EventStaffAssignment'
        unique_together = ('user', 'role', 'event_group')

    def __str__(self):
        scope = f"group: {self.event_group.name}" if self.event_group else "global"
        return f"{self.user} as {self.role.name} ({scope}) @ {self.role.event.name}"

class EventDeviceModel(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='device_pool')
    device_model = models.ForeignKey('eeg_api.DeviceModel', on_delete=models.CASCADE, related_name='event_pools')

    class Meta:
        db_table = 'Event_DeviceModel'
        unique_together = ('event', 'device_model')

    def __str__(self):
        return f"{self.device_model.name} allowed in {self.event.name}"


class EventGroupPageGroupDevice(models.Model):
    phase = models.ForeignKey('EventGroupPageGroup', on_delete=models.CASCADE, related_name='device_configs')
    device_from_pool = models.ForeignKey('EventDeviceModel', on_delete=models.CASCADE, related_name='phase_configs')
    
    metadata_instance = models.OneToOneField(
        'eeg_api.MetaDataGroupInstance', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='phase_device_config'
    )
    
    expected_channels = models.JSONField(
        default=list, 
        blank=True,
        help_text='List of expected channel names selected from Master, e.g., ["Fp1", "Fp2", "Cz"]'
    )

    is_archived = models.BooleanField(default=False)

    class Meta:
        db_table = 'EventGroupPageGroup_Device'
        unique_together = ('phase', 'device_from_pool')

    def __str__(self):
        return f"Config for {self.device_from_pool.device_model.name} in {self.phase}"
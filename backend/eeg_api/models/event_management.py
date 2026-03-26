from django.db import models
from django.conf import settings
from .ui import Event, PageGroup
from .subject import SubjectProfile

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

class EventGroup(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='groups')
    name = models.CharField(max_length=150)
    
    assigned_page_group = models.ForeignKey(
        PageGroup, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_event_groups'
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
        # a subject can only be assigned to one group per event
        unique_together = ('event', 'subject')

    def __str__(self):
        group_name = self.group.name if self.group else "unassigned"
        return f"{self.subject.identifier} -> {group_name} @ {self.event.name}"

class EventStaffAssignment(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='staff_assignments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='event_roles')
    role = models.ForeignKey(EventRole, on_delete=models.CASCADE, related_name='assignments')
    
    # limits the job to a specific group if needed. if null, it applies globally.
    target_group = models.ForeignKey(EventGroup, on_delete=models.CASCADE, null=True, blank=True, related_name='staff')

    class Meta:
        db_table = 'EventStaffAssignment'
        # allows a user to have multiple different roles in the same event and group
        unique_together = ('event', 'user', 'role', 'target_group')

    def __str__(self):
        scope = f"group: {self.target_group.name}" if self.target_group else "global"
        return f"{self.user} as {self.role.name} ({scope}) @ {self.event.name}"
from django.db import models
from .base import AuditBaseModel
from .subject import SubjectProfile
from .ui import Event, PageGroup, Location

class Session(AuditBaseModel):
    subject = models.ForeignKey(SubjectProfile, on_delete=models.PROTECT, related_name='sessions')
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name='sessions')
    page_group = models.ForeignKey(PageGroup, on_delete=models.PROTECT, related_name='sessions')
    start_datetime = models.DateTimeField()
    location = models.ForeignKey(
        Location, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sessions'
    )

    class Meta:
        db_table = 'Session'
        unique_together = ('subject', 'event', 'page_group')

    def __str__(self):
        return f"Session {self.id}: {self.subject.identifier} - {self.event.name} ({self.page_group.name})"
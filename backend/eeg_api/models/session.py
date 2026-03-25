from django.db import models
from .base import AuditBaseModel
from .subject import SubjectProfile
from .ui import Event, PageGroup, Location
from .device import DeviceInstance, DeviceModel
from .trigger import TriggerGroup

class FrequencyBand(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    low_hz = models.FloatField()
    high_hz = models.FloatField()

    class Meta:
        db_table = 'FrequencyBand'

    def __str__(self):
        return f"{self.name} ({self.low_hz}-{self.high_hz} Hz)"

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

class EEGDataFile(AuditBaseModel):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='eeg_files')
    device_instance = models.ForeignKey(DeviceInstance, on_delete=models.PROTECT)
    source = models.CharField(max_length=500)
    trigger_groups = models.ManyToManyField(TriggerGroup, through='EEGDataFileTriggerGroup', related_name='eeg_files')

    class Meta:
        db_table = 'EEGDataFile'

    def __str__(self):
        return f"EEG Data for Session {self.session.id}"

class EEGDataFileTriggerGroup(models.Model):
    eeg_data_file = models.ForeignKey(EEGDataFile, on_delete=models.CASCADE)
    trigger_group = models.ForeignKey(TriggerGroup, on_delete=models.CASCADE)

    class Meta:
        db_table = 'EEGDataFile_TriggerGroup'
        unique_together = ('eeg_data_file', 'trigger_group')

class HeartRateDataFile(AuditBaseModel):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='heart_rate_files')
    device_model = models.ForeignKey(DeviceModel, on_delete=models.PROTECT, null=True, blank=True)
    source = models.CharField(max_length=500)
    note = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'HeartRateDataFile'
from django.db import models
from .base import AuditBaseModel
from .subject import SubjectProfile
from .ui import Event
from .device import DeviceInstance
from .trigger import TriggerGroup

# -----------------------------------------------------------------------------
# 1. FREQUENCY BANDS
# -----------------------------------------------------------------------------
class FrequencyBand(models.Model):
    name = models.CharField(max_length=50, unique=True, help_text="e.g., Alpha, Beta, Theta")
    description = models.TextField(blank=True, null=True)
    
    # FloatFields used here since frequencies often have decimals (e.g., 0.5 Hz)
    low_hz = models.FloatField()
    high_hz = models.FloatField()

    class Meta:
        db_table = 'FrequencyBand'

    def __str__(self):
        return f"{self.name} ({self.low_hz}-{self.high_hz} Hz)"

# -----------------------------------------------------------------------------
# 2. THE SESSION ANCHOR
# -----------------------------------------------------------------------------
class Session(AuditBaseModel):
    """
    The root anchor point for any recording. 
    One Subject + One Event + One Time + One Location.
    """
    subject = models.ForeignKey(SubjectProfile, on_delete=models.PROTECT, related_name='sessions')
    event = models.ForeignKey(Event, on_delete=models.PROTECT, related_name='sessions')
    
    start_datetime = models.DateTimeField(help_text="The exact date and time the session started")
    
    location = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'Session'

    def __str__(self):
        formatted_time = self.start_datetime.strftime("%d-%m-%Y %H:%M")
        return f"Session {self.id}: {self.subject.identifier} - {self.event.name} on {formatted_time}"

# -----------------------------------------------------------------------------
# 3. DATA FILES
# -----------------------------------------------------------------------------
class EEGDataFile(AuditBaseModel):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='eeg_files')
    device_instance = models.ForeignKey(DeviceInstance, on_delete=models.PROTECT)
    
    source = models.CharField(max_length=500, help_text="File path or URI to the raw EDF/CSV data")
    
    trigger_groups = models.ManyToManyField(
        TriggerGroup,
        through='EEGDataFileTriggerGroup',
        related_name='eeg_files'
    )

    class Meta:
        db_table = 'EEGDataFile'

    def __str__(self):
        return f"EEG Data for Session {self.session.id} (Device: {self.device_instance.name})"

class EEGDataFileTriggerGroup(models.Model):
    eeg_data_file = models.ForeignKey(EEGDataFile, on_delete=models.CASCADE)
    trigger_group = models.ForeignKey(TriggerGroup, on_delete=models.CASCADE)

    class Meta:
        db_table = 'EEGDataFile_TriggerGroup'
        unique_together = ('eeg_data_file', 'trigger_group')

    def __str__(self):
        return f"File {self.eeg_data_file.id} uses Triggers: {self.trigger_group.name}"

class HeartRateDataFile(AuditBaseModel):
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='heart_rate_files')
    source = models.CharField(max_length=500, help_text="File path or URI to the heart rate data")
    note = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'HeartRateDataFile'

    def __str__(self):
        return f"HR Data for Session {self.session.id}"
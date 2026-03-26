from django.db import models
from .base import AuditBaseModel

def eeg_directory_path(instance, filename):
    return f'recordings/eeg/{filename}'

def hr_directory_path(instance, filename):
    return f'recordings/heartrate/{filename}'

def generic_directory_path(instance, filename):
    return f'recordings/generic/{filename}'


class EEGDataFile(AuditBaseModel):
    session = models.ForeignKey('eeg_api.Session', on_delete=models.CASCADE, related_name='eeg_recordings')
    device_instance = models.ForeignKey('eeg_api.DeviceInstance', on_delete=models.PROTECT)
    trigger_group = models.ForeignKey('eeg_api.TriggerGroup', on_delete=models.PROTECT, null=True, blank=True)
    file = models.FileField(upload_to=eeg_directory_path)

    class Meta:
        db_table = 'EEGDataFile'

    def __str__(self):
        return f"EEG Data - Session {self.session_id}"


class HeartRateDataFile(AuditBaseModel):
    session = models.ForeignKey('eeg_api.Session', on_delete=models.CASCADE, related_name='hr_recordings')
    device_model = models.ForeignKey('eeg_api.DeviceModel', on_delete=models.PROTECT)
    trigger_group = models.ForeignKey('eeg_api.TriggerGroup', on_delete=models.PROTECT, null=True, blank=True)
    file = models.FileField(upload_to=hr_directory_path)

    class Meta:
        db_table = 'HeartRateDataFile'

    def __str__(self):
        return f"HR Data - Session {self.session_id}"


class GenericRecordingCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'GenericRecordingCategory'

    def __str__(self):
        return self.name


class GenericRecording(AuditBaseModel):
    session = models.ForeignKey('eeg_api.Session', on_delete=models.CASCADE, related_name='generic_recordings')
    category = models.ForeignKey(GenericRecordingCategory, on_delete=models.PROTECT)
    file = models.FileField(upload_to=generic_directory_path)

    trigger_group = models.ForeignKey(
        'TriggerGroup', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='generic_recordings'
    )

    class Meta:
        db_table = 'GenericRecording'

    def __str__(self):
        return f"{self.category.name} - Session {self.session_id}"
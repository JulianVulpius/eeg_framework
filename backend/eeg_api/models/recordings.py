import os
from django.db import models
from django.utils.text import get_valid_filename
from .base import AuditBaseModel

def eeg_directory_path(instance, filename):
    event_name = get_valid_filename(instance.session.event.name)
    return f'recordings/eeg/{event_name}/{filename}'

def hr_directory_path(instance, filename):
    event_name = get_valid_filename(instance.session.event.name)
    return f'recordings/heartrate/{event_name}/{filename}'

def generic_directory_path(instance, filename):
    event_name = get_valid_filename(instance.session.event.name)
    
    if instance.category:
        cat_name = get_valid_filename(instance.category.name)
    else:
        cat_name = "undefined"
    return f'recordings/custom/{cat_name}/{event_name}/{filename}'

def cleanup_old_upload(model_class, session, order):
    """Sucht nach alten Dateien für denselben Slot und löscht die physische Datei."""
    old_entry = model_class.objects.filter(session=session, order=order).first()
    if old_entry and old_entry.file:
        if os.path.isfile(old_entry.file.path):
            os.remove(old_entry.file.path)
        old_entry.delete()

class EEGDataFile(AuditBaseModel):
    session = models.ForeignKey('eeg_api.Session', on_delete=models.CASCADE, related_name='eeg_recordings')
    device_instance = models.ForeignKey('eeg_api.DeviceInstance', on_delete=models.PROTECT, null=True, blank=True)
    trigger_group = models.ForeignKey('eeg_api.TriggerGroup', on_delete=models.PROTECT, null=True, blank=True)
    file = models.FileField(upload_to=eeg_directory_path)
    order = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        cleanup_old_upload(EEGDataFile, self.session, self.order)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'EEGDataFile'
        ordering = ['order']

    def __str__(self):
        return f"EEG Data - Session {self.session_id} (Pos: {self.order})"


class HeartRateDataFile(AuditBaseModel):
    session = models.ForeignKey('eeg_api.Session', on_delete=models.CASCADE, related_name='hr_recordings')
    device_model = models.ForeignKey('eeg_api.DeviceModel', on_delete=models.PROTECT, null=True, blank=True)
    trigger_group = models.ForeignKey('eeg_api.TriggerGroup', on_delete=models.PROTECT, null=True, blank=True)
    file = models.FileField(upload_to=hr_directory_path)
    order = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        cleanup_old_upload(HeartRateDataFile, self.session, self.order)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'HeartRateDataFile'
        ordering = ['order']

    def __str__(self):
        return f"HR Data - Session {self.session_id} (Pos: {self.order})"


class GenericRecordingCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'GenericRecordingCategory'

    def __str__(self):
        return self.name


class GenericRecording(AuditBaseModel):
    session = models.ForeignKey('eeg_api.Session', on_delete=models.CASCADE, related_name='generic_recordings')
    file = models.FileField(upload_to=generic_directory_path)
    category = models.ForeignKey(GenericRecordingCategory, on_delete=models.PROTECT, null=True, blank=True)
    order = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)

    trigger_group = models.ForeignKey(
        'TriggerGroup', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='generic_recordings'
    )


    def save(self, *args, **kwargs):
        cleanup_old_upload(GenericRecording, self.session, self.order)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'GenericRecording'
        ordering = ['order']
        
    def __str__(self):
        cat_name = self.category.name if self.category else "Uncategorized"
        return f"{cat_name} - Session {self.session_id} (Pos: {self.order})"
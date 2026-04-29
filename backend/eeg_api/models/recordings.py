import os
from django.db import models
from django.apps import apps
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
        cat_name = "Uncategorized"
    return f'recordings/custom/{cat_name}/{event_name}/{filename}'

def cleanup_old_upload(session, order, current_instance):
    
    EEGDataFile = apps.get_model('eeg_api', 'EEGDataFile')
    HeartRateDataFile = apps.get_model('eeg_api', 'HeartRateDataFile')
    GenericRecording = apps.get_model('eeg_api', 'GenericRecording')
    
    for model_class in [EEGDataFile, HeartRateDataFile, GenericRecording]:
        old_entries = model_class.objects.filter(session=session, order=order)
        
        for old_entry in old_entries:
            if old_entry.pk == current_instance.pk and type(old_entry) == type(current_instance):
                continue
            
            if old_entry.file and os.path.isfile(old_entry.file.path):
                try:
                    os.remove(old_entry.file.path)
                except OSError:
                    pass
            
            old_entry.delete()

class EEGDataFile(AuditBaseModel):
    session = models.ForeignKey('eeg_api.Session', on_delete=models.CASCADE, related_name='eeg_recordings')
    device_instance = models.ForeignKey('eeg_api.DeviceInstance', on_delete=models.PROTECT, null=True, blank=True)
    trigger_group = models.ForeignKey('eeg_api.TriggerGroup', on_delete=models.PROTECT, null=True, blank=True)
    file = models.FileField(upload_to=eeg_directory_path)
    order = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        cleanup_old_upload(self.session, self.order, self)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'EEGDataFile'
        ordering = ['order']

    def __str__(self):
        return f"EEG Data - Session {self.session_id} (Pos: {self.order})"


class HeartRateDataFile(AuditBaseModel):
    session = models.ForeignKey('eeg_api.Session', on_delete=models.CASCADE, related_name='hr_recordings')
    device_instance = models.ForeignKey('eeg_api.DeviceInstance', on_delete=models.PROTECT, null=True, blank=True)
    trigger_group = models.ForeignKey('eeg_api.TriggerGroup', on_delete=models.PROTECT, null=True, blank=True)
    file = models.FileField(upload_to=hr_directory_path)
    order = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        cleanup_old_upload(self.session, self.order, self)
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
    device_instance = models.ForeignKey('eeg_api.DeviceInstance', on_delete=models.PROTECT, null=True, blank=True)
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
        cleanup_old_upload(self.session, self.order, self)
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'GenericRecording'
        ordering = ['order']
        
    def __str__(self):
        cat_name = self.category.name if self.category else "Uncategorized"
        return f"{cat_name} - Session {self.session_id} (Pos: {self.order})"
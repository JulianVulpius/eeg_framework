from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from .base import AuditBaseModel

class FrequencyBand(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)
    low_hz = models.FloatField()
    high_hz = models.FloatField()

    class Meta:
        db_table = 'FrequencyBand'

    def __str__(self):
        return f"{self.name} ({self.low_hz}-{self.high_hz} Hz)"

class EEGChannel(models.Model):
    name = models.CharField(
        max_length=50, 
        unique=True, 
        help_text="Standardized channel name (e.g., 'Fp1', 'Cz')"
    )

    class Meta:
        db_table = 'EEGChannel'

    def __str__(self):
        return self.name

class ManufacturerCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'ManufacturerCategory'

    def __str__(self):
        return self.name

class Manufacturer(models.Model):
    name = models.CharField(max_length=150, unique=True)
    category = models.ForeignKey(
        ManufacturerCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='manufacturers'
    )
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'Manufacturer'

    def __str__(self):
        return self.name

class DeviceModelCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'DeviceModelCategory'

    def __str__(self):
        return self.name

class DeviceModel(models.Model):
    name = models.CharField(max_length=150, unique=True)
    manufacturer = models.ForeignKey(
        Manufacturer, 
        on_delete=models.SET_NULL,
        null=True, 
        blank=True, 
        related_name='device_models'
    )
    category = models.ForeignKey(
        DeviceModelCategory, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='device_models'
    )
    is_eeg = models.BooleanField(default=True)
    channels = models.ManyToManyField(
        EEGChannel,
        through='DeviceModelEEGChannel',
        related_name='device_models'
    )
    
    hardware_specs = models.OneToOneField(
        'eeg_api.MetaDataGroupInstance', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='specs_for_device_model',
        help_text="Immutable hardware facts (Never cloned downstream)"
    )

    default_settings = models.OneToOneField(
        'eeg_api.MetaDataGroupInstance', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='settings_for_device_model',
        help_text="Factory default variables (Cloned downstream)"
    )
    
    is_archived = models.BooleanField(default=False)
    metadata_instances = GenericRelation('eeg_api.MetaDataGroupInstance')

    class Meta:
        db_table = 'DeviceModel'

    def __str__(self):
        return f"{self.manufacturer} {self.name}" if self.manufacturer else self.name

class DeviceModelEEGChannel(models.Model):
    device_model = models.ForeignKey(DeviceModel, on_delete=models.CASCADE)
    eeg_channel = models.ForeignKey(EEGChannel, on_delete=models.CASCADE)

    class Meta:
        db_table = 'DeviceModel_EEGChannel'
        unique_together = ('device_model', 'eeg_channel')

    def __str__(self):
        return f"{self.device_model.name} supports {self.eeg_channel.name}"

class DeviceInstance(AuditBaseModel):
    session = models.ForeignKey(
        'eeg_api.Session', 
        on_delete=models.CASCADE, 
        related_name='device_instances'
    )
    
    device_model = models.ForeignKey(
        'eeg_api.DeviceModel', 
        on_delete=models.PROTECT, 
        related_name='instances'
    )

    phase_config = models.ForeignKey(
        'eeg_api.EventGroupPageGroupDevice', 
        on_delete=models.PROTECT, 
        related_name='instances'
    )
    
    metadata_overwrite_instance = models.OneToOneField(
        'eeg_api.MetaDataGroupInstance', 
        on_delete=models.PROTECT, 
        null=True, 
        blank=True,
        related_name='session_device_instance'
    )
    
    final_channels = models.JSONField(
        default=dict, 
        blank=True, 
        help_text='JSON dict of channels and their status, e.g., {"Fp1": "GOOD", "Fz": "NOISY"}'
    )

    class Meta:
        db_table = 'DeviceInstance'

    def __str__(self):
        return f"Device Instance for Session {self.session.id} ({self.device_model.name})"
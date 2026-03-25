from django.db import models
from .base import AuditBaseModel

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

class Manufacturer(models.Model):
    name = models.CharField(
        max_length=150, 
        unique=True,
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
    model = models.ForeignKey(DeviceModel, on_delete=models.PROTECT)
    
    name = models.CharField(
        max_length=150, 
        help_text="Internal name or asset tag for this specific physical device (e.g., 'Lab Headset A')"
    )
    
    active_channels = models.ManyToManyField(
        EEGChannel,
        through='DeviceInstanceEEGChannel',
        related_name='device_instances'
    )

    class Meta:
        db_table = 'DeviceInstance'

    def __str__(self):
        return f"{self.name} ({self.model.name})"

class DeviceInstanceEEGChannel(models.Model):
    device_instance = models.ForeignKey(DeviceInstance, on_delete=models.CASCADE)
    eeg_channel = models.ForeignKey(EEGChannel, on_delete=models.CASCADE)
    
    data_column_index = models.PositiveIntegerField(
        help_text="The exact column index (e.g., 0, 1, 2) in the EEG data file"
    )

    class Meta:
        db_table = 'DeviceInstance_EEGChannel'
        unique_together = ('device_instance', 'eeg_channel')
        # Automatically sort queries by the column index so  parsing script reads them in order
        ordering = ['data_column_index'] 

    def __str__(self):
        return f"{self.device_instance.name} - {self.eeg_channel.name} (Col: {self.data_column_index})"
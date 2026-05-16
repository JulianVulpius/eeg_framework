from django.db import models

class LocationCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'LocationCategory'

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(LocationCategory, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        db_table = 'Location'

    def __str__(self):
        return self.name

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
    name = models.CharField(max_length=50, unique=True, help_text="Standardized channel name (e.g., 'Fp1', 'Cz')")

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
    category = models.ForeignKey(ManufacturerCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='manufacturers')
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'Manufacturer'

    def __str__(self):
        return self.name
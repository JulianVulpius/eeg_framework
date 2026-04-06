import os
from django.db import models
from .base import AuditBaseModel

def media_directory_path(instance, filename):
    return f'assets/{instance.media_type.lower()}/{filename}'

class MediaAssetCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'MediaAssetCategory'

    def __str__(self):
        return self.name

class MediaAsset(AuditBaseModel):
    TYPE_CHOICES = (
        ('IMAGE', 'Image'),
        ('DOCUMENT', 'Document'),
        ('ICON', 'Icon'),
        ('VIDEO', 'Video'),
        ('AUDIO', 'Audio'),
    )
    
    category = models.ForeignKey(MediaAssetCategory, on_delete=models.PROTECT, null=True, blank=True, related_name='assets')
    file = models.FileField(upload_to=media_directory_path)
    media_type = models.CharField(max_length=15, choices=TYPE_CHOICES, default='IMAGE')
    original_filename = models.CharField(max_length=255)
    alt_text = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'MediaAsset'
    
    def __str__(self):
        return self.original_filename

    def save(self, *args, **kwargs):
        if self.file and not self.original_filename:
            self.original_filename = os.path.basename(self.file.name)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.file and os.path.isfile(self.file.path):
            try:
                os.remove(self.file.path)
            except OSError:
                pass
        super().delete(*args, **kwargs)
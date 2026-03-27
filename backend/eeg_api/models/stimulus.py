from django.db import models
from .base import AuditBaseModel

def stimulus_directory_path(instance, filename):
    return f'stimuli/{instance.type.lower()}/{filename}'

class StimulusCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'StimulusCategory'

    def __str__(self):
        return self.name


class Stimulus(AuditBaseModel):
    TYPE_CHOICES = (
        ('AUDIO', 'Audio'),
        ('IMAGE', 'Image'),
        ('VIDEO', 'Video'),
    )
    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey(StimulusCategory, on_delete=models.PROTECT, null=True, blank=True)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='AUDIO')
    
    file = models.FileField(upload_to=stimulus_directory_path, blank=True, null=True)
    duration = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'Stimulus'
    
    def __str__(self):
        return self.name

class PlaylistCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'PlaylistCategory'

    def __str__(self):
        return self.name

class StimulusPlaylist(AuditBaseModel):
    name = models.CharField(max_length=150)
    category = models.ForeignKey(PlaylistCategory, on_delete=models.PROTECT, null=True, blank=True)
    
    stimuli = models.ManyToManyField(
        Stimulus, 
        through='StimulusPlaylistStimulus',
        related_name='playlists'
    )

    class Meta:
        db_table = 'StimulusPlaylist'

    def __str__(self):
        return self.name


class StimulusPlaylistStimulus(models.Model):
    playlist = models.ForeignKey(StimulusPlaylist, on_delete=models.CASCADE)
    stimulus = models.ForeignKey(Stimulus, on_delete=models.CASCADE)
    
    order = models.PositiveIntegerField(help_text="Order of the stimulus in the playlist")

    class Meta:
        db_table = 'StimulusPlaylist_Stimulus'
        ordering = ['order']
        unique_together = ('playlist', 'order')

    def __str__(self):
        return f"{self.playlist.name} - {self.stimulus.name} (Pos: {self.order})"
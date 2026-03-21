from django.db import models

class StimulusCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'StimulusCategory'

    def __str__(self):
        return self.name


class Stimulus(models.Model):
    category = models.ForeignKey(StimulusCategory, on_delete=models.PROTECT)
    name = models.CharField(max_length=150)
    duration = models.PositiveIntegerField(default=10, help_text="Duration in seconds")
    
    # source is file path (for now)
    source = models.CharField(max_length=255, help_text="Path or URI to the stimulus file/resource")

    class Meta:
        db_table = 'Stimulus'

    def __str__(self):
        return self.name


class StimulusPlaylist(models.Model):
    name = models.CharField(max_length=150)
    
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
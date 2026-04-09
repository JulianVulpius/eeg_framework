from rest_framework import viewsets
from eeg_api.models.stimulus import Stimulus, Playlist
from eeg_api.serializers.stimulus import StimulusSerializer, PlaylistSerializer

class StimulusViewSet(viewsets.ModelViewSet):
    queryset = Stimulus.objects.all().order_by('id')
    serializer_class = StimulusSerializer

class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all().order_by('id')
    serializer_class = PlaylistSerializer
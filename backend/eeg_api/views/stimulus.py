from rest_framework import viewsets
from eeg_api.models.stimulus import Stimulus, StimulusPlaylist
from eeg_api.serializers.stimulus import StimulusSerializer, StimulusPlaylistSerializer

class StimulusViewSet(viewsets.ModelViewSet):
    queryset = Stimulus.objects.all().order_by('id')
    serializer_class = StimulusSerializer

class StimulusPlaylistViewSet(viewsets.ModelViewSet):
    queryset = StimulusPlaylist.objects.all().order_by('id')
    serializer_class = StimulusPlaylistSerializer
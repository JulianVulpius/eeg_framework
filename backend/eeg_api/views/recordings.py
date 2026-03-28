from rest_framework import viewsets
from eeg_api.models.recordings import EEGDataFile, HeartRateDataFile, GenericRecording
from eeg_api.serializers.recordings import (
    EEGDataFileSerializer, HeartRateDataFileSerializer, GenericRecordingSerializer
)

class EEGDataFileViewSet(viewsets.ModelViewSet):
    queryset = EEGDataFile.objects.all().order_by('-created_at')
    serializer_class = EEGDataFileSerializer

class HeartRateDataFileViewSet(viewsets.ModelViewSet):
    queryset = HeartRateDataFile.objects.all().order_by('-created_at')
    serializer_class = HeartRateDataFileSerializer

class GenericRecordingViewSet(viewsets.ModelViewSet):
    queryset = GenericRecording.objects.all().order_by('-created_at')
    serializer_class = GenericRecordingSerializer
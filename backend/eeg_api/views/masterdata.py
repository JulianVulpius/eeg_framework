from rest_framework import viewsets
from eeg_api.models import Location, FrequencyBand, EEGChannel, Manufacturer
from eeg_api.serializers.masterdata import (
    LocationSerializer, FrequencyBandSerializer, 
    EEGChannelSerializer, ManufacturerSerializer
)

class LocationViewSet(viewsets.ModelViewSet):
    """Handles CRUD operations for laboratory and testing locations."""
    queryset = Location.objects.all().order_by('name')
    serializer_class = LocationSerializer

class FrequencyBandViewSet(viewsets.ModelViewSet):
    """Handles standard frequency band definitions (e.g., Alpha, Beta)."""
    queryset = FrequencyBand.objects.all().order_by('id')
    serializer_class = FrequencyBandSerializer

class EEGChannelViewSet(viewsets.ModelViewSet):
    """Handles standardized EEG channel nomenclature."""
    queryset = EEGChannel.objects.all().order_by('name')
    serializer_class = EEGChannelSerializer

class ManufacturerViewSet(viewsets.ModelViewSet):
    """Handles hardware manufacturers."""
    queryset = Manufacturer.objects.all().order_by('name')
    serializer_class = ManufacturerSerializer
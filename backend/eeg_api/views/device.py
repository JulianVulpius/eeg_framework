from rest_framework import viewsets
from eeg_api.models.device import DeviceModel, Manufacturer, EEGChannel, FrequencyBand
from eeg_api.serializers.device import (
    DeviceModelSerializer, ManufacturerSerializer, 
    EEGChannelSerializer, FrequencyBandSerializer
)

class FrequencyBandViewSet(viewsets.ModelViewSet):
    queryset = FrequencyBand.objects.all().order_by('id')
    serializer_class = FrequencyBandSerializer

class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all().order_by('name')
    serializer_class = ManufacturerSerializer

class EEGChannelViewSet(viewsets.ModelViewSet):
    queryset = EEGChannel.objects.all().order_by('name')
    serializer_class = EEGChannelSerializer

class DeviceModelViewSet(viewsets.ModelViewSet):
    queryset = DeviceModel.objects.all().order_by('id')
    serializer_class = DeviceModelSerializer
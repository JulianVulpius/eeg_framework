from django.db.models import Exists, OuterRef
from django.db.models import ProtectedError
from rest_framework import viewsets, status
from eeg_api.models.device import DeviceModel, Manufacturer, EEGChannel, FrequencyBand, DeviceInstance
from eeg_api.serializers.device import (
    DeviceModelSerializer, ManufacturerSerializer, 
    EEGChannelSerializer, FrequencyBandSerializer,
    DeviceInstanceSerializer
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
    serializer_class = DeviceModelSerializer

    def get_queryset(self):
        return DeviceModel.objects.annotate(
            is_locked=Exists(DeviceInstance.objects.filter(device_model=OuterRef('pk')))
        ).order_by('name')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            instance.is_archived = True
            instance.save()
            return Response(
                {"message": "Device is in use and has been archived instead of deleted."},
                status=status.HTTP_200_OK
            )

class DeviceInstanceViewSet(viewsets.ModelViewSet):
    queryset = DeviceInstance.objects.all()
    serializer_class = DeviceInstanceSerializer

    def perform_create(self, serializer):
        device_instance = serializer.save()
        
        if device_instance.phase_config.metadata_instance:
            cloned_metadata = clone_metadata_group_instance(
                source_instance=device_instance.phase_config.metadata_instance,
                target_object=device_instance
            )
            device_instance.metadata_overwrite_instance = cloned_metadata
            
            expected = device_instance.phase_config.expected_channels
            
            device_instance.final_channels = {ch: "GOOD" for ch in expected}
            
            device_instance.save()
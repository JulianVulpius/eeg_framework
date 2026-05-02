from django.db.models import Exists, OuterRef
from django.contrib.contenttypes.models import ContentType
from django.db.models import ProtectedError
from eeg_api.utils import clone_metadata_group_instance
from rest_framework import viewsets, status
from eeg_api.models.device import DeviceModel, Manufacturer, EEGChannel, FrequencyBand, DeviceInstance
from eeg_api.models.metadata import MetaDataGroupInstance, MetaDataValue, MetaDataDefinition
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

    def get_queryset(self):
        queryset = super().get_queryset()
        session_id = self.request.query_params.get('session')
        if session_id:
            queryset = queryset.filter(session_id=session_id)
        return queryset

    def perform_create(self, serializer):
        metadata_overwrite_values = self.request.data.get('metadata_overwrite_values', None)
        
        instance = serializer.save()

        if instance.phase_config and instance.phase_config.metadata_instance:
            source_instance = instance.phase_config.metadata_instance
            
            cloned_metadata = MetaDataGroupInstance.objects.create(
                group=source_instance.group,
                creation_source=MetaDataGroupInstance.CreationSource.DEVICE_INSTANCE,
                content_type=ContentType.objects.get_for_model(DeviceInstance),
                object_id=instance.id
            )

            if metadata_overwrite_values is not None:
                for val_data in metadata_overwrite_values:
                    try:
                        definition = MetaDataDefinition.objects.get(id=val_data['definition'])
                        MetaDataValue.objects.create(
                            instance=cloned_metadata,
                            definition=definition,
                            value=val_data['value']
                        )
                    except MetaDataDefinition.DoesNotExist:
                        pass
            else:
                for val in source_instance.values.all():
                    MetaDataValue.objects.create(
                        instance=cloned_metadata,
                        definition=val.definition,
                        value=val.value
                    )

            instance.metadata_overwrite_instance = cloned_metadata
            instance.save()
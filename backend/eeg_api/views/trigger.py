from rest_framework import viewsets
from eeg_api.models.trigger import TriggerDefinition, TriggerGroup, TriggerPair, TriggerHotkeyMapping
from eeg_api.serializers.trigger import (
    TriggerDefinitionSerializer, TriggerGroupSerializer, 
    TriggerPairSerializer, TriggerHotkeyMappingSerializer
)

class TriggerDefinitionViewSet(viewsets.ModelViewSet):
    queryset = TriggerDefinition.objects.all().order_by('id')
    serializer_class = TriggerDefinitionSerializer

class TriggerGroupViewSet(viewsets.ModelViewSet):
    queryset = TriggerGroup.objects.all().order_by('id')
    serializer_class = TriggerGroupSerializer

class TriggerPairViewSet(viewsets.ModelViewSet):
    queryset = TriggerPair.objects.all().order_by('id')
    serializer_class = TriggerPairSerializer

class TriggerHotkeyMappingViewSet(viewsets.ModelViewSet):
    queryset = TriggerHotkeyMapping.objects.all().order_by('id')
    serializer_class = TriggerHotkeyMappingSerializer
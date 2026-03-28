from rest_framework import viewsets
from django.contrib.contenttypes.models import ContentType
from eeg_api.models.metadata import EntityMetaDataRegistry, MetaDataDefinition, MetaDataGroup
from eeg_api.serializers.metadata import (
    ContentTypeSerializer, EntityMetaDataRegistrySerializer, 
    MetaDataDefinitionSerializer, MetaDataGroupSerializer
)

class ContentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ContentType.objects.filter(app_label='eeg_api').order_by('model')
    serializer_class = ContentTypeSerializer

class EntityMetaDataRegistryViewSet(viewsets.ModelViewSet):
    queryset = EntityMetaDataRegistry.objects.all().order_by('-created_at')
    serializer_class = EntityMetaDataRegistrySerializer

class MetaDataDefinitionViewSet(viewsets.ModelViewSet):
    queryset = MetaDataDefinition.objects.all().order_by('id')
    serializer_class = MetaDataDefinitionSerializer

class MetaDataGroupViewSet(viewsets.ModelViewSet):
    queryset = MetaDataGroup.objects.all().distinct().order_by('id')
    serializer_class = MetaDataGroupSerializer
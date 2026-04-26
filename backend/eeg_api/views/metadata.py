from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from eeg_api.models.metadata import EntityMetaDataRegistry, MetaDataDefinition, MetaDataGroup, MetaDataGroupInstance, MetaDataValue, MetaDataGroup
from eeg_api.serializers.metadata import (
    ContentTypeSerializer, EntityMetaDataRegistrySerializer, 
    MetaDataDefinitionSerializer, MetaDataGroupSerializer , MetaDataGroupInstanceSerializer, MetaDataValueWriteSerializer
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

    @action(detail=False, methods=['get'], url_path='available-for-table')
    def available_for_table(self, request):
        content_type_id = request.query_params.get('content_type')
        if not content_type_id:
            return Response({"error": "content_type query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        allowed_category_ids = EntityMetaDataRegistry.objects.filter(
            target_table_id=content_type_id,
            is_active=True
        ).values_list('allowed_category_id', flat=True)
        
        groups = self.get_queryset().filter(category_id__in=allowed_category_ids)
        serializer = self.get_serializer(groups, many=True)
        return Response(serializer.data)

class MetaDataGroupInstanceViewSet(viewsets.ModelViewSet):
    queryset = MetaDataGroupInstance.objects.all().order_by('-created_at')
    serializer_class = MetaDataGroupInstanceSerializer

    def get_queryset(self):
        """ Allow filtering instances by exactly which row they belong to """
        queryset = super().get_queryset()
        content_type_id = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')
        
        if content_type_id and object_id:
            queryset = queryset.filter(content_type_id=content_type_id, object_id=object_id)
        return queryset

    @action(detail=False, methods=['post'], url_path='save-manual-instance')
    def save_manual_instance(self, request):
        """ 
        Custom endpoint to atomically save a new MANUAL Instance and its Values at the same time.
        Ensures the "must have at least one value" rule.
        """
        data = request.data
        values_data = data.pop('values', [])
        
        if not values_data:
            return Response({"error": "A MetaDataGroup must have at least one filled value to be saved."}, status=status.HTTP_400_BAD_REQUEST)

        # force creation source to MANUAL since this comes from the UI Tool
        data['creation_source'] = MetaDataGroupInstance.CreationSource.MANUAL
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()

        for val in values_data:
            MetaDataValue.objects.create(
                instance=instance,
                definition_id=val['definition'],
                value=val['value']
            )

        return Response(self.get_serializer(instance).data, status=status.HTTP_201_CREATED)
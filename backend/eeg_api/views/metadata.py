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
    
    @action(detail=True, methods=['put'], url_path='update-manual-instance')
    def update_manual_instance(self, request, pk=None):
        """ Updates existing values for an instance in hindsight """
        instance = self.get_object()
        values_data = request.data.get('values', [])
        
        for val in values_data:
            MetaDataValue.objects.update_or_create(
                instance=instance,
                definition_id=val['definition'],
                defaults={'value': val['value']}
            )
            
        return Response(self.get_serializer(instance).data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='bulk-check')
    def bulk_check(self, request):
        """
        Fast bulk check for tables to avoid N+1 query problems.
        Expects payload: {"content_type": 12, "object_ids": [1, 2, 3, 4, 5]}
        Returns mapping: {"1": true, "2": false, "3": true, ...}
        """
        content_type_id = request.data.get('content_type')
        object_ids = request.data.get('object_ids', [])

        if not content_type_id or not isinstance(object_ids, list):
            return Response(
                {"error": "content_type and a list of object_ids are required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        existing_instances = MetaDataGroupInstance.objects.filter(
            content_type_id=content_type_id,
            object_id__in=object_ids
        ).values_list('object_id', flat=True).distinct()

        result = {str(obj_id): (obj_id in existing_instances) for obj_id in object_ids}

        return Response(result, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """ 
        Expected Payload: {"content_type": 12, "match_type": "AND", "rules": [{"definition": 5, "operator": "exact", "value": "Herz"}]}
        """
        content_type_id = request.data.get('content_type')
        match_type = request.data.get('match_type', 'AND') # 'AND' 'OR'
        rules = request.data.get('rules', [])

        if not content_type_id:
            return Response({"error": "content_type required"}, status=status.HTTP_400_BAD_REQUEST)

        instances = MetaDataGroupInstance.objects.filter(content_type_id=content_type_id)
        all_obj_ids = set(instances.values_list('object_id', flat=True))
        
        if not rules:
            return Response(list(all_obj_ids), status=status.HTTP_200_OK)

        matching_obj_ids = set()

        for obj_id in all_obj_ids:
            obj_instances = instances.filter(object_id=obj_id)
            obj_values = MetaDataValue.objects.filter(instance__in=obj_instances)
            
            rule_matches = []
            
            for rule in rules:
                def_id = rule.get('definition')
                op = rule.get('operator', 'exact')
                val = str(rule.get('value', '')).lower()
                
                q = obj_values.filter(definition_id=def_id)
                found = False
                
                for v in q:
                    db_val = str(v.value).lower()
                    if op == 'contains' and val in db_val:
                        found = True
                        break
                    elif op == 'exact' and val == db_val:
                        found = True
                        break
                        
                rule_matches.append(found)

            if match_type == 'AND' and all(rule_matches):
                matching_obj_ids.add(obj_id)
            elif match_type == 'OR' and any(rule_matches):
                matching_obj_ids.add(obj_id)

        return Response(list(matching_obj_ids), status=status.HTTP_200_OK)
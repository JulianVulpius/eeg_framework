from django.shortcuts import render
from .models import TriggerDefinition
from rest_framework import viewsets
from rest_framework.serializers import ModelSerializer
from django.http import Http404
from rest_framework import serializers
from .models import TriggerGroup, TriggerPair
from .models.device import DeviceModel, Manufacturer, EEGChannel, DeviceModelEEGChannel
from .models.session import FrequencyBand, Session
from .models.subject import SubjectProfile
from .models.trigger import TriggerHotkeyMapping
from .models.stimulus import Stimulus, StimulusPlaylist, StimulusPlaylistStimulus
from django.contrib.contenttypes.models import ContentType
from .models.metadata import EntityMetaDataRegistry, MetaDataDefinition, MetaDataGroup, MetaDataGroupDefinition, MetaDataGroupInstance, MetaDataValue
from .models.ui import ComponentType, Event, PageGroup, EventPageGroup, Component, Page, PageComponent, PageGroupPage, Location
from rest_framework.decorators import action
from rest_framework.response import Response
import json
from rest_framework.exceptions import ValidationError

from .models import (
    MetaDataCategory, StimulusCategory, ComponentCategory,
    CustomScriptCategory, DataProcessCategory, DataDisplayCategory,
    MetaDataGroupCategory, DeviceModelCategory, PageCategory, PageGroupCategory, EventCategory
)

# maps the Vue frontend URL slugs to  Django Models
CATEGORY_MODEL_MAP = {
    'metadata-categories': MetaDataCategory,
    'stimulus-categories': StimulusCategory,
    'component-categories': ComponentCategory,
    'custom-script-categories': CustomScriptCategory,
    'data-process-categories': DataProcessCategory,
    'data-display-categories': DataDisplayCategory,
    'metadata-group-categories': MetaDataGroupCategory,
    'device-model-categories': DeviceModelCategory,
    'page-categories': PageCategory,
    'page-group-categories': PageGroupCategory,
    'event-categories': EventCategory,
}

class GenericCategoryViewSet(viewsets.ModelViewSet):
    """
    A single API endpoint that handles CRUD operations for ALL category tables.
    """
    
    def get_model_class(self):
        table_name = self.kwargs.get('table_name')
        model_class = CATEGORY_MODEL_MAP.get(table_name)
        if not model_class:
            raise Http404(f"Table mapping for '{table_name}' not found.")
        return model_class

    def get_queryset(self):
        model_class = self.get_model_class()
        # Returns all rows for the requested table, ordered by ID
        return model_class.objects.all().order_by('id')

    def get_serializer_class(self):
        model_class = self.get_model_class()

        # Dynamically create a serializer for the requested model
        class DynamicCategorySerializer(ModelSerializer):
            class Meta:
                model = model_class
                fields = ['id', 'name', 'description']

        return DynamicCategorySerializer

class TriggerDefinitionSerializer(ModelSerializer):
    class Meta:
        model = TriggerDefinition
        fields = ['id', 'name', 'trigger_character'] 

class TriggerDefinitionViewSet(viewsets.ModelViewSet):
    queryset = TriggerDefinition.objects.all().order_by('id')
    serializer_class = TriggerDefinitionSerializer

class TriggerGroupSerializer(serializers.ModelSerializer):
    triggers = serializers.PrimaryKeyRelatedField(
        queryset=TriggerDefinition.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = TriggerGroup
        fields = ['id', 'name', 'description', 'triggers']

class TriggerGroupViewSet(viewsets.ModelViewSet):
    queryset = TriggerGroup.objects.all().order_by('id')
    serializer_class = TriggerGroupSerializer

class TriggerPairSerializer(serializers.ModelSerializer):
    class Meta:
        model = TriggerPair
        fields = ['id', 'name', 'start_trigger', 'end_trigger']

class TriggerPairViewSet(viewsets.ModelViewSet):
    queryset = TriggerPair.objects.all().order_by('id')
    serializer_class = TriggerPairSerializer

class FrequencyBandSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrequencyBand
        fields = '__all__'

class FrequencyBandViewSet(viewsets.ModelViewSet):
    queryset = FrequencyBand.objects.all().order_by('id')
    serializer_class = FrequencyBandSerializer

class DeviceModelSerializer(serializers.ModelSerializer):
    channels = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    assigned_channels = serializers.SerializerMethodField(read_only=True)
    
    channel_names = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = DeviceModel
        fields = ['id', 'name', 'manufacturer', 'category', 'is_eeg', 'channels', 'assigned_channels', 'channel_names']

    def get_assigned_channels(self, obj):
        return [c.id for c in obj.channels.all()]

    def get_channel_names(self, obj):
        return ", ".join([c.name for c in obj.channels.all()])

    def create(self, validated_data):
        channels_data = validated_data.pop('channels', [])
        device_model = DeviceModel.objects.create(**validated_data)
        
        for channel_id in channels_data:
            DeviceModelEEGChannel.objects.create(
                device_model=device_model, 
                eeg_channel_id=channel_id
            )
        return device_model

    def update(self, instance, validated_data):
        if 'channels' in validated_data:
            channels_data = validated_data.pop('channels')
            DeviceModelEEGChannel.objects.filter(device_model=instance).delete()
            for channel_id in channels_data:
                DeviceModelEEGChannel.objects.create(
                    device_model=instance, 
                    eeg_channel_id=channel_id
                )
        
        instance.name = validated_data.get('name', instance.name)
        instance.manufacturer = validated_data.get('manufacturer', instance.manufacturer)
        instance.category = validated_data.get('category', instance.category)
        instance.save()
        
        return instance

class DeviceModelViewSet(viewsets.ModelViewSet):
    queryset = DeviceModel.objects.all().order_by('id')
    serializer_class = DeviceModelSerializer

class SubjectProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectProfile
        fields = '__all__'

class SubjectProfileViewSet(viewsets.ModelViewSet):
    queryset = SubjectProfile.objects.all().order_by('id')
    serializer_class = SubjectProfileSerializer

class TriggerHotkeyMappingSerializer(serializers.ModelSerializer):
    class Meta:
        model = TriggerHotkeyMapping
        fields = '__all__'

class TriggerHotkeyMappingViewSet(viewsets.ModelViewSet):
    queryset = TriggerHotkeyMapping.objects.all().order_by('id')
    serializer_class = TriggerHotkeyMappingSerializer

class StimulusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stimulus
        fields = '__all__'

class StimulusViewSet(viewsets.ModelViewSet):
    queryset = Stimulus.objects.all().order_by('id')
    serializer_class = StimulusSerializer

class StimulusPlaylistSerializer(serializers.ModelSerializer):
    stimuli = serializers.PrimaryKeyRelatedField(
        queryset=Stimulus.objects.all(),
        many=True,
        required=False
    )
    class Meta:
        model = StimulusPlaylist
        fields = ['id', 'name', 'stimuli']

    def create(self, validated_data):
        stimuli_data = validated_data.pop('stimuli', [])
        playlist = StimulusPlaylist.objects.create(**validated_data)
        for index, stimulus in enumerate(stimuli_data):
            StimulusPlaylistStimulus.objects.create(
                playlist=playlist,
                stimulus=stimulus,
                order=index + 1
            )
        return playlist

    def update(self, instance, validated_data):
        if 'stimuli' in validated_data:
            stimuli_data = validated_data.pop('stimuli')
            StimulusPlaylistStimulus.objects.filter(playlist=instance).delete()
            for index, stimulus in enumerate(stimuli_data):
                StimulusPlaylistStimulus.objects.create(
                    playlist=instance,
                    stimulus=stimulus,
                    order=index + 1
                )
        
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

class StimulusPlaylistViewSet(viewsets.ModelViewSet):
    queryset = StimulusPlaylist.objects.all().order_by('id')
    serializer_class = StimulusPlaylistSerializer

# serialize django's built-in content types so vue can display the table names
class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model']

# serialize the registry that links tables to metadata categories
class EntityMetaDataRegistrySerializer(serializers.ModelSerializer):
    class Meta:
        model = EntityMetaDataRegistry
        fields = ['id', 'target_table', 'allowed_category', 'description', 'is_active']

# read-only view for tables. filter to avoid cluttering the dropdown with standard django tables
class ContentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    # only get models from our specific eeg app
    queryset = ContentType.objects.filter(app_label='eeg_api').order_by('model')
    serializer_class = ContentTypeSerializer

# standard crud viewset for the registry
class EntityMetaDataRegistryViewSet(viewsets.ModelViewSet):
    queryset = EntityMetaDataRegistry.objects.all().order_by('-created_at')
    serializer_class = EntityMetaDataRegistrySerializer

class MetaDataDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetaDataDefinition
        fields = ['id', 'category', 'name', 'description', 'expected_data_type']

class MetaDataDefinitionViewSet(viewsets.ModelViewSet):
    queryset = MetaDataDefinition.objects.all().order_by('id')
    serializer_class = MetaDataDefinitionSerializer

class MetaDataGroupSerializer(serializers.ModelSerializer):
    # frontend sends Array of IDs to save (z.B. [3, 1, 5])
    definitions = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    assigned_definitions = serializers.SerializerMethodField(read_only=True)

    def validate_name(self, value):
        query = MetaDataGroup.objects.filter(name__iexact=value.strip())
        
        if self.instance:
            query = query.exclude(pk=self.instance.pk)
            
        if query.exists():
            raise serializers.ValidationError("A Metadata Group with this name already exists.")
            
        return value.strip()

    class Meta:
        model = MetaDataGroup
        fields = ['id', 'category', 'name', 'description', 'definitions', 'assigned_definitions']

    def get_assigned_definitions(self, obj):
        mgds = MetaDataGroupDefinition.objects.filter(group=obj).order_by('order')
        return [mgd.definition.id for mgd in mgds]

    def create(self, validated_data):
        definitions_data = validated_data.pop('definitions', [])
        group = MetaDataGroup.objects.create(**validated_data)
        
        for index, def_id in enumerate(definitions_data):
            definition = MetaDataDefinition.objects.get(id=def_id)
            MetaDataGroupDefinition.objects.create(
                group=group, 
                definition=definition, 
                order=index + 1 
            )
        return group

    def update(self, instance, validated_data):
        definitions_data = validated_data.pop('definitions', None)
        
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.description = validated_data.get('description', instance.description)
        instance.save()

        if definitions_data is not None:
            MetaDataGroupDefinition.objects.filter(group=instance).delete()
            for index, def_id in enumerate(definitions_data):
                definition = MetaDataDefinition.objects.get(id=def_id)
                MetaDataGroupDefinition.objects.create(
                    group=instance, 
                    definition=definition, 
                    order=index + 1
                )
        return instance

class MetaDataGroupViewSet(viewsets.ModelViewSet):
    queryset = MetaDataGroup.objects.all().distinct().order_by('id')
    serializer_class = MetaDataGroupSerializer

class ManufacturerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manufacturer
        fields = '__all__'

class ManufacturerViewSet(viewsets.ModelViewSet):
    queryset = Manufacturer.objects.all().order_by('name')
    serializer_class = ManufacturerSerializer

class EEGChannelSerializer(serializers.ModelSerializer):
    class Meta:
        model = EEGChannel
        fields = '__all__'

class EEGChannelViewSet(viewsets.ModelViewSet):
    queryset = EEGChannel.objects.all().order_by('name')
    serializer_class = EEGChannelSerializer

class ComponentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentType
        fields = ['id', 'name', 'identifier', 'description']

class ComponentTypeViewSet(viewsets.ModelViewSet):
    queryset = ComponentType.objects.all().order_by('name')
    serializer_class = ComponentTypeSerializer

class EventSerializer(serializers.ModelSerializer):
    page_groups = serializers.PrimaryKeyRelatedField(
        queryset=PageGroup.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Event
        fields = ['id', 'name', 'category', 'description', 'location', 'event_start', 'event_end', 'page_groups']

    def create(self, validated_data):
        page_groups_data = validated_data.pop('page_groups', [])
        event = Event.objects.create(**validated_data)
        
        for page_group in page_groups_data:
            EventPageGroup.objects.create(event=event, page_group=page_group)
        return event

    def update(self, instance, validated_data):
        if 'page_groups' in validated_data:
            page_groups_data = validated_data.pop('page_groups')
            EventPageGroup.objects.filter(event=instance).delete()
            for page_group in page_groups_data:
                EventPageGroup.objects.create(event=instance, page_group=page_group)

        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.description = validated_data.get('description', instance.description)
        instance.location = validated_data.get('location', instance.location) 
        instance.event_start = validated_data.get('event_start', instance.event_start)
        instance.event_end = validated_data.get('event_end', instance.event_end)
        instance.save()
        
        return instance

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-created_at')
    serializer_class = EventSerializer

class PageSerializer(serializers.ModelSerializer):
    components = serializers.PrimaryKeyRelatedField(
        queryset=Component.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Page
        fields = ['id', 'name', 'category', 'description', 'components']

    def create(self, validated_data):
        components_data = validated_data.pop('components', [])
        page = Page.objects.create(**validated_data)
        for index, comp in enumerate(components_data):
            PageComponent.objects.create(page=page, component=comp, order=index + 1)
        return page

    def update(self, instance, validated_data):
        if 'components' in validated_data:
            components_data = validated_data.pop('components')
            PageComponent.objects.filter(page=instance).delete()
            for index, comp in enumerate(components_data):
                PageComponent.objects.create(page=instance, component=comp, order=index + 1)
        
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance

class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all().order_by('-created_at')
    serializer_class = PageSerializer

class PageGroupSerializer(serializers.ModelSerializer):
    pages = serializers.PrimaryKeyRelatedField(
        queryset=Page.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = PageGroup
        fields = ['id', 'name', 'category', 'description', 'pages']

    def create(self, validated_data):
        pages_data = validated_data.pop('pages', [])
        group = PageGroup.objects.create(**validated_data)
        for index, page in enumerate(pages_data):
            PageGroupPage.objects.create(page_group=group, page=page, order=index + 1)
        return group

    def update(self, instance, validated_data):
        if 'pages' in validated_data:
            pages_data = validated_data.pop('pages')
            PageGroupPage.objects.filter(page_group=instance).delete()
            for index, page in enumerate(pages_data):
                PageGroupPage.objects.create(page_group=instance, page=page, order=index + 1)
                
        instance.name = validated_data.get('name', instance.name)
        instance.category = validated_data.get('category', instance.category)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance

class PageGroupViewSet(viewsets.ModelViewSet):
    queryset = PageGroup.objects.all().order_by('id')
    serializer_class = PageGroupSerializer

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'

class SessionViewSet(viewsets.ModelViewSet):
    queryset = Session.objects.all().order_by('-start_datetime')
    serializer_class = SessionSerializer

    def create(self, request, *args, **kwargs):
        event_id = request.data.get('event')
        subject_id = request.data.get('subject')
        page_group_id = request.data.get('page_group')
        location_id = request.data.get('location')
        start_datetime = request.data.get('start_datetime')

        session, created = Session.objects.get_or_create(
            event_id=event_id,
            subject_id=subject_id,
            page_group_id=page_group_id,
            defaults={
                'start_datetime': start_datetime,
                'location_id': location_id
            }
        )
        
        if not created:
            session.location_id = location_id
            session.start_datetime = start_datetime
            session.save()
        
        serializer = self.get_serializer(session)
        from rest_framework import status
        return Response(serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)

    @action(detail=True, methods=['get'])
    def blueprint(self, request, pk=None):
        session = self.get_object()
        pg = session.page_group
        
        blueprint_data = {
            "session_id": session.id,
            "event_name": session.event.name,
            "page_group_name": pg.name,
            "pages": []
        }
        
        pgps = pg.pagegrouppage_set.all().order_by('order')
        for pgp in pgps:
            page = pgp.page
            page_data = {"id": page.id, "name": page.name, "components": []}
            
            pcs = page.pagecomponent_set.all().order_by('order')
            for pc in pcs:
                comp = pc.component
                page_data["components"].append({
                    "id": comp.id,
                    "type": comp.component_type.identifier,
                    "parameters": comp.parameter
                })
            blueprint_data["pages"].append(page_data)
            
        return Response(blueprint_data)

    @action(detail=True, methods=['post', 'put'])
    def save_metadata(self, request, pk=None):
        session = self.get_object()
        group_id = request.data.get('group_id')
        values = request.data.get('values', [])
        
        group = MetaDataGroup.objects.get(id=group_id)
        session_ct = ContentType.objects.get_for_model(Session)
        
        instance, created = MetaDataGroupInstance.objects.get_or_create(
            group=group,
            content_type=session_ct,
            object_id=session.id
        )
        
        for val in values:
            definition = MetaDataDefinition.objects.get(id=val['definition_id'])
            MetaDataValue.objects.update_or_create(
                instance=instance,
                definition=definition,
                defaults={'value': str(val['value'])}
            )
            
        return Response({"status": "success", "updated": not created})

    @action(detail=True, methods=['get'])
    def saved_metadata(self, request, pk=None):
        session = self.get_object()
        session_ct = ContentType.objects.get_for_model(Session)
        
        instances = MetaDataGroupInstance.objects.filter(
            content_type=session_ct, 
            object_id=session.id
        )
        
        saved_data = {}
        for inst in instances:
            for val in inst.values.all():
                saved_data[val.definition.id] = val.value
                
        return Response(saved_data)
        
    @action(detail=True, methods=['post'])
    def reset(self, request, pk=None):
        session = self.get_object()
        session_ct = ContentType.objects.get_for_model(Session)
        
        MetaDataGroupInstance.objects.filter(
            content_type=session_ct, 
            object_id=session.id
        ).delete()
        
        import django.utils.timezone
        session.start_datetime = django.utils.timezone.now()
        session.save()
        
        return Response({"status": "session_reset"})

    @action(detail=True, methods=['get'])
    def report(self, request, pk=None):
        session = self.get_object()
        session_ct = ContentType.objects.get_for_model(Session)
        
        instances = MetaDataGroupInstance.objects.filter(
            content_type=session_ct, 
            object_id=session.id
        ).order_by('created_at')
        
        report_data = []
        for inst in instances:
            group_data = {
                "group_name": inst.group.name,
                "timestamp": inst.created_at,
                "answers": []
            }
            for val in inst.values.all().order_by('definition__name'):
                group_data["answers"].append({
                    "question": val.definition.name,
                    "answer": val.value,
                    "type": val.definition.expected_data_type
                })
            report_data.append(group_data)
            
        return Response({
            "session_id": session.id,
            "event_name": session.event.name,
            "page_group_name": session.page_group.name,
            "subject_identifier": session.subject.identifier,
            "start_time": session.start_datetime,
            "metadata_groups": report_data
        })

class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = ['id', 'name', 'category', 'component_type', 'description', 'parameter']

    def validate_parameter(self, value):
        # Ensure it's valid JSON if passed as string, though DRF usually handles dicts here
        if isinstance(value, str):
            try:
                return json.loads(value)
            except ValueError:
                raise ValidationError("Invalid JSON format for parameters.")
        return value

class ComponentViewSet(viewsets.ModelViewSet):
    queryset = Component.objects.all().order_by('-created_at')
    serializer_class = ComponentSerializer

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all().order_by('name')
    serializer_class = LocationSerializer
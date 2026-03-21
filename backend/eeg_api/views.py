from django.shortcuts import render
from .models import TriggerDefinition
from rest_framework import viewsets
from rest_framework.serializers import ModelSerializer
from django.http import Http404
from rest_framework import serializers
from .models import TriggerGroup, TriggerPair
from .models.device import DeviceModel, Manufacturer, EEGChannel, DeviceModelEEGChannel
from .models.session import FrequencyBand
from .models.subject import SubjectProfile
from .models.trigger import TriggerHotkeyMapping
from .models.stimulus import Stimulus, StimulusPlaylist, StimulusPlaylistStimulus
from django.contrib.contenttypes.models import ContentType
from .models.metadata import EntityMetaDataRegistry, MetaDataDefinition, MetaDataGroup, MetaDataGroupDefinition
from .models.ui import ComponentType

from .models import (
    MetaDataCategory, StimulusCategory, ComponentCategory,
    CustomScriptCategory, DataProcessCategory, DataDisplayCategory,
    MetaDataGroupCategory, DeviceModelCategory, PageCategory, PageGroupCategory
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

# handles the many-to-many junction table automatically
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
        fields = ['id', 'name', 'manufacturer', 'category', 'channels', 'assigned_channels', 'channel_names']

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

# read-only view for tables. filter by your app to avoid cluttering the dropdown with standard django tables
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
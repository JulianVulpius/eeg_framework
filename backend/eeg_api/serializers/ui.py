import json
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from eeg_api.serializers.media import MediaAssetSerializer
from eeg_api.models.event_management import EventDeviceModel
from eeg_api.models.device import DeviceModel
from eeg_api.models.ui import (
    ComponentType, Event, PageGroup, EventPageGroup, 
    Component, Page, PageComponent, PageGroupPage, Location, EventGallery
)
from eeg_api.serializers.media import MediaAssetSerializer

class ComponentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComponentType
        fields = ['id', 'name', 'identifier', 'description']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = ['id', 'name', 'category', 'component_type', 'description', 'parameter']

    def validate_parameter(self, value):
        if isinstance(value, str):
            try:
                return json.loads(value)
            except ValueError:
                raise ValidationError("Invalid JSON format for parameters.")
        return value

class PageSerializer(serializers.ModelSerializer):
    components = serializers.PrimaryKeyRelatedField(
        queryset=Component.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = Page
        fields = ['id', 'name', 'category', 'description', 'scope', 'components']

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
        instance.scope = validated_data.get('scope', instance.scope)
        instance.save()
        return instance

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

from eeg_api.models.event_management import EventDeviceModel

class EventSerializer(serializers.ModelSerializer):
    page_groups = serializers.PrimaryKeyRelatedField(
        queryset=PageGroup.objects.all(),
        many=True,
        required=False
    )

    devices = serializers.PrimaryKeyRelatedField(
        queryset=DeviceModel.objects.all(),
        many=True,
        required=False,
        write_only=True
    )
    session_locations = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'name', 'category', 'description', 'location', 'event_start', 'event_end', 'page_groups', 'devices', 'session_locations', 'logo', 'poster']

    def get_session_locations(self, obj):
            return list(obj.sessions.exclude(location__isnull=True).values_list('location_id', flat=True).distinct())

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['devices'] = list(instance.device_pool.values_list('device_model_id', flat=True))
        return ret

    def create(self, validated_data):
        page_groups_data = validated_data.pop('page_groups', [])
        devices_data = validated_data.pop('devices', []) 
        
        event = Event.objects.create(**validated_data)
        
        for page_group in page_groups_data:
            EventPageGroup.objects.create(event=event, page_group=page_group)
            
        for device in devices_data:
            EventDeviceModel.objects.create(event=event, device_model=device)
            
        return event

    def update(self, instance, validated_data):
        page_groups_data = validated_data.pop('page_groups', None)
        devices_data = validated_data.pop('devices', None)

        instance = super().update(instance, validated_data)

        if page_groups_data is not None:
            EventPageGroup.objects.filter(event=instance).delete()
            for page_group in page_groups_data:
                EventPageGroup.objects.create(event=instance, page_group=page_group)

        if devices_data is not None:
            EventDeviceModel.objects.filter(event=instance).delete()
            for device in devices_data:
                EventDeviceModel.objects.create(event=instance, device_model=device)

        return instance

class EventGallerySerializer(serializers.ModelSerializer):
    media_asset_details = MediaAssetSerializer(source='media', read_only=True)
    
    class Meta:
        model = EventGallery
        fields = ['id', 'event', 'media', 'media_asset_details', 'display_order']
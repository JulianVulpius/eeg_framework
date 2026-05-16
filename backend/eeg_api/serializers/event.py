from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from eeg_api.serializers.media import MediaAssetSerializer
from eeg_api.models import (
    Event, EventCategory, EventGallery, PageGroup, DeviceModel, EventPageGroup,
    EventRole, EventGroup, EventSubjectAssignment, EventStaffAssignment, 
    EventDeviceModel, EventGroupPageGroup, EventGroupPageGroupDevice
)

class EventCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = EventCategory
        fields = '__all__'

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
        fields = [
            'id', 'name', 'category', 'description', 'location', 
            'event_start', 'event_end', 'page_groups', 'devices', 
            'session_locations', 'logo', 'poster'
        ]

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
            current_pg_ids = set(EventPageGroup.objects.filter(event=instance).values_list('page_group_id', flat=True))
            new_pg_ids = set(pg.id for pg in page_groups_data)
            
            to_remove_pg = current_pg_ids - new_pg_ids
            if to_remove_pg:
                EventPageGroup.objects.filter(event=instance, page_group_id__in=to_remove_pg).delete()
                
            to_add_pg = new_pg_ids - current_pg_ids
            for pg_id in to_add_pg:
                pg_instance = next(p for p in page_groups_data if p.id == pg_id)
                EventPageGroup.objects.create(event=instance, page_group=pg_instance)

        if devices_data is not None:
            current_device_ids = set(EventDeviceModel.objects.filter(event=instance).values_list('device_model_id', flat=True))
            new_device_ids = set(dev.id for dev in devices_data)
            
            to_remove_dev = current_device_ids - new_device_ids
            if to_remove_dev:
                EventDeviceModel.objects.filter(event=instance, device_model_id__in=to_remove_dev).delete()
                
            to_add_dev = new_device_ids - current_device_ids
            for dev_id in to_add_dev:
                dev_instance = next(d for d in devices_data if d.id == dev_id)
                EventDeviceModel.objects.create(event=instance, device_model=dev_instance)

        return instance

class EventGallerySerializer(serializers.ModelSerializer):
    media_asset_details = MediaAssetSerializer(source='media', read_only=True)
    
    class Meta:
        model = EventGallery
        fields = ['id', 'event', 'media', 'media_asset_details', 'display_order']

class EventRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRole
        fields = '__all__'

class EventGroupSerializer(serializers.ModelSerializer):
    page_groups = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=PageGroup.objects.all(),
        required=False
    )

    class Meta:
        model = EventGroup
        fields = '__all__'

class EventSubjectAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventSubjectAssignment
        fields = '__all__'

class EventStaffAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventStaffAssignment
        fields = '__all__'

class EventDeviceModelSerializer(serializers.ModelSerializer):
    device_name = serializers.ReadOnlyField(source='device_model.name')

    class Meta:
        model = EventDeviceModel
        fields = ['id', 'event', 'device_model', 'device_name']

class EventGroupPageGroupDeviceSerializer(serializers.ModelSerializer):
    is_locked = serializers.BooleanField(read_only=True)
    device_name = serializers.ReadOnlyField(source='device_from_pool.device_model.name')
    device_model_id = serializers.ReadOnlyField(source='device_from_pool.device_model.id')
    page_group_id = serializers.ReadOnlyField(source='phase.page_group.id')
    
    event_group_id = serializers.IntegerField(write_only=True, required=False)
    target_page_group_id = serializers.IntegerField(write_only=True, required=False)
    master_device_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = EventGroupPageGroupDevice
        fields = [
            'id', 'phase', 'page_group_id', 'device_from_pool', 'device_name', 'device_model_id',
            'metadata_instance', 'expected_channels', 'is_archived', 'is_locked',
            'event_group_id', 'target_page_group_id', 'master_device_id'
        ]
        extra_kwargs = {
            'phase': {'required': False, 'allow_null': True},
            'device_from_pool': {'required': False, 'allow_null': True}
        }
        validators = [] 

    def validate(self, attrs):
        event_group_id = attrs.pop('event_group_id', None)
        target_page_group_id = attrs.pop('target_page_group_id', None)
        master_device_id = attrs.pop('master_device_id', None)

        if event_group_id and target_page_group_id:
            phase_obj, _ = EventGroupPageGroup.objects.get_or_create(
                event_group_id=event_group_id, 
                page_group_id=target_page_group_id
            )
            attrs['phase'] = phase_obj

        if master_device_id and event_group_id:
            try:
                event_group = EventGroup.objects.get(id=event_group_id)
                device_pool_obj = EventDeviceModel.objects.get(
                    event=event_group.event,
                    device_model_id=master_device_id
                )
                attrs['device_from_pool'] = device_pool_obj
            except EventDeviceModel.DoesNotExist:
                raise ValidationError({"master_device_id": "Device is not in Device-Pool."})

        if 'phase' in attrs and 'device_from_pool' in attrs:
            if EventGroupPageGroupDevice.objects.filter(phase=attrs['phase'], device_from_pool=attrs['device_from_pool']).exists():
                raise ValidationError({"non_field_errors": ["Device already assigned."]})

        return attrs

    def create(self, validated_data):
        return super().create(validated_data)
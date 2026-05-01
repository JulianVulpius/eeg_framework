from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from eeg_api.models.event_management import (
    EventRole, EventGroup, EventSubjectAssignment, EventStaffAssignment,
    EventDeviceModel, EventGroupPageGroup, EventGroupPageGroupDevice
)
from eeg_api.models.ui import PageGroup

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
    page_group_id = serializers.ReadOnlyField(source='phase.page_group.id')
    
    event_group_id = serializers.IntegerField(write_only=True, required=False)
    target_page_group_id = serializers.IntegerField(write_only=True, required=False)
    master_device_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = EventGroupPageGroupDevice
        fields = [
            'id', 'phase', 'page_group_id', 'device_from_pool', 'device_name', 
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
                raise ValidationError({"master_device_id": "Dieses Gerät ist nicht im Event-Pool freigegeben."})

        if 'phase' in attrs and 'device_from_pool' in attrs:
            if EventGroupPageGroupDevice.objects.filter(phase=attrs['phase'], device_from_pool=attrs['device_from_pool']).exists():
                raise ValidationError({"non_field_errors": ["Dieses Gerät ist dieser Phase bereits zugewiesen."]})

        return attrs

    def create(self, validated_data):
        return super().create(validated_data)
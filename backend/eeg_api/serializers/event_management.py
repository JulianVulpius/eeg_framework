from rest_framework import serializers
from eeg_api.models.event_management import (
    EventRole, EventGroup, EventSubjectAssignment, EventStaffAssignment,
    EventDeviceModel, EventGroupPageGroupDevice
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

    class Meta:
        model = EventGroupPageGroupDevice
        fields = [
            'id', 'phase', 'device_from_pool', 'device_name', 
            'metadata_instance', 'expected_channels', 'is_archived', 'is_locked'
        ]
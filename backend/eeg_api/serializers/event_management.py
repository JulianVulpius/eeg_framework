from rest_framework import serializers
from eeg_api.models.event_management import (
    EventRole, EventGroup, EventSubjectAssignment, EventStaffAssignment
)

class EventRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventRole
        fields = '__all__'

class EventGroupSerializer(serializers.ModelSerializer):
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
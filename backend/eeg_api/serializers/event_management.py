from rest_framework import serializers
from eeg_api.models.event_management import (
    EventRole, EventGroup, EventSubjectAssignment, EventStaffAssignment
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
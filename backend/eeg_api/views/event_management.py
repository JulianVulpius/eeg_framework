from rest_framework import viewsets
from eeg_api.models.event_management import (
    EventRole, EventGroup, EventSubjectAssignment, EventStaffAssignment
)
from eeg_api.serializers.event_management import (
    EventRoleSerializer, EventGroupSerializer, 
    EventSubjectAssignmentSerializer, EventStaffAssignmentSerializer
)

class EventRoleViewSet(viewsets.ModelViewSet):
    queryset = EventRole.objects.all().order_by('name')
    serializer_class = EventRoleSerializer

class EventGroupViewSet(viewsets.ModelViewSet):
    queryset = EventGroup.objects.all().order_by('name')
    serializer_class = EventGroupSerializer

class EventSubjectAssignmentViewSet(viewsets.ModelViewSet):
    queryset = EventSubjectAssignment.objects.all().order_by('id')
    serializer_class = EventSubjectAssignmentSerializer

class EventStaffAssignmentViewSet(viewsets.ModelViewSet):
    queryset = EventStaffAssignment.objects.all().order_by('id')
    serializer_class = EventStaffAssignmentSerializer
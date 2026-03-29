from rest_framework import viewsets
from eeg_api.models.event_management import (
    EventRole, EventGroup, EventSubjectAssignment, EventStaffAssignment
)
from eeg_api.serializers.event_management import (
    EventRoleSerializer, EventGroupSerializer, 
    EventSubjectAssignmentSerializer, EventStaffAssignmentSerializer
)

class EventRoleViewSet(viewsets.ModelViewSet):
    serializer_class = EventRoleSerializer

    def get_queryset(self):
        queryset = EventRole.objects.all().order_by('name')
        event_id = self.request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event__id=event_id)
        return queryset

class EventGroupViewSet(viewsets.ModelViewSet):
    serializer_class = EventGroupSerializer

    def get_queryset(self):
        queryset = EventGroup.objects.all().order_by('name')
        event_id = self.request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event__id=event_id)
        return queryset

class EventSubjectAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = EventSubjectAssignmentSerializer

    def get_queryset(self):
        queryset = EventSubjectAssignment.objects.all().order_by('id')
        event_id = self.request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event__id=event_id)
        return queryset

class EventStaffAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = EventStaffAssignmentSerializer

    def get_queryset(self):
        queryset = EventStaffAssignment.objects.all().order_by('id')
        event_id = self.request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(role__event__id=event_id)
        return queryset
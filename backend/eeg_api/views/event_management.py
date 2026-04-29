from django.db.models import Exists, OuterRef
from django.db.models import ProtectedError
from rest_framework import viewsets, status
from rest_framework.response import Response

from eeg_api.utils import clone_metadata_group_instance

from eeg_api.models.event_management import (
    EventRole, EventGroup, EventSubjectAssignment, EventStaffAssignment, 
    EventDeviceModel, EventGroupPageGroupDevice
)
from eeg_api.serializers.event_management import (
    EventRoleSerializer, EventGroupSerializer, 
    EventSubjectAssignmentSerializer, EventStaffAssignmentSerializer,
    EventDeviceModelSerializer, EventGroupPageGroupDeviceSerializer
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

class EventDeviceModelViewSet(viewsets.ModelViewSet):
    queryset = EventDeviceModel.objects.all()
    serializer_class = EventDeviceModelSerializer

class EventGroupPageGroupDeviceViewSet(viewsets.ModelViewSet):
    serializer_class = EventGroupPageGroupDeviceSerializer

    def get_queryset(self):
        return EventGroupPageGroupDevice.objects.annotate(
            is_locked=Exists(DeviceInstance.objects.filter(phase_config=OuterRef('pk')))
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            instance.is_archived = True
            instance.save()
            return Response(
                {"message": "Phase configuration is in use and has been archived."},
                status=status.HTTP_200_OK
            )

    def perform_create(self, serializer):

        phase_device_config = serializer.save()
        
        master_model = phase_device_config.device_from_pool.device_model
        
        if master_model.default_settings:
            cloned_metadata = clone_metadata_group_instance(
                source_instance=master_model.default_settings,
                target_object=phase_device_config
            )
            phase_device_config.metadata_instance = cloned_metadata
            phase_device_config.save()
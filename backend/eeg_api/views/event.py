from django.db.models import Exists, OuterRef, ProtectedError
from rest_framework import viewsets, status
from rest_framework.response import Response

from eeg_api.services.utils import clone_metadata_group_instance
from eeg_api.models import (
    Event, EventGallery, EventRole, EventGroup, 
    EventSubjectAssignment, EventStaffAssignment,
    EventDeviceModel, EventGroupPageGroupDevice, DeviceInstance
)
from eeg_api.serializers.event import (
    EventSerializer, EventGallerySerializer, EventRoleSerializer,
    EventGroupSerializer, EventSubjectAssignmentSerializer,
    EventStaffAssignmentSerializer, EventDeviceModelSerializer,
    EventGroupPageGroupDeviceSerializer
)

class EventViewSet(viewsets.ModelViewSet):
    """Handles CRUD operations for experimental events and studies."""
    queryset = Event.objects.prefetch_related('sessions').all().order_by('-created_at')
    serializer_class = EventSerializer

class EventGalleryViewSet(viewsets.ModelViewSet):
    """Handles media assets associated with an event gallery."""
    serializer_class = EventGallerySerializer

    def get_queryset(self):
        queryset = EventGallery.objects.all().order_by('display_order', 'id')
        event_id = self.request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset

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
    serializer_class = EventDeviceModelSerializer

    def get_queryset(self):
        queryset = EventDeviceModel.objects.all()
        event_id = self.request.query_params.get('event')
        if event_id:
            queryset = queryset.filter(event_id=event_id)
        return queryset

class EventGroupPageGroupDeviceViewSet(viewsets.ModelViewSet):
    serializer_class = EventGroupPageGroupDeviceSerializer

    def get_queryset(self):
        queryset = EventGroupPageGroupDevice.objects.annotate(
            is_locked=Exists(DeviceInstance.objects.filter(phase_config=OuterRef('pk')))
        )
        
        event_group_id = self.request.query_params.get('phase__event_group')
        if event_group_id:
            queryset = queryset.filter(phase__event_group_id=event_group_id)
            
        return queryset

    def destroy(self, request, *args, **kwargs):
        """Archives configuration if protected relations exist."""
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
        """Clones default device settings to the phase configuration."""
        phase_device_config = serializer.save()
        master_model = phase_device_config.device_from_pool.device_model
        
        if master_model.default_settings:
            cloned_metadata = clone_metadata_group_instance(
                source_instance=master_model.default_settings,
                target_object=phase_device_config
            )
            
            cloned_metadata.creation_source = 'DEVICE_PHASE'
            cloned_metadata.save()
            
            phase_device_config.metadata_instance = cloned_metadata
            phase_device_config.save()
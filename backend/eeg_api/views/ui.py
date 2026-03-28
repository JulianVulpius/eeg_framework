from rest_framework import viewsets
from eeg_api.models.ui import ComponentType, Event, PageGroup, Component, Page, Location
from eeg_api.serializers.ui import (
    ComponentTypeSerializer, EventSerializer, PageGroupSerializer, 
    ComponentSerializer, PageSerializer, LocationSerializer
)

class ComponentTypeViewSet(viewsets.ModelViewSet):
    queryset = ComponentType.objects.all().order_by('name')
    serializer_class = ComponentTypeSerializer

class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all().order_by('name')
    serializer_class = LocationSerializer

class ComponentViewSet(viewsets.ModelViewSet):
    queryset = Component.objects.all().order_by('-created_at')
    serializer_class = ComponentSerializer

class PageViewSet(viewsets.ModelViewSet):
    queryset = Page.objects.all().order_by('-created_at')
    serializer_class = PageSerializer

class PageGroupViewSet(viewsets.ModelViewSet):
    queryset = PageGroup.objects.all().order_by('id')
    serializer_class = PageGroupSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-created_at')
    serializer_class = EventSerializer
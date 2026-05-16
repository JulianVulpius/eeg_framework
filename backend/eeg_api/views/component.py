from rest_framework import viewsets
from eeg_api.models import ComponentType, Component
from eeg_api.serializers.component import ComponentTypeSerializer, ComponentSerializer

class ComponentTypeViewSet(viewsets.ModelViewSet):
    """Handles CRUD operations for UI component definitions and identifiers."""
    queryset = ComponentType.objects.all().order_by('name')
    serializer_class = ComponentTypeSerializer

class ComponentViewSet(viewsets.ModelViewSet):
    """Handles CRUD operations for configured UI component instances."""
    queryset = Component.objects.all().order_by('-created_at')
    serializer_class = ComponentSerializer
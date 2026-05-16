from rest_framework import viewsets
from eeg_api.models import Page, PageGroup
from eeg_api.serializers.page import PageSerializer, PageGroupSerializer

class PageViewSet(viewsets.ModelViewSet):
    """Handles CRUD operations for UI pages containing components."""
    queryset = Page.objects.all().order_by('-created_at')
    serializer_class = PageSerializer

class PageGroupViewSet(viewsets.ModelViewSet):
    """Handles CRUD operations for collections of pages (phases)."""
    queryset = PageGroup.objects.all().order_by('id')
    serializer_class = PageGroupSerializer
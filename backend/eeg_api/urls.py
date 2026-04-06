from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.category import GenericCategoryViewSet
from .views.device import (
    DeviceModelViewSet, ManufacturerViewSet, 
    EEGChannelViewSet, FrequencyBandViewSet
)
from .views.session import SessionViewSet
from .views.trigger import (
    TriggerDefinitionViewSet, TriggerGroupViewSet, 
    TriggerPairViewSet, TriggerHotkeyMappingViewSet
)
from .views.stimulus import StimulusViewSet, StimulusPlaylistViewSet
from .views.metadata import (
    ContentTypeViewSet, EntityMetaDataRegistryViewSet, 
    MetaDataDefinitionViewSet, MetaDataGroupViewSet
)
from .views.ui import (
    ComponentTypeViewSet, LocationViewSet, ComponentViewSet, 
    PageViewSet, PageGroupViewSet, EventViewSet, EventGalleryViewSet
)
from .views.subject import SubjectProfileViewSet
from .views.script import (
    CustomScriptLanguageViewSet, CustomScriptViewSet, 
    DataProcessViewSet, DataDisplayViewSet
)
from .views.recordings import (
    EEGDataFileViewSet, HeartRateDataFileViewSet, GenericRecordingViewSet
)
from .views.medical import MedicalHistoryViewSet, SubjectMedicalHistoryViewSet
from .views.media import MediaAssetViewSet
from .views.event_management import (
    EventRoleViewSet, EventGroupViewSet, 
    EventSubjectAssignmentViewSet, EventStaffAssignmentViewSet
)

router = DefaultRouter()

router.register(
    r'category/(?P<table_name>[\w-]+)', 
    GenericCategoryViewSet, 
    basename='generic-category'
)

# device routes
router.register(r'device-models', DeviceModelViewSet, basename='device-models')
router.register(r'manufacturers', ManufacturerViewSet, basename='manufacturer')
router.register(r'eeg-channels', EEGChannelViewSet, basename='eegchannel')
router.register(r'frequency-bands', FrequencyBandViewSet, basename='frequency-bands')

# session route
router.register(r'sessions', SessionViewSet, basename='sessions')

# trigger routes
router.register(r'triggers/definitions', TriggerDefinitionViewSet, basename='trigger-definitions')
router.register(r'triggers/groups', TriggerGroupViewSet, basename='trigger-groups')
router.register(r'triggers/pairs', TriggerPairViewSet, basename='trigger-pairs')
router.register(r'triggers/hotkeys', TriggerHotkeyMappingViewSet, basename='trigger-hotkeys')

# stimulus routes
router.register(r'stimuli', StimulusViewSet, basename='stimuli')
router.register(r'playlists', StimulusPlaylistViewSet, basename='playlists')

# metadata routes
router.register(r'content-types', ContentTypeViewSet, basename='content-types')
router.register(r'metadata/registry', EntityMetaDataRegistryViewSet, basename='metadata-registry')
router.register(r'metadata/definitions', MetaDataDefinitionViewSet, basename='metadata-definitions')
router.register(r'metadata/groups', MetaDataGroupViewSet, basename='metadata-groups')

# ui and event routes
router.register(r'component-types', ComponentTypeViewSet, basename='componenttype')
router.register(r'locations', LocationViewSet, basename='locations')
router.register(r'components', ComponentViewSet, basename='components')
router.register(r'pages', PageViewSet, basename='pages')
router.register(r'page-groups', PageGroupViewSet, basename='page-groups')
router.register(r'events', EventViewSet, basename='events')
router.register(r'event-gallery', EventGalleryViewSet, basename='event-gallery')

# subject route
router.register(r'subjects', SubjectProfileViewSet, basename='subjects')

# script routes
router.register(r'scripts/languages', CustomScriptLanguageViewSet, basename='script-languages')
router.register(r'scripts/custom', CustomScriptViewSet, basename='custom-scripts')
router.register(r'scripts/data-processes', DataProcessViewSet, basename='data-processes')
router.register(r'scripts/data-displays', DataDisplayViewSet, basename='data-displays')

# recordings routes
router.register(r'recordings/eeg', EEGDataFileViewSet, basename='recordings-eeg')
router.register(r'recordings/heart-rate', HeartRateDataFileViewSet, basename='recordings-hr')
router.register(r'recordings/generic', GenericRecordingViewSet, basename='recordings-generic')

# medical routes
router.register(r'medical/history', MedicalHistoryViewSet, basename='medical-history')
router.register(r'medical/subject-history', SubjectMedicalHistoryViewSet, basename='subject-medical-history')

# media route
router.register(r'media/assets', MediaAssetViewSet, basename='media-assets')

# event management routes
router.register(r'event-management/roles', EventRoleViewSet, basename='event-roles')
router.register(r'event-management/groups', EventGroupViewSet, basename='event-groups')
router.register(r'event-management/subject-assignments', EventSubjectAssignmentViewSet, basename='event-subject-assignments')
router.register(r'event-management/staff-assignments', EventStaffAssignmentViewSet, basename='event-staff-assignments')

urlpatterns = [
    path('', include(router.urls)),
]
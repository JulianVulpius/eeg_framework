from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.category import GenericCategoryViewSet
from .views.session import SessionViewSet
from .views.stimulus import StimulusViewSet, PlaylistViewSet
from .views.subject import SubjectProfileViewSet, SubjectProfileInfoViewSet
from .views.recordings import EEGDataFileViewSet, HeartRateDataFileViewSet, GenericRecordingViewSet
from .views.media import MediaAssetViewSet
from .views.trigger import (
    TriggerDefinitionViewSet, TriggerGroupViewSet, 
    TriggerPairViewSet, TriggerHotkeyMappingViewSet
)
from .views.metadata import (
    ContentTypeViewSet, EntityMetaDataRegistryViewSet, 
    MetaDataDefinitionViewSet, MetaDataGroupViewSet,
    MetaDataGroupInstanceViewSet
)
from .views.masterdata import (
    LocationViewSet, FrequencyBandViewSet, 
    EEGChannelViewSet, ManufacturerViewSet
)
from .views.device import DeviceModelViewSet, DeviceInstanceViewSet
from .views.component import ComponentTypeViewSet, ComponentViewSet
from .views.page import PageViewSet, PageGroupViewSet
from .views.event import (
    EventViewSet, EventGalleryViewSet, 
    EventRoleViewSet, EventGroupViewSet, 
    EventSubjectAssignmentViewSet, EventStaffAssignmentViewSet,
    EventDeviceModelViewSet, EventGroupPageGroupDeviceViewSet
)

router = DefaultRouter()

# ------------------------------------------
# Generic & Categories
# ------------------------------------------
router.register(r'category/(?P<table_name>[\w-]+)', GenericCategoryViewSet, basename='generic-category')

# ------------------------------------------
# Masterdata (Stammdaten)
# ------------------------------------------
router.register(r'locations', LocationViewSet, basename='locations')
router.register(r'manufacturers', ManufacturerViewSet, basename='manufacturer')
router.register(r'eeg-channels', EEGChannelViewSet, basename='eegchannel')
router.register(r'frequency-bands', FrequencyBandViewSet, basename='frequency-bands')

# ------------------------------------------
# Devices (Hardware & Session Instances)
# ------------------------------------------
router.register(r'device-models', DeviceModelViewSet, basename='device-models')
router.register(r'device-instances', DeviceInstanceViewSet, basename='device-instances')

# ------------------------------------------
# Session & Recordings
# ------------------------------------------
router.register(r'sessions', SessionViewSet, basename='sessions')
router.register(r'recordings/eeg', EEGDataFileViewSet, basename='recordings-eeg')
router.register(r'recordings/heart-rate', HeartRateDataFileViewSet, basename='recordings-hr')
router.register(r'recordings/generic', GenericRecordingViewSet, basename='recordings-generic')

# ------------------------------------------
# Triggers & Stimuli
# ------------------------------------------
router.register(r'triggers/definitions', TriggerDefinitionViewSet, basename='trigger-definitions')
router.register(r'triggers/groups', TriggerGroupViewSet, basename='trigger-groups')
router.register(r'triggers/pairs', TriggerPairViewSet, basename='trigger-pairs')
router.register(r'triggers/hotkeys', TriggerHotkeyMappingViewSet, basename='trigger-hotkeys')
router.register(r'stimuli', StimulusViewSet, basename='stimuli')
router.register(r'playlists', PlaylistViewSet, basename='playlists')

# ------------------------------------------
# Metadata System
# ------------------------------------------
router.register(r'content-types', ContentTypeViewSet, basename='content-types')
router.register(r'metadata/registry', EntityMetaDataRegistryViewSet, basename='metadata-registry')
router.register(r'metadata/definitions', MetaDataDefinitionViewSet, basename='metadata-definitions')
router.register(r'metadata/groups', MetaDataGroupViewSet, basename='metadata-groups')
router.register(r'metadata-instances', MetaDataGroupInstanceViewSet, basename='metadata-instances')

# ------------------------------------------
# Subjects (Probanden)
# ------------------------------------------
router.register(r'subjects', SubjectProfileViewSet, basename='subjects')
router.register(r'subject-profile-infos', SubjectProfileInfoViewSet, basename='subject-profile-infos')

# ------------------------------------------
# Media
# ------------------------------------------
router.register(r'media/assets', MediaAssetViewSet, basename='media-assets')

# ------------------------------------------
# UI Components & Pages
# ------------------------------------------
router.register(r'component-types', ComponentTypeViewSet, basename='componenttype')
router.register(r'components', ComponentViewSet, basename='components')
router.register(r'pages', PageViewSet, basename='pages')
router.register(r'page-groups', PageGroupViewSet, basename='page-groups')

# ------------------------------------------
# Events & Event Management
# ------------------------------------------
router.register(r'events', EventViewSet, basename='events')
router.register(r'event-gallery', EventGalleryViewSet, basename='event-gallery')
router.register(r'event-management/roles', EventRoleViewSet, basename='event-roles')
router.register(r'event-management/groups', EventGroupViewSet, basename='event-groups')
router.register(r'event-management/subject-assignments', EventSubjectAssignmentViewSet, basename='event-subject-assignments')
router.register(r'event-management/staff-assignments', EventStaffAssignmentViewSet, basename='event-staff-assignments')
router.register(r'event-management/device-pool', EventDeviceModelViewSet, basename='event-device-pool')
router.register(r'event-management/phase-device-configs', EventGroupPageGroupDeviceViewSet, basename='phase-device-configs')
router.register(r'event-device-models', EventDeviceModelViewSet, basename='event-device-model') # Legacy support for frontend


urlpatterns = [
    path('', include(router.urls)),
]
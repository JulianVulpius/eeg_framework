from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GenericCategoryViewSet, TriggerDefinitionViewSet,  TriggerGroupViewSet, TriggerPairViewSet, FrequencyBandViewSet, DeviceModelViewSet, SubjectProfileViewSet, TriggerHotkeyMappingViewSet, StimulusViewSet, StimulusPlaylistViewSet
from .views import ContentTypeViewSet, EntityMetaDataRegistryViewSet, MetaDataDefinitionViewSet, MetaDataGroupViewSet, ManufacturerViewSet, EEGChannelViewSet, ComponentTypeViewSet

router = DefaultRouter()


router.register(
    r'category/(?P<table_name>[\w-]+)', 
    GenericCategoryViewSet, 
    basename='generic-category'
)

router.register(
    r'triggers/definitions', 
    TriggerDefinitionViewSet, 
    basename='trigger-definitions'
)

router.register(
    r'triggers/groups', 
    TriggerGroupViewSet, 
    basename='trigger-groups'
)

router.register(
    r'triggers/pairs', 
    TriggerPairViewSet, 
    basename='trigger-pairs'
)

router.register(
    r'frequency-bands', 
    FrequencyBandViewSet, 
    basename='frequency-bands'
)

router.register(
    r'device-models', 
    DeviceModelViewSet, 
    basename='device-models'
)

router.register(
    r'subjects', 
    SubjectProfileViewSet, 
    basename='subjects'
)

router.register(
    r'triggers/hotkeys', 
    TriggerHotkeyMappingViewSet, 
    basename='trigger-hotkeys'
)

router.register(
    r'stimuli', 
    StimulusViewSet, 
    basename='stimuli'
)

router.register(
    r'playlists', 
    StimulusPlaylistViewSet, 
    basename='playlists'
)

router.register(
    r'content-types', 
    ContentTypeViewSet, 
    basename='content-types'
)

router.register(
    r'metadata/registry', 
    EntityMetaDataRegistryViewSet, 
    basename='metadata-registry'
)

router.register(
    r'metadata/definitions', 
    MetaDataDefinitionViewSet, 
    basename='metadata-definitions'
)

router.register(
    r'metadata/groups', 
    MetaDataGroupViewSet, 
    basename='metadata-groups'
)

router.register(
    r'manufacturers', 
    ManufacturerViewSet, 
    basename='manufacturer'
)

router.register(
    r'eeg-channels', 
    EEGChannelViewSet, 
    basename='eegchannel'
)

router.register(
    r'component-types', 
    ComponentTypeViewSet, 
    basename='componenttype'
    )

urlpatterns = [
    path('', include(router.urls)),
]
export const menuStructure = [
  {
    id: 'events',
    titleKey: 'nav.events',
    descKey: 'dashboard.events_desc', 
    items: [
      { labelKey: 'nav.events', route: '/events' },
      { labelKey: 'nav.page_groups', route: '/events/page-groups' },
      { labelKey: 'nav.pages', route: '/events/pages' },
      { labelKey: 'nav.components', route: '/events/components' }
    ]
  },
  {
    id: 'stimuli',
    titleKey: 'nav.stimuli_management', 
    descKey: 'dashboard.stimuli_desc',
    items: [
      { labelKey: 'nav.playlists', route: '/stimuli/playlists' },
      { labelKey: 'nav.stimuli', route: '/stimuli/items' }
    ]
  },
  {
    id: 'triggers',
    titleKey: 'nav.trigger_engine',
    descKey: 'dashboard.triggers_desc',
    items: [
      { labelKey: 'nav.trigger_groups', route: '/triggers/groups' },
      { labelKey: 'nav.trigger_pairs', route: '/triggers/pairs' },
      { labelKey: 'nav.trigger_definitions', route: '/triggers/definitions' }
    ]
  },
  {
    id: 'metadata',
    titleKey: 'nav.metadata_engine',
    descKey: 'dashboard.metadata_desc',
    items: [
      { labelKey: 'nav.registry_setup', route: '/metadata/registry' },
      { labelKey: 'nav.metadata_groups', route: '/metadata/groups' },
      { labelKey: 'nav.metadata_definitions', route: '/metadata/definitions' }
    ]
  },
  {
    id: 'masterData',
    titleKey: 'nav.master_data',
    descKey: 'dashboard.masterdata_desc',
    items: [
      { labelKey: 'nav.subjects', route: '/masterdata/subjects' },
      { labelKey: 'nav.locations', route: '/masterdata/locations' },
      { labelKey: 'nav.device_models', route: '/masterdata/device-models' },
      { labelKey: 'nav.manufacturers', route: '/masterdata/manufacturers' },
      { labelKey: 'nav.frequency_bands', route: '/masterdata/frequency-bands' },
      { labelKey: 'nav.eeg_channels', route: '/masterdata/eeg-channels' },
      { labelKey: 'nav.component_types', route: '/masterdata/component-types' }
    ]
  },
  {
    id: 'categories',
    titleKey: 'nav.categories',
    descKey: 'dashboard.categories_desc',
    items: [
      { labelKey: 'nav.event_categories', route: '/categories/event' },
      { labelKey: 'nav.page_group_categories', route: '/categories/page-group' },
      { labelKey: 'nav.page_categories', route: '/categories/page' },
      { labelKey: 'nav.component_categories', route: '/categories/component' },
      { labelKey: 'nav.stimulus_categories', route: '/categories/stimulus' },
      { labelKey: 'nav.playlist_categories', route: '/categories/playlist' },
      { labelKey: 'nav.trigger_group_categories', route: '/categories/trigger-group' },
      { labelKey: 'nav.metadata_group_categories', route: '/categories/metadata-group' },
      { labelKey: 'nav.metadata_categories', route: '/categories/metadata' },
      { labelKey: 'nav.location_categories', route: '/categories/location' },
      { labelKey: 'nav.device_model_categories', route: '/categories/device-model' },
      { labelKey: 'nav.manufacturer_categories', route: '/categories/manufacturer' },
      { labelKey: 'nav.generic_recording_categories', route: '/categories/generic-recording' }
    ]
  }
];
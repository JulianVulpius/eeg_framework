export const menuStructure = [
  {
    id: 'events',
    titleKey: 'nav.events',
    descKey: 'dashboard.events_desc', 
    items: [
      { labelKey: 'nav.events', route: '/events' },
      { labelKey: 'nav.page_groups', route: '/page-groups' },
      { labelKey: 'nav.pages', route: '/pages' },
      { labelKey: 'nav.components', route: '/components' }
    ]
  },
  {
    id: 'stimuli',
    titleKey: 'nav.stimuli_management', 
    descKey: 'dashboard.stimuli_desc',
    items: [
      { labelKey: 'nav.playlists', route: '/playlists' },
      { labelKey: 'nav.stimuli', route: '/stimuli' }
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
      { labelKey: 'nav.subjects', route: '/master-data/subjects' },
      { labelKey: 'nav.locations', route: '/locations' },
      { labelKey: 'nav.device_models', route: '/master-data/device-models' },
      { labelKey: 'nav.manufacturers', route: '/master-data/manufacturers' },
      { labelKey: 'nav.frequency_bands', route: '/master-data/frequency-bands' },
      { labelKey: 'nav.eeg_channels', route: '/master-data/eeg-channels' },
      { labelKey: 'nav.component_types', route: '/component-types' }
    ]
  },
  {
    id: 'categories',
    titleKey: 'nav.categories',
    descKey: 'dashboard.categories_desc',
    items: [
      { labelKey: 'nav.event_categories', route: '/category/event-categories' },
      { labelKey: 'nav.page_group_categories', route: '/category/page-group-categories' },
      { labelKey: 'nav.page_categories', route: '/category/page-categories' },
      { labelKey: 'nav.component_categories', route: '/category/component-categories' },
      { labelKey: 'nav.stimulus_categories', route: '/category/stimulus-categories' },
      { labelKey: 'nav.playlist_categories', route: '/category/playlist-categories' },
      { labelKey: 'nav.trigger_group_categories', route: '/category/trigger-group-categories' },
      { labelKey: 'nav.metadata_group_categories', route: '/category/metadata-group-categories' },
      { labelKey: 'nav.metadata_categories', route: '/category/metadata-categories' },
      { labelKey: 'nav.location_categories', route: '/category/location-categories' },
      { labelKey: 'nav.device_model_categories', route: '/category/device-model-categories' },
      { labelKey: 'nav.manufacturer_categories', route: '/category/manufacturer-categories' },
      { labelKey: 'nav.data_process_categories', route: '/category/data-process-categories' },
      { labelKey: 'nav.data_display_categories', route: '/category/data-display-categories' }
    ]
  }
]
import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'

// --- Categories ---
import CategoryManagerView from '../views/categories/CategoryManagerView.vue'

// --- Triggers ---
import TriggerDefinitionView from '../views/triggers/TriggerDefinitionView.vue'
import TriggerGroupView from '../views/triggers/TriggerGroupView.vue'
import TriggerPairView from '../views/triggers/TriggerPairView.vue'

// --- Master Data ---
import FrequencyBandView from '../views/masterdata/FrequencyBandView.vue'
import DeviceModelView from '../views/masterdata/DeviceModelView.vue'
import SubjectProfileView from '../views/masterdata/SubjectProfileView.vue'
import ManufacturerView from '../views/masterdata/ManufacturerView.vue'
import EEGChannelView from '../views/masterdata/EEGChannelView.vue' 
import ComponentTypeView from '../views/masterdata/ComponentTypeView.vue'
import LocationView from '../views/masterdata/LocationView.vue'

// --- Session ---
import SessionControlView from '../views/session/SessionControlView.vue'
import SessionLauncherView from '../views/session/SessionLauncherView.vue'
import SessionRunnerView from '../views/session/SessionRunnerView.vue'
import SessionHistoryView from '../views/session/SessionHistoryView.vue'
import SingleSessionReportView from '../views/session/SingleSessionReportView.vue'
import CombinedReportView from '../views/session/CombinedReportView.vue'
import PageGroupReportView from '../views/session/PageGroupReportView.vue'

// --- Stimuli ---
import StimulusView from '../views/stimuli/StimulusView.vue'
import PlaylistView from '../views/stimuli/PlaylistView.vue'

// --- Metadata ---
import MetaDataRegistryView from '../views/metadata/MetaDataRegistryView.vue'
import MetaDataDefinitionView from '../views/metadata/MetaDataDefinitionView.vue'
import MetaDataGroupView from '../views/metadata/MetaDataGroupView.vue'

// --- Events ---
import EventManagementView from '../views/events/EventManagementView.vue'
import PageGroupView from '../views/events/PageGroupView.vue'
import ComponentManagerView from '../views/events/ComponentManagerView.vue'
import PageManagerView from '../views/events/PageManagerView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: MainLayout,
      children: [
        { path: '', name: 'dashboard', component: () => import('../views/HomeView.vue') },
        
        { path: 'triggers/definitions', name: 'trigger-definitions', component: TriggerDefinitionView },
        { path: 'triggers/groups', name: 'trigger-groups', component: TriggerGroupView },
        { path: 'triggers/pairs', name: 'trigger-pairs', component: TriggerPairView },
        
        { path: 'master-data/frequency-bands', name: 'frequency-bands', component: FrequencyBandView },
        { path: 'master-data/device-models', name: 'device-models', component: DeviceModelView },
        { path: 'master-data/subjects', name: 'subjects', component: SubjectProfileView },
        { path: 'master-data/manufacturers', name: 'manufacturers', component: ManufacturerView },
        { path: 'master-data/eeg-channels', name: 'eeg-channels', component: EEGChannelView },
        { path: '/component-types', name: 'ComponentTypes', component: ComponentTypeView },
        { path: '/locations', name: 'Locations', component: LocationView },

        { path: 'session-control', name: 'session-control', component: SessionControlView },
        { path: 'launcher', name: 'session-launcher', component: SessionLauncherView },
        { path: 'session/run/:id', name: 'session-runner', component: SessionRunnerView, props: true },
        { path: 'session-history', name: 'session-history', component: SessionHistoryView },
        { path: 'session/report/:id', name: 'session-report', component: SingleSessionReportView, props: true },
        { path: '/session/aggregate-report/:eventId/:subjectId', name: 'CombinedReport', component: CombinedReportView, props: true },
        { path: '/session/pagegroup-report/:eventId/:pageGroupId', name: 'PageGroupReport', component: PageGroupReportView, props: true },

        { path: 'stimuli', name: 'stimuli', component: StimulusView },
        { path: 'playlists', name: 'playlists', component: PlaylistView },

        { path: 'metadata/registry', name: 'metadata-registry', component: MetaDataRegistryView },
        { path: 'metadata/definitions', name: 'metadata-definitions', component: MetaDataDefinitionView },
        { path: 'metadata/groups', name: 'metadata-groups', component: MetaDataGroupView },

        { path: 'events', name: 'events', component: EventManagementView },
        { path: 'page-groups', name: 'page-groups', component: PageGroupView },
        { path: 'components', name: 'components', component: ComponentManagerView },
        { path: 'pages', name: 'pages', component: PageManagerView },

        { path: 'category/:tableName', name: 'category-manager', component: CategoryManagerView, props: true }
      ]
    }
  ]
})

export default router
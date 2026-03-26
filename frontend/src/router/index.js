import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '../layouts/MainLayout.vue'
import CategoryManagerView from '../views/CategoryManagerView.vue'
import TriggerDefinitionView from '../views/TriggerDefinitionView.vue'
import TriggerGroupView from '../views/TriggerGroupView.vue'
import TriggerPairView from '../views/TriggerPairView.vue'
import FrequencyBandView from '../views/FrequencyBandView.vue'
import DeviceModelView from '../views/DeviceModelView.vue'
import SubjectProfileView from '../views/SubjectProfileView.vue'
import SessionControlView from '../views/SessionControlView.vue'
import StimulusView from '../views/StimulusView.vue'
import PlaylistView from '../views/PlaylistView.vue'
import MetaDataRegistryView from '../views/MetaDataRegistryView.vue'
import MetaDataDefinitionView from '../views/MetaDataDefinitionView.vue'
import MetaDataGroupView from '../views/MetaDataGroupView.vue'
import ManufacturerView from '../views/ManufacturerView.vue'
import EEGChannelView from '../views/EEGChannelView.vue' 
import ComponentTypeView from '../views/ComponentTypeView.vue'
import EventManagementView from '../views/EventManagementView.vue'
import PageGroupView from '../views/PageGroupView.vue'
import SessionLauncherView from '../views/SessionLauncherView.vue'
import SessionRunnerView from '../views/SessionRunnerView.vue'
import ComponentManagerView from '../views/ComponentManagerView.vue'
import PageManagerView from '../views/PageManagerView.vue'
import SessionHistoryView from '../views/SessionHistoryView.vue'
import LocationView from '../views/LocationView.vue'
import SingleSessionReportView from '../views/SingleSessionReportView.vue'
import CombinedReportView from '../views/CombinedReportView.vue'
import PageGroupReportView from '../views/PageGroupReportView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      // parent route
      path: '/',
      component: MainLayout,
      children: [
        {
          // default dashboard view when logging in
          path: '',
          name: 'dashboard',
          component: () => import('../views/HomeView.vue')
        },
        {
          path: 'triggers/definitions',
          name: 'trigger-definitions',
          component: TriggerDefinitionView
        },
        {
          path: 'triggers/groups',
          name: 'trigger-groups',
          component: TriggerGroupView
        },
        {
          path: 'triggers/pairs',
          name: 'trigger-pairs',
          component: TriggerPairView
        },
        {
          path: 'master-data/frequency-bands',
          name: 'frequency-bands',
          component: FrequencyBandView
        },
        {
          path: 'master-data/device-models',
          name: 'device-models',
          component: DeviceModelView
        },
        {
          path: 'master-data/subjects',
          name: 'subjects',
          component: SubjectProfileView
        },
        {
          path: 'session-control',
          name: 'session-control',
          component: SessionControlView
        },
        {
          path: 'stimuli',
          name: 'stimuli',
          component: StimulusView
        },
        {
          path: 'playlists',
          name: 'playlists',
          component: PlaylistView
        },
        {
          path: 'metadata/registry',
          name: 'metadata-registry',
          component: MetaDataRegistryView
        },
        {
          path: 'metadata/definitions',
          name: 'metadata-definitions',
          component: MetaDataDefinitionView
        },
        {
          path: 'metadata/groups',
          name: 'metadata-groups',
          component: MetaDataGroupView
        },
        {
          path: 'master-data/manufacturers',
          name: 'manufacturers',
          component: ManufacturerView
        },
        {
          path: 'master-data/eeg-channels',
          name: 'eeg-channels',
          component: EEGChannelView
        },
        {
          path: '/component-types',
          name: 'ComponentTypes',
          component: ComponentTypeView
        },
        {
          path: 'events',
          name: 'events',
          component: EventManagementView
        },
        {
          path: 'page-groups',
          name: 'page-groups',
          component: PageGroupView
        },
        {
          path: 'launcher',
          name: 'session-launcher',
          component: SessionLauncherView
        },
        {
          path: 'session/run/:id',
          name: 'session-runner',
          component: SessionRunnerView,
          props: true
        },
        {
          path: 'session/report/:id',
          name: 'session-report',
          component: SingleSessionReportView,
          props: true
        },
        {
          path: 'components',
          name: 'components',
          component: ComponentManagerView
        },
        {
          path: 'pages',
          name: 'pages',
          component: PageManagerView
        },
        {
          path: 'session-history',
          name: 'session-history',
          component: SessionHistoryView
        },
        {
          path: '/locations',
          name: 'Locations',
          component: LocationView
        },
        {
          path: '/session/aggregate-report/:eventId/:subjectId',
          name: 'CombinedReport',
          component: CombinedReportView,
          props: true
        },
        {
          path: '/session/pagegroup-report/:eventId/:pageGroupId',
          name: 'PageGroupReport',
          component: PageGroupReportView,
          props: true
        },
        {
          // dynamic route that powers all category CRUD tables
          path: 'category/:tableName',
          name: 'category-manager',
          component: CategoryManagerView,
          props: true // tells the router to pass the URL parameter as a prop to the component
        }
      ]
    }
  ]
})

export default router
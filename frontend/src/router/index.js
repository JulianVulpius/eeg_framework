import { createRouter, createWebHistory } from 'vue-router'
import MainLayout from '@/layouts/MainLayout.vue'
import HomeView from '@/views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: MainLayout,
      children: [
        { 
          path: '', 
          name: 'home', 
          component: HomeView 
        },
        { 
          path: 'events', 
          component: () => import('@/views/events/EventManagementView.vue') 
        },
        { 
          path: 'events/page-groups', 
          component: () => import('@/views/events/PageGroupView.vue') 
        },
        { 
          path: 'events/pages', 
          component: () => import('@/views/events/PageManagerView.vue') 
        },
        { 
          path: 'events/components', 
          component: () => import('@/views/events/ComponentManagerView.vue') 
        },
        { 
          path: 'events/:id', 
          component: () => import('@/views/events/EventDetailView.vue') 
        },
        { 
          path: 'stimuli/playlists', 
          component: () => import('@/views/stimuli/PlaylistView.vue') 
        },
        { 
          path: 'stimuli/items', 
          component: () => import('@/views/stimuli/StimulusView.vue') 
        },
        { 
          path: 'triggers/groups', 
          component: () => import('@/views/triggers/TriggerGroupView.vue') 
        },
        { 
          path: 'triggers/pairs', 
          component: () => import('@/views/triggers/TriggerPairView.vue') 
        },
        { 
          path: 'triggers/definitions', 
          component: () => import('@/views/triggers/TriggerDefinitionView.vue') 
        },
        { 
          path: 'metadata/registry', 
          component: () => import('@/views/metadata/MetaDataRegistryView.vue') 
        },
        { 
          path: 'metadata/groups', 
          component: () => import('@/views/metadata/MetaDataGroupView.vue') 
        },
        { 
          path: 'metadata/definitions', 
          component: () => import('@/views/metadata/MetaDataDefinitionView.vue') 
        },
        { 
          path: 'masterdata/subjects', 
          component: () => import('@/views/masterdata/SubjectProfileView.vue') 
        },
        { 
          path: 'masterdata/locations', 
          component: () => import('@/views/masterdata/LocationView.vue') 
        },
        { 
          path: 'masterdata/device-models', 
          component: () => import('@/views/masterdata/DeviceModelView.vue') 
        },
        { 
          path: 'masterdata/manufacturers', 
          component: () => import('@/views/masterdata/ManufacturerView.vue') 
        },
        { 
          path: 'masterdata/frequency-bands', 
          component: () => import('@/views/masterdata/FrequencyBandView.vue') 
        },
        { 
          path: 'masterdata/eeg-channels', 
          component: () => import('@/views/masterdata/EEGChannelView.vue') 
        },
        { 
          path: 'masterdata/component-types', 
          component: () => import('@/views/masterdata/ComponentTypeView.vue') 
        },
        { 
          path: 'categories/:categoryType', 
          component: () => import('@/views/categories/CategoryManagerView.vue'),
          props: true 
        },
        { 
          path: 'sessions/launcher', 
          component: () => import('@/views/session/SessionLauncherView.vue') 
        },
        { 
          path: 'sessions/runner', 
          component: () => import('@/views/session/SessionRunnerView.vue') 
        },
        { 
          path: 'sessions/control', 
          component: () => import('@/views/session/SessionControlView.vue') 
        },
        { 
          path: 'sessions/history', 
          component: () => import('@/views/session/SessionHistoryView.vue') 
        },
        { 
          path: 'sessions/reports/single', 
          component: () => import('@/views/session/SingleSessionReportView.vue') 
        },
        { 
          path: 'sessions/reports/combined', 
          component: () => import('@/views/session/CombinedReportView.vue') 
        },
        { 
          path: 'sessions/reports/page-groups', 
          component: () => import('@/views/session/PageGroupReportView.vue') 
        }
      ]
    }
  ]
})

export default router
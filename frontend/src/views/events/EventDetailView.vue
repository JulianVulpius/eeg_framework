<template>
  <div class="event-detail-view">
    
    <div class="header-area">
      <div style="width: 100%;">
        <BaseBreadcrumb :items="breadcrumbItems" />
        <h2 style="margin-top: 5px;">{{ $t('views.events.detail_title') }}: {{ eventData.name || '...' }}</h2>
      </div>
    </div>

    <div class="tabs">
      <button :class="['tab-btn', { active: activeTab === 'general' }]" @click="activeTab = 'general'">
        {{ $t('views.events.tab_general') }}
      </button>
      
      <button :class="['tab-btn', { active: activeTab === 'page_groups' }]" @click="activeTab = 'page_groups'">
        {{ $t('nav.page_groups') }}
      </button>

      <button :class="['tab-btn', { active: activeTab === 'groups' }]" @click="activeTab = 'groups'">
        {{ $t('views.events.tab_groups') }}
      </button>
      <button :class="['tab-btn', { active: activeTab === 'roles' }]" @click="activeTab = 'roles'" v-if="hasPermission('manage_roles') || hasPermission('admin')">
        {{ $t('views.events.tab_roles') }}
      </button>
      <button :class="['tab-btn', { active: activeTab === 'staff' }]" @click="activeTab = 'staff'">
        {{ $t('views.events.tab_staff') }}
      </button>
      <button :class="['tab-btn', { active: activeTab === 'subjects' }]" @click="activeTab = 'subjects'">
        {{ $t('views.events.tab_subjects') }}
      </button>
    </div>

    <div class="tab-content">
      
      <div v-if="activeTab === 'general'" class="panel">
        <h3>{{ $t('views.events.tab_general') }}</h3>
        <p>Hierhin kommen die normalen Formularfelder (Name, Datum, Ort).</p>
      </div>

      <div v-if="activeTab === 'page_groups'" class="panel">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
          <h3>{{ $t('nav.page_groups') }}</h3>
          <button class="btn-primary">{{ $t('actions.save') }}</button>
        </div>
        <p style="margin-bottom: 15px; color: #555;">Weise diesem Event die benötigten Phasen (Seiten-Gruppen) zu.</p>
        
        <BaseTransferList
          v-model="assignedPageGroups"
          :options="availablePageGroups"
          :leftTitle="$t('views.events.available_groups')"
          :rightTitle="$t('views.events.selected_groups')"
          :enableOrdering="true"
        />
      </div>

      <div v-if="activeTab === 'groups'" class="panel">
        <h3>{{ $t('views.events.tab_groups') }}</h3>
        <div v-if="hasPermission('admin')">
          <button class="btn-primary">+ {{ $t('actions.add_new') }} Gruppe</button>
        </div>
        <div v-else class="locked-area">🔒 {{ $t('views.events.permission_denied') }}</div>
      </div>

      <div v-if="activeTab === 'roles'" class="panel">
        <h3>{{ $t('views.events.tab_roles') }}</h3>
      </div>

      <div v-if="activeTab === 'staff'" class="panel">
        <h3>{{ $t('views.events.tab_staff') }}</h3>
      </div>

      <div v-if="activeTab === 'subjects'" class="panel">
        <h3>{{ $t('views.events.tab_subjects') }}</h3>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useMockAuth } from '@/composables/useMockAuth'

import BaseBreadcrumb from '@/components/ui/BaseBreadcrumb.vue'
import BaseTransferList from '@/components/ui/BaseTransferList.vue'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const { hasPermission } = useMockAuth()

const eventId = route.params.id
const activeTab = ref('general')
const eventData = ref({})

const availablePageGroups = ref([])
const assignedPageGroups = ref([])

const breadcrumbItems = computed(() => [
  { label: t('nav.events'), route: '/events' },
  { label: eventData.value.name || t('common.loading') }
])

const loadEventData = async () => {
  try {
    const res = await api.get(`events/${eventId}/`)
    eventData.value = res.data
    assignedPageGroups.value = res.data.page_groups || []
  } catch (error) {
    console.error("Could not load event details", error)
  }
}

const loadPageGroups = async () => {
  try {
    const res = await api.get('page-groups/')
    availablePageGroups.value = res.data
  } catch (error) {
    console.error("Could not load page groups", error)
  }
}

onMounted(() => {
  loadEventData()
  loadPageGroups()
})
</script>

<style scoped>
.event-detail-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.header-area {
  background: white;
  padding: 15px 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.header-area h2 {
  color: #2c3e50;
}
.tabs {
  display: flex;
  gap: 10px;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 0;
}
.tab-btn {
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  padding: 10px 20px;
  font-size: 1rem;
  font-weight: 600;
  color: #7f8c8d;
  cursor: pointer;
  transition: all 0.2s;
}
.tab-btn:hover { color: #3498db; }
.tab-btn.active {
  color: #3498db;
  border-bottom: 3px solid #3498db;
}
.panel {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  min-height: 400px;
}
.locked-area {
  padding: 40px;
  text-align: center;
  background: #f8f9fa;
  border: 2px dashed #e74c3c;
  border-radius: 8px;
  color: #c0392b;
  font-weight: bold;
}
</style>
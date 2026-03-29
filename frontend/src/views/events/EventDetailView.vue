<template>
  <div class="event-detail-view">
    <div class="header-area">
      <button @click="router.push('/events')" class="btn-secondary">
        ← {{ $t('actions.back') }}
      </button>
      <h2>{{ $t('views.events.detail_title') }}: {{ eventData.name || '...' }}</h2>
    </div>

    <div class="tabs">
      <button :class="['tab-btn', { active: activeTab === 'general' }]" @click="activeTab = 'general'">
        {{ $t('views.events.tab_general') }}
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
        <p>Hierhin kommen die normalen Formularfelder (Name, Datum, Ort) aus dem alten Modal, um die Basisdaten zu speichern.</p>
        </div>

      <div v-if="activeTab === 'groups'" class="panel">
        <h3>{{ $t('views.events.tab_groups') }}</h3>
        <div v-if="hasPermission('admin')">
          <p>Hier werden später die EventGroups (z.B. Placebo, Kontrollgruppe) und die zugewiesenen PageGroups verwaltet.</p>
          <button class="btn-primary">+ {{ $t('actions.add_new') }} Gruppe</button>
        </div>
        <div v-else class="locked-area">
           🔒 {{ $t('views.events.permission_denied') }}
        </div>
      </div>

      <div v-if="activeTab === 'roles'" class="panel">
        <h3>{{ $t('views.events.tab_roles') }}</h3>
        <p>Hier definieren wir die JSON-Permissions (z.B. Checkboxen für 'Can Add Subject', 'Can View Report').</p>
      </div>

      <div v-if="activeTab === 'staff'" class="panel">
        <h3>{{ $t('views.events.tab_staff') }}</h3>
        <p>Mitarbeiter diesem Event zuweisen und Rollen/Target-Groups verteilen.</p>
      </div>

      <div v-if="activeTab === 'subjects'" class="panel">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
          <h3>{{ $t('views.events.tab_subjects') }}</h3>
          
          <button v-if="hasPermission('add_subjects') || hasPermission('admin')" class="btn-primary">
            + Proband zuweisen
          </button>
        </div>

        <div v-if="hasPermission('view_subjects') || hasPermission('admin')">
          <table class="data-table">
            <thead>
              <tr>
                <th>Proband ID</th>
                <th>Zugewiesene Event-Gruppe</th>
                <th>Aktionen</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>SUB-001</td>
                <td>Treatment Gruppe</td>
                <td><button class="btn-secondary" disabled>Bearbeiten</button></td>
              </tr>
              <tr>
                <td>SUB-002</td>
                <td>Placebo Gruppe</td>
                <td><button class="btn-secondary" disabled>Bearbeiten</button></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="locked-area">
           🔒 {{ $t('views.events.permission_denied') }}
        </div>

      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useMockAuth } from '@/composables/useMockAuth'

const router = useRouter()
const route = useRoute()
const { t } = useI18n()

// import the mock permissions
const { hasPermission } = useMockAuth()

const eventId = route.params.id
const activeTab = ref('general')
const eventData = ref({})

const loadEventBaseData = async () => {
  try {
    // load base event data to show in the header
    const res = await api.get(`events/${eventId}/`)
    eventData.value = res.data
  } catch (error) {
    console.error("could not load event details", error)
  }
}

onMounted(() => {
  loadEventBaseData()
})
</script>

<style scoped>
.event-detail-view {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.header-area {
  display: flex;
  align-items: center;
  gap: 20px;
  background: white;
  padding: 15px 20px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
.header-area h2 {
  margin: 0;
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
.tab-btn:hover {
  color: #3498db;
}
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
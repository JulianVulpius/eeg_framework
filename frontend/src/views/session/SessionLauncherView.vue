<template>
  <div class="session-launcher">
    <div class="page-header">
      <h1>{{ $t('nav.session_launcher') }}</h1>
    </div>

    <div class="launcher-cards">
      <!-- 1. EVENT -->
      <div class="card">
        <h2>{{ $t('views.launcher.select_event') }}</h2>
        <BaseSearchSelect v-model="selectedEventId" :options="events" :placeholder="$t('common.search')" />
      </div>

      <!-- 2. SUBJECT (Gefiltert nach Event!) -->
      <div class="card" :class="{ 'disabled-card': !selectedEventId }">
        <h2>{{ $t('views.launcher.select_subject') }}</h2>
        
        <div v-if="isLoadingEventContext" class="text-muted mb-2">
          {{ $t('common.loading') }}...
        </div>
        
        <div v-else style="display: flex; gap: 10px; align-items: flex-start;">
          <div style="flex: 1;">
            <BaseSearchSelect 
              v-model="selectedSubjectId" 
              :options="availableSubjectsForEvent" 
              :placeholder="$t('common.search')" 
              :disabled="!selectedEventId" 
            />
          </div>
          <button class="btn-secondary" @click="isSubjectModalOpen = true" :disabled="!selectedEventId">
            {{ $t('actions.add_new') }}
          </button>
        </div>
      </div>

      <!-- 3. EVENT GROUP (Dynamisch anhand Subject) -->
      <div class="card" v-if="selectedSubjectId" :class="{ 'disabled-card': isLoadingEventContext }">
        <h2>Experimentelle Gruppe</h2>
        
        <div v-if="subjectGroupAssignments.length === 0" style="color: #c0392b; font-weight: bold; background: #fadbd8; padding: 10px; border-radius: 6px;">
          {{ $t('views.launcher.no_group_assigned') }}
        </div>
        
        <div v-else-if="subjectGroupAssignments.length === 1" style="color: #27ae60; font-weight: 500; background: #e8f8f5; padding: 10px; border-radius: 6px;">
          ✅ {{ $t('views.launcher.group_auto_selected') }} 
          <strong>{{ getGroupName(selectedEventGroupId) }}</strong>
        </div>
        
        <div v-else>
          <BaseSearchSelect 
            v-model="selectedEventGroupId" 
            :options="availableEventGroupsForDropdown" 
            :placeholder="$t('views.launcher.select_group')" 
          />
        </div>
      </div>

      <!-- 4. PHASE (Gefiltert nach Gruppe) -->
      <div class="card" :class="{ 'disabled-card': !selectedEventGroupId }">
        <h2>{{ $t('views.launcher.select_phase') }}</h2>
        <BaseSearchSelect v-model="selectedPageGroupId" :options="availablePageGroups" :placeholder="$t('common.search')" :disabled="!selectedEventGroupId" />
      </div>

      <!-- 5. LOCATION -->
      <div class="card" :class="{ 'disabled-card': !selectedEventId }">
        <h2>{{ $t('views.launcher.select_location') }} (Optional)</h2>
        <BaseSearchSelect v-model="selectedLocationId" :options="locations" :placeholder="$t('common.search')" :disabled="!selectedEventId" />
      </div>

      <!-- 6. SCOPE -->
      <div class="card" :class="{ 'disabled-card': !selectedPageGroupId }">
        <h2>{{ $t('views.launcher.select_scope') }}</h2>
        <select v-model="selectedScope" class="form-control" :disabled="!selectedPageGroupId" style="width: 100%; padding: 10px; font-size: 1rem; border: 1px solid #dcdde1; border-radius: 4px; background-color: #fff;">
          <option v-for="opt in scopeOptions" :key="opt.id" :value="opt.id">{{ opt.name }}</option>
        </select>
      </div>
    </div>

    <!-- FOOTER -->
    <div class="action-footer">
      <button class="btn-play-sync" :disabled="!isLaunchable" @click="startSession" style="font-size: 1.2rem; padding: 15px 30px;">
        <span class="play-icon">▶</span> {{ $t('views.launcher.start_session') }}
      </button>
    </div>

    <!-- NEUES MODAL FÜR SUBJEKTE -->
    <LauncherSubjectModal 
      :isOpen="isSubjectModalOpen"
      :eventId="selectedEventId"
      :eventName="selectedEventName"
      :eventGroups="rawEventGroups.filter(g => g.event === selectedEventId)"
      @saved="onSubjectCreated"
      @close="isSubjectModalOpen = false"
    />

    <BaseModal :isOpen="isResumeModalOpen" :title="$t('views.launcher.session_exists_title')" @close="isResumeModalOpen = false">
      <div style="margin-bottom: 25px; line-height: 1.5; font-size: 1.05rem; color: #2c3e50;">
        {{ $t('views.launcher.session_exists_desc') }}
      </div>
      <div class="modal-actions" style="justify-content: space-between;">
        <button type="button" class="btn-secondary" @click="isResumeModalOpen = false">{{ $t('actions.cancel') }}</button>
        <div style="display: flex; gap: 10px;">
          <button type="button" class="btn-secondary" style="background: #fadbd8; color: #c0392b; border-color: #e74c3c;" @click="resetSession">
            {{ $t('views.launcher.btn_reset') }}
          </button>
          <button type="button" class="btn-primary" @click="resumeSession">
            {{ $t('views.launcher.btn_resume') }}
          </button>
        </div>
      </div>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'

import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import LauncherSubjectModal from '@/components/runner/LauncherSubjectModal.vue'

const { t } = useI18n()
const router = useRouter()
const { showToast } = useToast()

const rawEvents = ref([])
const rawSubjects = ref([])
const rawPageGroups = ref([])
const rawLocations = ref([])
const rawEventGroups = ref([]) 

// State für Event Kontext
const eventAssignments = ref([]) // Alle Zuweisungen für das aktuelle Event
const isLoadingEventContext = ref(false)

const selectedEventId = ref(null)
const selectedSubjectId = ref(null)
const selectedEventGroupId = ref(null) 
const selectedPageGroupId = ref(null)
const selectedLocationId = ref(null)
const selectedScope = ref('ALL')

const isSubjectModalOpen = ref(false)
const isResumeModalOpen = ref(false)
const existingSessionId = ref(null)

const events = computed(() => rawEvents.value.map(e => ({ id: e.id, name: e.name })))
const locations = computed(() => rawLocations.value.map(l => ({ id: l.id, name: l.name }))) 

const selectedEventName = computed(() => {
  const ev = rawEvents.value.find(e => e.id === selectedEventId.value)
  return ev ? ev.name : ''
})

const scopeOptions = computed(() => [
  { id: 'ALL', name: t('views.launcher.scope_all') },
  { id: 'SUBJECT', name: t('views.launcher.scope_subject') },
  { id: 'ADMIN', name: t('views.launcher.scope_admin') }
])

// --- 1. FILTERUNG SUBJECT NACH EVENT ---
// Baut das Dropdown für Subjects auf, basierend auf den Zuweisungen des Events
const availableSubjectsForEvent = computed(() => {
  if (!selectedEventId.value) return []
  
  // Extrahiere alle einzigartigen Subjekt-IDs, die diesem Event zugewiesen sind
  const assignedSubjectIds = [...new Set(eventAssignments.value.map(a => a.subject))]
  
  return rawSubjects.value
    .filter(s => assignedSubjectIds.includes(s.id))
    .map(s => ({
      id: s.id,
      name: `${s.identifier} ${s.first_name ? '(' + s.first_name + ' ' + s.last_name + ')' : ''}`
    }))
})

// --- 2. FILTERUNG EVENTGROUP NACH SUBJECT ---
// Extrahiert die Gruppen des aktuell gewählten Subjekts, FILTERT NULL WIEDER HERAUS!
const subjectGroupAssignments = computed(() => {
  if (!selectedSubjectId.value) return []
  
  // Nimm alle Zuweisungen des Subjekts im aktuellen Event, ABER nur jene, die auch eine Gruppe haben
  return eventAssignments.value
    .filter(a => a.subject === selectedSubjectId.value && a.group !== null)
})

// Baut das Dropdown, falls es > 1 echte Zuweisungen gibt
const availableEventGroupsForDropdown = computed(() => {
  return subjectGroupAssignments.value.map(a => {
    const g = rawEventGroups.value.find(rg => rg.id === a.group)
    return g ? { id: g.id, name: g.name } : { id: a.group, name: `Group ${a.group}` }
  })
})

const getGroupName = (id) => {
  const g = rawEventGroups.value.find(rg => rg.id === id)
  return g ? g.name : id
}

// --- 3. FILTERUNG PHASEN NACH GRUPPE ---
const availablePageGroups = computed(() => {
  if (!selectedEventGroupId.value) return []
  const group = rawEventGroups.value.find(g => g.id === selectedEventGroupId.value)
  if (!group || !group.page_groups) return []
  
  return group.page_groups.map(id => {
    const pg = rawPageGroups.value.find(p => p.id === id)
    return pg ? { id: pg.id, name: pg.name } : { id, name: `ID: ${id}` }
  })
})

const isLaunchable = computed(() => {
  return selectedEventId.value && selectedSubjectId.value && selectedEventGroupId.value && selectedPageGroupId.value
})

// --- WATCHERS ---

// Wenn ein Event gewählt wird, lade dessen Kontext!
watch(selectedEventId, async (newVal) => { 
  selectedSubjectId.value = null
  selectedEventGroupId.value = null
  selectedPageGroupId.value = null
  eventAssignments.value = []
  
  if (!newVal) return

  isLoadingEventContext.value = true
  try {
    const res = await api.get(`event-management/subject-assignments/?event=${newVal}`)
    eventAssignments.value = res.data
  } catch (e) {
    console.error(e)
  } finally {
    isLoadingEventContext.value = false
  }
})

// Wenn ein Subjekt gewählt wird, prüfe die Gruppen
watch(selectedSubjectId, (newVal) => {
  selectedEventGroupId.value = null
  selectedPageGroupId.value = null
  
  if (!newVal) return
  
  // Auto-Select, falls genau EINE echte Gruppe existiert
  if (subjectGroupAssignments.value.length === 1) {
    selectedEventGroupId.value = subjectGroupAssignments.value[0].group
  }
})

watch(selectedEventGroupId, () => {
  selectedPageGroupId.value = null
})

// --- METHODS ---

const loadData = async () => {
  try {
    const [eventsRes, subjectsRes, pgRes, locRes, groupsRes] = await Promise.all([
      api.get('events/'), api.get('subjects/'), api.get('page-groups/'), api.get('locations/'), api.get('event-management/groups/')
    ])
    rawEvents.value = eventsRes.data
    rawSubjects.value = subjectsRes.data
    rawPageGroups.value = pgRes.data
    rawLocations.value = locRes.data
    rawEventGroups.value = groupsRes.data
  } catch (error) {}
}

const onSubjectCreated = async (newSubject) => {
  // Das Modal hat Subjekt + Assignment im Backend gespeichert.
  // Wir updaten unsere lokale Liste, damit das neue Subjekt sofort im Dropdown auftaucht!
  rawSubjects.value.push(newSubject)
  
  // Wir laden die Assignments für das Event neu, damit die neue Verknüpfung greift
  isLoadingEventContext.value = true
  try {
    const res = await api.get(`event-management/subject-assignments/?event=${selectedEventId.value}`)
    eventAssignments.value = res.data
    
    // Auto-Select des neuen Subjekts
    selectedSubjectId.value = newSubject.id
  } catch (e) {
    console.error(e)
  } finally {
    isLoadingEventContext.value = false
  }
}

const startSession = async () => {
  try {
    const payload = {
      event: selectedEventId.value,
      page_group: selectedPageGroupId.value,
      subject: selectedSubjectId.value,
      location: selectedLocationId.value,
      start_datetime: new Date().toISOString()
    }
    const response = await api.post('sessions/', payload)
    
    if (response.status === 200) {
      existingSessionId.value = response.data.id
      isResumeModalOpen.value = true
    } else {
      router.push({ path: '/sessions/runner', query: { sessionId: response.data.id, scope: selectedScope.value } })
    }
  } catch (error) {}
}

const resumeSession = () => {
  isResumeModalOpen.value = false
  router.push({ path: '/sessions/runner', query: { sessionId: existingSessionId.value, scope: selectedScope.value } })
}

const resetSession = async () => {
  try {
    await api.post(`sessions/${existingSessionId.value}/reset/`)
    isResumeModalOpen.value = false
    router.push({ path: '/sessions/runner', query: { sessionId: existingSessionId.value, scope: selectedScope.value } })
  } catch (error) {}
}

onMounted(loadData)
</script>
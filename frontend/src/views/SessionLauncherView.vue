<template>
  <div class="session-launcher">
    <div class="page-header">
      <h1>{{ $t('nav.session_launcher') }}</h1>
    </div>

    <div class="launcher-cards">
      <div class="card">
        <h2>{{ $t('views.launcher.select_event') }}</h2>
        <BaseSearchSelect v-model="selectedEventId" :options="events" :placeholder="$t('common.search')" />
      </div>

      <div class="card" :class="{ 'disabled-card': !selectedEventId }">
        <h2>{{ $t('views.launcher.select_phase') }}</h2>
        <BaseSearchSelect v-model="selectedPageGroupId" :options="availablePageGroups" :placeholder="$t('common.search')" :disabled="!selectedEventId" />
      </div>

      <div class="card" :class="{ 'disabled-card': !selectedPageGroupId }">
        <h2>{{ $t('views.launcher.select_subject') }}</h2>
        <div style="display: flex; gap: 10px; align-items: flex-start;">
          <div style="flex: 1;">
            <BaseSearchSelect v-model="selectedSubjectId" :options="subjects" :placeholder="$t('common.search')" :disabled="!selectedPageGroupId" />
          </div>
          <button class="btn-secondary" @click="isSubjectModalOpen = true" :disabled="!selectedPageGroupId">{{ $t('actions.add_new') }}</button>
        </div>
      </div>

      <div class="card" :class="{ 'disabled-card': !selectedEventId }">
        <h2>{{ $t('views.launcher.select_location') }} (Optional)</h2>
        <BaseSearchSelect v-model="selectedLocationId" :options="locations" :placeholder="$t('common.search')" :disabled="!selectedEventId" />
      </div>
    </div>

    <div class="action-footer">
      <button class="btn-play-sync" :disabled="!selectedEventId || !selectedPageGroupId || !selectedSubjectId" @click="startSession" style="font-size: 1.2rem; padding: 15px 30px;">
        <span class="play-icon">▶</span> {{ $t('views.launcher.start_session') }}
      </button>
    </div>

    <BaseModal :isOpen="isSubjectModalOpen" :title="$t('views.launcher.create_subject')" @close="closeSubjectModal">
      <form @submit.prevent="saveSubject">
        <div class="form-group">
          <label>{{ $t('master_data.identifier') }} *</label>
          <input type="text" v-model="subjectForm.identifier" class="form-control" required />
        </div>
        <div class="form-row" style="display: flex; gap: 1rem; margin-bottom: 1rem;">
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('master_data.firstname') }}</label>
            <input type="text" v-model="subjectForm.first_name" class="form-control" />
          </div>
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('master_data.lastname') }}</label>
            <input type="text" v-model="subjectForm.last_name" class="form-control" />
          </div>
        </div>
        <div class="form-row" style="display: flex; gap: 1rem; margin-bottom: 1rem;">
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('master_data.birthday') }}</label>
            <input type="date" v-model="subjectForm.date_of_birth" class="form-control" />
          </div>
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('master_data.gender') }}</label>
            <select v-model="subjectForm.gender" class="form-control">
              <option value="M">{{ $t('master_data.gender_male') }}</option>
              <option value="F">{{ $t('master_data.gender_female') }}</option>
              <option value="O">{{ $t('master_data.gender_other') }}</option>
              <option value="N">{{ $t('master_data.none') }}</option>
            </select>
          </div>
        </div>
        <div class="modal-actions">
          <button type="button" class="btn-secondary" @click="closeSubjectModal">{{ $t('actions.cancel') }}</button>
          <button type="submit" class="btn-primary">{{ $t('actions.save') }}</button>
        </div>
      </form>
    </BaseModal>

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

    <WarningModal :isOpen="showWarningModal" :message="warningMessage" @close="showWarningModal = false" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'

import BaseSearchSelect from '@/components/BaseSearchSelect.vue'
import BaseModal from '@/components/BaseModal.vue'
import WarningModal from '@/components/WarningModal.vue'

const { t } = useI18n()
const router = useRouter()

const rawEvents = ref([])
const rawSubjects = ref([])
const rawPageGroups = ref([])
const rawLocations = ref([])

const selectedEventId = ref(null)
const selectedPageGroupId = ref(null)
const selectedSubjectId = ref(null)
const selectedLocationId = ref(null)

const isSubjectModalOpen = ref(false)
const isResumeModalOpen = ref(false)
const existingSessionId = ref(null)

const showWarningModal = ref(false)
const warningMessage = ref('')

const subjectForm = ref({ identifier: '', first_name: '', last_name: '', date_of_birth: '', gender: 'N' })

const events = computed(() => rawEvents.value.map(e => ({ id: e.id, name: e.name })))
const locations = computed(() => rawLocations.value.map(l => ({ id: l.id, name: l.name }))) // format locations for dropdown

const subjects = computed(() => rawSubjects.value.map(s => ({ 
  id: s.id, 
  name: `${s.identifier} ${s.first_name ? '(' + s.first_name + ' ' + s.last_name + ')' : ''}` 
})))

const availablePageGroups = computed(() => {
  if (!selectedEventId.value) return []
  const ev = rawEvents.value.find(e => e.id === selectedEventId.value)
  if (!ev || !ev.page_groups) return []
  return ev.page_groups.map(id => {
    const pg = rawPageGroups.value.find(p => p.id === id)
    return pg ? { id: pg.id, name: pg.name } : { id, name: `ID: ${id}` }
  })
})

watch(selectedEventId, () => { selectedPageGroupId.value = null })

const loadData = async () => {
  try {
    const [eventsRes, subjectsRes, pgRes, locRes] = await Promise.all([
      api.get('events/'), api.get('subjects/'), api.get('page-groups/'), api.get('locations/')
    ])
    rawEvents.value = eventsRes.data
    rawSubjects.value = subjectsRes.data
    rawPageGroups.value = pgRes.data
    rawLocations.value = locRes.data
  } catch (error) { showError(t('errors.load_failed')) }
}

const closeSubjectModal = () => {
  isSubjectModalOpen.value = false
  subjectForm.value = { identifier: '', first_name: '', last_name: '', date_of_birth: '', gender: 'N' }
}

const saveSubject = async () => {
  try {
    const payload = { ...subjectForm.value }
    if (!payload.date_of_birth) payload.date_of_birth = null
    const response = await api.post('subjects/', payload)
    rawSubjects.value.push(response.data)
    selectedSubjectId.value = response.data.id
    closeSubjectModal()
  } catch (error) { showError(t('errors.save_failed')) }
}

const startSession = async () => {
  try {
    const payload = {
      event: selectedEventId.value,
      page_group: selectedPageGroupId.value,
      subject: selectedSubjectId.value,
      location: selectedLocationId.value, // added location to payload
      start_datetime: new Date().toISOString()
    }
    const response = await api.post('sessions/', payload)
    
    // status 200 means get_or_create returned an existing session
    if (response.status === 200) {
      existingSessionId.value = response.data.id
      isResumeModalOpen.value = true
    } else {
      router.push(`/session/run/${response.data.id}`)
    }
  } catch (error) { showError(t('errors.save_failed')) }
}

const resumeSession = () => {
  isResumeModalOpen.value = false
  router.push(`/session/run/${existingSessionId.value}`)
}

const resetSession = async () => {
  try {
    await api.post(`sessions/${existingSessionId.value}/reset/`)
    isResumeModalOpen.value = false
    router.push(`/session/run/${existingSessionId.value}`)
  } catch (error) { showError(t('errors.unknown')) }
}

const showError = (msg) => { warningMessage.value = msg; showWarningModal.value = true }
onMounted(loadData)
</script>

<style scoped>
.launcher-cards { display: flex; flex-direction: column; gap: 20px; max-width: 800px; margin: 0 auto; }
.card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); border: 1px solid #e0e0e0; transition: opacity 0.3s; }
.card h2 { margin-top: 0; font-size: 1.2rem; color: #2c3e50; margin-bottom: 15px; border-bottom: 2px solid #f4f7f6; padding-bottom: 10px; }
.disabled-card { opacity: 0.5; pointer-events: none; }
.action-footer { margin-top: 40px; display: flex; justify-content: center; }
.btn-play-sync:disabled { opacity: 0.5; cursor: not-allowed; transform: none; box-shadow: none; }
</style>
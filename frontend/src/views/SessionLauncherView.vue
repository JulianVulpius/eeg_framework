<template>
  <div class="session-launcher">
    <div class="page-header">
      <h1>{{ $t('nav.session_launcher') }}</h1>
    </div>

    <div class="launcher-cards">
      <div class="card">
        <h2>{{ $t('views.launcher.select_event') }}</h2>
        <BaseSearchSelect
          v-model="selectedEventId"
          :options="events"
          :placeholder="$t('common.search')"
        />
      </div>

      <div class="card" :class="{ 'disabled-card': !selectedEventId }">
        <h2>{{ $t('views.launcher.select_subject') }}</h2>
        <div style="display: flex; gap: 10px; align-items: flex-start;">
          <div style="flex: 1;">
            <BaseSearchSelect
              v-model="selectedSubjectId"
              :options="subjects"
              :placeholder="$t('common.search')"
              :disabled="!selectedEventId"
            />
          </div>
          <button 
            class="btn-secondary" 
            @click="isSubjectModalOpen = true"
            :disabled="!selectedEventId"
          >
            {{ $t('actions.add_new') }}
          </button>
        </div>
      </div>
    </div>

    <div class="action-footer">
      <button 
        class="btn-play-sync" 
        :disabled="!selectedEventId || !selectedSubjectId"
        @click="startSession"
        style="font-size: 1.2rem; padding: 15px 30px;"
      >
        <span class="play-icon">▶</span> {{ $t('views.launcher.start_session') }}
      </button>
    </div>

    <BaseModal 
      :isOpen="isSubjectModalOpen" 
      :title="$t('views.launcher.create_subject')"
      @close="closeSubjectModal"
    >
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

    <WarningModal 
      :isOpen="showWarningModal" 
      :message="warningMessage" 
      @close="showWarningModal = false" 
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
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

const selectedEventId = ref(null)
const selectedSubjectId = ref(null)

const isSubjectModalOpen = ref(false)
const showWarningModal = ref(false)
const warningMessage = ref('')

const subjectForm = ref({
  identifier: '',
  first_name: '',
  last_name: '',
  date_of_birth: '',
  gender: 'N'
})

const events = computed(() => {
  return rawEvents.value.map(e => ({ id: e.id, name: e.name }))
})

const subjects = computed(() => {
  return rawSubjects.value.map(s => ({ 
    id: s.id, 
    name: `${s.identifier} ${s.first_name ? '(' + s.first_name + ' ' + s.last_name + ')' : ''}` 
  }))
})

const loadData = async () => {
  try {
    const [eventsRes, subjectsRes] = await Promise.all([
      api.get('events/'),
      api.get('subjects/')
    ])
    rawEvents.value = eventsRes.data
    rawSubjects.value = subjectsRes.data
  } catch (error) {
    showError(t('errors.load_failed'))
  }
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
  } catch (error) {
    showError(t('errors.save_failed'))
  }
}

const startSession = async () => {
  try {
    const payload = {
      event: selectedEventId.value,
      subject: selectedSubjectId.value,
      start_datetime: new Date().toISOString()
    }
    const response = await api.post('sessions/', payload)
    router.push(`/session/run/${response.data.id}`)
  } catch (error) {
    showError(t('errors.save_failed'))
  }
}

const showError = (msg) => {
  warningMessage.value = msg
  showWarningModal.value = true
}

onMounted(loadData)
</script>

<style scoped>
.launcher-cards {
  display: flex;
  flex-direction: column;
  gap: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.card {
  background: white;
  padding: 25px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  border: 1px solid #e0e0e0;
  transition: opacity 0.3s;
}

.card h2 {
  margin-top: 0;
  font-size: 1.2rem;
  color: #2c3e50;
  margin-bottom: 15px;
  border-bottom: 2px solid #f4f7f6;
  padding-bottom: 10px;
}

.disabled-card {
  opacity: 0.5;
  pointer-events: none;
}

.action-footer {
  margin-top: 40px;
  display: flex;
  justify-content: center;
}

.btn-play-sync:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}
</style>
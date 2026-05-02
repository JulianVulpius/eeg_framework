<template>
  <BaseModal :isOpen="isOpen" :title="$t('views.launcher.create_subject')" @close="$emit('close')">
    <form @submit.prevent="saveSubjectAndAssign">
      
      <!-- Hinweis auf Event-Zuweisung -->
      <div class="mb-3 p-2" style="background: #e8f4f8; border-left: 3px solid #3498db; font-size: 0.9rem; color: #2980b9;">
        Dieses Subjekt wird automatisch dem Event <strong>{{ eventName }}</strong> zugewiesen.
      </div>

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
            <option :value="null">{{ $t('master_data.none') }}</option>
            <option value="M">{{ $t('master_data.gender_male') }}</option>
            <option value="F">{{ $t('master_data.gender_female') }}</option>
            <option value="O">{{ $t('master_data.gender_other') }}</option>
          </select>
        </div>
      </div>

      <!-- Optionale Gruppenzuweisung direkt im Modal -->
      <div class="form-group" style="margin-top: 15px; border-top: 1px dashed #ccc; padding-top: 15px;">
        <label>Experimentelle Gruppe (Optional)</label>
        <BaseSearchSelect 
          v-model="selectedGroupId" 
          :options="eventGroups" 
          placeholder="Subjekt einer Gruppe zuweisen..." 
          :nullLabel="$t('master_data.none')"
        />
        <small class="text-muted" style="display:block; margin-top:4px;">Wenn keine Gruppe gewählt wird, kann später keine Session gestartet werden.</small>
      </div>

      <div class="modal-actions mt-4" style="display: flex; justify-content: flex-end; gap: 10px;">
        <button type="button" class="btn-secondary" @click="$emit('close')" :disabled="isSaving">{{ $t('actions.cancel') }}</button>
        <button type="submit" class="btn-primary" :disabled="isSaving">
          {{ isSaving ? $t('common.saving') : $t('actions.save') }}
        </button>
      </div>
    </form>
  </BaseModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import api from '@/services/api'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'

const props = defineProps({
  isOpen: Boolean,
  eventId: [Number, String],
  eventName: String,
  eventGroups: Array // Array von Objekten: {id, name}
})

const emit = defineEmits(['close', 'saved'])

const isSaving = ref(false)
const selectedGroupId = ref(null)
const subjectForm = ref({ identifier: '', first_name: '', last_name: '', date_of_birth: '', gender: null })

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    // Formular zurücksetzen beim Öffnen
    subjectForm.value = { identifier: '', first_name: '', last_name: '', date_of_birth: '', gender: null }
    selectedGroupId.value = null
  }
})

const saveSubjectAndAssign = async () => {
  if (!props.eventId) return
  isSaving.value = true

  try {
    // 1. Subjekt erstellen
    const payload = { ...subjectForm.value }
    if (!payload.date_of_birth) payload.date_of_birth = null
    const subRes = await api.post('subjects/', payload)
    const newSubject = subRes.data

    // 2. Subjekt dem Event zuweisen (mit oder ohne EventGroup)
    await api.post('event-management/subject-assignments/', {
      event: props.eventId,
      subject: newSubject.id,
      group: selectedGroupId.value || null
    })

    // 3. Dem Parent Bescheid geben
    emit('saved', newSubject)
    emit('close')
  } catch (error) {
    console.error("Error creating subject or assignment:", error)
  } finally {
    isSaving.value = false
  }
}
</script>
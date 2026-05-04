<template>
  <BaseModal :isOpen="isOpen" :title="$t('views.launcher.create_subject')" @close="$emit('close')">
    <form @submit.prevent="saveSubjectAndAssign">
      
      <div class="mb-3 p-2" style="background: #e8f4f8; border-left: 3px solid #3498db; font-size: 0.9rem; color: #2980b9;" v-html="$t('views.launcher.subject_auto_assign_event', { eventName })">
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

      <div class="form-group" style="margin-top: 15px; border-top: 1px dashed #ccc; padding-top: 15px;">
        <label>{{ $t('views.launcher.experimental_group_optional') }}</label>
        <BaseSearchSelect 
          v-model="selectedGroupId" 
          :options="eventGroups" 
          :placeholder="$t('views.launcher.assign_subject_to_group')" 
          :nullLabel="$t('master_data.none')"
        />
        <small class="text-muted" style="display:block; margin-top:4px;">{{ $t('views.launcher.no_group_warning_subtext') }}</small>
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
  eventGroups: Array
})

const emit = defineEmits(['close', 'saved'])

const isSaving = ref(false)
const selectedGroupId = ref(null)
const subjectForm = ref({ identifier: '', first_name: '', last_name: '', date_of_birth: '', gender: null })

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    subjectForm.value = { identifier: '', first_name: '', last_name: '', date_of_birth: '', gender: null }
    selectedGroupId.value = null
  }
})

const saveSubjectAndAssign = async () => {
  if (!props.eventId) return
  isSaving.value = true

  try {
    const payload = { ...subjectForm.value }
    if (!payload.date_of_birth) payload.date_of_birth = null
    const subRes = await api.post('subjects/', payload)
    const newSubject = subRes.data

    await api.post('event-management/subject-assignments/', {
      event: props.eventId,
      subject: newSubject.id,
      group: selectedGroupId.value || null
    })

    emit('saved', newSubject)
    emit('close')
  } catch (error) {
    console.error(error)
  } finally {
    isSaving.value = false
  }
}
</script>
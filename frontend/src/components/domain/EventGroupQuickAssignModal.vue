<template>
  <BaseModal :isOpen="isOpen" :title="$t('views.events.quick_assign')" @close="closeModal" width="800px">
    <div class="quick-assign-content">
      <div class="form-group" style="max-width: 400px; margin-bottom: 20px;">
        <label>{{ $t('views.events.select_target_group') }}</label>
        <select v-model="selectedGroupId" class="form-control">
          <option :value="null" disabled>{{ $t('common.select') }}</option>
          <option v-for="g in eventGroups" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
      </div>

      <div v-if="selectedGroupId">
        <BaseTransferList
          v-model="assignedSubjects"
          :options="mappedEventSubjects"
          :leftTitle="$t('views.events.available_subjects')"
          :rightTitle="$t('views.events.assigned_subjects')"
          :enableOrdering="false"
        />
      </div>
      <div v-else class="placeholder-text">
        {{ $t('views.events.please_select_group_first') }}
      </div>
    </div>

    <div class="modal-actions">
      <button @click="closeModal" class="btn-secondary">{{ $t('actions.cancel') }}</button>
      <button @click="saveAssignments" class="btn-primary" :disabled="!selectedGroupId">{{ $t('actions.save') }}</button>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseTransferList from '@/components/ui/BaseTransferList.vue'
import api from '@/services/api'
import { useCrud } from '@/composables/useCrud'
import { useI18n } from 'vue-i18n'

const props = defineProps({
  isOpen: Boolean,
  eventId: [String, Number],
  eventGroups: Array,
  subjects: Array,
  assignments: Array
})
const emit = defineEmits(['close', 'saved'])

const crudHelper = useCrud()
const { t } = useI18n()

const selectedGroupId = ref(null)
const assignedSubjects = ref([])

const mappedEventSubjects = computed(() => {
  const uniqueSubjectIds = [...new Set(props.assignments.map(a => a.subject))]
  return uniqueSubjectIds.map(id => {
    const s = props.subjects.find(sub => sub.id === id)
    if (!s) return { id, name: 'Unknown' }
    return {
      id: s.id,
      name: `${s.identifier || s.subject_id} ${s.firstname ? '('+s.firstname+' '+s.lastname+')' : ''}`.trim()
    }
  })
})

watch(selectedGroupId, (newVal) => {
  if (newVal) {
    assignedSubjects.value = props.assignments.filter(a => a.group === newVal).map(a => a.subject)
  } else {
    assignedSubjects.value = []
  }
})

const closeModal = () => {
  selectedGroupId.value = null
  assignedSubjects.value = []
  emit('close')
}

const saveAssignments = async () => {
  try {
    const oldSubjectIds = props.assignments.filter(a => a.group === selectedGroupId.value).map(a => a.subject)
    const newSubjectIds = assignedSubjects.value

    const toRemove = props.assignments.filter(a => a.group === selectedGroupId.value && !newSubjectIds.includes(a.subject))
    const toAdd = newSubjectIds.filter(id => !oldSubjectIds.includes(id))

    const promises = []

    for (const a of toRemove) {
      const otherAssignments = props.assignments.filter(other => other.subject === a.subject && other.id !== a.id)
      if (otherAssignments.length === 0) {
        promises.push(api.put(`event-management/subject-assignments/${a.id}/`, { event: props.eventId, subject: a.subject, group: null }))
      } else {
        promises.push(api.delete(`event-management/subject-assignments/${a.id}/`))
      }
    }

    for (const subId of toAdd) {
      const nullAssignment = props.assignments.find(a => a.subject === subId && a.group === null)
      if (nullAssignment) {
        promises.push(api.put(`event-management/subject-assignments/${nullAssignment.id}/`, { event: props.eventId, subject: subId, group: selectedGroupId.value }))
      } else {
        promises.push(api.post(`event-management/subject-assignments/`, { event: props.eventId, subject: subId, group: selectedGroupId.value }))
      }
    }

    await Promise.all(promises)
    crudHelper.notifySuccess('updated', t)
    emit('saved')
    closeModal()
  } catch (error) {
    crudHelper.parseApiError(error, t, 'errors.save_failed')
  }
}
</script>

<style scoped>
.quick-assign-content { min-height: 350px; }
.placeholder-text { text-align: center; color: #7f8c8d; padding: 40px; background: #f8f9fa; border-radius: 8px; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 25px; padding-top: 15px; border-top: 1px solid #eee; }
</style>
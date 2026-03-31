<template>
  <BaseModal :isOpen="isOpen" :title="$t('views.events.randomize_assignment')" @close="closeModal" width="800px">
    
    <div style="display: flex; gap: 20px; align-items: flex-start; margin-bottom: 20px;">
      <div style="flex: 1;">
        <label>{{ $t('views.events.select_groups_to_randomize') }}</label>
        <SearchableCheckboxGroup v-model="selectedGroups" :options="eventGroups" />
        <div v-if="selectedGroups.length < 2" style="font-size: 0.8rem; color: #e74c3c; margin-top: 5px;">
          {{ $t('views.events.need_at_least_two_groups') }}
        </div>
      </div>
    </div>

    <div>
      <label>{{ $t('views.events.subjects_to_randomize') }}</label>
      <BaseTransferList
        v-model="selectedSubjects"
        :options="mappedEventSubjects"
        :leftTitle="$t('views.events.available_subjects')"
        :rightTitle="$t('views.events.selected_subjects')"
        :enableOrdering="false"
      />
    </div>

    <div class="modal-actions">
      <button @click="closeModal" class="btn-secondary">{{ $t('actions.cancel') }}</button>
      <button @click="executeRandomizer" class="btn-primary" style="background-color: #9b59b6; border-color: #8e44ad;" :disabled="selectedGroups.length < 2 || selectedSubjects.length === 0">
        🎲 {{ $t('views.events.randomize_btn') }}
      </button>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, computed } from 'vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseTransferList from '@/components/ui/BaseTransferList.vue'
import SearchableCheckboxGroup from '@/components/ui/SearchableCheckboxGroup.vue'
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

const selectedGroups = ref([])
const selectedSubjects = ref([])

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

const closeModal = () => {
  selectedGroups.value = []
  selectedSubjects.value = []
  emit('close')
}

const executeRandomizer = async () => {
  try {
    const assignmentsToDelete = props.assignments.filter(a => 
      selectedSubjects.value.includes(a.subject) && selectedGroups.value.includes(a.group)
    )
    
    if (assignmentsToDelete.length > 0) {
      const deletePromises = assignmentsToDelete.map(a => 
        api.delete(`event-management/subject-assignments/${a.id}/`)
      )
      await Promise.all(deletePromises)
    }
    
    const shuffledSubjects = [...selectedSubjects.value].sort(() => Math.random() - 0.5)
    
    const postPromises = []
    for (let i = 0; i < shuffledSubjects.length; i++) {
      const subjectId = shuffledSubjects[i]
      const groupId = selectedGroups.value[i % selectedGroups.value.length]
      
      postPromises.push(api.post(`event-management/subject-assignments/`, {
        event: props.eventId,
        subject: subjectId,
        group: groupId
      }))
    }

    await Promise.all(postPromises)
    crudHelper.notifySuccess('updated', t)
    emit('saved')
    closeModal()
  } catch (error) {
    crudHelper.parseApiError(error, t, 'errors.save_failed')
  }
}
</script>

<style scoped>
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 25px; padding-top: 15px; border-top: 1px solid #eee; }
</style>
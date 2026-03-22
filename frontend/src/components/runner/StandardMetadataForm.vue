<template>
  <div class="metadata-form-card">
    <h2 v-if="groupData">{{ groupData.name }}</h2>
    <p v-if="groupData" class="group-desc">{{ groupData.description }}</p>

    <div v-if="isLoading" class="loading">{{ $t('common.loading') }}</div>

    <form v-else @submit.prevent="submitForm">
      <div v-for="def in activeDefinitions" :key="def.id" class="form-group">
        <label>{{ def.name }}</label>
        
        <input v-if="def.expected_data_type === 'STRING'" type="text" v-model="formValues[def.id]" class="form-control" required />
        <input v-else-if="def.expected_data_type === 'INTEGER'" type="number" step="1" v-model="formValues[def.id]" class="form-control" required />
        <input v-else-if="def.expected_data_type === 'FLOAT'" type="number" step="any" v-model="formValues[def.id]" class="form-control" required />
        <label v-else-if="def.expected_data_type === 'BOOLEAN'" class="checkbox-label">
          <input type="checkbox" v-model="formValues[def.id]" /> {{ $t('common.yes') }}
        </label>
        <textarea v-else-if="def.expected_data_type === 'JSON'" v-model="formValues[def.id]" rows="3" class="form-control"></textarea>
      </div>

      <div class="action-footer">
        <button type="button" class="btn-secondary" @click="$emit('go-back')" style="margin-right: 15px;">{{ $t('actions.back') }}</button>
        <button type="submit" class="btn-primary" :disabled="isSaving">
          {{ isSaving ? $t('common.saving') : $t('actions.continue') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/api'

const props = defineProps({
  parameters: { type: Object, required: true },
  sessionId: { type: [String, Number], required: true }
})
const emit = defineEmits(['completed'])

const isLoading = ref(true)
const isSaving = ref(false)
const groupData = ref(null)
const activeDefinitions = ref([])
const formValues = ref({})

const loadFormDefinition = async () => {
  try {
    const groupId = props.parameters.metadata_group_id
    if (!groupId) return

    const [groupRes, defRes] = await Promise.all([
      api.get(`metadata/groups/${groupId}/`),
      api.get(`metadata/definitions/`)
    ])
    
    groupData.value = groupRes.data
    const assignedIds = groupRes.data.assigned_definitions || []
    
    activeDefinitions.value = assignedIds.map(id => defRes.data.find(d => d.id === id)).filter(Boolean)
    
    activeDefinitions.value.forEach(def => {
      formValues.value[def.id] = def.expected_data_type === 'BOOLEAN' ? false : ''
    })
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

const submitForm = async () => {
  isSaving.value = true
  try {
    const valuesArray = Object.keys(formValues.value).map(defId => ({
      definition_id: parseInt(defId),
      value: formValues.value[defId]
    }))

    await api.post(`sessions/${props.sessionId}/save_metadata/`, {
      group_id: props.parameters.metadata_group_id,
      values: valuesArray
    })
    emit('completed')
  } catch (error) {
    console.error(error)
  } finally {
    isSaving.value = false
  }
}

onMounted(loadFormDefinition)
</script>

<style scoped>
.metadata-form-card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.group-desc { color: #7f8c8d; margin-bottom: 20px; }
.checkbox-label { display: flex; align-items: center; gap: 10px; font-weight: normal; cursor: pointer; }
.action-footer { display: flex; justify-content: flex-end; margin-top: 20px; }
.loading { text-align: center; color: #7f8c8d; padding: 20px; }
</style>
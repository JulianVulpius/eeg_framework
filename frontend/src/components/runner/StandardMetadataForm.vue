<template>
  <div class="metadata-form-card">
    <h2 v-if="groupData && showTitle">{{ groupData.name }}</h2>
    <p v-if="groupData" class="group-desc">{{ groupData.description }}</p>

    <div v-if="isLoading" class="loading">{{ $t('common.loading') }}</div>

    <form v-else @submit.prevent>
      <div v-for="def in activeDefinitions" :key="def.id" class="form-group" style="margin-bottom: 15px;">
        <label>{{ def.name }} *</label>
        
        <input 
          v-if="def.expected_data_type === 'STRING'" 
          type="text" 
          v-model="formValues[def.id]" 
          class="form-control" 
          :class="{ 'input-invalid': fieldErrors[def.id] }" 
          @input="clearError(def.id)"
        />
        <input 
          v-else-if="def.expected_data_type === 'INTEGER'" 
          type="number" step="1" 
          v-model="formValues[def.id]" 
          class="form-control" 
          :class="{ 'input-invalid': fieldErrors[def.id] }" 
          @input="clearError(def.id)"
        />
        <input 
          v-else-if="def.expected_data_type === 'FLOAT'" 
          type="number" step="any" 
          v-model="formValues[def.id]" 
          class="form-control" 
          :class="{ 'input-invalid': fieldErrors[def.id] }" 
          @input="clearError(def.id)"
        />
        <label v-else-if="def.expected_data_type === 'BOOLEAN'" class="checkbox-label">
          <input type="checkbox" v-model="formValues[def.id]" /> {{ $t('common.yes') }}
        </label>
        <textarea 
          v-else-if="def.expected_data_type === 'JSON'" 
          v-model="formValues[def.id]" 
          rows="3" 
          class="form-control" 
          :class="{ 'input-invalid': fieldErrors[def.id] }"
          @input="clearError(def.id)">
        </textarea>

        <BaseInputError :message="fieldErrors[def.id]" />
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import BaseInputError from '@/components/ui/BaseInputError.vue'
import { useGlobalModal } from '@/composables/useGlobalModal'

const props = defineProps({
  parameters: { type: Object, required: true },
  sessionId: { type: [String, Number], required: true }
})

const { t } = useI18n()
const { showWarning } = useGlobalModal()

const isLoading = ref(true)
const groupData = ref(null)
const activeDefinitions = ref([])

const formValues = ref({})
const fieldErrors = ref({})

const showTitle = computed(() => {
  if (props.parameters && props.parameters.show_title !== undefined) {
    return props.parameters.show_title
  }
  return true 
})

const clearError = (id) => {
  if (fieldErrors.value[id]) fieldErrors.value[id] = ''
}

const loadFormDefinition = async () => {
  try {
    const groupId = props.parameters.metadata_group_id
    if (!groupId) return

    const [groupRes, defRes, savedRes] = await Promise.all([
      api.get(`metadata/groups/${groupId}/`),
      api.get(`metadata/definitions/`),
      api.get(`sessions/${props.sessionId}/saved_metadata/`)
    ])
    
    groupData.value = groupRes.data
    const assignedIds = groupRes.data.assigned_definitions || []
    activeDefinitions.value = assignedIds.map(id => defRes.data.find(d => d.id === id)).filter(Boolean)
    const savedData = savedRes.data || {}

    activeDefinitions.value.forEach(def => {
      fieldErrors.value[def.id] = ''
      if (savedData[def.id] !== undefined) {
        let val = savedData[def.id]
        if (def.expected_data_type === 'BOOLEAN') formValues.value[def.id] = (val === 'true' || val === 'True')
        else if (def.expected_data_type === 'INTEGER') formValues.value[def.id] = parseInt(val, 10)
        else if (def.expected_data_type === 'FLOAT') formValues.value[def.id] = parseFloat(val)
        else formValues.value[def.id] = val
      } else {
        formValues.value[def.id] = def.expected_data_type === 'BOOLEAN' ? false : ''
      }
    })
  } catch (error) {
    showWarning(t('common.error_loading') || 'Error loading metadata', t('common.error'))
  } finally {
    isLoading.value = false
  }
}

const submit = async () => {
  let hasErrors = false
  
  for (const def of activeDefinitions.value) {
    if (def.expected_data_type !== 'BOOLEAN') {
      const val = formValues.value[def.id]
      if (val === '' || val === null || val === undefined) {
        fieldErrors.value[def.id] = t('errors.required_field') || 'Pflichtfeld'
        hasErrors = true
      }
    }
  }

  if (hasErrors) {
    throw new Error("Validation failed")
  }

  try {
    const valuesArray = Object.keys(formValues.value).map(defId => {
      let val = formValues.value[defId]
      if (typeof val === 'boolean') val = val ? 'true' : 'false'
      return { definition_id: parseInt(defId), value: val }
    })

    await api.post(`sessions/${props.sessionId}/save_metadata/`, {
      group_id: props.parameters.metadata_group_id,
      values: valuesArray
    })
    
  } catch (error) {
    showWarning(t('common.error_saving') || 'Save failed', t('common.error'))
    throw error 
  }
}

defineExpose({ submit })

onMounted(loadFormDefinition)
</script>

<style scoped>
.metadata-form-card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.group-desc { color: #7f8c8d; margin-bottom: 20px; }
.checkbox-label { display: flex; align-items: center; gap: 10px; font-weight: normal; cursor: pointer; }
.loading { text-align: center; color: #7f8c8d; padding: 20px; }
</style>
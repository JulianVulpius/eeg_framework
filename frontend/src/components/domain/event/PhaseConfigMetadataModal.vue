<template>
  <BaseModal
    :isOpen="isOpen"
    :title="$t('views.events.edit_settings') + (configName ? ' - ' + configName : '')"
    @close="$emit('close')"
  >
    <div v-if="isLoading" class="loading-state">
      {{ $t('common.loading') }}...
    </div>

    <div v-else-if="!instanceData" class="empty-state">
      {{ $t('views.events.no_settings') }}
    </div>

    <form v-else @submit.prevent="saveMetadata">
      <div v-for="def in definitions" :key="def.id" class="form-group">
        <label>{{ def.name }}</label>
        
        <input 
          v-if="def.expected_data_type === 'INTEGER' || def.expected_data_type === 'FLOAT'" 
          type="number" 
          step="any"
          v-model="editValues[def.id]" 
          class="form-control" 
        />
        
        <input 
          v-else-if="def.expected_data_type === 'BOOLEAN'" 
          type="checkbox" 
          v-model="editValues[def.id]" 
          style="width: 20px; height: 20px; margin-top: 5px;"
        />
        
        <input 
          v-else 
          type="text" 
          v-model="editValues[def.id]" 
          class="form-control" 
        />
      </div>

      <div class="modal-actions" style="margin-top: 25px;">
        <button type="button" class="btn-secondary" @click="$emit('close')">{{ $t('actions.cancel') }}</button>
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

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  instanceId: { type: Number, default: null },
  configName: { type: String, default: '' }
})

const emit = defineEmits(['close', 'saved'])

const isLoading = ref(false)
const isSaving = ref(false)
const instanceData = ref(null)
const definitions = ref([])
const editValues = ref({})

const loadInstance = async () => {
  if (!props.instanceId) {
    instanceData.value = null
    return
  }

  isLoading.value = true
  try {
    const res = await api.get(`metadata-instances/${props.instanceId}/`)
    instanceData.value = res.data

    const groupRes = await api.get(`metadata/groups/${res.data.group}/`)
    definitions.value = groupRes.data.full_definitions || []

    const newValues = {}
    definitions.value.forEach(def => {
      const existingVal = res.data.values.find(v => v.definition === def.id || v.definition_id === def.id)
      let val = existingVal ? existingVal.value : ''
      if (def.expected_data_type === 'BOOLEAN') {
        val = (val === 'true' || val === true)
      }
      newValues[def.id] = val
    })
    editValues.value = newValues

  } catch (error) {
  } finally {
    isLoading.value = false
  }
}

const saveMetadata = async () => {
  if (!instanceData.value) return
  isSaving.value = true

  const formattedValues = Object.keys(editValues.value).map(defId => ({
    definition: parseInt(defId),
    value: editValues.value[defId] !== null && editValues.value[defId] !== undefined ? String(editValues.value[defId]) : ''
  }))

  try {
    await api.put(`metadata-instances/${props.instanceId}/`, {
      group: instanceData.value.group,
      values: formattedValues
    })
    emit('saved')
    emit('close')
  } catch (error) {
  } finally {
    isSaving.value = false
  }
}

watch(() => props.isOpen, (newVal) => {
  if (newVal) loadInstance()
})
</script>

<style scoped>
.empty-state { text-align: center; color: #95a5a6; font-style: italic; padding: 20px; }
.loading-state { text-align: center; color: #7f8c8d; padding: 20px; }
</style>
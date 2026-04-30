<template>
  <BaseModal
    :isOpen="isOpen"
    :title="$t('master_data.edit_metadata') + (device ? ' - ' + device.name : '')"
    @close="$emit('close')"
    customClass="large-modal"
  >
    <div v-if="device" class="metadata-tabs-container">
      
      <!-- Tab Header -->
      <div class="tabs-header">
        <button 
          v-if="device.current_hardware_specs_group_id"
          :class="['tab-btn', activeTab === 'hardware_specs' ? 'active' : '']"
          @click="activeTab = 'hardware_specs'"
        >
          {{ $t('master_data.hardware_specs') }}
        </button>
        <button 
          v-if="device.current_default_settings_group_id"
          :class="['tab-btn', activeTab === 'default_settings' ? 'active' : '']"
          @click="activeTab = 'default_settings'"
        >
          {{ $t('master_data.default_settings') }}
        </button>
      </div>

      <!-- Tab Content -->
      <div class="tab-content" style="padding-top: 20px;">
        
        <div v-if="isLoading" class="loading-state">
          {{ $t('common.loading') }}...
        </div>

        <div v-else-if="!hasAnyGroup" class="empty-state" style="padding: 30px; color: #e74c3c;">
          Fehlende Verknüpfung! Bitte weise diesem Gerät zuerst eine Gruppe zu und speichere es.
        </div>

        <form v-else @submit.prevent="saveAllMetadata">
          
          <div v-if="currentDefinitions.length === 0" class="empty-state" style="padding: 30px;">
            Die ausgewählte Metadaten-Gruppe für diesen Tab enthält noch keine Felder (Definitions).
          </div>

          <!-- Dynamische Formularfelder (v-model greift auf den getrennten State zu) -->
          <div v-for="def in currentDefinitions" :key="def.id" class="form-group">
            <label>{{ def.name }} <span v-if="def.is_required">*</span></label>
            
            <input 
              v-if="def.expected_data_type === 'INTEGER' || def.expected_data_type === 'FLOAT'" 
              type="number" 
              step="any"
              v-model="currentValues[def.id]" 
              class="form-control" 
              :required="def.is_required" 
            />
            
            <input 
              v-else-if="def.expected_data_type === 'BOOLEAN'" 
              type="checkbox" 
              v-model="currentValues[def.id]" 
              style="width: 20px; height: 20px; margin-top: 5px;"
            />
            
            <input 
              v-else 
              type="text" 
              v-model="currentValues[def.id]" 
              class="form-control" 
              :required="def.is_required" 
            />
            
            <small class="hint-text" v-if="def.description">{{ def.description }}</small>
          </div>

          <div class="modal-actions" style="margin-top: 25px;">
            <button type="button" class="btn-secondary" @click="$emit('close')">{{ $t('actions.cancel') }}</button>
            <button type="submit" class="btn-primary" :disabled="isSaving || totalDefinitions === 0">
              {{ isSaving ? $t('common.saving') : $t('actions.save') }}
            </button>
          </div>
        </form>

      </div>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import BaseModal from '@/components/ui/BaseModal.vue'

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  device: { type: Object, required: true }
})

const emit = defineEmits(['close'])
const { t } = useI18n()
const toast = useToast()

const activeTab = ref('hardware_specs')
const isLoading = ref(false)
const isSaving = ref(false)

const tabsState = ref({
  hardware_specs: { definitions: [], values: {} },
  default_settings: { definitions: [], values: {} }
})

const hasAnyGroup = computed(() => props.device.current_hardware_specs_group_id || props.device.current_default_settings_group_id)

const currentDefinitions = computed(() => tabsState.value[activeTab.value].definitions)
const currentValues = computed(() => tabsState.value[activeTab.value].values)
const totalDefinitions = computed(() => tabsState.value.hardware_specs.definitions.length + tabsState.value.default_settings.definitions.length)


const fetchTabData = async (tabKey, groupId, instanceId) => {
  try {
    const groupRes = await api.get(`metadata/groups/${groupId}/`)
    let loadedDefs = groupRes.data.full_definitions || []

    const instanceRes = await api.get(`metadata-instances/${instanceId}/`)
    const currentVals = instanceRes.data.values || []

    const newValues = {}
    loadedDefs.forEach(def => {
      const existingVal = currentVals.find(v => v.definition === def.id || v.definition_id === def.id)
      newValues[def.id] = existingVal ? existingVal.value : ''
      
      if (def.expected_data_type === 'BOOLEAN') {
        newValues[def.id] = (existingVal?.value === 'true' || existingVal?.value === '1' || existingVal?.value === true)
      }
    })

    tabsState.value[tabKey].definitions = loadedDefs
    tabsState.value[tabKey].values = newValues
  } catch (error) {
  }
}

const loadAllMetadata = async () => {
  if (!hasAnyGroup.value) return

  isLoading.value = true
  
  if (props.device.current_hardware_specs_group_id) {
    activeTab.value = 'hardware_specs'
  } else if (props.device.current_default_settings_group_id) {
    activeTab.value = 'default_settings'
  }

  const promises = []
  if (props.device.current_hardware_specs_group_id && props.device.hardware_specs) {
    promises.push(fetchTabData('hardware_specs', props.device.current_hardware_specs_group_id, props.device.hardware_specs))
  }
  if (props.device.current_default_settings_group_id && props.device.default_settings) {
    promises.push(fetchTabData('default_settings', props.device.current_default_settings_group_id, props.device.default_settings))
  }

  await Promise.all(promises)
  isLoading.value = false
}

const formatValuesForApi = (valuesObj) => {
  return Object.keys(valuesObj).map(defId => {
    let rawVal = valuesObj[defId]
    let strVal = (rawVal === null || rawVal === undefined) ? '' : String(rawVal)
    
    return {
      definition: parseInt(defId),
      value: strVal
    }
  })
}

const saveAllMetadata = async () => {
  isSaving.value = true
  
  try {
    const savePromises = []

    if (props.device.hardware_specs && tabsState.value.hardware_specs.definitions.length > 0) {
      savePromises.push(
        api.put(`metadata-instances/${props.device.hardware_specs}/`, {
          group: props.device.current_hardware_specs_group_id,
          values: formatValuesForApi(tabsState.value.hardware_specs.values)
        })
      )
    }

    if (props.device.default_settings && tabsState.value.default_settings.definitions.length > 0) {
      savePromises.push(
        api.put(`metadata-instances/${props.device.default_settings}/`, {
          group: props.device.current_default_settings_group_id,
          values: formatValuesForApi(tabsState.value.default_settings.values)
        })
      )
    }

    await Promise.all(savePromises)
    
    toast.success('Erfolgreich gespeichert.')
    emit('close')
  } catch (error) {
  } finally {
    isSaving.value = false
  }
}

onMounted(() => {
  loadAllMetadata()
})

watch(() => props.isOpen, (newVal) => {
  if (newVal) loadAllMetadata()
})
</script>

<style scoped>
.metadata-tabs-container { display: flex; flex-direction: column; }
.tabs-header { display: flex; border-bottom: 2px solid #e0e0e0; }
.tab-btn {
  flex: 1; padding: 12px; background: transparent; border: none;
  border-bottom: 3px solid transparent; font-weight: 600; font-size: 1rem;
  color: #7f8c8d; cursor: pointer; transition: all 0.2s ease;
}
.tab-btn.active { color: #2980b9; border-bottom-color: #2980b9; }
.tab-btn:hover:not(.active) { background: #f8f9fa; }
.hint-text { color: #95a5a6; display: block; margin-top: 4px; font-size: 0.85rem; }
.loading-state { padding: 40px; text-align: center; color: #7f8c8d; }
.empty-state { text-align: center; color: #95a5a6; font-style: italic; }
</style>
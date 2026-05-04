<template>
  <div class="recording-upload card">
    <h2 style="margin-bottom: 10px;">{{ $t('views.runner.upload_title') }}</h2>
    
    <div v-if="isLoadingContext" class="text-muted mb-4">
      {{ $t('views.runner.loading_device_context') }}
    </div>

    <form v-else @submit.prevent>
      
      <div class="device-context-section mb-4 p-3" style="background: #f8f9fa; border: 1px solid #dcdde1; border-radius: 6px;">
        <h4 style="margin-top: 0; color: #2c3e50; font-size: 1.05rem;">{{ $t('views.runner.select_recording_device') }}</h4>
        
        <div class="form-group mb-3">
          <label>{{ $t('views.runner.planned_devices_phase') }}</label>
          <select v-model="selectedPhaseConfigId" class="form-control" @change="onDeviceSelectionChange">
            <option :value="null">{{ $t('views.runner.please_select_device') }}</option>
            <option v-for="cfg in plannedPhaseConfigs" :key="cfg.id" :value="cfg.id">
              {{ cfg.device_name }}
            </option>
          </select>
        </div>

        <div class="text-right mb-3">
          <button type="button" class="btn-icon" style="font-size: 0.85rem; color: #3498db; text-decoration: underline;" @click="openAdHocModal">
            {{ $t('views.runner.add_other_device_pool') }}
          </button>
        </div>

        <div v-if="selectedPhaseConfig" class="instance-action-area p-3" style="background: white; border-radius: 4px; border: 1px solid #eee;">
          
          <div v-if="existingInstancesForSelection.length > 0 && !forceNewInstance">
            <p style="color: #27ae60; font-weight: 600; margin-top: 0; margin-bottom: 10px;">
              {{ $t('views.runner.existing_instances_found') }}
            </p>
            <p style="font-size: 0.85rem; color: #7f8c8d; margin-bottom: 15px;">
              {{ $t('views.runner.choose_or_create_instance') }}
            </p>
            
            <div style="display: flex; gap: 10px; align-items: flex-end; flex-wrap: wrap;">
              <div class="form-group" style="margin-bottom: 0; flex: 1; min-width: 200px;">
                <select v-model="selectedInstanceIdToReuse" class="form-control" style="font-family: monospace; font-size: 0.9rem;">
                  <option v-for="inst in existingInstancesForSelection" :key="inst.id" :value="inst.id">
                    {{ $t('views.runner.instance_id', { id: inst.id, time: new Date(inst.created_at).toLocaleTimeString() }) }}
                  </option>
                </select> 
              </div>
              <button type="button" class="btn-secondary btn-sm" @click="forceNewInstance = true">
                {{ $t('views.runner.create_new') }}
              </button>
            </div>
          </div>

          <div v-else>
            <p style="color: #e67e22; font-weight: 600; margin-top: 0; margin-bottom: 10px;">
              {{ $t('views.runner.configure_new_instance') }}
            </p>
            <p style="font-size: 0.85rem; color: #7f8c8d; margin-bottom: 15px;">
              {{ $t('views.runner.configure_channels_settings_first') }}
            </p>
            <div style="display: flex; gap: 10px;">
              <button type="button" class="btn-primary btn-sm" @click="isInstanceModalOpen = true">
                {{ $t('views.runner.start_setup') }}
              </button>
              <button v-if="forceNewInstance && existingInstancesForSelection.length > 0" type="button" class="btn-secondary btn-sm" @click="forceNewInstance = false">
                {{ $t('actions.cancel') }}
              </button>
            </div>
          </div>

        </div>
      </div>

      <hr style="margin: 25px 0; border: 0; border-top: 1px solid #ecf0f1;" />

      <div class="form-row" style="display: flex; gap: 1rem; margin-bottom: 15px;">
        <div class="form-group" style="flex: 2;">
          <label>{{ $t('views.runner.upload_type') }} *</label>
          <select v-model="recordingType" class="form-control" required @change="onTypeChange">
             <option value="eeg">{{ $t('views.runner.upload_type_eeg') }}</option>
             <option value="hr">{{ $t('views.runner.upload_type_hr') }}</option>
             <option value="generic">{{ $t('views.runner.upload_type_generic') }}</option>
          </select>
        </div>
        
        <div class="form-group" style="flex: 1;">
          <label>{{ $t('views.runner.upload_order_fixed') }}</label>
          <input type="number" :value="fixedOrder" class="form-control" disabled style="background-color: #f9f9f9; cursor: not-allowed;" />
        </div>
      </div>

      <div v-if="recordingType === 'generic'" class="form-group" style="margin-bottom: 15px; padding: 15px; background: #f8f9fa; border: 1px dashed #bdc3c7; border-radius: 6px;">
        <label style="color: #2c3e50; font-weight: bold;">{{ $t('views.runner.upload_generic_category') }} *</label>
        <BaseSearchSelect 
          v-model="selectedGenericCategory" 
          :options="genericCategories" 
          :placeholder="$t('views.runner.upload_generic_category_placeholder')" 
        />
        <BaseInputError :message="fieldErrors.category" />
      </div>

      <div class="form-group" style="margin-bottom: 15px;">
        <label>{{ $t('views.runner.upload_file') }}</label>
        <input type="file" @change="onFileChange" class="form-control" />
      </div>

      <div class="form-group" style="margin-bottom: 15px;">
        <label>{{ $t('views.runner.upload_custom_name') }}</label>
        <input type="text" v-model="customFileName" class="form-control" :placeholder="$t('views.runner.upload_custom_name_placeholder')" />
      </div>

      <div class="form-group" style="margin-bottom: 25px;">
        <label>{{ $t('views.runner.upload_desc') }}</label>
        <textarea v-model="description" rows="3" class="form-control" :placeholder="$t('views.runner.upload_desc_placeholder')"></textarea>
      </div>
    </form>

    <WarningModal
      :isOpen="isSkipModalOpen"
      :title="$t('views.runner.upload_skip_title')"
      :message="$t('views.runner.upload_skip_message')"
      :confirmText="$t('views.runner.upload_skip_confirm')"
      :hideCancel="false"
      @confirm="onConfirmSkip"
      @cancel="onCancelSkip"
      @close="isSkipModalOpen = false"
    />

    <BaseModal 
      :isOpen="isAdHocModalOpen" 
      :title="$t('views.runner.add_device_from_pool')" 
      @close="isAdHocModalOpen = false"
    >
      <div v-if="isLoadingAdHocPool" class="text-center p-3">
        {{ $t('views.runner.loading_event_pool') }}
      </div>
      <div v-else-if="adHocPoolDevices.length === 0" class="text-muted text-center p-3">
        {{ $t('views.runner.no_more_devices_in_pool') }}
      </div>
      <div v-else>
        <p class="mb-3" style="font-size: 0.9rem; color: #7f8c8d;">
          {{ $t('views.runner.select_pool_device_spontaneous') }}
        </p>
        <div class="list-group">
          <button 
            v-for="dev in adHocPoolDevices" 
            :key="dev.id" 
            class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
            @click="addAdHocDevice(dev)"
            :disabled="isAddingAdHocDevice"
            style="margin-bottom: 8px; border: 1px solid #ccc; border-radius: 4px; padding: 10px; background: #fff; width: 100%; text-align: left; cursor: pointer;"
          >
            <span>
              <strong>{{ dev.device_name }}</strong>
            </span>
            <span v-if="isAddingAdHocDevice" class="text-muted small">{{ $t('views.runner.adding') }}</span>
            <span v-else class="text-primary small" style="font-weight: bold;">{{ $t('views.runner.add') }}</span>
          </button>
        </div>
      </div>
      <div class="modal-actions mt-3 text-right">
        <button class="btn-secondary" @click="isAdHocModalOpen = false">{{ $t('actions.cancel') }}</button>
      </div>
    </BaseModal>

    <DeviceInstanceModal 
      :isOpen="isInstanceModalOpen"
      :sessionId="sessionId"
      :phaseConfig="selectedPhaseConfig"
      @saved="onInstanceCreated"
      @close="isInstanceModalOpen = false"
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'

import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'
import BaseInputError from '@/components/ui/BaseInputError.vue'
import WarningModal from '@/components/ui/WarningModal.vue'
import DeviceInstanceModal from '@/components/runner/DeviceInstanceModal.vue'
import { useGlobalModal } from '@/composables/useGlobalModal'

const props = defineProps({
  parameters: Object,
  sessionId: [String, Number],
  eventId: [String, Number],
  pageGroupId: [String, Number],
  eventGroupId: [String, Number]
})

const { t } = useI18n()
const { showWarning } = useGlobalModal()

const isLoadingContext = ref(true)
const plannedPhaseConfigs = ref([])
const existingSessionInstances = ref([])

const selectedPhaseConfigId = ref(null)
const selectedInstanceIdToReuse = ref(null) 
const forceNewInstance = ref(false)
const isInstanceModalOpen = ref(false)

const selectedPhaseConfig = computed(() => {
  return plannedPhaseConfigs.value.find(c => c.id === selectedPhaseConfigId.value)
})

const existingInstancesForSelection = computed(() => {
  if (!selectedPhaseConfigId.value) return []
  return existingSessionInstances.value.filter(inst => inst.phase_config === selectedPhaseConfigId.value)
})

const finalInstanceId = computed(() => {
  if (forceNewInstance.value) return null
  if (selectedInstanceIdToReuse.value) return selectedInstanceIdToReuse.value
  if (existingInstancesForSelection.value.length > 0) return existingInstancesForSelection.value[0].id
  return null
})

const fixedOrder = computed(() => props.parameters?.order || 1)
const recordingType = ref('eeg')
const selectedGenericCategory = ref(null)
const genericCategories = ref([])
const file = ref(null)
const customFileName = ref('')
const description = ref('')
const fieldErrors = ref({ category: '' })

const isAdHocModalOpen = ref(false)
const isLoadingAdHocPool = ref(false)
const adHocPoolDevices = ref([])
const isAddingAdHocDevice = ref(false)

const isSkipModalOpen = ref(false)
let resolveSubmitPromise = null
let rejectSubmitPromise = null

onMounted(async () => {
  try {
    const catRes = await api.get('category/generic-recording/') 
    genericCategories.value = catRes.data

    if (props.eventId && props.pageGroupId) {
      let configUrl = `event-management/phase-device-configs/?phase__page_group=${props.pageGroupId}`
      if (props.eventGroupId) {
        configUrl += `&phase__event_group=${props.eventGroupId}`
      } else {
        configUrl += `&phase__event_group__event=${props.eventId}`
      }

      const [phaseRes, instanceRes] = await Promise.all([
        api.get(configUrl),
        api.get(`device-instances/?session=${props.sessionId}`)
      ])
      
      plannedPhaseConfigs.value = phaseRes.data
      existingSessionInstances.value = instanceRes.data
      
      if (plannedPhaseConfigs.value.length === 1) {
        selectedPhaseConfigId.value = plannedPhaseConfigs.value[0].id
        autoSelectDefaultInstance()
      }
    }
  } catch (error) {
    console.error(error)
  } finally {
    isLoadingContext.value = false
  }
})

const onDeviceSelectionChange = () => {
  forceNewInstance.value = false
  autoSelectDefaultInstance()
}

const autoSelectDefaultInstance = () => {
  if (existingInstancesForSelection.value.length > 0) {
    const latest = existingInstancesForSelection.value[existingInstancesForSelection.value.length - 1]
    selectedInstanceIdToReuse.value = latest.id
  } else {
    selectedInstanceIdToReuse.value = null
  }
}

const onInstanceCreated = (newInstance) => {
  existingSessionInstances.value.push(newInstance)
  forceNewInstance.value = false
  selectedInstanceIdToReuse.value = newInstance.id
}

const onTypeChange = () => {
  if (recordingType.value !== 'generic') selectedGenericCategory.value = null
  fieldErrors.value.category = ''
}

const onFileChange = (e) => { 
  file.value = e.target.files[0] || null 
}

const onConfirmSkip = () => {
  isSkipModalOpen.value = false
  if (resolveSubmitPromise) resolveSubmitPromise()
}

const onCancelSkip = () => {
  isSkipModalOpen.value = false
  if (rejectSubmitPromise) rejectSubmitPromise(new Error("Upload aborted by user"))
}

const submit = () => {
  return new Promise(async (resolve, reject) => {
    fieldErrors.value = { category: '' }

    if (plannedPhaseConfigs.value.length > 0 && !finalInstanceId.value && file.value) {
      showWarning(t('views.runner.warning_select_configure_device'), t('views.runner.warning_device_missing'))
      return reject(new Error("No device instance configured"))
    }

    if (recordingType.value === 'generic' && !selectedGenericCategory.value) {
      fieldErrors.value.category = t('views.runner.upload_error_no_category') || t('errors.required_field')
      return reject(new Error("Inline validation failed"))
    }

    if (!file.value) {
      resolveSubmitPromise = resolve
      rejectSubmitPromise = reject
      isSkipModalOpen.value = true
      return 
    }

    const formData = new FormData()
    let uploadFileName = file.value.name
    
    if (customFileName.value.trim() !== '') {
      const extension = uploadFileName.split('.').pop()
      uploadFileName = `${customFileName.value.trim()}.${extension}`
    }

    formData.append('file', file.value, uploadFileName)
    formData.append('session', props.sessionId) 
    formData.append('order', fixedOrder.value)
    
    if (finalInstanceId.value) {
      formData.append('device_instance', finalInstanceId.value)
    }

    if (description.value) formData.append('description', description.value)
    if (recordingType.value === 'generic') formData.append('category', selectedGenericCategory.value)
    
    let endpoint = recordingType.value === 'eeg' ? 'recordings/eeg/' : (recordingType.value === 'hr' ? 'recordings/heart-rate/' : 'recordings/generic/')

    try {
      await api.post(endpoint, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
      resolve()
    } catch (error) {
      showWarning(t('views.runner.upload_error') || t('common.error_saving'), t('common.error'))
      reject(error)
    }
  })
}

const openAdHocModal = async () => {
  isAdHocModalOpen.value = true
  isLoadingAdHocPool.value = true
  try {
    const poolRes = await api.get(`event-device-models/?event=${props.eventId}`)
    const allPoolDevices = poolRes.data

    const alreadyPlannedDeviceModelIds = plannedPhaseConfigs.value.map(cfg => cfg.device_model_id || cfg.master_device_id)
    
    adHocPoolDevices.value = allPoolDevices.filter(d => !alreadyPlannedDeviceModelIds.includes(d.device_model))
  } catch (e) {
    console.error(e)
  } finally {
    isLoadingAdHocPool.value = false
  }
}

const addAdHocDevice = async (poolDevice) => {
  isAddingAdHocDevice.value = true
  try {
    const payload = {
      event_group_id: props.eventGroupId,
      target_page_group_id: props.pageGroupId,
      master_device_id: poolDevice.device_model,
      expected_channels: [] 
    }

    const res = await api.post('event-management/phase-device-configs/', payload)
    const newPhaseConfig = res.data

    plannedPhaseConfigs.value.push(newPhaseConfig)
    
    selectedPhaseConfigId.value = newPhaseConfig.id
    forceNewInstance.value = true 
    
    isAdHocModalOpen.value = false
    isInstanceModalOpen.value = true

  } catch (e) {
    console.error(e)
  } finally {
    isAddingAdHocDevice.value = false
  }
}

defineExpose({ submit })
</script>

<style scoped>
.btn-sm { padding: 6px 12px; font-size: 0.85rem; }
.btn-icon { background: none; border: none; cursor: pointer; padding: 0; }
.btn-icon:hover { color: #2980b9 !important; }
</style>
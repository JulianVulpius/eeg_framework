<template>
  <div class="recording-upload card">
    <h2 style="margin-bottom: 10px;">{{ $t('views.runner.upload_title') }}</h2>
    <p style="color: #e67e22; font-size: 0.9rem; margin-bottom: 20px;">
      ⚠️ {{ $t('views.runner.upload_overwrite_warning') }}
    </p>
    
    <form @submit.prevent>
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
        <input 
          type="file" 
          @change="onFileChange" 
          class="form-control" 
        />
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'

import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'
import BaseInputError from '@/components/ui/BaseInputError.vue'
import WarningModal from '@/components/ui/WarningModal.vue'
import { useGlobalModal } from '@/composables/useGlobalModal'

const props = defineProps({
  parameters: Object,
  sessionId: [String, Number]
})

const { t } = useI18n()
const { showWarning } = useGlobalModal()

const fixedOrder = computed(() => props.parameters?.order || 1)

const recordingType = ref('eeg')
const selectedGenericCategory = ref(null)
const genericCategories = ref([])

const file = ref(null)
const customFileName = ref('')
const description = ref('')

const fieldErrors = ref({ category: '' })

const isSkipModalOpen = ref(false)
let resolveSubmitPromise = null
let rejectSubmitPromise = null

onMounted(async () => {
  try {
    const res = await api.get('category/generic-recording/') 
    genericCategories.value = res.data
  } catch (error) {
    showWarning(t('common.error_loading') || 'Error', t('common.error'))
  }
})

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

defineExpose({ submit })
</script>
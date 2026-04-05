<template>
  <div class="recording-upload card">
    <h2 style="margin-bottom: 10px;">{{ $t('views.runner.upload_title') }}</h2>
    <p style="color: #e67e22; font-size: 0.9rem; margin-bottom: 20px;">
      ⚠️ {{ $t('views.runner.upload_overwrite_warning') }}
    </p>
    
    <form @submit.prevent="uploadFile">
      
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
      </div>

      <div class="form-group" style="margin-bottom: 15px;">
        <label>{{ $t('views.runner.upload_file') }} *</label>
        <input type="file" @change="onFileChange" class="form-control" required />
      </div>

      <div class="form-group" style="margin-bottom: 15px;">
        <label>{{ $t('views.runner.upload_custom_name') }}</label>
        <input type="text" v-model="customFileName" class="form-control" :placeholder="$t('views.runner.upload_custom_name_placeholder')" />
      </div>

      <div class="form-group" style="margin-bottom: 25px;">
        <label>{{ $t('views.runner.upload_desc') }}</label>
        <textarea v-model="description" rows="3" class="form-control" :placeholder="$t('views.runner.upload_desc_placeholder')"></textarea>
      </div>

      <div class="form-actions" style="display: flex; gap: 15px; justify-content: flex-end;">
         <button type="button" class="btn-secondary" @click="$emit('go-back')">{{ $t('actions.back') }}</button>
         <button type="submit" class="btn-primary" :disabled="isUploading || !file">
            {{ isUploading ? $t('views.runner.upload_btn_uploading') : $t('views.runner.upload_btn_upload') }}
         </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'

const props = defineProps({
  parameters: Object,
  sessionId: [String, Number]
})

const emit = defineEmits(['completed', 'go-back'])
const { t } = useI18n()
const { showToast } = useToast()

const fixedOrder = computed(() => props.parameters?.order || 1)

const recordingType = ref('eeg')
const selectedGenericCategory = ref(null)
const genericCategories = ref([])

const file = ref(null)
const customFileName = ref('')
const description = ref('')
const isUploading = ref(false)

onMounted(async () => {
  try {
    const res = await api.get('category/generic-recording/') 
    genericCategories.value = res.data
  } catch (error) {
    console.error("Konnte Generic Kategorien nicht laden:", error)
  }
})

const onTypeChange = () => {
  if (recordingType.value !== 'generic') {
    selectedGenericCategory.value = null
  }
}

const onFileChange = (e) => { file.value = e.target.files[0] || null }

const uploadFile = async () => {
  if (!file.value) return

  if (recordingType.value === 'generic' && !selectedGenericCategory.value) {
    showToast(t('views.runner.upload_error_no_category'), 'error')
    return
  }

  isUploading.value = true
  
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
  
  if (recordingType.value === 'generic') {
    formData.append('category', selectedGenericCategory.value)
  }
  
  let endpoint = recordingType.value === 'eeg' ? 'recordings/eeg/' : (recordingType.value === 'hr' ? 'recordings/heart-rate/' : 'recordings/generic/')

  try {
    await api.post(endpoint, formData, { headers: { 'Content-Type': 'multipart/form-data' } })
    showToast(t('views.runner.upload_success'), 'success')
    emit('completed')
  } catch (error) {
    showToast(t('views.runner.upload_error'), 'error')
  } finally { isUploading.value = false }
}
</script>
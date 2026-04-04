<template>
  <div class="recording-upload card">
    <h2 style="margin-bottom: 20px;">{{ $t('views.runner.upload_title') }}</h2>
    
    <form @submit.prevent="uploadFile">
      
      <div class="form-group" style="margin-bottom: 15px;">
        <label>{{ $t('views.runner.upload_type') }} *</label>
        <select v-model="recordingType" class="form-control" required>
           <option value="eeg">{{ $t('views.runner.upload_type_eeg') }}</option>
           <option value="hr">{{ $t('views.runner.upload_type_hr') }}</option>
           <option value="generic">{{ $t('views.runner.upload_type_generic') }}</option>
        </select>
      </div>

      <div class="form-group" style="margin-bottom: 15px;">
        <label>{{ $t('views.runner.upload_file') }} *</label>
        <input type="file" @change="onFileChange" class="form-control" required />
      </div>

      <div class="form-group" style="margin-bottom: 15px;">
        <label>{{ $t('views.runner.upload_custom_name') }}</label>
        <input 
          type="text" 
          v-model="customFileName" 
          class="form-control" 
          :placeholder="$t('views.runner.upload_custom_name_placeholder')" 
        />
      </div>

      <div class="form-row" style="display: flex; gap: 1rem; margin-bottom: 15px;">
        <div class="form-group" style="flex: 1;">
          <label>{{ $t('views.runner.upload_order') }}</label>
          <input type="number" v-model="order" class="form-control" min="0" />
        </div>
      </div>

      <div class="form-group" style="margin-bottom: 25px;">
        <label>{{ $t('views.runner.upload_desc') }}</label>
        <textarea 
          v-model="description" 
          rows="3" 
          class="form-control" 
          :placeholder="$t('views.runner.upload_desc_placeholder')">
        </textarea>
      </div>

      <div class="form-actions" style="display: flex; gap: 15px; justify-content: flex-end;">
         <button type="button" class="btn-secondary" @click="$emit('go-back')">
            {{ $t('actions.back') }}
         </button>
         <button type="submit" class="btn-primary" :disabled="isUploading || !file">
            {{ isUploading ? $t('views.runner.upload_btn_uploading') : $t('views.runner.upload_btn_upload') }}
         </button>
      </div>
      
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  parameters: Object,
  sessionId: [String, Number]
})

const emit = defineEmits(['completed', 'go-back'])
const { t } = useI18n()
const { showToast } = useToast()

const recordingType = ref('eeg')
const file = ref(null)
const customFileName = ref('')
const order = ref(0)
const description = ref('')
const isUploading = ref(false)

const onFileChange = (e) => {
  file.value = e.target.files[0] || null
}

const uploadFile = async () => {
  if (!file.value) return
  isUploading.value = true
  
  const formData = new FormData()
  
  let uploadFileName = file.value.name
  if (customFileName.value.trim() !== '') {
    const extension = uploadFileName.split('.').pop()
    uploadFileName = `${customFileName.value.trim()}.${extension}`
  }

  formData.append('file', file.value, uploadFileName)
  
  formData.append('session', props.sessionId) 
  formData.append('order', order.value)
  if (description.value) {
    formData.append('description', description.value)
  }
  
  let endpoint = ''
  if (recordingType.value === 'eeg') endpoint = 'recordings/eeg/'
  else if (recordingType.value === 'hr') endpoint = 'recordings/heartrate/'
  else endpoint = 'recordings/generic/'

  try {
    await api.post(endpoint, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    showToast(t('views.runner.upload_success'), 'success')
    emit('completed')
  } catch (error) {
    console.error(error)
    showToast(t('views.runner.upload_error'), 'error')
  } finally {
    isUploading.value = false
  }
}
</script>

<style scoped>
.recording-upload {
  max-width: 600px;
  margin: 0 auto;
  padding: 30px;
}
</style>
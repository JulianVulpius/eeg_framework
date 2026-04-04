<template>
  <div class="recording-upload card">
    <h2 style="margin-bottom: 20px;">📁 Messdaten hochladen</h2>
    
    <form @submit.prevent="uploadFile">
      
      <div class="form-group" style="margin-bottom: 15px;">
        <label>Art der Messung *</label>
        <select v-model="recordingType" class="form-control" required>
           <option value="eeg">EEG Data</option>
           <option value="hr">Heart Rate Data</option>
           <option value="generic">Generic Recording</option>
        </select>
      </div>

      <div class="form-group" style="margin-bottom: 15px;">
        <label>Datei auswählen *</label>
        <input type="file" @change="onFileChange" class="form-control" required />
      </div>

      <div class="form-row" style="display: flex; gap: 1rem; margin-bottom: 15px;">
        <div class="form-group" style="flex: 1;">
          <label>Reihenfolge (Order)</label>
          <input type="number" v-model="order" class="form-control" min="0" />
        </div>
      </div>

      <div class="form-group" style="margin-bottom: 25px;">
        <label>Beschreibung / Notizen (Optional)</label>
        <textarea v-model="description" rows="3" class="form-control" placeholder="Auffälligkeiten während der Messung..."></textarea>
      </div>

      <div class="form-actions" style="display: flex; gap: 15px; justify-content: flex-end;">
         <button type="button" class="btn-secondary" @click="$emit('go-back')">
            Zurück
         </button>
         <button type="submit" class="btn-primary" :disabled="isUploading || !file">
            {{ isUploading ? 'Wird hochgeladen...' : 'Hochladen & Weiter' }}
         </button>
      </div>
      
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/services/api'
import { useToast } from '@/composables/useToast'

const props = defineProps({
  parameters: Object,
  sessionId: [String, Number]
})

const emit = defineEmits(['completed', 'go-back'])
const { showToast } = useToast()

const recordingType = ref('eeg')
const file = ref(null)
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
  formData.append('file', file.value)
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
    showToast('Erfolgreich hochgeladen!', 'success')
    emit('completed')
  } catch (error) {
    console.error(error)
    showToast('Fehler beim Upload', 'error')
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
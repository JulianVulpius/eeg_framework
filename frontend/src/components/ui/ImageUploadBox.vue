<template>
  <div class="image-box-container">
    
    <div class="upload-controls">
      <input type="file" accept="image/*" @change="onFileChange" ref="fileInput" style="display: none;" />
      
      <div v-if="selectedFile" class="pending-upload">
        
        <div class="mini-preview" v-if="localPreviewUrl">
          <img :src="localPreviewUrl" alt="Local Preview" />
        </div>

        <span class="file-name" :title="selectedFile.name">{{ selectedFile.name }}</span>
        
        <div class="btn-group">
          <button class="btn-primary btn-sm" @click="upload" :disabled="isUploading">
            {{ isUploading ? $t('common.uploading') : $t('actions.save') }}
          </button>
          <button class="btn-secondary btn-sm" @click="cancelSelection" :disabled="isUploading">
            X
          </button>
        </div>
      </div>
      
      <button v-else class="btn-secondary" @click="$refs.fileInput.click()">
        {{ $t('actions.select_image') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useGlobalModal } from '@/composables/useGlobalModal'

const emit = defineEmits(['success'])
const { t } = useI18n()
const { showWarning } = useGlobalModal()

const fileInput = ref(null)
const selectedFile = ref(null)
const localPreviewUrl = ref(null)
const isUploading = ref(false)

const onFileChange = (e) => {
  const file = e.target.files[0]
  if (file) {
    selectedFile.value = file
    localPreviewUrl.value = URL.createObjectURL(file)
  }
}

const cancelSelection = () => {
  selectedFile.value = null
  localPreviewUrl.value = null
  if (fileInput.value) fileInput.value.value = ''
}

const upload = async () => {
  if (!selectedFile.value) return
  isUploading.value = true

  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('media_type', 'IMAGE')
  formData.append('original_filename', selectedFile.value.name)

  try {
    const res = await api.post('media/assets/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    emit('success', res.data.id) 
    
    selectedFile.value = null
    localPreviewUrl.value = null
    if (fileInput.value) fileInput.value.value = ''
    
  } catch (error) {
    showWarning(t('common.error_saving'), t('common.error'))
  } finally {
    isUploading.value = false
  }
}
</script>

<style scoped>
.image-box-container {
  width: 250px;
  height: 200px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px dashed #bdc3c7;
  background: #fdfdfd;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;
}
.upload-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
}
.pending-upload {
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-items: center;
  width: 100%;
}
.mini-preview {
  width: 100px;
  height: 80px;
  background: #eee;
  border-radius: 4px;
  overflow: hidden;
}
.mini-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.file-name {
  font-size: 0.8rem;
  color: #2c3e50;
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.btn-group {
  display: flex;
  gap: 8px;
}
.btn-sm {
  padding: 5px 10px;
  font-size: 0.85rem;
}
</style>
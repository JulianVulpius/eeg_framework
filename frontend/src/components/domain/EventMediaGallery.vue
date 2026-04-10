<template>
  <div class="event-media-gallery">
    
    <div class="gallery-toolbar">
      
      <div class="filter-container">
        <div class="filter-item">
          <label>{{ $t('common.creator') }}</label>
          <input 
            type="text" 
            v-model="creatorFilter" 
            class="form-control" 
            :placeholder="$t('common.search')" 
          />
        </div>
        
        <div class="filter-item">
          <label>{{ $t('master_data.category') }}</label>
          <div class="search-select-wrapper">
            <BaseSearchSelect 
              v-model="categoryFilter"
              :options="mediaCategories"
              :nullLabel="`${$t('common.all')}`"
            />
          </div>
        </div>

        <div class="filter-item">
          <label>{{ $t('views.events.media_type') }}</label>
          <select v-model="mediaTypeFilter" class="form-control">
            <option value="">{{ $t('common.all') }}</option>
            <option value="IMAGE">{{ $t('views.stimulus.type_image') }}</option>
            <option value="VIDEO">{{ $t('views.stimulus.type_video') }}</option>
            <option value="AUDIO">{{ $t('views.stimulus.type_audio') }}</option>
            <option value="DOCUMENT">{{ $t('views.events.type_document') }}</option>
          </select>
        </div>
      </div>

      <div class="action-group">
        <button 
          class="btn-secondary" 
          @click="exportVisibleFiles" 
          :disabled="isExporting || filteredGalleryItems.length === 0"
          :title="$t('views.events.export_visible_desc')"
        >
          <span v-if="isExporting" class="spinner">⏳</span>
          <span v-else>📥</span>
          {{ isExporting ? $t('common.loading') : $t('views.events.export_visible') }}
        </button>

        <input type="file" @change="onFileSelected" ref="fileInput" style="display: none;" accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.xls,.xlsx,.csv,.txt" />
        <button class="btn-primary" @click="$refs.fileInput.click()" :disabled="isUploading">
          {{ isUploading ? $t('common.uploading') + '...' : '+ ' + ($t('views.events.upload_media')) }}
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="loading-state">{{ $t('common.loading') }}</div>

    <div v-else class="gallery-grid">
      <div v-for="item in filteredGalleryItems" :key="item.id" class="gallery-item card">
        
        <div 
          class="media-preview" 
          :class="{ 'clickable': item.media_asset_details?.media_type !== 'AUDIO' && item.media_asset_details?.file_exists }"
          @click="item.media_asset_details?.media_type !== 'AUDIO' && item.media_asset_details?.file_exists ? handleMediaClick(item) : null"
        >
          <div v-if="!item.media_asset_details?.file_exists" class="error-state-box" :title="$t('common.file_not_found')">
            <span class="error-icon">⚠️</span>
            <span class="error-text">{{ $t('common.file_not_found') }}</span>
          </div>

          <template v-else>
            <img v-if="item.media_asset_details?.media_type === 'IMAGE'" :src="getAbsoluteUrl(item.media_asset_details.file)" alt="Media" :title="$t('views.events.open_image')" />
            <div v-else-if="item.media_asset_details?.media_type === 'VIDEO'" class="media-icon" :title="$t('views.events.open_video')">🎬</div>
            <audio v-else-if="item.media_asset_details?.media_type === 'AUDIO'" controls :src="getAbsoluteUrl(item.media_asset_details.file)" class="inline-audio-player"></audio>
            <div v-else class="media-icon" :title="$t('views.events.open_file')">📄</div>
          </template>
        </div>

        <div class="media-info">
          <div class="info-text" style="width: 100%;">
            <span class="file-name" :title="item.media_asset_details?.original_filename">
              {{ item.media_asset_details?.original_filename || 'Unknown' }}
            </span>
            
            <select 
              class="category-inline-select" 
              :value="item.media_asset_details?.category || ''" 
              @change="updateCategory(item.media_asset_details?.id, $event.target.value)"
            >
              <option value="">{{ $t('views.events.select_media_category')}}</option>
              <option v-for="cat in mediaCategories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
            </select>

            <span v-if="item.media_asset_details?.creator" style="font-size: 0.7rem; color: #7f8c8d; margin-top: 2px;">
              {{ item.media_asset_details.creator }}
            </span>
          </div>

          <button class="delete-btn" @click="deleteItem(item.media_asset_details?.id)" :title="$t('actions.delete')">🗑️</button>
        </div>

      </div>
      
      <div v-if="filteredGalleryItems.length === 0" class="empty-gallery">
        {{ $t('common.no_data') }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useGlobalModal } from '@/composables/useGlobalModal'

import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'

const props = defineProps({
  eventId: { type: [String, Number], required: true },
  eventName: { type: String, default: 'general' }
})

const { t } = useI18n()
const { showWarning, requireConfirmation } = useGlobalModal()

const fileInput = ref(null)
const isUploading = ref(false)
const isLoading = ref(true)
const isExporting = ref(false)

const galleryItems = ref([])
const mediaCategories = ref([]) 

const creatorFilter = ref('')
const categoryFilter = ref(null)
const mediaTypeFilter = ref('')

const filteredGalleryItems = computed(() => {
  return galleryItems.value.filter(item => {
    const details = item.media_asset_details
    if (!details) return false

    if (categoryFilter.value !== null && categoryFilter.value !== '' && details.category !== categoryFilter.value) {
      return false
    }

    if (mediaTypeFilter.value !== '' && details.media_type !== mediaTypeFilter.value) {
      return false
    }

    if (creatorFilter.value) {
      const creatorName = details.creator ? details.creator.toLowerCase() : ''
      if (!creatorName.includes(creatorFilter.value.toLowerCase())) {
        return false
      }
    }

    return true
  })
})

const getAbsoluteUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const baseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/').replace(/\/api\/?$/, '')
  return baseUrl + path
}

const loadGalleryAndCategories = async () => {
  try {
    const [galleryRes, catRes] = await Promise.all([
      api.get(`event-gallery/?event=${props.eventId}`),
      api.get(`category/media-asset/`)
    ])
    galleryItems.value = galleryRes.data.reverse()
    mediaCategories.value = catRes.data
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

const getMediaType = (fileType) => {
  if (fileType.startsWith('image/')) return 'IMAGE'
  if (fileType.startsWith('video/')) return 'VIDEO'
  if (fileType.startsWith('audio/')) return 'AUDIO'
  return 'DOCUMENT' 
}

const updateCategory = async (assetId, categoryId) => {
  if (!assetId) return
  try {
    const payload = { category: categoryId ? parseInt(categoryId) : null }
    await api.patch(`media/assets/${assetId}/`, payload)
    
    const item = galleryItems.value.find(i => i.media_asset_details?.id === assetId)
    if (item && item.media_asset_details) {
      item.media_asset_details.category = categoryId ? parseInt(categoryId) : null
    }
  } catch(e) {
    showWarning(t('common.error_saving'), t('common.error'))
  }
}

const onFileSelected = async (e) => {
  const file = e.target.files[0]
  if (!file) return

  const mediaType = getMediaType(file.type)
  if (!mediaType) {
    showWarning(t('views.events.unsupported_media') || 'Unsupported media type')
    fileInput.value.value = null
    return
  }

  isUploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('media_type', mediaType)
    formData.append('original_filename', file.name)
    formData.append('event_name', props.eventName)

    const mediaRes = await api.post('media/assets/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    const newAssetId = mediaRes.data.id

    await api.post('event-gallery/', {
      event: props.eventId,
      media: newAssetId
    })

    await loadGalleryAndCategories()
  } catch (error) {
    showWarning(t('common.error_saving'), t('common.error'))
  } finally {
    isUploading.value = false
    fileInput.value.value = null
  }
}

const deleteItem = (mediaAssetId) => {
  if (!mediaAssetId) return
  requireConfirmation(async () => {
    try {
      await api.delete(`media/assets/${mediaAssetId}/`)
      await loadGalleryAndCategories()
    } catch (error) {
      showWarning(t('common.error'), t('common.error'))
    }
  })
}

const handleMediaClick = (item) => {
  const details = item.media_asset_details
  if (!details) return

  const url = getAbsoluteUrl(details.file)
  window.open(url, '_blank')
}

const downloadFile = async (url, filename) => {
  try {
    const response = await fetch(url)
    if (!response.ok) throw new Error('Network response was not ok')
    const blob = await response.blob()
    const link = document.createElement('a')
    link.href = window.URL.createObjectURL(blob)
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(link.href)
  } catch (error) {
    console.error('Download failed', error)
  }
}

const exportVisibleFiles = async () => {
  if (filteredGalleryItems.value.length === 0) return
  
  isExporting.value = true
  try {
    for (const item of filteredGalleryItems.value) {
      const details = item.media_asset_details
      if (details && details.file_exists) {
        const url = getAbsoluteUrl(details.file)
        const filename = details.original_filename || `export_${details.id}`
        await downloadFile(url, filename)
        await new Promise(resolve => setTimeout(resolve, 400))
      }
    }
  } catch (error) {
    showWarning(t('common.error'), t('common.error'))
  } finally {
    isExporting.value = false
  }
}

onMounted(loadGalleryAndCategories)
</script>

<style scoped>
.gallery-toolbar { 
  margin-bottom: 20px; 
  display: flex; 
  justify-content: space-between; 
  align-items: flex-end; 
  flex-wrap: wrap; 
  gap: 20px; 
  background: #fdfdfd;
  padding: 15px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.filter-container {
  display: flex;
  gap: 15px;
  flex: 1;
  flex-wrap: wrap;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
  min-width: 150px;
  max-width: 250px;
}

.filter-item label {
  font-size: 0.85rem;
  font-weight: 600;
  color: #34495e;
  margin: 0;
  padding: 0;
}

.filter-item .form-control {
  width: 100%;
}

.search-select-wrapper {
  width: 100%;
}

.search-select-wrapper :deep(.form-group) {
  margin-bottom: 0 !important;
}

.action-group {
  display: flex;
  justify-content: flex-end;
  align-items: flex-end; 
  gap: 12px;
  padding-bottom: 1px; 
}

.spinner {
  display: inline-block;
  animation: spin 2s linear infinite;
}
@keyframes spin { 100% { transform: rotate(360deg); } }

.gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }
.gallery-item { display: flex; flex-direction: column; overflow: hidden; padding: 0; border: 1px solid #e0e0e0; }

.media-preview { height: 160px; background: #f1f2f6; display: flex; justify-content: center; align-items: center; border-bottom: 1px solid #e0e0e0; position: relative; }
.media-preview img { width: 100%; height: 100%; object-fit: cover; }
.media-icon { font-size: 3rem; user-select: none; }

.media-preview.clickable { cursor: pointer; transition: opacity 0.2s, background-color 0.2s; }
.media-preview.clickable:hover { opacity: 0.85; background-color: #e5e7eb; }

.inline-audio-player { width: 90%; max-width: 200px; outline: none; }

.media-info { display: flex; justify-content: space-between; align-items: flex-start; padding: 12px 15px; background: white; gap: 10px; }
.info-text { display: flex; flex-direction: column; overflow: hidden; gap: 8px; }
.file-name { font-size: 0.9rem; font-weight: 600; color: #2c3e50; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 140px; }

.category-inline-select {
  padding: 4px 6px;
  border: 1px solid #bdc3c7;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #34495e;
  width: 100%;
  background-color: #f9f9f9;
  cursor: pointer;
}
.category-inline-select:focus {
  outline: none;
  border-color: #3498db;
}

.delete-btn { background: transparent; border: none; cursor: pointer; font-size: 1.2rem; padding: 5px; opacity: 0.6; transition: opacity 0.2s; margin-top: -4px;}
.delete-btn:hover { opacity: 1; color: #e74c3c; }
.empty-gallery { grid-column: 1 / -1; text-align: center; padding: 40px; color: #7f8c8d; font-style: italic; background: #f8f9fa; border-radius: 8px; border: 2px dashed #dcdde1; }

.error-state-box { display: flex; flex-direction: column; align-items: center; justify-content: center; background: #ffeaa7; width: 100%; height: 100%; color: #d63031; text-align: center; padding: 10px; border-bottom: 1px solid #dcdde1; }
.error-state-box .error-icon { font-size: 2.5rem; margin-bottom: 5px; }
.error-state-box .error-text { font-size: 0.8rem; font-weight: bold; line-height: 1.2; }
</style>
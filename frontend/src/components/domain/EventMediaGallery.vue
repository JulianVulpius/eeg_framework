<template>
  <div class="event-media-gallery">
    <div class="gallery-toolbar">
      <div class="category-select" style="min-width: 250px;">
        <BaseSearchSelect 
          v-model="selectedCategory" 
          :options="mediaCategories" 
          :placeholder="$t('views.events.select_media_category')" 
          :nullLabel="$t('master_data.none')" 
        />
      </div>

      <input type="file" @change="onFileSelected" ref="fileInput" style="display: none;" accept="image/*,video/*,audio/*" />
      <button class="btn-primary" @click="$refs.fileInput.click()" :disabled="isUploading">
        {{ isUploading ? $t('common.uploading') + '...' : '+ ' + $t('views.events.upload_media') }}
      </button>
    </div>

    <div v-if="isLoading" class="loading-state">{{ $t('common.loading') }}</div>

    <div v-else class="gallery-grid">
      <div v-for="item in galleryItems" :key="item.id" class="gallery-item card">
        <div class="media-preview">
          <img v-if="item.media_asset_details?.media_type === 'IMAGE'" :src="getAbsoluteUrl(item.media_asset_details.file)" alt="Media" />
          <div v-else-if="item.media_asset_details?.media_type === 'VIDEO'" class="media-icon">🎬</div>
          <div v-else-if="item.media_asset_details?.media_type === 'AUDIO'" class="media-icon">🎵</div>
          <div v-else class="media-icon">📄</div>
        </div>

        <div class="media-info">
          <div class="info-text">
            <span class="file-name" :title="item.media_asset_details?.original_filename">
              {{ item.media_asset_details?.original_filename || 'Unknown' }}
            </span>
            <span v-if="item.media_asset_details?.category" class="category-badge">Cat-ID: {{ item.media_asset_details.category }}</span>
          </div>
          <button class="delete-btn" @click="deleteItem(item.media_asset_details?.id)">🗑️</button>
        </div>
      </div>
      
      <div v-if="galleryItems.length === 0" class="empty-gallery">{{ $t('common.no_data') }}</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useGlobalModal } from '@/composables/useGlobalModal'
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue' 

const props = defineProps({ eventId: { type: [String, Number], required: true } })
const { t } = useI18n()
const { showWarning, requireConfirmation } = useGlobalModal()

const fileInput = ref(null)
const isUploading = ref(false)
const isLoading = ref(true)

const galleryItems = ref([])
const mediaCategories = ref([]) 
const selectedCategory = ref(null) 

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
    galleryItems.value = galleryRes.data
    mediaCategories.value = catRes.data
  } catch (error) {
    console.error(error)
  } finally { isLoading.value = false }
}

const getMediaType = (fileType) => {
  if (fileType.startsWith('image/')) return 'IMAGE'
  if (fileType.startsWith('video/')) return 'VIDEO'
  if (fileType.startsWith('audio/')) return 'AUDIO'
  return null
}

const onFileSelected = async (e) => {
  const file = e.target.files[0]
  if (!file) return

  const mediaType = getMediaType(file.type)
  if (!mediaType) {
    showWarning(t('views.events.unsupported_media') || 'Unsupported media type', t('common.error'))
    fileInput.value.value = null
    return
  }

  isUploading.value = true
  try {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('media_type', mediaType)
    formData.append('original_filename', file.name)
    if (selectedCategory.value) formData.append('category', selectedCategory.value)

    const mediaRes = await api.post('media/assets/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    const newAssetId = mediaRes.data.id

    await api.post('event-gallery/', {
      event: props.eventId,
      media: newAssetId,
      display_order: galleryItems.value.length + 1
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

onMounted(loadGalleryAndCategories)
</script>

<style scoped>
.gallery-toolbar { margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center; gap: 20px; }
.gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }
.gallery-item { display: flex; flex-direction: column; overflow: hidden; padding: 0; border: 1px solid #e0e0e0; }
.media-preview { height: 160px; background: #f1f2f6; display: flex; justify-content: center; align-items: center; border-bottom: 1px solid #e0e0e0; }
.media-preview img { width: 100%; height: 100%; object-fit: cover; }
.media-icon { font-size: 3rem; }
.media-info { display: flex; justify-content: space-between; align-items: center; padding: 12px 15px; background: white; }
.info-text { display: flex; flex-direction: column; overflow: hidden; }
.file-name { font-size: 0.9rem; font-weight: 600; color: #2c3e50; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 140px; }
.category-badge { font-size: 0.75rem; color: #7f8c8d; margin-top: 4px; }
.delete-btn { background: transparent; border: none; cursor: pointer; font-size: 1.2rem; padding: 5px; opacity: 0.6; transition: opacity 0.2s; }
.delete-btn:hover { opacity: 1; color: #e74c3c; }
.empty-gallery { grid-column: 1 / -1; text-align: center; padding: 40px; color: #7f8c8d; font-style: italic; background: #f8f9fa; border-radius: 8px; border: 2px dashed #dcdde1; }
</style>
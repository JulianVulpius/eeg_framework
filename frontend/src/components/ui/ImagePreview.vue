<template>
  <div class="image-box-container">
    <div v-if="assetDetails" class="preview-content-wrapper">
      
      <div class="category-wrapper" v-if="mediaCategories && mediaCategories.length > 0">
        <BaseSearchSelect
          v-model="selectedCategory"
          :options="mediaCategories"
          :placeholder="$t('views.events.select_media_category') || 'Kategorie'"
          :nullLabel="$t('master_data.none')"
          @update:modelValue="updateCategory"
        />
      </div>

      <div class="preview-container" v-if="assetDetails.file_exists">
        <img :src="assetUrl" alt="Preview" class="preview-img" />
        <button class="delete-overlay-btn" @click="handleDelete" :title="$t('actions.delete_image')">🗑️</button>
      </div>

      <div class="preview-container error-state" v-else>
        <div class="error-content">
          <span class="error-icon">⚠️</span>
          <span class="error-text">{{ $t('common.file_not_found') }}</span>
        </div>
        <button class="delete-overlay-btn" @click="handleDelete" :title="$t('actions.delete_image')">🗑️</button>
      </div>

    </div>
    
    <div v-else class="loading-container">
      <span class="spinner-text">{{ $t('common.loading') }}...</span>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useGlobalModal } from '@/composables/useGlobalModal'
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'

const props = defineProps({
  assetId: { type: [Number, String], required: true },
  mediaCategories: { type: Array, default: () => [] } 
})
const emit = defineEmits(['deleted'])

const { t } = useI18n()
const { showWarning, requireConfirmation } = useGlobalModal()

const assetDetails = ref(null)
const assetUrl = ref(null)
const selectedCategory = ref(null)

const loadAsset = async (id) => {
  if (!id) return
  try {
    const res = await api.get(`media/assets/${id}/`)
    assetDetails.value = res.data
    selectedCategory.value = res.data.category 
    
    let url = res.data.file
    if (url && url.startsWith('/')) {
       const baseUrl = (import.meta.env.VITE_API_URL)
       url = baseUrl + url
    }
    assetUrl.value = url
  } catch (err) {
    showWarning(t('common.error_loading') || 'Error loading preview', t('common.error'))
  }
}

const updateCategory = async (newVal) => {
  try {
    await api.patch(`media/assets/${props.assetId}/`, { category: newVal || null })
  } catch (err) {
    showWarning(t('common.error_saving') || 'Save failed', t('common.error'))
  }
}

const handleDelete = () => {
  requireConfirmation(async () => {
    try {
      await api.delete(`media/assets/${props.assetId}/`)
      emit('deleted') 
      assetDetails.value = null
      assetUrl.value = null
    } catch (err) {
      showWarning(t('common.error_saving') || 'Delete failed', t('common.error'))
    }
  })
}

onMounted(() => loadAsset(props.assetId))
watch(() => props.assetId, (newId) => loadAsset(newId))
</script>

<style scoped>
.image-box-container { width: 100%; height: 100%; min-height: 220px; border-radius: 8px; overflow: hidden; border: 1px solid #dcdde1; background: #fdfdfd; box-shadow: 0 2px 4px rgba(0,0,0,0.05); display: flex; flex-direction: column; padding: 15px; min-width: 0; }
.preview-content-wrapper { display: flex; flex-direction: column; gap: 15px; width: 100%; height: 100%; min-width: 0; }
.category-wrapper { width: 100%; min-width: 0; }
.preview-container { position: relative; flex: 1; display: flex; align-items: center; justify-content: center; background: #f1f2f6; border-radius: 6px; overflow: hidden; min-width: 0; }
.preview-img { max-width: 100%; max-height: 100%; object-fit: contain; }
.loading-container { display: flex; justify-content: center; align-items: center; height: 100%; color: #95a5a6; font-weight: 500; font-size: 0.9rem; }
.delete-overlay-btn { position: absolute; top: 8px; right: 8px; background: rgba(231, 76, 60, 0.9); color: white; border: none; border-radius: 4px; padding: 6px 10px; cursor: pointer; transition: all 0.2s; font-size: 1.1rem; z-index: 10; }
.delete-overlay-btn:hover { transform: scale(1.1); background: #c0392b; }
.error-state { background: #ffeaa7; border: 1px dashed #d63031; }
.error-content { display: flex; flex-direction: column; align-items: center; text-align: center; color: #d63031; padding: 10px; }
.error-icon { font-size: 2.5rem; margin-bottom: 5px; }
.error-text { font-size: 0.85rem; font-weight: 600; }
</style>
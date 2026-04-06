<template>
  <div class="image-box-container">
    <div v-if="assetUrl" class="preview-container">
      <img :src="assetUrl" alt="Preview" class="preview-img" />
      <button class="delete-overlay-btn" @click="handleDelete" :title="$t('actions.delete_image')">
        🗑️
      </button>
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

const props = defineProps({
  assetId: { type: [Number, String], required: true }
})
const emit = defineEmits(['deleted'])

const { t } = useI18n()
const { showWarning, requireConfirmation } = useGlobalModal()
const assetUrl = ref(null)

const loadAsset = async (id) => {
  if (!id) return
  try {
    const res = await api.get(`media/assets/${id}/`)
    let url = res.data.file
    
    if (url && url.startsWith('/')) {
       const baseUrl = (import.meta.env.VITE_API_URL)
       url = baseUrl + url
    }
    assetUrl.value = url
  } catch (err) {
    showWarning(t('common.error_loading'))
  }
}

const handleDelete = () => {
  requireConfirmation(async () => {
    try {
      await api.delete(`media/assets/${props.assetId}/`)
      emit('deleted') 
      assetUrl.value = null
    } catch (err) {
      showWarning(t('common.error_saving'))
    }
  })
}

onMounted(() => loadAsset(props.assetId))
watch(() => props.assetId, (newId) => loadAsset(newId))
</script>

<style scoped>
.image-box-container {
  width: 250px;
  height: 200px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #dcdde1;
  background: #fdfdfd;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  display: flex;
  align-items: center;
  justify-content: center;
}
.preview-container {
  position: relative;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f1f2f6;
}
.preview-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
.loading-container {
  color: #95a5a6;
  font-weight: 500;
  font-size: 0.9rem;
}
.delete-overlay-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  background: rgba(231, 76, 60, 0.9);
  color: white;
  border: none;
  border-radius: 4px;
  padding: 6px 10px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 1.1rem;
}
.delete-overlay-btn:hover {
  transform: scale(1.1);
  background: #c0392b;
}
</style>
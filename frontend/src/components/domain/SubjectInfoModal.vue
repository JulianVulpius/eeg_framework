<template>
  <BaseModal 
    :isOpen="isOpen" 
    :title="$t('modal.subject_infos', { name: subject?.identifier || '' })" 
    @close="closeModal"
    width="700px"
  >
    <div class="chat-layout">
      <button class="modal-close-x" @click="closeModal" title="Schließen">✕</button>

      <div class="filter-section">
        <SubjectInfoFilter 
          :categories="categories" 
          v-model="selectedCategoryIds" 
        />
      </div>

      <div class="chat-history">
        <div v-if="filteredInfos.length === 0" class="empty-state">
          {{ $t('common.no_entries') }}
        </div>

        <div 
          v-for="info in filteredInfos" 
          :key="info.id" 
          class="chat-bubble"
        >
          <div class="bubble-header">
            <span class="bubble-category">{{ getCategoryName(info.category) }}</span>
            <strong class="bubble-title">{{ info.title }}</strong>
          </div>
          <div class="bubble-body">
            {{ info.description }}
          </div>
          <div class="bubble-footer">
            {{ formatDate(info.created_at) }}
          </div>
        </div>
      </div>

      <form class="chat-input-area" @submit.prevent="submitInfo">
        <div class="input-row">
          <select v-model="formData.category" class="form-control category-select">
            <option :value="null">{{ $t('master_data.no_category') }}</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">
              {{ cat.name }}
            </option>
          </select>
          <input 
            type="text" 
            v-model="formData.title" 
            class="form-control title-input" 
            :placeholder="$t('master_data.title')" 
            required 
          />
        </div>
        
        <div class="input-row align-end">
          <textarea 
            v-model="formData.description" 
            class="form-control" 
            rows="2" 
            :placeholder="$t('master_data.description')" 
            required
          ></textarea>
          <button type="submit" class="btn-primary send-btn" :disabled="isSubmitting">
            {{ $t('actions.send') }}
          </button>
        </div>
        <BaseInputError v-if="crud.fieldErrors.value.non_field_errors" :message="crud.fieldErrors.value.non_field_errors" />
      </form>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useCrud } from '@/composables/useCrud'
import { useFormatters } from '@/composables/useFormatters' 

import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInputError from '@/components/ui/BaseInputError.vue'
import SubjectInfoFilter from '@/components/domain/SubjectInfoFilter.vue'

const props = defineProps({
  isOpen: { type: Boolean, required: true },
  subject: { type: Object, default: null }
})

const emit = defineEmits(['close'])
const { t } = useI18n()
const crud = useCrud()
const { formatDate } = useFormatters() 

const categories = ref([])
const infos = ref([])
const selectedCategoryIds = ref([])
const isSubmitting = ref(false)

const defaultForm = { category: null, title: '', description: '' }
const formData = ref({ ...defaultForm })

watch(() => props.isOpen, async (newVal) => {
  if (newVal && props.subject) {
    crud.clearErrors()
    selectedCategoryIds.value = []
    formData.value = { ...defaultForm }
    loadCategories()
    loadInfos()
  }
})

const loadCategories = async () => {
  try {
    const response = await api.get('subject-profile-info-categories/')
    categories.value = response.data
  } catch (error) {
    console.error("Categories failed to load", error)
  }
}

const loadInfos = async () => {
  try {
    const response = await api.get(`subject-profile-infos/?subject=${props.subject.id}`)
    infos.value = response.data
  } catch (error) {}
}

const filteredInfos = computed(() => {
  if (selectedCategoryIds.value.length === 0) return infos.value
  return infos.value.filter(info => selectedCategoryIds.value.includes(info.category))
})

const getCategoryName = (categoryId) => {
  if (!categoryId) return t('master_data.no_category')
  const cat = categories.value.find(c => c.id === categoryId)
  return cat ? cat.name : t('master_data.no_category')
}

const submitInfo = async () => {
  crud.clearErrors()
  isSubmitting.value = true
  try {
    await api.post('subject-profile-infos/', {
      subject: props.subject.id,
      ...formData.value
    })
    formData.value = { ...defaultForm }
    await loadInfos()
  } catch (error) {
    crud.handleFormError(error, t)
  } finally {
    isSubmitting.value = false
  }
}

const closeModal = () => {
  crud.clearErrors()
  emit('close')
}
</script>

<style scoped>
.chat-layout {
  display: flex;
  flex-direction: column;
  height: 60vh;
  position: relative; 
}

.modal-close-x {
  position: absolute;
  top: 0;
  right: 0;
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #888;
  z-index: 10;
  padding: 5px;
  line-height: 1;
}
.modal-close-x:hover { 
  color: #333; 
}

.filter-section {
  padding-right: 30px;
  margin-bottom: 15px;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  background-color: #f0f2f5;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.chat-bubble {
  background-color: #dcf8c6;
  border-radius: 8px;
  padding: 10px 12px;
  max-width: 90%;
  align-self: flex-start;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  word-wrap: break-word;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.bubble-header {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: baseline;
  margin-bottom: 4px;
}

.bubble-category {
  color: #075e54;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
}

.bubble-body {
  color: #303030;
  font-size: 0.9rem;
  line-height: 1.4;
  white-space: pre-wrap;
}

.bubble-footer {
  text-align: right;
  font-size: 0.7rem;
  color: #667781;
  margin-top: 5px;
}

.chat-input-area {
  background: white;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid #ddd;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-row { display: flex; gap: 8px; }
.align-end { align-items: flex-end; }
.category-select { width: 150px; }
.title-input { flex: 1; }
.send-btn { height: 38px; }

.empty-state {
  text-align: center;
  color: #888;
  margin: auto;
}
</style>
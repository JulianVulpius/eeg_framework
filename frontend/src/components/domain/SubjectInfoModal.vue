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

      <div class="chat-history" ref="chatContainer">
        <div v-if="filteredInfos.length === 0" class="empty-state">
          {{ $t('common.no_entries') }}
        </div>

        <div 
          v-for="info in filteredInfos" 
          :key="info.id" 
          class="chat-bubble"
          :class="{ 'is-deleting': deletingInfoId === info.id }"
        >
          <template v-if="deletingInfoId !== info.id">
            <button 
              class="delete-bubble-btn" 
              @click="deletingInfoId = info.id" 
              title="Löschen / Delete"
            >
              −
            </button>

            <div class="bubble-header">
              <span v-if="info.category" class="bubble-category">
                {{ getCategoryName(info.category) }}
              </span>
              <strong class="bubble-title">{{ info.title }}</strong>
            </div>
            <div class="bubble-body">
              {{ info.description }}
            </div>
            <div class="bubble-footer">
              {{ formatDate(info.created_at) }}
            </div>
          </template>

          <div v-else class="inline-confirm">
            <p>Eintrag wirklich löschen? / Really delete entry?</p>
            <div class="inline-confirm-actions">
              <button type="button" class="btn-cancel-sm" @click="deletingInfoId = null">✕ Abbrechen / Cancel</button>
              <button type="button" class="btn-delete-sm" @click="executeDelete(info.id)">✓ Löschen / Delete</button>
            </div>
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
import { ref, computed, watch, nextTick } from 'vue'
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

const deletingInfoId = ref(null)
const chatContainer = ref(null)

const defaultForm = { category: null, title: '', description: '' }
const formData = ref({ ...defaultForm })

const scrollToBottom = async () => {
  await nextTick() 
  if (chatContainer.value) {
    chatContainer.value.scrollTop = chatContainer.value.scrollHeight
  }
}

watch(() => props.isOpen, async (newVal) => {
  if (newVal && props.subject) {
    crud.clearErrors()
    selectedCategoryIds.value = []
    formData.value = { ...defaultForm }
    deletingInfoId.value = null
    await loadCategories()
    await loadInfos() 
    scrollToBottom()
  }
})

watch(selectedCategoryIds, () => scrollToBottom())

const loadCategories = async () => {
  try {
    const response = await api.get('category/subject-profile-info/')
    categories.value = response.data.results || response.data
  } catch (error) {
  }
}

const loadInfos = async () => {
  try {
    const response = await api.get(`subject-profile-infos/?subject=${props.subject.id}`)
    infos.value = response.data.results || response.data
  } catch (error) {
  }
}

const filteredInfos = computed(() => {
  let filtered = infos.value
  if (selectedCategoryIds.value.length > 0) {
    filtered = infos.value.filter(info => selectedCategoryIds.value.includes(info.category))
  }
  return [...filtered].sort((a, b) => new Date(a.created_at) - new Date(b.created_at))
})

const getCategoryName = (categoryId) => {
  if (!categoryId) return ''
  const cat = categories.value.find(c => c.id === categoryId)
  return cat ? cat.name : ''
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
    scrollToBottom()
  } catch (error) {
    crud.handleFormError(error, t)
  } finally {
    isSubmitting.value = false
  }
}

const executeDelete = async (infoId) => {
  try {
    await api.delete(`subject-profile-infos/${infoId}/`)
    deletingInfoId.value = null
    await loadInfos()
  } catch (error) {
    crud.handleFormError(error, t)
  }
}

const closeModal = () => {
  crud.clearErrors()
  deletingInfoId.value = null
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
  scroll-behavior: smooth;
}

.chat-bubble {
  background-color: #dcf8c6;
  border-radius: 8px;
  padding: 10px 12px;
  padding-right: 22px;
  position: relative; 
  max-width: 90%;
  align-self: flex-start;
  box-shadow: 0 1px 2px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
  word-wrap: break-word;
  overflow-wrap: anywhere;
  word-break: break-word;
  transition: background-color 0.3s;
}

.chat-bubble.is-deleting {
  background-color: #ffebee;
  border: 1px solid #ffcdd2;
}

.delete-bubble-btn {
  position: absolute;
  top: 4px;
  right: 4px;
  background: transparent;
  border: none;
  color: #555;
  font-size: 0.9rem;
  font-weight: bold;
  line-height: 1;
  cursor: pointer;
  opacity: 0.15;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  width: 16px;
  height: 16px;
  transition: opacity 0.2s, background-color 0.2s, color 0.2s;
}

.delete-bubble-btn:hover {
  opacity: 1;
  color: #d32f2f;
  background-color: rgba(211, 47, 47, 0.1); 
}

.inline-confirm {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 4px 0;
}
.inline-confirm p {
  margin: 0;
  font-size: 0.85rem;
  font-weight: 600;
  color: #c62828;
}
.inline-confirm-actions {
  display: flex;
  gap: 8px;
}
.btn-cancel-sm, .btn-delete-sm {
  border: none;
  border-radius: 4px;
  padding: 6px 10px;
  font-size: 0.75rem;
  cursor: pointer;
  font-weight: 600;
  transition: opacity 0.2s;
}
.btn-cancel-sm:hover, .btn-delete-sm:hover {
  opacity: 0.8;
}
.btn-cancel-sm {
  background: #e0e0e0;
  color: #333;
}
.btn-delete-sm {
  background: #c62828;
  color: white;
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
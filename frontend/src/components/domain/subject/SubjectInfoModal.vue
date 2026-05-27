<template>
  <BaseModal 
    :isOpen="isOpen" 
    :title="$t('modal.subject_infos', { name: subject?.identifier })" 
    @close="closeModal"
    customClass="large-modal"
  >
    <div class="chat-layout">
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
              :title="$t('actions.delete')"
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
            <p>{{ $t('actions.confirm_delete') }}</p>
            <div class="inline-confirm-actions">
              <button type="button" class="btn-cancel-sm" @click="deletingInfoId = null">
                ✕ {{ $t('actions.cancel') }}
              </button>
              <button type="button" class="btn-delete-sm" @click="executeDelete(info.id)">
                ✓ {{ $t('actions.delete') }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <form class="chat-input-area" @submit.prevent="submitInfo">
        <div class="input-row">
          <input 
            type="text" 
            v-model="formData.title" 
            class="form-control title-input" 
            :placeholder="$t('master_data.title')" 
            required 
          />
          <BaseSearchSelect 
            v-model="formData.category"
            :options="categories"
            :placeholder="$t('master_data.category')"
            :nullLabel="$t('master_data.no_category')"
            class="category-select"
          />
        </div>
        
        <div class="input-row">
          <textarea 
            v-model="formData.description" 
            class="form-control" 
            rows="2" 
            :placeholder="$t('master_data.description')" 
            required
          ></textarea>
        </div>

        <div class="input-row actions-row" style="justify-content: flex-end; gap: 10px; margin-top: 8px;">
          <button type="button" class="btn-secondary cancel-btn" @click="closeModal">
            {{ $t('actions.cancel') }}
          </button>
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
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'
import SubjectInfoFilter from '@/components/domain/subject/SubjectInfoFilter.vue'

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

const resetForm = () => {
  formData.value = { ...defaultForm }
  crud.clearErrors()
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
<template>
  <div class="category-manager">
    <CrudHeader 
      :title="$t('nav.stimuli')" 
      v-model="crud.showIdColumn.value" 
      @add="crud.openAddDialog(resetForm)" 
    />

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-if="crud.showIdColumn.value" class="id-column">{{ $t('common.id') }}</th>
            <th style="width: 20%;">
              <ColumnHeaderFilter :title="$t('common.name')" v-model="columnFilters.name" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 15%;">
              <ColumnHeaderFilter :title="$t('master_data.category')" v-model="columnFilters.category" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 15%;">
              <ColumnHeaderFilter :title="$t('views.stimulus.type')" v-model="columnFilters.type" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 20%;">
              <ColumnHeaderFilter :title="$t('views.stimulus.file')" v-model="columnFilters.file" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 15%;">
              <ColumnHeaderFilter :title="$t('common.creator')" v-model="columnFilters.creator" :placeholder="$t('common.search')" />
            </th>
            <th class="actions-column">{{ $t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredItems.length === 0">
            <td :colspan="crud.showIdColumn.value ? 7 : 6" class="empty-state">{{ $t('common.no_data') }}</td>
          </tr>
          <tr v-for="item in filteredItems" :key="item.id">
            <td v-if="crud.showIdColumn.value" class="id-column">{{ item.id }}</td>
            <td><strong>{{ item.name }}</strong></td>
            <td><span class="badge category-badge">{{ getCategoryName(item.category) }}</span></td>
            <td>{{ getTypeName(item.type) }}</td>
            <td>
              <span v-if="item.type === 'CUSTOM'" class="text-muted">-</span>
              <a v-else-if="item.file" :href="item.file" target="_blank" style="color: #3498db; text-decoration: none; font-size: 0.9rem;">
                {{ item.file.split('/').pop() }}
              </a>
              <span v-else class="text-muted">-</span>
            </td>
            <td>{{ item.creator || '-' }}</td>
            <TableActionButtons @edit="crud.openEditDialog(item.id, () => populateForm(item))" @delete="confirmAndDelete(item.id)" />
          </tr>
        </tbody>
      </table>
    </div>

    <StimulusDeleteWarningModal
      :isOpen="isWarningModalOpen"
      :affectedPlaylists="affectedPlaylistsForDelete"
      @cancel="isWarningModalOpen = false"
      @confirm="executeDelete(stimulusToDelete)"
    />

    <BaseModal :isOpen="crud.isDialogOpen.value" :title="crud.isEditing.value ? $t('modal.edit_record') : $t('modal.add_record')" @close="crud.closeDialog">
      <form @submit.prevent="saveRecord">
        
        <div class="form-group">
          <label>{{ $t('common.name') }} *</label>
          <input type="text" v-model="formData.name" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.name }" />
          <BaseInputError :message="crud.fieldErrors.value.name" />
        </div>

        <div class="form-group">
          <label>{{ $t('views.stimulus.type') }} *</label>
          <select v-model="formData.type" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.type }">
            <option value="" disabled>{{ $t('actions.select') }}</option>
            <option v-for="opt in typeOptions" :key="opt.id" :value="opt.id">{{ opt.name }}</option>
          </select>
          <BaseInputError :message="crud.fieldErrors.value.type" />
        </div>

        <BaseSearchSelect 
          v-model="formData.category"
          :options="categories"
          :label="$t('master_data.category')"
          :nullLabel="$t('master_data.none')"
          :error="crud.fieldErrors.value.category"
        />

        <template v-if="formData.type && formData.type !== 'CUSTOM'">
          
          <div class="form-group">
            <label>{{ $t('views.stimulus.file') }} *</label>
            <div style="display: flex; align-items: center; gap: 10px; padding: 10px; border: 1px dashed #bdc3c7; border-radius: 4px; background: #fdfdfd;" :class="{ 'input-invalid': crud.fieldErrors.value.file }">
              <input type="file" ref="fileInput" style="display: none;" @change="handleFileUpload" :accept="acceptedFileTypes" />
              
              <button type="button" class="btn-secondary" style="padding: 5px 15px; font-size: 0.85rem;" @click="$refs.fileInput.click()">
                {{ (selectedFile || formData.file) ? $t('views.stimulus.replace_file') : $t('views.stimulus.select_file') }}
              </button>
              
              <div style="font-size: 0.85rem; color: #2c3e50; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; max-width: 250px;">
                <strong v-if="selectedFile">{{ selectedFile.name }}</strong>
                <a v-else-if="formData.file" :href="formData.file" target="_blank" style="color: #3498db; text-decoration: none;">
                  {{ formData.file.split('/').pop() }}
                </a>
                <span v-else class="text-muted" style="font-style: italic;">{{ $t('views.stimulus.no_file') }}</span>
              </div>
            </div>
            <BaseInputError :message="crud.fieldErrors.value.file" />
          </div>

          <div class="form-group" style="margin-bottom: 15px;">
            <label>
              {{ $t('views.stimulus.duration') }} 
              <span v-if="formData.type === 'AUDIO' || formData.type === 'VIDEO'">*</span>
            </label>
            <input type="text" v-model="durationDisplay" @blur="parseAndFormatDuration" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.duration }" :placeholder="$t('views.stimulus.duration_placeholder')" />
            <BaseInputError :message="crud.fieldErrors.value.duration" />
            <small style="color: #7f8c8d; font-size: 0.8rem; display: block; margin-top: 5px;">
              {{ $t('views.stimulus.duration_info') }}
            </small>
          </div>

        </template>

        <div class="form-group" style="margin-bottom: 15px;">
          <label>{{ $t('common.description') }}</label>
          <textarea v-model="formData.description" class="form-control" rows="3" :placeholder="$t('modal.desc_placeholder')"></textarea>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-secondary" @click="crud.closeDialog">{{ $t('actions.cancel') }}</button>
          <button type="submit" class="btn-primary" :disabled="isUploading">
            {{ isUploading ? $t('common.saving') : $t('actions.save') }}
          </button>
        </div>
      </form>
    </BaseModal>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useCrud } from '@/composables/useCrud'
import { useGlobalModal } from '@/composables/useGlobalModal'

import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInputError from '@/components/ui/BaseInputError.vue'
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'
import CrudHeader from '@/components/ui/CrudHeader.vue'

import ColumnHeaderFilter from '@/components/table/ColumnHeaderFilter.vue'
import TableActionButtons from '@/components/table/TableActionButtons.vue'
import StimulusDeleteWarningModal from '@/components/domain/StimulusDeleteWarningModal.vue'

const { t } = useI18n()
const items = ref([])
const categories = ref([])
const crud = useCrud()
const { requireConfirmation } = useGlobalModal()

const fileInput = ref(null)
const selectedFile = ref(null)
const isUploading = ref(false)

const isWarningModalOpen = ref(false)
const affectedPlaylistsForDelete = ref([])
const stimulusToDelete = ref(null)

const typeOptions = computed(() => [
  { id: 'AUDIO', name: t('views.stimulus.type_audio') },
  { id: 'VIDEO', name: t('views.stimulus.type_video') },
  { id: 'IMAGE', name: t('views.stimulus.type_image') },
  { id: 'CUSTOM', name: t('views.stimulus.type_custom') }
])

const acceptedFileTypes = computed(() => {
  if (formData.value.type === 'AUDIO') return 'audio/*'
  if (formData.value.type === 'VIDEO') return 'video/*'
  if (formData.value.type === 'IMAGE') return 'image/*'
  return '*'
})

const columnFilters = ref({ name: '', type: '', category: '', file: '', creator: '' })

const getTypeName = (typeId) => {
  const tObj = typeOptions.value.find(o => o.id === typeId)
  return tObj ? tObj.name : typeId
}

const filteredItems = computed(() => {
  return items.value.filter(item => {
    if (columnFilters.value.name && !item.name.toLowerCase().includes(columnFilters.value.name.toLowerCase())) return false
    
    if (columnFilters.value.type) {
      const typeStr = getTypeName(item.type).toLowerCase()
      if (!typeStr.includes(columnFilters.value.type.toLowerCase())) return false
    }

    if (columnFilters.value.category) {
      const cName = getCategoryName(item.category).toLowerCase()
      if (!cName.includes(columnFilters.value.category.toLowerCase())) return false
    }

    if (columnFilters.value.file && (!item.file || !item.file.toLowerCase().includes(columnFilters.value.file.toLowerCase()))) return false
    
    if (columnFilters.value.creator) {
      const creatorName = item.creator ? item.creator.toLowerCase() : ''
      if (!creatorName.includes(columnFilters.value.creator.toLowerCase())) return false
    }
    return true
  })
})

const formData = ref({ name: '', type: '', category: null, file: null, duration: null, description: '' })
const durationDisplay = ref('')

const handleFileUpload = (event) => {
  const file = event.target.files[0]
  if (file) {
    selectedFile.value = file
    crud.fieldErrors.value.file = null

    if (formData.value.type === 'AUDIO' || formData.value.type === 'VIDEO') {
      extractDuration(file)
    }
  }
}

const extractDuration = (file) => {
  const fileUrl = URL.createObjectURL(file)
  const mediaElement = formData.value.type === 'VIDEO' ? document.createElement('video') : document.createElement('audio')
  
  mediaElement.preload = 'metadata'
  mediaElement.onloadedmetadata = () => {
    URL.revokeObjectURL(fileUrl)
    const durationInSeconds = Math.round(mediaElement.duration)
    if (!isNaN(durationInSeconds)) {
      formData.value.duration = durationInSeconds
      formatDurationDisplay(durationInSeconds)
    }
  }
  mediaElement.src = fileUrl
}

const formatDurationDisplay = (totalSeconds) => {
  const h = Math.floor(totalSeconds / 3600).toString().padStart(2, '0')
  const m = Math.floor((totalSeconds % 3600) / 60).toString().padStart(2, '0')
  const s = (totalSeconds % 60).toString().padStart(2, '0')
  durationDisplay.value = `${h}:${m}:${s}`
}

const parseAndFormatDuration = () => {
  let str = durationDisplay.value.replace(/[^0-9:]/g, '').trim()
  if (!str) {
    durationDisplay.value = ''
    formData.value.duration = null
    return
  }

  const parts = str.split(':').map(num => parseInt(num) || 0)
  let totalSeconds = 0

  if (parts.length === 1) {
    totalSeconds = parts[0]
  } else if (parts.length === 2) {
    totalSeconds = (parts[0] * 60) + parts[1]
  } else if (parts.length >= 3) {
    totalSeconds = (parts[0] * 3600) + (parts[1] * 60) + parts[2]
  }

  formatDurationDisplay(totalSeconds)
  formData.value.duration = totalSeconds
}

watch(() => formData.value.duration, (newVal) => {
  if (newVal === null || newVal === undefined || newVal === '') {
    durationDisplay.value = ''
    return
  }
  const totalSeconds = parseInt(newVal) || 0
  formatDurationDisplay(totalSeconds)
}, { immediate: true })

watch(() => formData.value.type, () => {
  crud.clearErrors()
})

const resetForm = () => { 
  formData.value = { name: '', type: '', category: null, file: null, duration: null, description: '' } 
  durationDisplay.value = ''
  selectedFile.value = null
  if (fileInput.value) fileInput.value.value = ''
}

const populateForm = (item) => { 
  formData.value = { ...item } 
  if (!formData.value.type) formData.value.type = 'AUDIO'
  selectedFile.value = null
  if (fileInput.value) fileInput.value.value = ''
}

const loadData = async () => {
  try {
    const [resItems, resCats] = await Promise.all([
      api.get('stimuli/'),
      api.get('category/stimulus/')
    ])
    items.value = resItems.data
    categories.value = resCats.data
  } catch (error) {}
}

const getCategoryName = (id) => {
  const cat = categories.value.find(c => c.id === id)
  return cat ? cat.name : '-'
}

const saveRecord = async () => {
  crud.clearErrors()
  let hasErrors = false

  if (!formData.value.name || formData.value.name.trim() === '') { crud.fieldErrors.value.name = t('errors.required_field'); hasErrors = true }
  if (!formData.value.type) { crud.fieldErrors.value.type = t('errors.required_field'); hasErrors = true }

  if (formData.value.type && formData.value.type !== 'CUSTOM') {
    if (!selectedFile.value && (!formData.value.file || typeof formData.value.file !== 'string')) { 
      crud.fieldErrors.value.file = t('errors.required_field'); 
      hasErrors = true 
    }
    if (formData.value.type === 'AUDIO' || formData.value.type === 'VIDEO') {
      if (formData.value.duration === null || formData.value.duration === '') { 
        crud.fieldErrors.value.duration = t('errors.required_field'); 
        hasErrors = true 
      }
    }
  }

  if (hasErrors) return
  isUploading.value = true

  const payload = new FormData()
  payload.append('name', formData.value.name)
  payload.append('type', formData.value.type)
  if (formData.value.category) payload.append('category', formData.value.category)
  if (formData.value.description) payload.append('description', formData.value.description)

  if (formData.value.type !== 'CUSTOM') {
    if (formData.value.duration !== null) payload.append('duration', formData.value.duration)
    if (selectedFile.value) payload.append('file', selectedFile.value)
  } else {
    payload.append('duration', '') 
  }

  try {
    const config = { headers: { 'Content-Type': 'multipart/form-data' } }
    if (crud.isEditing.value) {
      await api.patch(`stimuli/${crud.editingId.value}/`, payload, config)
    } else {
      await api.post('stimuli/', payload, config)
    }
    crud.closeDialog()
    loadData()
  } catch (error) {
    crud.handleFormError(error, t)
  } finally {
    isUploading.value = false
  }
}

const confirmAndDelete = (id) => {
  requireConfirmation(async () => {
    try {
      const res = await api.get('playlists/')
      const playlists = res.data
      
      const affected = playlists.filter(p => p.stimuli && p.stimuli.includes(id))

      if (affected.length > 0) {
        affectedPlaylistsForDelete.value = affected
        stimulusToDelete.value = id
        isWarningModalOpen.value = true
      } else {
        executeDelete(id)
      }
    } catch (error) {
      console.error("Fehler beim Prüfen der Playlisten", error)
      executeDelete(id)
    }
  })
}

const executeDelete = async (id) => {
  try {
    await api.delete(`stimuli/${id}/`)
    isWarningModalOpen.value = false
    loadData()
  } catch (error) {
    console.error("Löschen fehlgeschlagen", error)
  }
}

onMounted(loadData)
</script>
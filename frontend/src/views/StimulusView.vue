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
            <th style="width: 20%;">
              <ColumnHeaderFilter :title="$t('master_data.category')" v-model="columnFilters.category" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 25%;">
              <ColumnHeaderFilter :title="$t('views.stimulus.source')" v-model="columnFilters.source" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 20%;">
              <ColumnHeaderFilter :title="$t('common.creator')" v-model="columnFilters.creator" :placeholder="$t('common.search')" />
            </th>
            <th class="actions-column">{{ $t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredItems.length === 0">
            <td :colspan="crud.showIdColumn.value ? 6 : 5" class="empty-state">{{ $t('common.no_data') }}</td>
          </tr>
          <tr v-for="item in filteredItems" :key="item.id">
            <td v-if="crud.showIdColumn.value" class="id-column">{{ item.id }}</td>
            <td><strong>{{ item.name }}</strong></td>
            <td><span class="badge category-badge">{{ getCategoryName(item.category) }}</span></td>
            <td>{{ item.source }}</td>
            <td>{{ item.creator || '-' }}</td>
            <TableActionButtons @edit="crud.openEditDialog(item.id, () => populateForm(item))" @delete="crud.requestDelete(item.id)" />
          </tr>
        </tbody>
      </table>
    </div>

    <BaseModal :isOpen="crud.isDialogOpen.value" :title="crud.isEditing.value ? $t('modal.edit_record') : $t('modal.add_record')" @close="crud.closeDialog">
      <form @submit.prevent="saveRecord">
        <div class="form-group">
          <label>{{ $t('common.name') }} *</label>
          <input type="text" v-model="formData.name" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.name }" />
          <BaseInputError :message="crud.fieldErrors.value.name" />
        </div>

        <BaseSearchSelect 
          v-model="formData.category"
          :options="categories"
          :label="$t('master_data.category') + ' *'"
          :error="crud.fieldErrors.value.category"
        />

        <div class="form-group">
          <label>{{ $t('views.stimulus.source') }} *</label>
          <div class="input-with-prefix" :class="{ 'input-invalid-wrapper': crud.fieldErrors.value.source }">
            <span class="path-prefix">/stimuli/</span>
            <input type="text" v-model="formData.source" :placeholder="$t('views.stimulus.source_placeholder')" class="filename-input" />
          </div>
          <BaseInputError :message="crud.fieldErrors.value.source" />
          <small class="help-text" v-html="$t('views.stimulus.source_help')"></small>
        </div>

        <div class="form-group" style="margin-bottom: 15px;">
          <label>{{ $t('views.stimulus.duration') }} *</label>
          <input type="text" v-model="durationDisplay" @blur="parseAndFormatDuration" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.duration }" :placeholder="$t('views.stimulus.duration_placeholder')" />
          <BaseInputError :message="crud.fieldErrors.value.duration" />
          <small style="color: #7f8c8d; font-size: 0.8rem; display: block; margin-top: 5px;">
            {{ $t('views.stimulus.duration_info') }}
          </small>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-secondary" @click="crud.closeDialog">{{ $t('actions.cancel') }}</button>
          <button type="submit" class="btn-primary">{{ $t('actions.save') }}</button>
        </div>
      </form>
    </BaseModal>

    <ConfirmDeleteModal :isOpen="crud.isConfirmOpen.value" @cancel="crud.cancelDelete" @confirm="executeDelete" />
    <WarningModal :isOpen="showWarningModal" :title="$t('common.warning')" :message="warningMessage" @close="showWarningModal = false" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useCrud } from '@/composables/useCrud'

import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInputError from '@/components/ui/BaseInputError.vue'
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'
import ConfirmDeleteModal from '@/components/ui/ConfirmDeleteModal.vue'
import WarningModal from '@/components/ui/WarningModal.vue'
import CrudHeader from '@/components/ui/CrudHeader.vue'

import ColumnHeaderFilter from '@/components/table/ColumnHeaderFilter.vue'
import TableActionButtons from '@/components/table/TableActionButtons.vue'

const { t } = useI18n()
const items = ref([])
const categories = ref([])
const crud = useCrud()

const showWarningModal = ref(false)
const warningMessage = ref('')

const columnFilters = ref({ name: '', category: '', source: '', creator: '' })

const filteredItems = computed(() => {
  return items.value.filter(item => {
    if (columnFilters.value.name && !item.name.toLowerCase().includes(columnFilters.value.name.toLowerCase())) return false
    if (columnFilters.value.category) {
      const cName = getCategoryName(item.category).toLowerCase()
      if (!cName.includes(columnFilters.value.category.toLowerCase())) return false
    }
    if (columnFilters.value.source && (!item.source || !item.source.toLowerCase().includes(columnFilters.value.source.toLowerCase()))) return false
    if (columnFilters.value.creator) {
      const creatorName = item.creator ? item.creator.toLowerCase() : ''
      if (!creatorName.includes(columnFilters.value.creator.toLowerCase())) return false
    }
    return true
  })
})

const formData = ref({ name: '', category: null, source: '', duration: null })
const durationDisplay = ref('')

// smart duration parsing logic
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

  const h = Math.floor(totalSeconds / 3600).toString().padStart(2, '0')
  const m = Math.floor((totalSeconds % 3600) / 60).toString().padStart(2, '0')
  const s = (totalSeconds % 60).toString().padStart(2, '0')

  durationDisplay.value = `${h}:${m}:${s}`
  formData.value.duration = totalSeconds
}

watch(() => formData.value.duration, (newVal) => {
  if (newVal === null || newVal === undefined || newVal === '') {
    durationDisplay.value = ''
    return
  }
  const totalSeconds = parseInt(newVal) || 0
  const h = Math.floor(totalSeconds / 3600).toString().padStart(2, '0')
  const m = Math.floor((totalSeconds % 3600) / 60).toString().padStart(2, '0')
  const s = (totalSeconds % 60).toString().padStart(2, '0')
  durationDisplay.value = `${h}:${m}:${s}`
}, { immediate: true })

const resetForm = () => { 
  formData.value = { name: '', category: null, source: '', duration: null } 
  durationDisplay.value = ''
}

const populateForm = (item) => { formData.value = { ...item } }

const loadData = async () => {
  try {
    const [resItems, resCats] = await Promise.all([
      api.get('stimuli/'),
      api.get('category/stimulus-categories/')
    ])
    items.value = resItems.data
    categories.value = resCats.data
  } catch (error) { 
    warningMessage.value = crud.parseApiError(error, t, 'errors.load_failed')
    showWarningModal.value = true
  }
}

const getCategoryName = (id) => {
  const cat = categories.value.find(c => c.id === id)
  return cat ? cat.name : '-'
}

const saveRecord = async () => {
  crud.clearErrors()

  let hasErrors = false
  if (!formData.value.name || formData.value.name.trim() === '') { crud.fieldErrors.value.name = t('errors.required_field'); hasErrors = true }
  if (!formData.value.category) { crud.fieldErrors.value.category = t('errors.required_field'); hasErrors = true }
  if (!formData.value.source || formData.value.source.trim() === '') { crud.fieldErrors.value.source = t('errors.required_field'); hasErrors = true }
  if (formData.value.duration === null || formData.value.duration === '') { crud.fieldErrors.value.duration = t('errors.required_field'); hasErrors = true }

  if (hasErrors) return

  try {
    if (crud.isEditing.value) {
      await api.put(`stimuli/${crud.editingId.value}/`, formData.value)
      crud.notifySuccess('updated', t)
    } else {
      await api.post('stimuli/', formData.value)
      crud.notifySuccess('created', t)
    }
    crud.closeDialog()
    loadData()
  } catch (error) {
    crud.handleFormError(error, t, 'errors.save_failed')
  }
}

const executeDelete = async () => {
  try {
    await api.delete(`stimuli/${crud.itemToDelete.value}/`)
    crud.notifySuccess('deleted', t)
    crud.cancelDelete()
    loadData()
  } catch (error) { 
    crud.cancelDelete()
    warningMessage.value = crud.parseApiError(error, t, 'errors.delete_failed')
    showWarningModal.value = true
  }
}

onMounted(loadData)
</script>
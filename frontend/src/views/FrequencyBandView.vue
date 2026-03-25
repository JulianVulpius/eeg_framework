<template>
  <div class="category-manager">
    <CrudHeader 
      :title="$t('nav.frequency_bands')" 
      v-model="crud.showIdColumn.value" 
      @add="crud.openAddDialog(resetForm)" 
    />

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-if="crud.showIdColumn.value" class="id-column">{{ $t('common.id') }}</th>
            <th style="width: 25%;">
              <ColumnHeaderFilter 
                :title="$t('common.name')" 
                v-model="columnFilters.name" 
                :placeholder="$t('common.search')" 
              />
            </th>
            
            <th style="width: 20%;">
              <ColumnHeaderRangeFilter 
                :title="$t('master_data.low_hz')" 
                v-model="columnFilters.hzRange" 
                :filterTitle="$t('master_data.low_hz') + ' - ' + $t('master_data.high_hz')"
              />
            </th>
            <th style="width: 20%;">
              <ColumnHeaderRangeFilter 
                :title="$t('master_data.high_hz')" 
                v-model="columnFilters.hzRange" 
                :filterTitle="$t('master_data.low_hz') + ' - ' + $t('master_data.high_hz')"
              />
            </th>
            
            <th style="width: 25%;">
              <ColumnHeaderFilter 
                :title="$t('common.description')" 
                v-model="columnFilters.description" 
                :placeholder="$t('common.search')" 
              />
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
            <td><span class="badge secondary-badge">{{ item.low_hz }}</span></td>
            <td><span class="badge secondary-badge">{{ item.high_hz }}</span></td>
            <td>{{ item.description || '-' }}</td>
            <TableActionButtons 
              @edit="crud.openEditDialog(item.id, () => populateForm(item))"
              @delete="crud.requestDelete(item.id)"
            />
          </tr>
        </tbody>
      </table>
    </div>

    <BaseModal 
      :isOpen="crud.isDialogOpen.value" 
      :title="crud.isEditing.value ? $t('modal.edit_record') : $t('modal.add_record')"
      :errorMessage="crud.errorMessage.value"
      @close="crud.closeDialog"
    >
      <form @submit.prevent="saveRecord">
        <div class="form-group">
          <label>{{ $t('common.name') }} *</label>
          <input 
            type="text" 
            v-model="formData.name" 
            class="form-control"
            :class="{ 'input-invalid': crud.fieldErrors.value.name }"
          />
          <BaseInputError :message="crud.fieldErrors.value.name" />
        </div>
        <div class="form-group" style="display: flex; gap: 10px;">
          <div style="flex: 1;">
            <label>{{ $t('master_data.low_hz') }} *</label>
            <input 
              type="number" 
              step="0.1" 
              min="0"
              v-model.number="formData.low_hz" 
              class="form-control"
              :class="{ 'input-invalid': crud.fieldErrors.value.low_hz }"
            />
            <BaseInputError :message="crud.fieldErrors.value.low_hz" />
          </div>
          <div style="flex: 1;">
            <label>{{ $t('master_data.high_hz') }} *</label>
            <input 
              type="number" 
              step="0.1" 
              min="0"
              v-model.number="formData.high_hz" 
              class="form-control"
              :class="{ 'input-invalid': crud.fieldErrors.value.high_hz }"
            />
            <BaseInputError :message="crud.fieldErrors.value.high_hz" />
          </div>
        </div>
        <div class="form-group">
          <label>{{ $t('common.description') }}</label>
          <textarea 
            v-model="formData.description" 
            rows="4"
            class="form-control"
            :class="{ 'input-invalid': crud.fieldErrors.value.description }"
          ></textarea>
          <BaseInputError :message="crud.fieldErrors.value.description" />
        </div>
        <div class="modal-actions">
          <button type="button" class="btn-secondary" @click="crud.closeDialog">{{ $t('actions.cancel') }}</button>
          <button type="submit" class="btn-primary">{{ $t('actions.save') }}</button>
        </div>
      </form>
    </BaseModal>

    <ConfirmDeleteModal 
      :isOpen="crud.isConfirmOpen.value" 
      @cancel="crud.cancelDelete" 
      @confirm="executeDelete" 
    />

    <WarningModal 
      :isOpen="showWarningModal" 
      :title="$t('common.warning')" 
      :message="warningMessage" 
      @close="showWarningModal = false" 
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useCrud } from '@/composables/useCrud'

import BaseModal from '@/components/BaseModal.vue'
import BaseInputError from '@/components/BaseInputError.vue'
import ConfirmDeleteModal from '@/components/ConfirmDeleteModal.vue'
import WarningModal from '@/components/WarningModal.vue'
import ColumnHeaderFilter from '@/components/ColumnHeaderFilter.vue'
import ColumnHeaderRangeFilter from '@/components/ColumnHeaderRangeFilter.vue' // new import
import CrudHeader from '@/components/CrudHeader.vue'
import TableActionButtons from '@/components/TableActionButtons.vue'

const { t } = useI18n()
const items = ref([])
const crud = useCrud()

const showWarningModal = ref(false)
const warningMessage = ref('')

const columnFilters = ref({
  name: '',
  description: '',
  hzRange: { min: null, max: null } 
})

const filteredItems = computed(() => {
  return items.value.filter(item => {
    
    if (columnFilters.value.name) {
      const q = columnFilters.value.name.toLowerCase()
      if (!item.name.toLowerCase().includes(q)) return false
    }
    
    if (columnFilters.value.description) {
      const q = columnFilters.value.description.toLowerCase()
      if (!item.description || !item.description.toLowerCase().includes(q)) return false
    }

    const minFilter = columnFilters.value.hzRange.min
    const maxFilter = columnFilters.value.hzRange.max

    if (minFilter !== null && item.low_hz < minFilter) {
      return false
    }
    if (maxFilter !== null && item.high_hz > maxFilter) {
      return false
    }

    return true
  })
})

const formData = ref({ name: '', description: '', low_hz: 0, high_hz: 0 })

const resetForm = () => { 
  formData.value = { name: '', description: '', low_hz: 0, high_hz: 0 } 
}

const populateForm = (item) => { 
  formData.value = { ...item } 
}

const loadData = async () => {
  try {
    const response = await api.get('frequency-bands/')
    items.value = response.data
  } catch (error) { 
    warningMessage.value = crud.parseApiError(error, t, 'errors.load_failed')
    showWarningModal.value = true
  }
}

const saveRecord = async () => {
  crud.clearErrors()

  let hasErrors = false

  if (!formData.value.name || formData.value.name.trim() === '') {
    crud.fieldErrors.value.name = t('errors.required_field')
    hasErrors = true
  }
  
  if (formData.value.low_hz === null || formData.value.low_hz === '') {
    crud.fieldErrors.value.low_hz = t('errors.required_field')
    hasErrors = true
  }

  if (formData.value.high_hz === null || formData.value.high_hz === '') {
    crud.fieldErrors.value.high_hz = t('errors.required_field')
    hasErrors = true
  }

  if (hasErrors) return

  try {
    if (crud.isEditing.value) await api.put(`frequency-bands/${crud.editingId.value}/`, formData.value)
    else await api.post('frequency-bands/', formData.value)
    crud.closeDialog()
    loadData()
  } catch (error) {
    crud.handleFormError(error, t, 'errors.save_failed')
  }
}

const executeDelete = async () => {
  try {
    await api.delete(`frequency-bands/${crud.itemToDelete.value}/`)
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

<style scoped>
/* allow the absolute positioned dropdown to overflow the table */
.table-container {
  overflow: visible !important;
}
</style>
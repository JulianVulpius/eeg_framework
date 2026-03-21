<template>
  <div class="category-manager">
    <CrudHeader 
      :title="$t('nav.trigger_definitions')" 
      v-model="crud.showIdColumn.value" 
      @add="crud.openAddDialog(resetForm)" 
    />

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-if="crud.showIdColumn.value" class="id-column">{{ $t('common.id') }}</th>
            <th style="width: 45%;">
              <ColumnHeaderFilter 
                :title="$t('common.name')" 
                v-model="columnFilters.name" 
                :placeholder="$t('common.search')" 
              />
            </th>
            <th style="width: 45%;">
              <ColumnHeaderFilter 
                :title="$t('views.triggers.trigger_character')" 
                v-model="columnFilters.trigger_character" 
                :placeholder="$t('common.search')" 
              />
            </th>
            <th class="actions-column">{{ $t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredItems.length === 0">
            <td :colspan="crud.showIdColumn.value ? 4 : 3" class="empty-state">{{ $t('common.no_data') }}</td>
          </tr>
          <tr v-for="item in filteredItems" :key="item.id">
            <td v-if="crud.showIdColumn.value" class="id-column">{{ item.id }}</td>
            <td><strong>{{ item.name }}</strong></td>
            <td><code>{{ item.trigger_character }}</code></td>
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
            :placeholder="$t('modal.name_placeholder')" 
          />
          <BaseInputError :message="crud.fieldErrors.value.name" />
        </div>
        <div class="form-group">
          <label>{{ $t('views.triggers.trigger_character') }} *</label>
          <input 
            type="text" 
            v-model="formData.trigger_character" 
            class="form-control"
            :class="{ 'input-invalid': crud.fieldErrors.value.trigger_character }"
            placeholder="e.g., 255, S1, Space" 
          />
          <BaseInputError :message="crud.fieldErrors.value.trigger_character" />
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
import CrudHeader from '@/components/CrudHeader.vue'
import TableActionButtons from '@/components/TableActionButtons.vue'

const { t } = useI18n()
const items = ref([])
const crud = useCrud()

const showWarningModal = ref(false)
const warningMessage = ref('')

const columnFilters = ref({
  name: '',
  trigger_character: ''
})

const filteredItems = computed(() => {
  return items.value.filter(item => {
    if (columnFilters.value.name) {
      const q = columnFilters.value.name.toLowerCase()
      if (!item.name.toLowerCase().includes(q)) return false
    }
    if (columnFilters.value.trigger_character) {
      const q = columnFilters.value.trigger_character.toLowerCase()
      if (!item.trigger_character || !item.trigger_character.toLowerCase().includes(q)) return false
    }
    return true
  })
})

const formData = ref({ name: '', trigger_character: '' })

const resetForm = () => { 
  formData.value = { name: '', trigger_character: '' } 
}

const populateForm = (item) => { 
  formData.value = { name: item.name, trigger_character: item.trigger_character } 
}

const loadData = async () => {
  try {
    const response = await api.get('triggers/definitions/')
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
  if (!formData.value.trigger_character || formData.value.trigger_character.trim() === '') {
    crud.fieldErrors.value.trigger_character = t('errors.required_field')
    hasErrors = true
  }

  if (hasErrors) return

  try {
    if (crud.isEditing.value) await api.put(`triggers/definitions/${crud.editingId.value}/`, formData.value)
    else await api.post('triggers/definitions/', formData.value)
    crud.closeDialog()
    loadData()
  } catch (error) {
    crud.handleFormError(error, t, 'errors.save_failed')
  }
}

const executeDelete = async () => {
  try {
    await api.delete(`triggers/definitions/${crud.itemToDelete.value}/`)
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
code { 
  background-color: #f1f3f5; 
  padding: 2px 6px; 
  border-radius: 4px; 
  font-family: monospace; 
}
</style>
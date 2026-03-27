<template>
  <div class="category-manager">
    <CrudHeader 
      :title="$t('common.managing', { table: translatedTitle })" 
      v-model="crud.showIdColumn.value" 
      @add="crud.openAddDialog(resetForm)" 
    />

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-if="crud.showIdColumn.value" class="id-column">{{ $t('common.id') }}</th>
            <th style="width: 40%;">
              <ColumnHeaderFilter :title="$t('common.name')" v-model="columnFilters.name" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 40%;">
              <ColumnHeaderFilter :title="$t('common.description')" v-model="columnFilters.description" :placeholder="$t('common.search')" />
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
            <td>{{ item.description }}</td>
            <TableActionButtons @edit="crud.openEditDialog(item.id, () => populateForm(item))" @delete="crud.requestDelete(item.id)" />
          </tr>
        </tbody>
      </table>
    </div>

    <BaseModal :isOpen="crud.isDialogOpen.value" :title="crud.isEditing.value ? $t('modal.edit_record') : $t('modal.add_record')" @close="crud.closeDialog">
      <form @submit.prevent="saveRecord">
        <div class="form-group">
          <label>{{ $t('common.name') }} *</label>
          <input type="text" v-model="formData.name" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.name }" :placeholder="$t('modal.name_placeholder')" />
          <BaseInputError :message="crud.fieldErrors.value.name" />
        </div>
        <div class="form-group">
          <label>{{ $t('common.description') }}</label>
          <textarea v-model="formData.description" rows="4" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.description }" :placeholder="$t('modal.desc_placeholder')"></textarea>
          <BaseInputError :message="crud.fieldErrors.value.description" />
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
import { ref, watch, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useCrud } from '@/composables/useCrud'

import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInputError from '@/components/ui/BaseInputError.vue'
import ConfirmDeleteModal from '@/components/ui/ConfirmDeleteModal.vue'
import WarningModal from '@/components/ui/WarningModal.vue'
import CrudHeader from '@/components/ui/CrudHeader.vue'

import ColumnHeaderFilter from '@/components/table/ColumnHeaderFilter.vue'
import TableActionButtons from '@/components/table/TableActionButtons.vue'

const { t } = useI18n()
const props = defineProps({ tableName: { type: String, required: true } })

const items = ref([])
const crud = useCrud()

const showWarningModal = ref(false)
const warningMessage = ref('')

const columnFilters = ref({ name: '', description: '' })

const filteredItems = computed(() => {
  return items.value.filter(item => {
    if (columnFilters.value.name && !item.name.toLowerCase().includes(columnFilters.value.name.toLowerCase())) return false
    if (columnFilters.value.description && (!item.description || !item.description.toLowerCase().includes(columnFilters.value.description.toLowerCase()))) return false
    return true
  })
})

const translatedTitle = computed(() => t(`nav.${props.tableName.replace(/-/g, '_')}`))
const formData = ref({ name: '', description: '' })

const resetForm = () => { formData.value = { name: '', description: '' } }
const populateForm = (item) => { formData.value = { name: item.name, description: item.description } }

const loadData = async () => {
  try {
    const response = await api.get(`category/${props.tableName}/`)
    items.value = response.data
  } catch (error) { 
    warningMessage.value = crud.parseApiError(error, t, 'errors.load_failed')
    showWarningModal.value = true
  }
}

const saveRecord = async () => {
  crud.clearErrors()
  if (!formData.value.name || formData.value.name.trim() === '') {
    crud.fieldErrors.value.name = t('errors.required_field')
    return
  }

  try {
    if (crud.isEditing.value) {
      await api.put(`category/${props.tableName}/${crud.editingId.value}/`, formData.value)
      crud.notifySuccess('updated', t) // <-- NEUER TOAST
    } else {
      await api.post(`category/${props.tableName}/`, formData.value)
      crud.notifySuccess('created', t) // <-- NEUER TOAST
    }
    crud.closeDialog()
    loadData()
  } catch (error) { 
    crud.handleFormError(error, t, 'errors.save_failed')
  }
}

const executeDelete = async () => {
  try {
    await api.delete(`category/${props.tableName}/${crud.itemToDelete.value}/`)
    crud.notifySuccess('deleted', t) // <-- NEUER TOAST
    crud.cancelDelete()
    loadData()
  } catch (error) { 
    crud.cancelDelete()
    warningMessage.value = crud.parseApiError(error, t, 'errors.delete_failed')
    showWarningModal.value = true
  }
}

onMounted(loadData)
watch(() => props.tableName, loadData)
</script>
<template>
  <div class="category-manager">
    <CrudHeader :title="$t('nav.subjects')" v-model="crud.showIdColumn.value" @add="crud.openAddDialog(resetForm)" />

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-if="crud.showIdColumn.value" class="id-column">{{ $t('common.id') }}</th>
            <th style="width: 20%;"><ColumnHeaderFilter :title="$t('master_data.identifier')" v-model="columnFilters.identifier" :placeholder="$t('common.search')" /></th>
            <th style="width: 25%;"><ColumnHeaderFilter :title="$t('master_data.lastname')" v-model="columnFilters.lastname" :placeholder="$t('common.search')" /></th>
            <th style="width: 25%;"><ColumnHeaderFilter :title="$t('master_data.firstname')" v-model="columnFilters.firstname" :placeholder="$t('common.search')" /></th>
            <th>{{ $t('master_data.birthday') }}</th>
            <th>{{ $t('master_data.gender') }}</th>
            <th class="actions-column">{{ $t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredItems.length === 0"><td :colspan="crud.showIdColumn.value ? 7 : 6" class="empty-state">{{ $t('common.no_data') }}</td></tr>
          <tr v-for="item in filteredItems" :key="item.id">
            <td v-if="crud.showIdColumn.value" class="id-column">{{ item.id }}</td>
            <td><strong>{{ item.identifier }}</strong></td>
            <td>{{ item.lastname }}</td>
            <td>{{ item.firstname }}</td>
            <td>{{ formatDate(item.birthday) }}</td>
            <td>{{ getGenderLabel(item.gender) }}</td>
            <TableActionButtons @edit="crud.openEditDialog(item.id, () => populateForm(item))" @delete="crud.requestDelete(item.id)" />
          </tr>
        </tbody>
      </table>
    </div>

    <BaseModal :isOpen="crud.isDialogOpen.value" :title="crud.isEditing.value ? $t('modal.edit_record') : $t('modal.add_record')" :errorMessage="crud.errorMessage.value" @close="crud.closeDialog">
      <form @submit.prevent="saveRecord">
        <div class="form-group">
          <label>{{ $t('master_data.identifier') }} *</label>
          <input type="text" v-model="formData.identifier" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.identifier }" />
          <BaseInputError :message="crud.fieldErrors.value.identifier" />
        </div>
        
        <div class="form-group" style="display: flex; gap: 10px;">
          <div style="flex: 1;">
            <label>{{ $t('master_data.firstname') }}</label>
            <input type="text" v-model="formData.firstname" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.firstname }" />
            <BaseInputError :message="crud.fieldErrors.value.firstname" />
          </div>
          <div style="flex: 1;">
            <label>{{ $t('master_data.lastname') }}</label>
            <input type="text" v-model="formData.lastname" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.lastname }" />
            <BaseInputError :message="crud.fieldErrors.value.lastname" />
          </div>
        </div>

        <div class="form-group">
          <label>{{ $t('master_data.birthday') }}</label>
          <input type="date" v-model="formData.birthday" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.birthday }" />
          <BaseInputError :message="crud.fieldErrors.value.birthday" />
        </div>

        <div class="form-group">
          <label>{{ $t('master_data.gender') }}</label>
          <select v-model="formData.gender" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.gender }">
            <option :value="null">{{ $t('master_data.none') }}</option>
            <option value="M">{{ $t('master_data.gender_male') }}</option>
            <option value="F">{{ $t('master_data.gender_female') }}</option>
            <option value="O">{{ $t('master_data.gender_other') }}</option>
          </select>
          <BaseInputError :message="crud.fieldErrors.value.gender" />
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
import { ref, computed, onMounted } from 'vue'
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
const items = ref([])
const crud = useCrud()

const showWarningModal = ref(false)
const warningMessage = ref('')

const columnFilters = ref({ identifier: '', firstname: '', lastname: '' })

const filteredItems = computed(() => {
  return items.value.filter(item => {
    if (columnFilters.value.identifier && !item.identifier.toLowerCase().includes(columnFilters.value.identifier.toLowerCase())) return false
    if (columnFilters.value.firstname && (!item.firstname || !item.firstname.toLowerCase().includes(columnFilters.value.firstname.toLowerCase()))) return false
    if (columnFilters.value.lastname && (!item.lastname || !item.lastname.toLowerCase().includes(columnFilters.value.lastname.toLowerCase()))) return false
    return true
  })
})

const formData = ref({ identifier: '', firstname: '', lastname: '', birthday: '', gender: null })

const resetForm = () => { formData.value = { identifier: '', firstname: '', lastname: '', birthday: '', gender: null } }
const populateForm = (item) => { formData.value = { identifier: item.identifier, firstname: item.firstname, lastname: item.lastname, birthday: item.birthday || '', gender: item.gender } }

const loadData = async () => {
  try {
    const response = await api.get('subjects/')
    items.value = response.data
  } catch (error) { 
    warningMessage.value = crud.parseApiError(error, t, 'errors.load_failed')
    showWarningModal.value = true
  }
}

const getGenderLabel = (genderCode) => {
  if (genderCode === 'M') return t('master_data.gender_male')
  if (genderCode === 'F') return t('master_data.gender_female')
  if (genderCode === 'O') return t('master_data.gender_other')
  return '-'
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  const [year, month, day] = dateString.split('-')
  return `${day}-${month}-${year}`
}

const saveRecord = async () => {
  crud.clearErrors()
  if (!formData.value.identifier || formData.value.identifier.trim() === '') {
    crud.fieldErrors.value.identifier = t('errors.required_field')
    return
  }

  const payload = { ...formData.value }
  if (payload.birthday === '') payload.birthday = null

  try {
    if (crud.isEditing.value) {
      await api.put(`subjects/${crud.editingId.value}/`, payload)
      crud.notifySuccess('updated', t)
    } else {
      await api.post('subjects/', payload)
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
    await api.delete(`subjects/${crud.itemToDelete.value}/`)
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
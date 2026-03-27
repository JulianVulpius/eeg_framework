<template>
  <div class="category-manager">
    <CrudHeader 
      :title="$t('nav.metadata_definitions')" 
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
              <ColumnHeaderFilter :title="$t('views.metadata.category')" v-model="columnFilters.category" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 15%;">
               <ColumnHeaderSelectFilter :title="$t('views.metadata.data_type')" v-model="columnFilters.data_type" :options="dataTypes" :placeholder="$t('master_data.none')" />
            </th>
            <th style="width: 25%;">
              <ColumnHeaderFilter :title="$t('common.description')" v-model="columnFilters.description" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 20%;">
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
            <td><span class="badge secondary-badge">{{ getDataTypeLabel(item.expected_data_type) }}</span></td>
            <td>{{ item.description || '-' }}</td>
            <td>{{ item.creator || '-' }}</td>
            <TableActionButtons @edit="crud.openEditDialog(item.id, () => populateForm(item))" @delete="crud.requestDelete(item.id)" />
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
          <input type="text" v-model="formData.name" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.name }" :placeholder="$t('modal.name_placeholder')" />
          <BaseInputError :message="crud.fieldErrors.value.name" />
        </div>

        <BaseSearchSelect 
          v-model="formData.category"
          :options="categories"
          :label="$t('views.metadata.category') + ' *'"
          :error="crud.fieldErrors.value.category"
          :placeholder="$t('views.metadata.select_category')"
        />

        <div class="form-group">
          <label>{{ $t('views.metadata.expected_data_type') }} *</label>
          <select v-model="formData.expected_data_type" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.expected_data_type }">
            <option v-for="type in dataTypes" :key="type.value" :value="type.value">{{ type.label }}</option>
          </select>
          <BaseInputError :message="crud.fieldErrors.value.expected_data_type" />
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
import { ref, onMounted, computed } from 'vue'
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
import ColumnHeaderSelectFilter from '@/components/table/ColumnHeaderSelectFilter.vue' 
import TableActionButtons from '@/components/table/TableActionButtons.vue'

const { t } = useI18n()
const items = ref([])
const categories = ref([])
const crud = useCrud()

const showWarningModal = ref(false)
const warningMessage = ref('')

const columnFilters = ref({
  name: '',
  category: '',
  description: '',
  data_type: '', 
  creator: '' 
})

const dataTypes = computed(() => [
  { value: 'STRING', label: t('views.metadata.type_string') },
  { value: 'INTEGER', label: t('views.metadata.type_integer') },
  { value: 'FLOAT', label: t('views.metadata.type_float') },
  { value: 'BOOLEAN', label: t('views.metadata.type_boolean') },
  { value: 'JSON', label: t('views.metadata.type_json') }
])

const filteredItems = computed(() => {
  return items.value.filter(item => {
    if (columnFilters.value.name && !item.name.toLowerCase().includes(columnFilters.value.name.toLowerCase())) return false
    if (columnFilters.value.category) {
      const cName = getCategoryName(item.category).toLowerCase()
      if (!cName.includes(columnFilters.value.category.toLowerCase())) return false
    }
    if (columnFilters.value.description && (!item.description || !item.description.toLowerCase().includes(columnFilters.value.description.toLowerCase()))) return false
    if (columnFilters.value.data_type && item.expected_data_type !== columnFilters.value.data_type) return false
    if (columnFilters.value.creator) {
      const creatorName = item.creator ? item.creator.toLowerCase() : ''
      if (!creatorName.includes(columnFilters.value.creator.toLowerCase())) return false
    }
    return true
  })
})

const formData = ref({ name: '', category: null, expected_data_type: 'STRING', description: '' })

const resetForm = () => { formData.value = { name: '', category: null, expected_data_type: 'STRING', description: '' } }
const populateForm = (item) => { formData.value = { name: item.name, category: item.category, expected_data_type: item.expected_data_type, description: item.description } }

const getCategoryName = (id) => {
  const cat = categories.value.find(c => c.id === id)
  return cat ? cat.name : 'Unknown'
}

const getDataTypeLabel = (val) => {
  const typeObj = dataTypes.value.find(t => t.value === val)
  return typeObj ? typeObj.label : val
}

const loadData = async () => {
  try {
    const [resDefs, resCats] = await Promise.all([
      api.get('metadata/definitions/'), 
      api.get('category/metadata-categories/')
    ])
    items.value = resDefs.data
    categories.value = resCats.data
  } catch (error) { 
    warningMessage.value = crud.parseApiError(error, t, 'errors.load_failed')
    showWarningModal.value = true
  }
}

const saveRecord = async () => {
  crud.clearErrors()

  let hasErrors = false
  if (!formData.value.name || formData.value.name.trim() === '') {
    crud.fieldErrors.value.name = t('errors.required_field'); hasErrors = true
  }
  if (!formData.value.category) {
    crud.fieldErrors.value.category = t('errors.required_field'); hasErrors = true
  }
  if (!formData.value.expected_data_type) {
    crud.fieldErrors.value.expected_data_type = t('errors.required_field'); hasErrors = true
  }

  if (hasErrors) return

  try {
    if (crud.isEditing.value) {
      await api.put(`metadata/definitions/${crud.editingId.value}/`, formData.value)
      crud.notifySuccess('updated', t)
    } else {
      await api.post('metadata/definitions/', formData.value)
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
    await api.delete(`metadata/definitions/${crud.itemToDelete.value}/`)
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
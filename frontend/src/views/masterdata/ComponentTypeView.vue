<template>
  <div class="category-manager">
    <CrudHeader 
      :title="$t('nav.component_types')" 
      v-model="crud.showIdColumn.value" 
      @add="crud.openAddDialog(resetForm)" 
    />

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-if="crud.showIdColumn.value" class="id-column">{{ $t('common.id') }}</th>
            <th style="width: 30%;">
              <ColumnHeaderFilter :title="$t('common.name')" v-model="columnFilters.name" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 25%;">
              <ColumnHeaderFilter :title="$t('views.models.identifier')" v-model="columnFilters.identifier" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 30%;">
              <ColumnHeaderFilter :title="$t('common.description')" v-model="columnFilters.description" :placeholder="$t('common.search')" />
            </th>
            <th class="actions-column">{{ $t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredItems.length === 0">
            <td :colspan="crud.showIdColumn.value ? 5 : 4" class="empty-state">{{ $t('common.no_data') }}</td>
          </tr>
          <tr v-for="item in filteredItems" :key="item.id">
            <td v-if="crud.showIdColumn.value" class="id-column">{{ item.id }}</td>
            <td><strong>{{ item.name }}</strong></td>
            <td><span class="badge secondary-badge">{{ item.identifier }}</span></td>
            <td>{{ item.description }}</td>
            <TableActionButtons @edit="crud.openEditDialog(item.id, () => populateForm(item))" @delete="confirmAndDelete(item.id)" />
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
        
        <div class="form-group">
          <label>{{ $t('views.models.identifier') }} *</label>
          <input type="text" v-model="formData.identifier" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.identifier }" placeholder="TEXT_INPUT" />
          <BaseInputError :message="crud.fieldErrors.value.identifier" />
          <small style="color: #7f8c8d; font-size: 0.8rem; display: block; margin-top: 4px;">
            {{ $t('views.models.identifier_hint') }}
          </small>
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useCrud } from '@/composables/useCrud'
import { useGlobalModal } from '@/composables/useGlobalModal'

import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInputError from '@/components/ui/BaseInputError.vue'
import CrudHeader from '@/components/ui/CrudHeader.vue'

import ColumnHeaderFilter from '@/components/table/ColumnHeaderFilter.vue'
import TableActionButtons from '@/components/table/TableActionButtons.vue'

const { t } = useI18n()
const items = ref([])
const crud = useCrud()
const { requireConfirmation } = useGlobalModal()

const columnFilters = ref({ name: '', identifier: '', description: '' })

const filteredItems = computed(() => {
  return items.value.filter(item => {
    if (columnFilters.value.name && !item.name.toLowerCase().includes(columnFilters.value.name.toLowerCase())) return false
    if (columnFilters.value.identifier && (!item.identifier || !item.identifier.toLowerCase().includes(columnFilters.value.identifier.toLowerCase()))) return false
    if (columnFilters.value.description && (!item.description || !item.description.toLowerCase().includes(columnFilters.value.description.toLowerCase()))) return false
    return true
  })
})

const formData = ref({ name: '', identifier: '', description: '' })

const resetForm = () => { formData.value = { name: '', identifier: '', description: '' } }
const populateForm = (item) => { formData.value = { name: item.name, identifier: item.identifier, description: item.description } }

const loadData = async () => {
  try {
    const response = await api.get('/component-types/')
    items.value = response.data
  } catch (error) {}
}

const saveRecord = async () => {
  crud.clearErrors()
  let hasErrors = false
  if (!formData.value.name || formData.value.name.trim() === '') { crud.fieldErrors.value.name = t('errors.required_field'); hasErrors = true }
  if (!formData.value.identifier || formData.value.identifier.trim() === '') { crud.fieldErrors.value.identifier = t('errors.required_field'); hasErrors = true }
  if (hasErrors) return

  formData.value.identifier = formData.value.identifier.toUpperCase().replace(/\s+/g, '_')

  try {
    if (crud.isEditing.value) {
      await api.put(`/component-types/${crud.editingId.value}/`, formData.value)
    } else {
      await api.post('/component-types/', formData.value)
    }
    crud.closeDialog()
    loadData()
  } catch (error) { 
    crud.handleFormError(error, t)
  }
}

const confirmAndDelete = (id) => {
  requireConfirmation(async () => {
    try {
      await api.delete(`/component-types/${id}/`)
      loadData()
    } catch (error) {}
  })
}

onMounted(loadData)
</script>
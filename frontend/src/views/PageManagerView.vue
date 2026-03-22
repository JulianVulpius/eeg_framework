<template>
  <div class="page-manager">
    <CrudHeader :title="$t('nav.pages')" v-model="crud.showIdColumn.value" @add="crud.openAddDialog(resetForm)" />

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-if="crud.showIdColumn.value" class="id-column">{{ $t('common.id') }}</th>
            <th>{{ $t('common.name') }}</th>
            <th class="actions-column">{{ $t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="items.length === 0"><td :colspan="crud.showIdColumn.value ? 3 : 2" class="empty-state">{{ $t('common.no_data') }}</td></tr>
          <tr v-for="item in items" :key="item.id">
            <td v-if="crud.showIdColumn.value" class="id-column">{{ item.id }}</td>
            <td><strong>{{ item.name }}</strong></td>
            <TableActionButtons @edit="crud.openEditDialog(item.id, () => populateForm(item))" @delete="crud.requestDelete(item.id)" />
          </tr>
        </tbody>
      </table>
    </div>

    <BaseModal :isOpen="crud.isDialogOpen.value" :title="crud.isEditing.value ? $t('modal.edit_record') : $t('modal.add_record')" @close="crud.closeDialog" customClass="large-modal">
      <form @submit.prevent="saveRecord">
        <div class="form-row" style="display: flex; gap: 1rem; margin-bottom: 1rem;">
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('common.name') }} *</label>
            <input type="text" v-model="formData.name" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.name }" />
            <BaseInputError :message="crud.fieldErrors.value.name" />
          </div>
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('master_data.category') }} *</label>
            <BaseSearchSelect v-model="formData.category" :options="categories" />
          </div>
        </div>

        <div class="form-group">
          <label style="font-weight: bold; font-size: 1.1rem; border-bottom: 1px solid #eee; padding-bottom: 5px;">{{ $t('views.pages.assign_components') }}</label>
          <BaseTransferList
            v-model="formData.components"
            :options="availableComponents"
            :leftTitle="$t('views.pages.available_components')"
            :rightTitle="$t('views.pages.selected_components')"
            :enableOrdering="true"
          />
        </div>

        <div class="modal-actions" style="margin-top: 2rem;">
          <button type="button" class="btn-secondary" @click="crud.closeDialog">{{ $t('actions.cancel') }}</button>
          <button type="submit" class="btn-primary">{{ $t('actions.save') }}</button>
        </div>
      </form>
    </BaseModal>

    <ConfirmDeleteModal :isOpen="crud.isConfirmOpen.value" @cancel="crud.cancelDelete" @confirm="executeDelete" />
    <WarningModal :isOpen="showWarningModal" :message="warningMessage" @close="showWarningModal = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useCrud } from '@/composables/useCrud'

import BaseModal from '@/components/BaseModal.vue'
import BaseInputError from '@/components/BaseInputError.vue'
import BaseSearchSelect from '@/components/BaseSearchSelect.vue'
import BaseTransferList from '@/components/BaseTransferList.vue'
import ConfirmDeleteModal from '@/components/ConfirmDeleteModal.vue'
import WarningModal from '@/components/WarningModal.vue'
import CrudHeader from '@/components/CrudHeader.vue'
import TableActionButtons from '@/components/TableActionButtons.vue'

const { t } = useI18n()
const crud = useCrud()

const items = ref([]); const categories = ref([]); const availableComponents = ref([])
const showWarningModal = ref(false); const warningMessage = ref('')

const formData = ref({ name: '', category: null, description: '', components: [] })

const resetForm = () => { formData.value = { name: '', category: null, description: '', components: [] } }

const populateForm = (item) => { formData.value = { name: item.name, category: item.category, description: item.description || '', components: item.components || [] } }

const loadData = async () => {
  try {
    const [pageRes, catRes, compRes] = await Promise.all([api.get('pages/'), api.get('category/page-categories/'), api.get('components/')])
    items.value = pageRes.data; categories.value = catRes.data; availableComponents.value = compRes.data
  } catch (error) { warningMessage.value = t('errors.load_failed'); showWarningModal.value = true }
}

const saveRecord = async () => {
  crud.clearErrors(); if (!formData.value.name) { crud.fieldErrors.value.name = t('errors.required_field'); return }
  try {
    if (crud.isEditing.value) await api.put(`pages/${crud.editingId.value}/`, formData.value)
    else await api.post('pages/', formData.value)
    crud.closeDialog(); loadData()
  } catch (error) { crud.handleFormError(error, t, 'errors.save_failed') }
}

const executeDelete = async () => {
  try { await api.delete(`pages/${crud.itemToDelete.value}/`); crud.cancelDelete(); loadData() } 
  catch (error) { crud.cancelDelete(); warningMessage.value = t('errors.delete_failed'); showWarningModal.value = true }
}

onMounted(loadData)
</script>

<style scoped> .large-modal { max-width: 800px; width: 90vw; } </style>
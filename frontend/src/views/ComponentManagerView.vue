<template>
  <div class="component-manager">
    <CrudHeader :title="$t('nav.components')" v-model="crud.showIdColumn.value" @add="crud.openAddDialog(resetForm)" />

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-if="crud.showIdColumn.value" class="id-column">{{ $t('common.id') }}</th>
            <th>{{ $t('common.name') }}</th>
            <th>{{ $t('views.components.type') }}</th>
            <th class="actions-column">{{ $t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="items.length === 0"><td :colspan="crud.showIdColumn.value ? 4 : 3" class="empty-state">{{ $t('common.no_data') }}</td></tr>
          <tr v-for="item in items" :key="item.id">
            <td v-if="crud.showIdColumn.value" class="id-column">{{ item.id }}</td>
            <td><strong>{{ item.name }}</strong></td>
            <td>{{ getTypeName(item.component_type) }}</td>
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
        
        <div class="form-row" style="display: flex; gap: 1rem; margin-bottom: 1rem;">
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('master_data.category') }} *</label>
            <BaseSearchSelect v-model="formData.category" :options="categories" />
          </div>
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('views.components.type') }} *</label>
            <BaseSearchSelect v-model="formData.component_type" :options="types" />
          </div>
        </div>

        <div class="form-group">
          <label>{{ $t('common.description') }}</label>
          <textarea v-model="formData.description" rows="2" class="form-control"></textarea>
        </div>

        <div v-if="isMetadataFormSelected" class="form-group" style="margin-bottom: 1.5rem; background: #f8f9fa; padding: 15px; border-radius: 6px; border: 1px solid #e0e0e0;">
          <label style="color: #2980b9;">{{ $t('views.components.select_metadata_group') }} *</label>
          <BaseSearchSelect 
            v-model="selectedMetadataGroupId" 
            :options="metadataGroups" 
            :placeholder="$t('common.search')"
            @update:modelValue="updateMetadataParameter"
          />
          <small style="color: #7f8c8d; display: block; margin-top: 5px;">{{ $t('views.components.metadata_auto_hint') }}</small>
        </div>

        <div v-else class="form-group" style="margin-bottom: 1.5rem;">
          <label>{{ $t('views.components.parameters') }}</label>
          <textarea v-model="formData.parameter" rows="4" class="form-control" style="font-family: monospace;" :placeholder="$t('views.components.param_placeholder')"></textarea>
          <BaseInputError :message="jsonError" />
        </div>

        <div class="modal-actions">
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
import { ref, onMounted, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useCrud } from '@/composables/useCrud'

import BaseModal from '@/components/BaseModal.vue'
import BaseInputError from '@/components/BaseInputError.vue'
import BaseSearchSelect from '@/components/BaseSearchSelect.vue'
import ConfirmDeleteModal from '@/components/ConfirmDeleteModal.vue'
import WarningModal from '@/components/WarningModal.vue'
import CrudHeader from '@/components/CrudHeader.vue'
import TableActionButtons from '@/components/TableActionButtons.vue'

const { t } = useI18n()
const crud = useCrud()

const items = ref([]); const categories = ref([]); const types = ref([]); const metadataGroups = ref([])
const showWarningModal = ref(false); const warningMessage = ref('')
const jsonError = ref('')

const formData = ref({ name: '', category: null, component_type: null, description: '', parameter: '{}' })
const selectedMetadataGroupId = ref(null)

const getTypeName = (id) => { const t = types.value.find(x => x.id === id); return t ? t.name : id }

const isMetadataFormSelected = computed(() => {
  if (!formData.value.component_type) return false
  const selectedType = types.value.find(t => t.id === formData.value.component_type)
  return selectedType && selectedType.identifier === 'METADATA_FORM'
})

const updateMetadataParameter = (groupId) => {
  if (groupId) {
    formData.value.parameter = JSON.stringify({ metadata_group_id: groupId }, null, 2)
  } else {
    formData.value.parameter = '{}'
  }
}

const resetForm = () => { 
  formData.value = { name: '', category: null, component_type: null, description: '', parameter: '{}' }
  selectedMetadataGroupId.value = null
  jsonError.value = '' 
}

const populateForm = (item) => {
  let paramStr = typeof item.parameter === 'object' ? JSON.stringify(item.parameter, null, 2) : item.parameter
  formData.value = { ...item, parameter: paramStr }
  jsonError.value = ''
  
  // Try to parse out the group ID if it's a metadata form
  try {
    const parsed = JSON.parse(paramStr)
    if (parsed && parsed.metadata_group_id) {
      selectedMetadataGroupId.value = parsed.metadata_group_id
    } else {
      selectedMetadataGroupId.value = null
    }
  } catch(e) { selectedMetadataGroupId.value = null }
}

const loadData = async () => {
  try {
    const [compRes, catRes, typeRes, mdRes] = await Promise.all([
      api.get('components/'), 
      api.get('category/component-categories/'), 
      api.get('component-types/'),
      api.get('metadata/groups/')
    ])
    items.value = compRes.data; categories.value = catRes.data; types.value = typeRes.data; metadataGroups.value = mdRes.data
  } catch (error) { warningMessage.value = t('errors.load_failed'); showWarningModal.value = true }
}

const saveRecord = async () => {
  crud.clearErrors(); jsonError.value = ''; let hasError = false
  if (!formData.value.name) { crud.fieldErrors.value.name = t('errors.required_field'); hasError = true }
  
  let parsedJson = {}
  try { parsedJson = JSON.parse(formData.value.parameter || '{}') } 
  catch (e) { jsonError.value = t('errors.invalid_input') + " (Invalid JSON)"; hasError = true }

  if (hasError) return

  const payload = { ...formData.value, parameter: parsedJson }
  try {
    if (crud.isEditing.value) await api.put(`components/${crud.editingId.value}/`, payload)
    else await api.post('components/', payload)
    crud.closeDialog(); loadData()
  } catch (error) { crud.handleFormError(error, t, 'errors.save_failed') }
}

const executeDelete = async () => {
  try { await api.delete(`components/${crud.itemToDelete.value}/`); crud.cancelDelete(); loadData() } 
  catch (error) { crud.cancelDelete(); warningMessage.value = t('errors.delete_failed'); showWarningModal.value = true }
}

onMounted(loadData)
</script>
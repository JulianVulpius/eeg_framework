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

    <BaseModal :isOpen="crud.isDialogOpen.value" :title="crud.isEditing.value ? $t('modal.edit_record') : $t('modal.add_record')" @close="crud.closeDialog" customClass="large-modal">
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

        <div class="form-group" style="margin-bottom: 20px;">
          <label>{{ $t('common.description') }}</label>
          <textarea v-model="formData.description" rows="2" class="form-control"></textarea>
        </div>

        <div style="border-top: 2px solid #f4f7f6; padding-top: 20px; margin-bottom: 1.5rem;">
          
          <div v-if="isMetadataFormSelected" class="dynamic-config-box">
            <label style="color: #2980b9; font-weight: bold; margin-bottom: 10px; display: block;">{{ $t('views.components.select_metadata_group') }} *</label>
            <BaseSearchSelect 
              v-model="selectedMetadataGroupId" 
              :options="metadataGroups" 
              :placeholder="$t('common.search')"
              @update:modelValue="updateMetadataParameter"
            />
            <small class="hint-text">{{ $t('views.components.metadata_auto_hint') }}</small>
          </div>

          <div v-else-if="isTextBlockSelected" class="dynamic-config-box">
            <label style="color: #27ae60; font-weight: bold; margin-bottom: 10px; display: block;">{{ $t('views.components.text_content') }} *</label>
            <div class="editor-container" style="background: white;">
              <QuillEditor 
                v-model:content="textContent" 
                contentType="html" 
                theme="snow" 
                @update:content="updateTextParameter"
                style="min-height: 200px;"
              />
            </div>
            <small class="hint-text">{{ $t('views.components.text_auto_hint') }}</small>
          </div>

          <div v-else class="empty-config-box">
            {{ formData.component_type ? $t('views.components.no_config_needed') : $t('views.components.select_type_prompt') }}
          </div>
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
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useCrud } from '@/composables/useCrud'

import { QuillEditor } from '@vueup/vue-quill'
import '@vueup/vue-quill/dist/vue-quill.snow.css'

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

const formData = ref({ name: '', category: null, component_type: null, description: '', parameter: '{}' })

const selectedMetadataGroupId = ref(null)
const textContent = ref('')

const getTypeName = (id) => { const t = types.value.find(x => x.id === id); return t ? t.name : id }

const isMetadataFormSelected = computed(() => {
  if (!formData.value.component_type) return false
  const selectedType = types.value.find(t => t.id === formData.value.component_type)
  return selectedType && selectedType.identifier === 'METADATA_FORM'
})

const isTextBlockSelected = computed(() => {
  if (!formData.value.component_type) return false
  const selectedType = types.value.find(t => t.id === formData.value.component_type)
  return selectedType && selectedType.identifier === 'TEXT_BLOCK'
})

const updateMetadataParameter = (groupId) => {
  formData.value.parameter = groupId ? JSON.stringify({ metadata_group_id: groupId }) : '{}'
}

const updateTextParameter = () => {
  formData.value.parameter = JSON.stringify({ text: textContent.value })
}

const resetForm = () => { 
  formData.value = { name: '', category: null, component_type: null, description: '', parameter: '{}' }
  selectedMetadataGroupId.value = null
  textContent.value = ''
}

const populateForm = (item) => {
  let paramStr = typeof item.parameter === 'object' ? JSON.stringify(item.parameter) : (item.parameter || '{}')
  formData.value = { ...item, parameter: paramStr }
  
  selectedMetadataGroupId.value = null
  textContent.value = ''
  
  try {
    const parsed = JSON.parse(paramStr)
    if (parsed && parsed.metadata_group_id) {
      selectedMetadataGroupId.value = parsed.metadata_group_id
    }
    if (parsed && parsed.text) {
      textContent.value = parsed.text
    }
  } catch(e) { console.error("Could not parse parameters on edit.") }
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
  crud.clearErrors(); let hasError = false
  if (!formData.value.name) { crud.fieldErrors.value.name = t('errors.required_field'); hasError = true }
  
  if (hasError) return

  const payload = { ...formData.value, parameter: JSON.parse(formData.value.parameter || '{}') }
  
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

<style scoped>
.large-modal { max-width: 900px; width: 90vw; }

.dynamic-config-box {
  background: #fdfdfd; 
  padding: 15px 20px; 
  border-radius: 6px; 
  border: 1px solid #e0e0e0;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}

.empty-config-box {
  padding: 30px 20px; 
  text-align: center; 
  background: #f8f9fa; 
  border: 2px dashed #dcdde1; 
  border-radius: 6px; 
  color: #7f8c8d;
  font-style: italic;
}

.hint-text {
  color: #95a5a6; 
  display: block; 
  margin-top: 8px;
  font-size: 0.85rem;
}

:deep(.ql-toolbar) { border-top-left-radius: 4px; border-top-right-radius: 4px; background: #fdfdfd; }
:deep(.ql-container) { border-bottom-left-radius: 4px; border-bottom-right-radius: 4px; font-size: 1rem; }
</style>
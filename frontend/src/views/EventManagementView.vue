<template>
  <div class="event-manager">
    <CrudHeader 
      :title="$t('nav.events')" 
      v-model="crud.showIdColumn.value" 
      @add="crud.openAddDialog(resetForm)" 
    />

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-if="crud.showIdColumn.value" class="id-column">{{ $t('common.id') }}</th>
            <th>{{ $t('common.name') }}</th>
            <th>{{ $t('views.events.start') }}</th>
            <th>{{ $t('views.events.end') }}</th>
            <th class="actions-column">{{ $t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="items.length === 0">
            <td :colspan="crud.showIdColumn.value ? 5 : 4" class="empty-state">{{ $t('common.no_data') }}</td>
          </tr>
          <tr v-for="item in items" :key="item.id">
            <td v-if="crud.showIdColumn.value" class="id-column">{{ item.id }}</td>
            <td><strong>{{ item.name }}</strong></td>
            <td>{{ formatDate(item.event_start) }}</td>
            <td>{{ formatDate(item.event_end) }}</td>
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
      customClass="large-modal"
    >
      <form @submit.prevent="saveRecord">
        
        <div class="form-row" style="display: flex; gap: 1rem; margin-bottom: 1rem;">
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('common.name') }} *</label>
            <input 
              type="text" 
              v-model="formData.name" 
              class="form-control"
              :class="{ 'input-invalid': crud.fieldErrors.value.name }"
            />
            <BaseInputError :message="crud.fieldErrors.value.name" />
          </div>
          
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('master_data.category') }} *</label>
            <BaseSearchSelect
              v-model="formData.category"
              :options="categories"
              :placeholder="$t('views.events.select_category')"
              :error="crud.fieldErrors.value.category"
            />
          </div>
        </div>

        <div class="form-row" style="display: flex; gap: 1rem; margin-bottom: 1rem;">
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('views.events.start') }}</label>
            <input type="datetime-local" v-model="formData.event_start" class="form-control" />
          </div>
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('views.events.end') }}</label>
            <input type="datetime-local" v-model="formData.event_end" class="form-control" />
          </div>
        </div>

        <div class="form-group" style="margin-bottom: 1.5rem;">
          <label>{{ $t('common.description') }}</label>
          <textarea v-model="formData.description" rows="2" class="form-control"></textarea>
        </div>

        <div class="form-group">
          <label style="font-weight: bold; font-size: 1.1rem; border-bottom: 1px solid #eee; padding-bottom: 5px;">
            {{ $t('views.events.assign_groups') }}
          </label>
          <BaseTransferList
            v-model="formData.page_groups"
            :options="pageGroups"
            :leftTitle="$t('views.events.available_groups')"
            :rightTitle="$t('views.events.selected_groups')"
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

const items = ref([])
const categories = ref([])
const pageGroups = ref([])

const showWarningModal = ref(false)
const warningMessage = ref('')

const formData = ref({
  name: '',
  category: null,
  description: '',
  event_start: '',
  event_end: '',
  page_groups: []
})

// format iso string to html datetime-local value
const formatForInput = (isoString) => {
  if (!isoString) return ''
  return new Date(isoString).toISOString().slice(0, 16)
}

const formatDate = (isoString) => {
  if (!isoString) return '-'
  return new Date(isoString).toLocaleString()
}

const resetForm = () => {
  formData.value = { name: '', category: null, description: '', event_start: '', event_end: '', page_groups: [] }
}

const populateForm = (item) => {
  formData.value = {
    name: item.name,
    category: item.category,
    description: item.description || '',
    event_start: formatForInput(item.event_start),
    event_end: formatForInput(item.event_end),
    page_groups: item.page_groups || []
  }
}

const loadData = async () => {
  try {
    const [eventsRes, catRes, pgRes] = await Promise.all([
      api.get('events/'),
      api.get('category/event-categories/'),
      api.get('page-groups/')
    ])
    items.value = eventsRes.data
    categories.value = catRes.data
    pageGroups.value = pgRes.data
  } catch (error) {
    warningMessage.value = crud.parseApiError(error, t, 'errors.load_failed')
    showWarningModal.value = true
  }
}

const saveRecord = async () => {
  crud.clearErrors()
  let hasError = false

  if (!formData.value.name) { crud.fieldErrors.value.name = t('errors.required_field'); hasError = true }
  if (!formData.value.category) { crud.fieldErrors.value.category = t('errors.required_field'); hasError = true }
  
  if (hasError) return

  // format empty strings to null for django datetime fields
  const payload = { ...formData.value }
  if (!payload.event_start) payload.event_start = null
  if (!payload.event_end) payload.event_end = null

  try {
    if (crud.isEditing.value) {
      await api.put(`events/${crud.editingId.value}/`, payload)
    } else {
      await api.post('events/', payload)
    }
    crud.closeDialog()
    loadData()
  } catch (error) {
    crud.handleFormError(error, t, 'errors.save_failed')
  }
}

const executeDelete = async () => {
  try {
    await api.delete(`events/${crud.itemToDelete.value}/`)
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
.large-modal { max-width: 800px; width: 90vw; }
</style>
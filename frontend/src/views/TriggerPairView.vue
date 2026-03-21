<template>
  <div class="category-manager">
    <CrudHeader 
      :title="$t('nav.trigger_pairs')" 
      v-model="crud.showIdColumn.value" 
      @add="crud.openAddDialog(resetForm)" 
    />

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-if="crud.showIdColumn.value" class="id-column">{{ $t('common.id') }}</th>
            <th style="width: 30%;">
              <ColumnHeaderFilter 
                :title="$t('common.name')" 
                v-model="columnFilters.name" 
                :placeholder="$t('common.search')" 
              />
            </th>
            <th>{{ $t('views.triggers.start_trigger') }}</th>
            <th>{{ $t('views.triggers.end_trigger') }}</th>
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
            <td>{{ getTriggerName(item.start_trigger) }}</td>
            <td>{{ getTriggerName(item.end_trigger) }}</td>
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
          />
          <BaseInputError :message="crud.fieldErrors.value.name" />
        </div>

        <BaseSearchSelect 
          v-model="formData.start_trigger"
          :options="triggerOptions"
          :label="$t('views.triggers.start_trigger') + ' *'"
          :error="crud.fieldErrors.value.start_trigger"
          :placeholder="$t('views.triggers.select_placeholder')"
        />

        <BaseSearchSelect 
          v-model="formData.end_trigger"
          :options="triggerOptions"
          :label="$t('views.triggers.end_trigger') + ' *'"
          :error="crud.fieldErrors.value.end_trigger"
          :placeholder="$t('views.triggers.select_placeholder')"
        />

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
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useCrud } from '@/composables/useCrud'

import BaseModal from '@/components/BaseModal.vue'
import BaseInputError from '@/components/BaseInputError.vue'
import BaseSearchSelect from '@/components/BaseSearchSelect.vue'
import ConfirmDeleteModal from '@/components/ConfirmDeleteModal.vue'
import WarningModal from '@/components/WarningModal.vue'
import ColumnHeaderFilter from '@/components/ColumnHeaderFilter.vue'
import CrudHeader from '@/components/CrudHeader.vue'
import TableActionButtons from '@/components/TableActionButtons.vue'

const { t } = useI18n()
const items = ref([])
const allTriggerDefs = ref([])
const crud = useCrud()

const showWarningModal = ref(false)
const warningMessage = ref('')

const columnFilters = ref({
  name: ''
})

const filteredItems = computed(() => {
  return items.value.filter(item => {
    if (columnFilters.value.name) {
      const q = columnFilters.value.name.toLowerCase()
      if (!item.name.toLowerCase().includes(q)) return false
    }
    return true
  })
})

const triggerOptions = computed(() => {
  return allTriggerDefs.value.map(def => ({
    id: def.id,
    name: `${def.name} (${def.trigger_character})`
  }))
})

const formData = ref({ name: '', start_trigger: null, end_trigger: null })

const resetForm = () => { 
  formData.value = { name: '', start_trigger: null, end_trigger: null }
}

const populateForm = (item) => { 
  formData.value = { name: item.name, start_trigger: item.start_trigger, end_trigger: item.end_trigger }
}

const loadData = async () => {
  try {
    const [resPairs, resDefs] = await Promise.all([
      api.get('triggers/pairs/'),
      api.get('triggers/definitions/')
    ])
    items.value = resPairs.data
    allTriggerDefs.value = resDefs.data
  } catch (error) { 
    warningMessage.value = crud.parseApiError(error, t, 'errors.load_failed')
    showWarningModal.value = true
  }
}

const getTriggerName = (id) => {
  if (!id) return '-'
  const def = allTriggerDefs.value.find(d => d.id === id)
  return def ? `${def.name} (${def.trigger_character})` : id
}

const saveRecord = async () => {
  crud.clearErrors()

  let hasErrors = false
  if (!formData.value.name || formData.value.name.trim() === '') {
    crud.fieldErrors.value.name = t('errors.required_field')
    hasErrors = true
  }
  if (!formData.value.start_trigger) {
    crud.fieldErrors.value.start_trigger = t('errors.required_field')
    hasErrors = true
  }
  if (!formData.value.end_trigger) {
    crud.fieldErrors.value.end_trigger = t('errors.required_field')
    hasErrors = true
  }

  if (hasErrors) return

  try {
    if (crud.isEditing.value) await api.put(`triggers/pairs/${crud.editingId.value}/`, formData.value)
    else await api.post('triggers/pairs/', formData.value)
    crud.closeDialog()
    loadData()
  } catch (error) { 
    crud.handleFormError(error, t, 'errors.save_failed')
  }
}

const executeDelete = async () => {
  try {
    await api.delete(`triggers/pairs/${crud.itemToDelete.value}/`)
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
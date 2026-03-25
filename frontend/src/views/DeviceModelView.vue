<template>
  <div class="category-manager">
    <CrudHeader 
      :title="$t('nav.device_models')" 
      v-model="crud.showIdColumn.value" 
      @add="crud.openAddDialog(resetForm)" 
    />

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-if="crud.showIdColumn.value" class="id-column">{{ $t('common.id') }}</th>
            
            <th style="width: 20%;">
              <ColumnHeaderFilter 
                :title="$t('common.name')" 
                v-model="columnFilters.name" 
                :placeholder="$t('common.search')" 
              />
            </th>
            <th style="width: 20%;">
              <ColumnHeaderFilter 
                :title="$t('master_data.manufacturer')" 
                v-model="columnFilters.manufacturer" 
                :placeholder="$t('common.search')" 
              />
            </th>
            <th style="width: 20%;">
              <ColumnHeaderFilter 
                :title="$t('master_data.category')" 
                v-model="columnFilters.category" 
                :placeholder="$t('common.search')" 
              />
            </th>
            <th style="width: 25%;">
              <ColumnHeaderMultiFilter 
                :title="$t('common.eeg_channel')" 
                v-model="columnFilters.channels" 
                :options="channels"
                :placeholder="$t('common.search')" 
                :filterTitle="$t('common.must_include')" 
              />
            </th> 
            <th class="actions-column">{{ $t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredItems.length === 0">
            <td :colspan="crud.showIdColumn.value ? 6 : 5" class="empty-state">{{ $t('common.no_data') }}</td>
          </tr>
          <tr v-for="item in filteredItems" :key="item.id">
            <td v-if="crud.showIdColumn.value" class="id-column">{{ item.id }}</td>
            <td><strong>{{ item.name }}</strong></td>
            <td>{{ getManufacturerName(item.manufacturer) }}</td>
            <td><span class="badge category-badge">{{ getCategoryName(item.category) }}</span></td>
            
            <td class="channels-cell" :title="item.channel_names">
              <span class="badge secondary-badge">{{ item.channel_names || '-' }}</span>
            </td>
            
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
      :errorMessage="crud.errorMessage.value"
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
          v-model="formData.manufacturer"
          :options="manufacturers"
          :label="$t('master_data.manufacturer')"
          :error="crud.fieldErrors.value.manufacturer"
        />

        <BaseSearchSelect 
          v-model="formData.category"
          :options="categories"
          :label="$t('master_data.category')"
          :error="crud.fieldErrors.value.category"
        />

        <div class="form-group">
          <label>{{ $t('common.eeg_channel') }}</label>
          <BaseCheckboxGroup 
            v-model="formData.channels" 
            :options="channels" 
            :searchable="true"
            :searchPlaceholder="$t('common.search')"
          />
          <BaseInputError :message="crud.fieldErrors.value.channels" />
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
import BaseSearchSelect from '@/components/BaseSearchSelect.vue'
import BaseCheckboxGroup from '@/components/BaseCheckboxGroup.vue'
import ConfirmDeleteModal from '@/components/ConfirmDeleteModal.vue'
import WarningModal from '@/components/WarningModal.vue'
import ColumnHeaderFilter from '@/components/ColumnHeaderFilter.vue'
import ColumnHeaderMultiFilter from '@/components/ColumnHeaderMultiFilter.vue' // new multi-filter component
import CrudHeader from '@/components/CrudHeader.vue'
import TableActionButtons from '@/components/TableActionButtons.vue'

const { t } = useI18n()
const crud = useCrud()

const items = ref([])
const categories = ref([])
const manufacturers = ref([])
const channels = ref([])

const showWarningModal = ref(false)
const warningMessage = ref('')

const columnFilters = ref({
  name: '',
  manufacturer: '',
  category: '',
  channels: [] // added array to hold selected required channels
})

const filteredItems = computed(() => {
  return items.value.filter(item => {
    // filter by name
    if (columnFilters.value.name) {
      const q = columnFilters.value.name.toLowerCase()
      if (!item.name.toLowerCase().includes(q)) return false
    }
    
    // filter by manufacturer
    if (columnFilters.value.manufacturer) {
      const q = columnFilters.value.manufacturer.toLowerCase()
      const mName = getManufacturerName(item.manufacturer).toLowerCase()
      if (!mName.includes(q)) return false
    }

    // filter by category
    if (columnFilters.value.category) {
      const q = columnFilters.value.category.toLowerCase()
      const cName = getCategoryName(item.category).toLowerCase()
      if (!cName.includes(q)) return false
    }

    // strict 'must include' filter for eeg channels
    if (columnFilters.value.channels && columnFilters.value.channels.length > 0) {
      const itemChannels = item.assigned_channels || []
      const hasAllRequired = columnFilters.value.channels.every(reqId => itemChannels.includes(reqId))
      if (!hasAllRequired) return false
    }

    return true
  })
})

const formData = ref({ name: '', manufacturer: null, category: null, channels: [] })

const resetForm = () => { 
  formData.value = { name: '', manufacturer: null, category: null, channels: [] } 
}

const populateForm = (item) => { 
  formData.value = { 
    name: item.name, 
    manufacturer: item.manufacturer, 
    category: item.category,
    channels: item.assigned_channels || [] 
  } 
}

const loadData = async () => {
  try {
    const [resModels, resCats, resManuf, resChannels] = await Promise.all([
      api.get('device-models/'),
      api.get('category/device-model-categories/'),
      api.get('manufacturers/'),
      api.get('eeg-channels/') 
    ])
    items.value = resModels.data
    categories.value = resCats.data
    manufacturers.value = resManuf.data
    channels.value = resChannels.data 
  } catch (error) { 
    console.error(error)
    warningMessage.value = crud.parseApiError(error, t, 'errors.load_failed')
    showWarningModal.value = true
  }
}

const getCategoryName = (categoryId) => {
  if (!categoryId) return '-'
  const cat = categories.value.find(c => c.id === categoryId)
  return cat ? cat.name : '-'
}

const getManufacturerName = (manufacturerId) => {
  if (!manufacturerId) return '-'
  const m = manufacturers.value.find(x => x.id === manufacturerId)
  return m ? m.name : String(manufacturerId)
}

const saveRecord = async () => {
  crud.clearErrors() 

  if (!formData.value.name || formData.value.name.trim() === '') {
    crud.fieldErrors.value.name = t('errors.required_field') 
    return
  }

  try {
    if (crud.isEditing.value) await api.put(`device-models/${crud.editingId.value}/`, formData.value)
    else await api.post('device-models/', formData.value)
    crud.closeDialog()
    loadData()
  } catch (error) {
    // let the crud composable do all the hard work handling backend errors
    crud.handleFormError(error, t, 'errors.save_failed')
  }
}

const executeDelete = async () => {
  try {
    await api.delete(`device-models/${crud.itemToDelete.value}/`)
    crud.cancelDelete()
    loadData()
  } catch (error) { 
    crud.cancelDelete()
    warningMessage.value = crud.parseApiError(error, t, 'errors.delete_failed')
    showWarningModal.value = true
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
/* override global table overflow to prevent the absolute dropdown from getting clipped */
.table-container {
  overflow: visible !important;
}
</style>
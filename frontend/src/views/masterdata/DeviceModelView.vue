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
              <ColumnHeaderFilter :title="$t('common.name')" v-model="columnFilters.name" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 20%;">
              <ColumnHeaderFilter :title="$t('master_data.manufacturer')" v-model="columnFilters.manufacturer" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 20%;">
              <ColumnHeaderFilter :title="$t('master_data.category')" v-model="columnFilters.category" :placeholder="$t('common.search')" />
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
          <input type="text" v-model="formData.name" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.name }" />
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
          :nullLabel="$t('master_data.none')"
          :error="crud.fieldErrors.value.category"
        />

        <div class="form-group inline-flex">
          <input type="checkbox" v-model="formData.is_eeg" id="isEegDevice" />
          <label for="isEegDevice">{{ $t('master_data.is_eeg') }}</label>
        </div>

        <div class="form-group" v-if="formData.is_eeg">
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
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'
import BaseCheckboxGroup from '@/components/ui/BaseCheckboxGroup.vue'
import CrudHeader from '@/components/ui/CrudHeader.vue'

import ColumnHeaderFilter from '@/components/table/ColumnHeaderFilter.vue'
import ColumnHeaderMultiFilter from '@/components/table/ColumnHeaderMultiFilter.vue'
import TableActionButtons from '@/components/table/TableActionButtons.vue'

const { t } = useI18n()
const crud = useCrud()
const { requireConfirmation } = useGlobalModal()

const items = ref([])
const categories = ref([])
const manufacturers = ref([])
const channels = ref([])

const columnFilters = ref({
  name: '',
  manufacturer: '',
  category: '',
  channels: [] 
})

const filteredItems = computed(() => {
  return items.value.filter(item => {
    if (columnFilters.value.name && !item.name.toLowerCase().includes(columnFilters.value.name.toLowerCase())) return false
    if (columnFilters.value.manufacturer) {
      const mName = getManufacturerName(item.manufacturer).toLowerCase()
      if (!mName.includes(columnFilters.value.manufacturer.toLowerCase())) return false
    }
    if (columnFilters.value.category) {
      const cName = getCategoryName(item.category).toLowerCase()
      if (!cName.includes(columnFilters.value.category.toLowerCase())) return false
    }
    if (columnFilters.value.channels && columnFilters.value.channels.length > 0) {
      const itemChannels = item.assigned_channels || []
      const hasAllRequired = columnFilters.value.channels.every(reqId => itemChannels.includes(reqId))
      if (!hasAllRequired) return false
    }
    return true
  })
})

const formData = ref({ name: '', manufacturer: null, category: null, is_eeg: false, channels: [] })

const resetForm = () => { 
  formData.value = { name: '', manufacturer: null, category: null, is_eeg: false, channels: [] } 
}

const populateForm = (item) => { 
  formData.value = { 
    name: item.name, 
    manufacturer: item.manufacturer, 
    category: item.category,
    is_eeg: item.is_eeg !== undefined ? item.is_eeg : false,
    channels: item.assigned_channels || [] 
  } 
}

const loadData = async () => {
  try {
    const [resModels, resCats, resManuf, resChannels] = await Promise.all([
      api.get('device-models/'),
      api.get('category/device-model/'),
      api.get('manufacturers/'),
      api.get('eeg-channels/') 
    ])
    items.value = resModels.data; categories.value = resCats.data
    manufacturers.value = resManuf.data; channels.value = resChannels.data 
  } catch (error) { 
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

  const payload = { ...formData.value }
  if (!payload.is_eeg) payload.channels = []

  try {
    if (crud.isEditing.value) {
      await api.put(`device-models/${crud.editingId.value}/`, payload)
    } else {
      await api.post('device-models/', payload)
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
      await api.delete(`device-models/${id}/`)
      loadData()
    } catch (error) {
    }
  })
}

onMounted(() => { loadData() })
</script>

<style scoped>
.table-container { overflow: visible !important; }
.inline-flex { display: flex; align-items: center; gap: 8px; margin-top: 15px; margin-bottom: 15px; }
.inline-flex input { margin: 0; width: auto; cursor: pointer; height: 18px; width: 18px; }
.inline-flex label { margin: 0; font-weight: 600; cursor: pointer; color: var(--text-main); }
</style>
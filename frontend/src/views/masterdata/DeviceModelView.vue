<template>
  <div class="category-manager">
    <CrudHeader 
      :title="$t('nav.device_models')" 
      v-model="crud.showIdColumn.value" 
      @add="crud.openAddDialog(resetForm)" 
    >
      <label class="header-toggle-wrapper">
        <input type="checkbox" v-model="showArchived" />
        {{ $t('master_data.show_archived') }}
      </label>
    </CrudHeader>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-if="crud.showIdColumn.value" class="id-column">{{ $t('common.id') }}</th>
            <th style="width: 20%;">
              <ColumnHeaderFilter :title="$t('common.name')" v-model="columnFilters.name" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 15%;">
              <ColumnHeaderFilter :title="$t('master_data.manufacturer')" v-model="columnFilters.manufacturer" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 15%;">
              <ColumnHeaderFilter :title="$t('master_data.category')" v-model="columnFilters.category" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 15%;">
              <ColumnHeaderMultiFilter 
                :title="$t('common.eeg_channel')" 
                v-model="columnFilters.channels" 
                :options="channels"
                :placeholder="$t('common.search')" 
                :filterTitle="$t('common.must_include')" 
              />
            </th> 
            <th style="width: 10%;">{{ $t('common.status') }}</th>
            <th class="actions-column" style="width: 15%;">{{ $t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredItems.length === 0">
            <td :colspan="crud.showIdColumn.value ? 7 : 6" class="empty-state">{{ $t('common.no_data') }}</td>
          </tr>
          <tr 
            v-for="item in filteredItems" 
            :key="item.id"
            :style="item.is_archived ? 'opacity: 0.6; background-color: #f8f9fa;' : ''"
          >
            <td v-if="crud.showIdColumn.value" class="id-column">{{ item.id }}</td>
            <td>
              <strong>{{ item.name }}</strong>
              <span v-if="item.is_locked" style="margin-left: 8px; cursor: help;" :title="$t('master_data.is_locked')">🔒</span>
            </td>
            <td>{{ getManufacturerName(item.manufacturer) }}</td>
            <td><span class="badge category-badge">{{ getCategoryName(item.category) }}</span></td>
            
            <td class="channels-cell" :title="item.channel_names">
              <span class="badge secondary-badge">{{ item.channel_names || '-' }}</span>
            </td>

            <td>
              <span v-if="item.is_archived" class="badge danger-badge">{{ $t('master_data.archived') }}</span>
              <span v-else class="badge success-badge">{{ $t('common.active') }}</span>
            </td>
            
            <td class="actions-column">
              <div style="display: flex; gap: 8px; justify-content: flex-end;">
                <button 
                  type="button" 
                  class="btn-icon" 
                  style="cursor: pointer; background: none; border: none; font-size: 1.1rem;"
                  :title="$t('master_data.edit_metadata')" 
                  @click="openMetadataTabs(item)"
                >
                  🏷️
                </button>
                <TableActionButtons 
                  @edit="crud.openEditDialog(item.id, () => populateForm(item))" 
                  @delete="handleSmartDelete(item)" 
                />
              </div>
            </td>
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
        <div class="form-group">
          <label>{{ $t('common.name') }} *</label>
          <input type="text" v-model="formData.name" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value?.name }" />
          <BaseInputError :message="crud.fieldErrors.value?.name" />
        </div>

        <div class="form-row" style="display: flex; gap: 1rem; margin-bottom: 1rem;">
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('master_data.manufacturer') }}</label>
            <BaseSearchSelect 
              v-model="formData.manufacturer"
              :options="manufacturers"
              :error="crud.fieldErrors.value?.manufacturer"
            />
          </div>
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('master_data.category') }}</label>
            <BaseSearchSelect 
              v-model="formData.category"
              :options="categories"
              :nullLabel="$t('master_data.none')"
              :error="crud.fieldErrors.value?.category"
            />
          </div>
        </div>

        <div class="form-group inline-flex">
          <input type="checkbox" v-model="formData.is_eeg" id="isEegDevice" :disabled="crud.isEditing.value && activeItemLocked" />
          <label for="isEegDevice">{{ $t('master_data.is_eeg') }}</label>
        </div>

        <div class="form-group" v-if="formData.is_eeg" style="margin-bottom: 20px;">
          <label>{{ $t('common.eeg_channel') }}</label>
          <BaseCheckboxGroup 
            v-model="formData.channels" 
            :options="channels" 
            :searchable="true"
            :searchPlaceholder="$t('common.search')"
            :disabled="crud.isEditing.value && activeItemLocked"
          />
          <BaseInputError :message="crud.fieldErrors.value?.channels" />
        </div>

        <div style="border-top: 2px solid #f4f7f6; padding-top: 20px; margin-bottom: 1.5rem;">
          <div class="form-group" style="margin-bottom: 15px;">
            <label style="color: #2980b9; font-weight: bold; margin-bottom: 10px; display: block;">{{ $t('master_data.hardware_specs') }}</label>
            <BaseSearchSelect 
              v-model="formData.hardware_specs_group_id" 
              :options="metadataGroups" 
              :placeholder="$t('master_data.select_specs_group')"
              :nullLabel="$t('master_data.none')"
            />
            <small class="hint-text">{{ $t('master_data.device_specs_hint') }}</small>
          </div>

          <div class="form-group">
            <label style="color: #27ae60; font-weight: bold; margin-bottom: 10px; display: block;">{{ $t('master_data.default_settings') }}</label>
            <BaseSearchSelect 
              v-model="formData.default_settings_group_id" 
              :options="metadataGroups" 
              :placeholder="$t('master_data.select_settings_group')"
              :nullLabel="$t('master_data.none')"
            />
            <small class="hint-text">{{ $t('master_data.device_settings_hint') }}</small>
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-secondary" @click="crud.closeDialog">{{ $t('actions.cancel') }}</button>
          <button type="submit" class="btn-primary">{{ $t('actions.save') }}</button>
        </div>
      </form>
    </BaseModal>

    <BaseModal 
      :isOpen="showArchiveWarning" 
      :title="$t('master_data.archive_warning_title')" 
      @close="showArchiveWarning = false"
    >
      <div style="padding: 10px 0 20px 0;">
        <p>{{ $t('master_data.archive_warning_text') }}</p>
      </div>
      <div class="modal-actions">
        <button class="btn-secondary" @click="showArchiveWarning = false">{{ $t('actions.cancel') }}</button>
        <button class="btn-primary danger-badge" @click="executeArchive">{{ $t('master_data.archived') }}</button>
      </div>
    </BaseModal>

    <DeviceMetadataManagerModal
      v-if="showMetadataTabsModal"
      :isOpen="showMetadataTabsModal"
      :device="activeDeviceForMetadata"
      @close="closeMetadataTabs"
    />
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
import DeviceMetadataManagerModal from '@/components/domain/DeviceMetadataManagerModal.vue'

const { t } = useI18n()
const crud = useCrud()
const { requireConfirmation, showWarning } = useGlobalModal()

const items = ref([])
const categories = ref([])
const manufacturers = ref([])
const channels = ref([])
const metadataGroups = ref([])

const showArchived = ref(false)
const showArchiveWarning = ref(false)
const deviceToArchiveId = ref(null)

const showMetadataTabsModal = ref(false)
const activeDeviceForMetadata = ref(null)

const columnFilters = ref({
  name: '',
  manufacturer: '',
  category: '',
  channels: [] 
})

const activeItemLocked = computed(() => {
  if (!crud.isEditing.value) return false
  const item = items.value.find(i => i.id === crud.editingId.value)
  return item ? item.is_locked : false
})

const filteredItems = computed(() => {
  return items.value.filter(item => {
    if (!showArchived.value && item.is_archived) return false

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
      const itemChannels = item.channels || []
      const hasAllRequired = columnFilters.value.channels.every(reqId => itemChannels.includes(reqId))
      if (!hasAllRequired) return false
    }
    return true
  })
})

const formData = ref({ 
  name: '', 
  manufacturer: null, 
  category: null, 
  is_eeg: false, 
  channels: [],
  hardware_specs_group_id: null,
  default_settings_group_id: null
})

const resetForm = () => { 
  formData.value = { 
    name: '', 
    manufacturer: null, 
    category: null, 
    is_eeg: false, 
    channels: [],
    hardware_specs_group_id: null,
    default_settings_group_id: null
  } 
}

const populateForm = (item) => { 
  formData.value = { 
    name: item.name, 
    manufacturer: item.manufacturer, 
    category: item.category,
    is_eeg: item.is_eeg !== undefined ? item.is_eeg : false,
    channels: item.channels || [],
    hardware_specs_group_id: item.current_hardware_specs_group_id || null,
    default_settings_group_id: item.current_default_settings_group_id || null
  } 
}

const loadData = async () => {
  try {
    const [resModels, resCats, resManuf, resChannels, mdRes] = await Promise.all([
      api.get('device-models/'),
      api.get('category/device-model/'),
      api.get('manufacturers/'),
      api.get('eeg-channels/'),
      api.get('metadata/groups/')
    ])
    items.value = resModels.data
    categories.value = resCats.data
    manufacturers.value = resManuf.data
    channels.value = resChannels.data 
    metadataGroups.value = mdRes.data
  } catch (error) {}
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
    crud.fieldErrors.value = { name: t('errors.required_field') }
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

const handleSmartDelete = (item) => {
  if (item.is_locked) {
    deviceToArchiveId.value = item.id
    showArchiveWarning.value = true
  } else {
    confirmAndDelete(item.id)
  }
}

const executeArchive = async () => {
  try {
    await api.patch(`device-models/${deviceToArchiveId.value}/`, { is_archived: true })
    showArchiveWarning.value = false
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
      crud.handleFormError(error, t)
    }
  })
}

const openMetadataTabs = (item) => {
  activeDeviceForMetadata.value = item;
  showMetadataTabsModal.value = true;
}

const closeMetadataTabs = () => {
  showMetadataTabsModal.value = false;
  loadData(); 
}

onMounted(() => { loadData() })
</script>

<style scoped>
.table-container { overflow: visible !important; }
.inline-flex { display: flex; align-items: center; gap: 8px; margin-top: 15px; margin-bottom: 15px; }
.inline-flex input { margin: 0; width: auto; cursor: pointer; height: 18px; width: 18px; }
.inline-flex label { margin: 0; font-weight: 600; cursor: pointer; color: var(--text-main); }

.hint-text { color: #95a5a6; display: block; margin-top: 8px; font-size: 0.85rem; }
.danger-badge { background-color: #e74c3c !important; color: white !important; border: none; }
.success-badge { background-color: #2ecc71 !important; color: white !important; }
</style>
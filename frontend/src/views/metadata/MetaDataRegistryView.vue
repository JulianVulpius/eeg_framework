<template>
  <div class="category-manager">
    <div class="page-header">
      <h1>{{ $t('nav.registry_setup') }}</h1>
      <div class="header-actions">
        <button class="btn-primary" @click="openAddDialog">{{ $t('actions.add_new') }}</button>
      </div>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th style="width: 30%;">
              <ColumnHeaderFilter 
                :title="$t('views.registry.target_table')" 
                v-model="columnFilters.target_table" 
                :placeholder="$t('common.search')" 
              />
            </th>
            <th style="width: 40%;">
              <ColumnHeaderMultiFilter 
                :title="$t('views.registry.allowed_categories')" 
                v-model="columnFilters.categories" 
                :options="categories"
                :placeholder="$t('common.search')" 
                :filterTitle="$t('common.must_include')"
              />
            </th>
            <th style="width: 15%;">
              <ColumnHeaderSelectFilter 
                :title="$t('views.registry.active')" 
                v-model="columnFilters.is_active" 
                :options="activeOptions"
                :placeholder="$t('master_data.none')" 
              />
            </th>
            <th class="actions-column">{{ $t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredGroupedItems.length === 0">
            <td colspan="4" class="empty-state">{{ $t('common.no_data') }}</td>
          </tr>
          <tr v-for="group in filteredGroupedItems" :key="group.target_table">
            <td><strong>{{ group.tableName }}</strong></td>
            
            <td>
              <div class="badge-container">
                <span class="badge category-badge" v-for="catId in group.categories" :key="catId">
                  {{ getCategoryName(catId) }}
                </span>
              </div>
            </td>
            
            <td>
              <span :style="{ color: group.isActive ? '#2ecc71' : '#e74c3c', fontWeight: 'bold' }">
                {{ group.isActive ? $t('views.registry.yes') : $t('views.registry.no') }}
              </span>
            </td>
            <td class="actions-cell">
              <button class="btn-icon" @click="openEditDialog(group)" :title="$t('actions.edit')">✏️</button>
              <button class="btn-icon" @click="requestDelete(group)" :title="$t('actions.delete')">🗑️</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <BaseModal 
      :isOpen="isDialogOpen" 
      :title="isEditing ? $t('views.registry.edit_title') : $t('views.registry.add_title')"
      customClass="large-modal"
      @close="closeDialog"
    >
      <form @submit.prevent="saveRecord">
        
        <div class="form-group">
          <label>{{ $t('views.registry.target_table') }} *</label>
          <div class="searchable-select" v-click-outside="() => showTableDropdown = false">
            <input 
              type="text" 
              v-model="tableSearchQuery" 
              class="form-control"
              :class="{ 'input-invalid': fieldErrorTable }"
              @focus="showTableDropdown = true"
              :disabled="isEditing"
              :placeholder="$t('views.registry.search_table')" 
            />
            <ul v-if="showTableDropdown && !isEditing" class="dropdown-list">
              <li v-for="ct in filteredContentTypes" :key="ct.id" @click="selectTargetTable(ct)">
                {{ ct.model }}
              </li>
              <li v-if="filteredContentTypes.length === 0" class="no-results">{{ $t('views.registry.no_tables_found') }}</li>
            </ul>
          </div>
          <BaseInputError :message="fieldErrorTable" />
        </div>

        <div class="form-group inline-flex">
          <input type="checkbox" v-model="formData.is_active" id="isActive" />
          <label for="isActive">{{ $t('views.registry.set_all_active') }}</label>
        </div>

        <BaseTransferList
          v-model="formData.selected_categories"
          :options="categories"
          :leftTitle="$t('views.registry.available_categories')"
          :rightTitle="$t('views.registry.assigned_categories')"
          :searchPlaceholder="$t('common.search')"
        />

        <div class="modal-actions" style="margin-top: 20px;">
          <button type="button" class="btn-secondary" @click="closeDialog">{{ $t('actions.cancel') }}</button>
          <button type="submit" class="btn-primary" :disabled="!formData.target_table">{{ $t('actions.save') }}</button>
        </div>
      </form>
    </BaseModal>

    <ConfirmDeleteModal :isOpen="isConfirmOpen" @cancel="cancelDelete" @confirm="executeDelete" />
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
import BaseTransferList from '@/components/ui/BaseTransferList.vue'
import ConfirmDeleteModal from '@/components/ui/ConfirmDeleteModal.vue'
import WarningModal from '@/components/ui/WarningModal.vue'

import ColumnHeaderFilter from '@/components/table/ColumnHeaderFilter.vue'
import ColumnHeaderMultiFilter from '@/components/table/ColumnHeaderMultiFilter.vue'
import ColumnHeaderSelectFilter from '@/components/table/ColumnHeaderSelectFilter.vue'

const { t } = useI18n()
const crud = useCrud() 

const rawRegistryItems = ref([])
const categories = ref([])
const contentTypes = ref([])

// Column Filter State
const columnFilters = ref({
  target_table: '',
  categories: [],
  is_active: ''
})

const isDialogOpen = ref(false)
const isEditing = ref(false)
const isConfirmOpen = ref(false)
const groupToDelete = ref(null)

const showWarningModal = ref(false)
const warningMessage = ref('')
const fieldErrorTable = ref('')

const showTableDropdown = ref(false)
const tableSearchQuery = ref('')

const formData = ref({ target_table: null, selected_categories: [], original_registry_items: [], is_active: true })

const activeOptions = computed(() => [
  { value: 'true', label: t('views.registry.yes') },
  { value: 'false', label: t('views.registry.no') }
])

const loadData = async () => {
  try {
    const [resReg, resCats, resCt] = await Promise.all([
      api.get('metadata/registry/'),
      api.get('category/metadata-group/'),
      api.get('content-types/') 
    ])
    rawRegistryItems.value = resReg.data
    categories.value = resCats.data
    contentTypes.value = resCt.data
  } catch (error) {
    warningMessage.value = crud.parseApiError(error, t, 'errors.load_failed')
    showWarningModal.value = true
  }
}

const groupedRegistry = computed(() => {
  const groups = {}
  rawRegistryItems.value.forEach(item => {
    if (!groups[item.target_table]) {
      groups[item.target_table] = { target_table: item.target_table, tableName: getTableName(item.target_table), categories: [], registryItems: [], isActive: item.is_active }
    }
    groups[item.target_table].categories.push(item.allowed_category)
    groups[item.target_table].registryItems.push(item)
  })
  return Object.values(groups)
})

const filteredGroupedItems = computed(() => {
  return groupedRegistry.value.filter(group => {
    if (columnFilters.value.target_table) {
      const q = columnFilters.value.target_table.toLowerCase()
      if (!group.tableName.toLowerCase().includes(q)) return false
    }

    if (columnFilters.value.categories && columnFilters.value.categories.length > 0) {
      const hasAllRequired = columnFilters.value.categories.every(reqId => group.categories.includes(reqId))
      if (!hasAllRequired) return false
    }

    if (columnFilters.value.is_active !== '') {
      const isFilterActive = columnFilters.value.is_active === 'true'
      if (group.isActive !== isFilterActive) return false
    }

    return true
  })
})

const usedTableIds = computed(() => groupedRegistry.value.map(group => group.target_table))

const filteredContentTypes = computed(() => {
  const availableCts = contentTypes.value.filter(ct => !usedTableIds.value.includes(ct.id))
  if (!tableSearchQuery.value) return availableCts
  return availableCts.filter(ct => ct.model.toLowerCase().includes(tableSearchQuery.value.toLowerCase()))
})

const selectTargetTable = (ct) => {
  formData.value.target_table = ct.id
  tableSearchQuery.value = ct.model
  showTableDropdown.value = false
  fieldErrorTable.value = ''
}

const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = function(event) {
      if (!(el === event.target || el.contains(event.target))) { binding.value(event) }
    }
    document.body.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) { document.body.removeEventListener('click', el.clickOutsideEvent) }
}

const getTableName = (id) => { const ct = contentTypes.value.find(c => c.id === id); return ct ? ct.model : t('views.registry.unknown') }
const getCategoryName = (id) => { const cat = categories.value.find(c => c.id === id); return cat ? cat.name : t('views.registry.unknown') }

const openAddDialog = () => {
  fieldErrorTable.value = ''
  isEditing.value = false
  tableSearchQuery.value = ''
  formData.value = { target_table: null, selected_categories: [], original_registry_items: [], is_active: true }
  isDialogOpen.value = true
}

const openEditDialog = (group) => {
  fieldErrorTable.value = ''
  isEditing.value = true
  tableSearchQuery.value = group.tableName
  formData.value = { target_table: group.target_table, selected_categories: [...group.categories], original_registry_items: [...group.registryItems], is_active: group.isActive }
  isDialogOpen.value = true
}

const closeDialog = () => { isDialogOpen.value = false }

const requestDelete = (group) => { groupToDelete.value = group; isConfirmOpen.value = true }
const cancelDelete = () => { isConfirmOpen.value = false; groupToDelete.value = null }

const saveRecord = async () => {
  fieldErrorTable.value = ''
  if (!formData.value.target_table) { fieldErrorTable.value = t('errors.required_field'); return }

  try {
    const tableId = formData.value.target_table
    const currentCats = formData.value.selected_categories
    const oldItems = formData.value.original_registry_items
    const oldCatIds = oldItems.map(item => item.allowed_category)

    const toAdd = currentCats.filter(id => !oldCatIds.includes(id))
    const toRemoveItems = oldItems.filter(item => !currentCats.includes(item.allowed_category))
    const toKeepItems = oldItems.filter(item => currentCats.includes(item.allowed_category))

    const apiCalls = []

    toRemoveItems.forEach(item => { apiCalls.push(api.delete(`metadata/registry/${item.id}/`)) })
    toAdd.forEach(catId => { apiCalls.push(api.post('metadata/registry/', { target_table: tableId, allowed_category: catId, is_active: formData.value.is_active, description: 'Assigned via UI' })) })
    toKeepItems.forEach(item => {
      if (item.is_active !== formData.value.is_active) { apiCalls.push(api.patch(`metadata/registry/${item.id}/`, { is_active: formData.value.is_active })) }
    })

    await Promise.all(apiCalls)
    crud.notifySuccess('updated', t)
    closeDialog()
    await loadData()
  } catch (error) {
    warningMessage.value = crud.parseApiError(error, t, 'errors.save_failed')
    showWarningModal.value = true
  }
}

const executeDelete = async () => {
  try {
    const apiCalls = groupToDelete.value.registryItems.map(item => api.delete(`metadata/registry/${item.id}/`))
    await Promise.all(apiCalls)
    crud.notifySuccess('deleted', t)
    isConfirmOpen.value = false
    groupToDelete.value = null
    await loadData()
  } catch (error) {
    isConfirmOpen.value = false
    warningMessage.value = crud.parseApiError(error, t, 'errors.delete_failed')
    showWarningModal.value = true
  }
}

onMounted(() => { loadData() })
</script>
<template>
  <div class="page-group-manager">
    <CrudHeader 
      :title="$t('nav.page_groups')" 
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
                :title="$t('master_data.category')" 
                v-model="columnFilters.category" 
                :placeholder="$t('common.search')" 
              />
            </th>
            <th style="width: 25%;">
              <ColumnHeaderFilter 
                :title="$t('common.description')" 
                v-model="columnFilters.description" 
                :placeholder="$t('common.search')" 
              />
            </th>
            <th style="width: 20%;">
              <ColumnHeaderFilter 
                :title="$t('common.creator')" 
                v-model="columnFilters.creator" 
                :placeholder="$t('common.search')" 
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
            <td><span class="badge category-badge">{{ getCategoryName(item.category) }}</span></td>
            <td>{{ item.description || '-' }}</td>
            <td>{{ item.creator || '-' }}</td>
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

        <div class="form-group" style="margin-bottom: 1.5rem;">
          <label>{{ $t('common.description') }}</label>
          <textarea v-model="formData.description" rows="2" class="form-control"></textarea>
        </div>

        <div class="form-group">
          <label style="font-weight: bold; font-size: 1.1rem; border-bottom: 1px solid #eee; padding-bottom: 5px;">
            {{ $t('views.page_groups.assign_pages') }}
          </label>
          <BaseTransferList
            v-model="formData.pages"
            :options="availablePages"
            :leftTitle="$t('views.page_groups.available_pages')"
            :rightTitle="$t('views.page_groups.selected_pages')"
            :enableOrdering="true"
            :leftFilterFn="filterAvailableLogic"
            :rightFilterFn="filterSelectedLogic"
          >
            <template #left-filters>
              <BaseSearchSelect
                v-model="filterAvailable"
                :options="pageCategories"
                :placeholder="$t('views.metadata.search_category')"
                :nullLabel="$t('views.metadata.filter_category_all')"
              />
            </template>
            <template #right-filters>
              <BaseSearchSelect
                v-model="filterSelected"
                :options="pageCategories"
                :placeholder="$t('views.metadata.search_category')"
                :nullLabel="$t('views.metadata.filter_category_all')"
              />
            </template>
          </BaseTransferList>
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
import { ref, onMounted, computed } from 'vue'
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
import ColumnHeaderFilter from '@/components/ColumnHeaderFilter.vue'

const { t } = useI18n()
const crud = useCrud()

const items = ref([])
const categories = ref([])
const availablePages = ref([])
const pageCategories = ref([])

const showWarningModal = ref(false)
const warningMessage = ref('')

const filterAvailable = ref(null)
const filterSelected = ref(null)

const columnFilters = ref({
  name: '',
  category: '',
  description: '',
  creator: '' 
})

const filterAvailableLogic = (opt) => {
  if (!filterAvailable.value) return true
  return opt.category === filterAvailable.value
}

const filterSelectedLogic = (opt) => {
  if (!filterSelected.value) return true
  return opt.category === filterSelected.value
}

const filteredItems = computed(() => {
  return items.value.filter(item => {
    if (columnFilters.value.name) {
      const q = columnFilters.value.name.toLowerCase()
      if (!item.name.toLowerCase().includes(q)) return false
    }
    if (columnFilters.value.category) {
      const q = columnFilters.value.category.toLowerCase()
      const cName = getCategoryName(item.category).toLowerCase()
      if (!cName.includes(q)) return false
    }
    if (columnFilters.value.description) {
      const q = columnFilters.value.description.toLowerCase()
      if (!item.description || !item.description.toLowerCase().includes(q)) return false
    }
    if (columnFilters.value.creator) {
      const q = columnFilters.value.creator.toLowerCase()
      const creatorName = item.creator ? item.creator.toLowerCase() : ''
      if (!creatorName.includes(q)) return false
    }
    return true
  })
})

const formData = ref({
  name: '',
  category: null,
  description: '',
  pages: []
})

const getCategoryName = (id) => {
  const cat = categories.value.find(c => c.id === id)
  return cat ? cat.name : '-'
}

const resetForm = () => {
  formData.value = { name: '', category: null, description: '', pages: [] }
  filterAvailable.value = null
  filterSelected.value = null 
}

const populateForm = (item) => {
  formData.value = {
    name: item.name,
    category: item.category,
    description: item.description || '',
    pages: item.pages || []
  }
  filterAvailable.value = null
  filterSelected.value = null
}

const loadData = async () => {
  try {
    const [pgRes, catRes, pageRes, pageCatRes] = await Promise.all([
      api.get('page-groups/'),
      api.get('category/page-group-categories/'),
      api.get('pages/'),
      api.get('category/page-categories/')
    ])
    items.value = pgRes.data
    categories.value = catRes.data
    availablePages.value = pageRes.data
    pageCategories.value = pageCatRes.data
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

  try {
    if (crud.isEditing.value) {
      await api.put(`page-groups/${crud.editingId.value}/`, formData.value)
    } else {
      await api.post('page-groups/', formData.value)
    }
    crud.closeDialog()
    loadData()
  } catch (error) {
    crud.handleFormError(error, t, 'errors.save_failed')
  }
}

const executeDelete = async () => {
  try {
    await api.delete(`page-groups/${crud.itemToDelete.value}/`)
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
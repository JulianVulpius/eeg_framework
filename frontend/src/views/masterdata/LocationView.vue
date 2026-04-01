<template>
  <div class="category-manager">
    <CrudHeader 
      :title="$t('nav.locations')" 
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
            <th style="width: 20%;">
              <ColumnHeaderFilter 
                :title="$t('master_data.category')" 
                v-model="columnFilters.category" 
                :placeholder="$t('common.search')" 
              />
            </th>
            <th style="width: 35%;">
              <ColumnHeaderFilter 
                :title="$t('common.description')" 
                v-model="columnFilters.description" 
                :placeholder="$t('common.search')" 
              />
            </th>
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
            <td><span class="badge category-badge">{{ getCategoryName(item.category) }}</span></td>
            <td>{{ item.description || '-' }}</td>
            <TableActionButtons 
              @edit="crud.openEditDialog(item.id, () => populateForm(item))"
              @delete="confirmAndDelete(item.id)"
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
            <label>{{ $t('master_data.category') }}</label>
            <BaseSearchSelect 
              v-model="formData.category" 
              :options="categories" 
              :nullLabel="$t('master_data.none')" 
            />
          </div>
        </div>

        <div class="form-group">
          <label>{{ $t('common.description') }}</label>
          <textarea 
            v-model="formData.description" 
            rows="3" 
            class="form-control"
          ></textarea>
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
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useCrud } from '@/composables/useCrud'
import { useGlobalModal } from '@/composables/useGlobalModal'

import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInputError from '@/components/ui/BaseInputError.vue'
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'
import CrudHeader from '@/components/ui/CrudHeader.vue'

import ColumnHeaderFilter from '@/components/table/ColumnHeaderFilter.vue'
import TableActionButtons from '@/components/table/TableActionButtons.vue'

const { t } = useI18n()
const crud = useCrud()
const { requireConfirmation } = useGlobalModal()

const items = ref([])
const categories = ref([])

const columnFilters = ref({
  name: '',
  category: '',
  description: ''
})

const getCategoryName = (id) => {
  const cat = categories.value.find(c => c.id === id)
  return cat ? cat.name : '-'
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
    return true
  })
})

const formData = ref({
  name: '',
  category: null,
  description: ''
})

const resetForm = () => {
  formData.value = { name: '', category: null, description: '' }
}

const populateForm = (item) => {
  formData.value = {
    name: item.name,
    category: item.category || null,
    description: item.description || ''
  }
}

const loadData = async () => {
  try {
    const [resLocs, resCats] = await Promise.all([
      api.get('locations/'),
      api.get('category/location/')
    ])
    items.value = resLocs.data
    categories.value = resCats.data
  } catch (error) {}
}

const saveRecord = async () => {
  crud.clearErrors()
  let hasError = false

  if (!formData.value.name || formData.value.name.trim() === '') {
    crud.fieldErrors.value.name = t('errors.required_field')
    hasError = true
  }
  
  if (hasError) return

  try {
    if (crud.isEditing.value) {
      await api.put(`locations/${crud.editingId.value}/`, formData.value)
    } else {
      await api.post('locations/', formData.value)
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
      await api.delete(`locations/${id}/`)
      loadData()
    } catch (error) {}
  })
}

onMounted(loadData)
</script>
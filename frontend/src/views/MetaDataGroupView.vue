<template>
  <div class="category-manager">
    <CrudHeader 
      :title="$t('nav.metadata_groups')" 
      v-model="crud.showIdColumn.value" 
      @add="crud.openAddDialog(resetForm)" 
    />

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-if="crud.showIdColumn.value" class="id-column">{{ $t('common.id') }}</th>
            <th style="width: 25%;">
              <ColumnHeaderFilter 
                :title="$t('common.name')" 
                v-model="columnFilters.name" 
                :placeholder="$t('common.search')" 
              />
            </th>
            <th style="width: 20%;">
              <ColumnHeaderFilter 
                :title="$t('views.metadata.category')" 
                v-model="columnFilters.category" 
                :placeholder="$t('common.search')" 
              />
            </th>
            <th>{{ $t('views.metadata.assigned_definitions') }}</th>
            <th style="width: 25%;">
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
            <td :colspan="crud.showIdColumn.value ? 6 : 5" class="empty-state">{{ $t('common.no_data') }}</td>
          </tr>
          <tr v-for="item in filteredItems" :key="item.id">
            <td v-if="crud.showIdColumn.value" class="id-column">{{ item.id }}</td>
            <td><strong>{{ item.name }}</strong></td>
            <td><span class="badge category-badge">{{ getGroupCategoryName(item.category) }}</span></td>
            <td>
              <div class="badge-container">
                <span class="badge secondary-badge" v-for="defId in (item.assigned_definitions || [])" :key="defId">
                  {{ getDefinitionName(defId) }}
                </span>
                <span v-if="!item.assigned_definitions || item.assigned_definitions.length === 0" class="text-muted">-</span>
              </div>
            </td>
            <td>{{ item.description }}</td>
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
      customClass="large-modal"
      @close="crud.closeDialog"
    >
      <form @submit.prevent="saveRecord">
        <div class="form-row">
          <div class="form-group half-width">
            <label>{{ $t('common.name') }} *</label>
            <input 
              type="text" 
              v-model="formData.name" 
              class="form-control"
              :class="{ 'input-invalid': crud.fieldErrors.value.name }"
              :placeholder="$t('modal.name_placeholder')" 
            />
            <BaseInputError :message="crud.fieldErrors.value.name" />
          </div>

          <div class="form-group half-width">
            <BaseSearchSelect 
              v-model="formData.category"
              :options="groupCategories"
              :label="$t('views.metadata.category') + ' *'"
              :error="crud.fieldErrors.value.category"
              :placeholder="$t('views.metadata.select_category')"
            />
          </div>
        </div>

        <div class="form-group">
          <label>{{ $t('common.description') }}</label>
          <textarea 
            v-model="formData.description" 
            rows="2" 
            class="form-control"
            :class="{ 'input-invalid': crud.fieldErrors.value.description }"
            :placeholder="$t('modal.desc_placeholder')"
          ></textarea>
          <BaseInputError :message="crud.fieldErrors.value.description" />
        </div>

        <div class="info-banner">{{ $t('views.metadata.assigned_order_info') }}</div>

        <div class="shuffle-container">
          <div class="shuffle-box">
            <label>{{ $t('views.registry.available_categories') }}</label>
            <div class="filter-row">
              <div class="searchable-select filter-select" v-click-outside="() => showCatDropdown = false">
                <input type="text" v-model="catSearchQuery" @focus="showCatDropdown = true" :placeholder="$t('views.metadata.search_category')" class="shuffle-filter" />
                <ul v-if="showCatDropdown" class="dropdown-list">
                  <li @click="selectDefCategory(null)">{{ $t('views.metadata.filter_category_all') }}</li>
                  <li v-for="cat in filteredDefCats" :key="cat.id" @click="selectDefCategory(cat)">{{ cat.name }}</li>
                </ul>
              </div>
              <input type="text" v-model="searchAvailable" :placeholder="$t('common.search')" class="shuffle-search" />
            </div>
            
            <select multiple v-model="selectedInAvailable" class="shuffle-list">
              <option v-for="def in filteredAvailableDefs" :key="def.id" :value="def.id">{{ def.name }}</option>
            </select>
          </div>

          <div class="shuffle-controls">
            <button type="button" class="btn-shuffle" @click="moveRight" :disabled="!selectedInAvailable.length">🡒</button>
            <button type="button" class="btn-shuffle" @click="moveLeft" :disabled="!selectedInAssigned.length">🡐</button>
          </div>

          <div class="shuffle-box">
            <label>{{ $t('views.registry.assigned_categories') }}</label>
            <input type="text" v-model="searchAssigned" :placeholder="$t('common.search')" class="shuffle-search full-width" />
            
            <div class="list-with-controls">
              <select multiple v-model="selectedInAssigned" class="shuffle-list">
                <option v-for="def in filteredAssignedDefs" :key="def.id" :value="def.id">{{ def.name }}</option>
              </select>
              <div class="order-controls">
                <button type="button" class="btn-order" @click="moveUp" :disabled="!selectedInAssigned.length" :title="$t('views.metadata.move_up')">↑</button>
                <button type="button" class="btn-order" @click="moveDown" :disabled="!selectedInAssigned.length" :title="$t('views.metadata.move_down')">↓</button>
              </div>
            </div>
          </div>
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

const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = function(event) {
      if (!(el === event.target || el.contains(event.target))) binding.value(event)
    }
    document.body.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) { document.body.removeEventListener('click', el.clickOutsideEvent) }
}

const items = ref([])
const groupCategories = ref([])
const definitions = ref([])
const defCategories = ref([])
const crud = useCrud()

const showWarningModal = ref(false)
const warningMessage = ref('')

const columnFilters = ref({
  name: '',
  category: '',
  description: ''
})

const filteredItems = computed(() => {
  return items.value.filter(item => {
    if (columnFilters.value.name) {
      const q = columnFilters.value.name.toLowerCase()
      if (!item.name.toLowerCase().includes(q)) return false
    }
    if (columnFilters.value.category) {
      const q = columnFilters.value.category.toLowerCase()
      const cName = getGroupCategoryName(item.category).toLowerCase()
      if (!cName.includes(q)) return false
    }
    if (columnFilters.value.description) {
      const q = columnFilters.value.description.toLowerCase()
      if (!item.description || !item.description.toLowerCase().includes(q)) return false
    }
    return true
  })
})

const formData = ref({ name: '', category: null, description: '', definitions: [] })

const searchAvailable = ref('')
const searchAssigned = ref('')
const selectedInAvailable = ref([])
const selectedInAssigned = ref([])
const showCatDropdown = ref(false)
const catSearchQuery = ref('')
const filterDefCategory = ref(null)

const resetForm = () => { 
  formData.value = { name: '', category: null, description: '', definitions: [] } 
  searchAvailable.value = ''; searchAssigned.value = ''; filterDefCategory.value = null; catSearchQuery.value = '';
}
const populateForm = (item) => { 
  formData.value = { name: item.name, category: item.category, description: item.description, definitions: item.assigned_definitions ? [...item.assigned_definitions] : [] } 
  searchAvailable.value = ''; searchAssigned.value = ''; filterDefCategory.value = null; catSearchQuery.value = '';
}

const loadData = async () => {
  try {
    const [resGroups, resGroupCats, resDefs, resDefCats] = await Promise.all([
      api.get('metadata/groups/'), api.get('category/metadata-group-categories/'),
      api.get('metadata/definitions/'), api.get('category/metadata-categories/')
    ])
    items.value = resGroups.data; groupCategories.value = resGroupCats.data;
    definitions.value = resDefs.data; defCategories.value = resDefCats.data;
  } catch (error) { 
    warningMessage.value = crud.parseApiError(error, t, 'errors.load_failed')
    showWarningModal.value = true
  }
}

const getGroupCategoryName = (id) => { const cat = groupCategories.value.find(c => c.id === id); return cat ? cat.name : 'Unknown' }
const getDefinitionName = (id) => { const def = definitions.value.find(d => d.id === id); return def ? def.name : `ID:${id}` }

const filteredDefCats = computed(() => !catSearchQuery.value ? defCategories.value : defCategories.value.filter(c => c.name.toLowerCase().includes(catSearchQuery.value.toLowerCase())))
const selectDefCategory = (cat) => { if (cat === null) { filterDefCategory.value = null; catSearchQuery.value = '' } else { filterDefCategory.value = cat.id; catSearchQuery.value = cat.name }; showCatDropdown.value = false }

const filteredAvailableDefs = computed(() => {
  let available = definitions.value.filter(d => !formData.value.definitions.includes(d.id))
  if (filterDefCategory.value) available = available.filter(d => d.category === filterDefCategory.value)
  if (searchAvailable.value) available = available.filter(d => d.name.toLowerCase().includes(searchAvailable.value.toLowerCase()))
  return available
})
const filteredAssignedDefs = computed(() => {
  let assigned = formData.value.definitions.map(id => definitions.value.find(d => d.id === id)).filter(d => d)
  if (searchAssigned.value) assigned = assigned.filter(d => d.name.toLowerCase().includes(searchAssigned.value.toLowerCase()))
  return assigned
})

const moveRight = () => { formData.value.definitions.push(...selectedInAvailable.value); selectedInAvailable.value = [] }
const moveLeft = () => { formData.value.definitions = formData.value.definitions.filter(id => !selectedInAssigned.value.includes(id)); selectedInAssigned.value = [] }
const moveUp = () => {
  const selected = [...selectedInAssigned.value].sort((a, b) => formData.value.definitions.indexOf(a) - formData.value.definitions.indexOf(b))
  selected.forEach(id => {
    const idx = formData.value.definitions.indexOf(id)
    if (idx > 0) { const temp = formData.value.definitions[idx - 1]; formData.value.definitions[idx - 1] = id; formData.value.definitions[idx] = temp }
  })
}
const moveDown = () => {
  const selected = [...selectedInAssigned.value].sort((a, b) => formData.value.definitions.indexOf(b) - formData.value.definitions.indexOf(a))
  selected.forEach(id => {
    const idx = formData.value.definitions.indexOf(id)
    if (idx < formData.value.definitions.length - 1 && idx !== -1) { const temp = formData.value.definitions[idx + 1]; formData.value.definitions[idx + 1] = id; formData.value.definitions[idx] = temp }
  })
}

const saveRecord = async () => {
  crud.clearErrors()
  
  const trimmedName = formData.value.name.trim()
  if (!trimmedName) {
    crud.fieldErrors.value.name = t('errors.required_field')
    return
  }
  
  if (!formData.value.category) {
    crud.fieldErrors.value.category = t('errors.required_field')
    return
  }

  if (items.value.some(item => item.name.toLowerCase() === trimmedName.toLowerCase() && item.id !== crud.editingId.value)) {
    crud.fieldErrors.value.name = t('errors.duplicate_entry')
    return 
  }

  try {
    formData.value.name = trimmedName
    if (crud.isEditing.value) await api.put(`metadata/groups/${crud.editingId.value}/`, formData.value)
    else await api.post('metadata/groups/', formData.value)
    crud.closeDialog()
    loadData()
  } catch (error) { 
    crud.handleFormError(error, t, 'errors.save_failed')
  }
}

const executeDelete = async () => {
  try {
    await api.delete(`metadata/groups/${crud.itemToDelete.value}/`)
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
.text-muted { color: #bdc3c7; font-style: italic; }
.badge-container { display: flex; flex-wrap: wrap; gap: 6px; }
.form-row { display: flex; gap: 20px; align-items: flex-start; }
.half-width { flex: 1; }
.info-banner { background-color: #e8f4fd; color: #2980b9; padding: 12px; border-radius: 6px; font-size: 0.9rem; margin-bottom: 15px; border-left: 4px solid #3498db; }
.searchable-select { position: relative; }
.filter-select { flex: 1; }
.dropdown-list { position: absolute; top: 100%; left: 0; right: 0; background: white; border: 1px solid #ddd; border-radius: 4px; max-height: 200px; overflow-y: auto; z-index: 10; padding: 0; margin: 5px 0 0 0; list-style: none; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
.dropdown-list li { padding: 10px; cursor: pointer; border-bottom: 1px solid #eee; font-size: 0.85rem;}
.dropdown-list li:hover { background-color: #f8f9fa; color: #3498db; }
.shuffle-container { display: flex; justify-content: space-between; align-items: stretch; gap: 15px; }
.shuffle-box { flex: 1; display: flex; flex-direction: column; gap: 10px; }
.shuffle-box label { font-size: 0.9rem; margin: 0; color: #7f8c8d; font-weight: 600;}
.filter-row { display: flex; gap: 10px; align-items: stretch; }
.shuffle-filter { width: 100%; padding: 6px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem; font-family: inherit;}
.shuffle-search { flex: 1; padding: 6px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem; }
.full-width { width: 100%; }
.shuffle-list { height: 250px; width: 100%; padding: 5px; border: 1px solid #ddd; border-radius: 4px; font-family: inherit; }
.shuffle-controls { display: flex; flex-direction: column; justify-content: center; gap: 10px; }
.btn-shuffle { background: #ecf0f1; border: 1px solid #bdc3c7; border-radius: 4px; padding: 10px; cursor: pointer; font-weight: bold; transition: 0.2s; }
.btn-shuffle:hover:not(:disabled) { background: #bdc3c7; }
.btn-shuffle:disabled { opacity: 0.4; cursor: not-allowed; }
.list-with-controls { display: flex; gap: 10px; align-items: stretch; }
.order-controls { display: flex; flex-direction: column; justify-content: center; gap: 10px; }
.btn-order { background: #fdfefe; border: 1px solid #d0d3d4; color: #34495e; border-radius: 4px; padding: 8px; cursor: pointer; font-weight: bold; font-size: 1.1rem; transition: 0.2s; }
.btn-order:hover:not(:disabled) { background: #e5e8e8; }
.btn-order:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
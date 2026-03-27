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
            <th style="width: 15%;">
              <ColumnHeaderFilter :title="$t('common.name')" v-model="columnFilters.name" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 15%;">
              <ColumnHeaderDateFilter :title="$t('views.events.start')" v-model="columnFilters.event_start" />
            </th>
            <th style="width: 15%;">
              <ColumnHeaderDateFilter :title="$t('views.events.end')" v-model="columnFilters.event_end" />
            </th>
            <th style="width: 15%;">
              <ColumnHeaderFilter :title="$t('nav.locations')" v-model="columnFilters.location" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 15%;">
              <ColumnHeaderFilter :title="$t('master_data.category')" v-model="columnFilters.category" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 15%;">
              <ColumnHeaderFilter :title="$t('common.creator')" v-model="columnFilters.creator" :placeholder="$t('common.search')" />
            </th>
            <th class="actions-column">{{ $t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredItems.length === 0">
            <td :colspan="crud.showIdColumn.value ? 8 : 7" class="empty-state">{{ $t('common.no_data') }}</td>
          </tr>
          <tr v-for="item in filteredItems" :key="item.id">
            <td v-if="crud.showIdColumn.value" class="id-column">{{ item.id }}</td>
            <td><strong>{{ item.name }}</strong></td>
            <td>{{ formatDisplayDate(item.event_start) }}</td>
            <td>{{ formatDisplayDate(item.event_end) }}</td>
            <td>{{ getLocationName(item.location) }}</td>
            <td><span class="badge category-badge">{{ getCategoryName(item.category) }}</span></td>
            <td>{{ item.creator || '-' }}</td>
            <TableActionButtons @edit="crud.openEditDialog(item.id, () => populateForm(item))" @delete="crud.requestDelete(item.id)" />
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
            <input type="text" v-model="formData.name" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.name }" />
            <BaseInputError :message="crud.fieldErrors.value.name" />
          </div>
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('master_data.category') }} *</label>
            <BaseSearchSelect v-model="formData.category" :options="categories" :placeholder="$t('views.events.select_category')" :error="crud.fieldErrors.value.category" />
          </div>
        </div>

        <div class="form-group" style="margin-bottom: 1rem;">
          <label>{{ $t('nav.locations') }}</label>
          <BaseSearchSelect v-model="formData.location" :options="locations" :placeholder="$t('common.search')" :nullLabel="$t('master_data.none')" />
        </div>

        <div class="form-group" style="margin-bottom: 1.5rem;">
          <label>{{ $t('common.description') }}</label>
          <textarea v-model="formData.description" rows="2" class="form-control"></textarea>
        </div>

        <div class="form-row" style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('views.events.start') }}</label>
            <div style="display: flex; gap: 10px;">
              <input type="date" v-model="formData.event_start" class="form-control" />
              <input v-if="formData.event_start" type="time" v-model="formData.event_start_time" class="form-control" style="max-width: 130px;" title="Optional Time" />
            </div>
          </div>
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('views.events.end') }}</label>
            <div style="display: flex; gap: 10px;">
              <input type="date" v-model="formData.event_end" class="form-control" />
              <input v-if="formData.event_end" type="time" v-model="formData.event_end_time" class="form-control" style="max-width: 130px;" title="Optional Time" />
            </div>
          </div>
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
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useCrud } from '@/composables/useCrud'

import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInputError from '@/components/ui/BaseInputError.vue'
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'
import BaseTransferList from '@/components/ui/BaseTransferList.vue'
import ConfirmDeleteModal from '@/components/ui/ConfirmDeleteModal.vue'
import WarningModal from '@/components/ui/WarningModal.vue'
import CrudHeader from '@/components/ui/CrudHeader.vue'

import ColumnHeaderFilter from '@/components/table/ColumnHeaderFilter.vue'
import ColumnHeaderDateFilter from '@/components/table/ColumnHeaderDateFilter.vue'
import TableActionButtons from '@/components/table/TableActionButtons.vue'

const { t } = useI18n()
const crud = useCrud()

const items = ref([])
const categories = ref([])
const pageGroups = ref([])
const locations = ref([]) 

const showWarningModal = ref(false)
const warningMessage = ref('')

const columnFilters = ref({
  name: '',
  event_start: '',
  event_end: '',
  location: '',
  category: '',
  creator: ''
})

const getLocationName = (id) => {
  if (!id) return '-'
  const loc = locations.value.find(l => l.id === id)
  return loc ? loc.name : id
}

const getCategoryName = (id) => {
  if (!id) return '-'
  const cat = categories.value.find(c => c.id === id)
  return cat ? cat.name : id
}

const filteredItems = computed(() => {
  return items.value.filter(item => {
    if (columnFilters.value.name && !item.name.toLowerCase().includes(columnFilters.value.name.toLowerCase())) return false
    if (columnFilters.value.event_start && (!item.event_start || !item.event_start.startsWith(columnFilters.value.event_start))) return false
    if (columnFilters.value.event_end && (!item.event_end || !item.event_end.startsWith(columnFilters.value.event_end))) return false
    if (columnFilters.value.location) {
      const locName = getLocationName(item.location).toLowerCase()
      if (!locName.includes(columnFilters.value.location.toLowerCase())) return false
    }
    if (columnFilters.value.category) {
      const catName = getCategoryName(item.category).toLowerCase()
      if (!catName.includes(columnFilters.value.category.toLowerCase())) return false
    }
    if (columnFilters.value.creator) {
      const creatorName = item.creator ? item.creator.toLowerCase() : ''
      if (!creatorName.includes(columnFilters.value.creator.toLowerCase())) return false
    }
    return true
  })
})

const formData = ref({
  name: '',
  category: null,
  description: '',
  location: null,
  event_start: '',
  event_start_time: '',
  event_end: '',
  event_end_time: '',
  page_groups: []
})

const extractDatePart = (isoString) => {
  if (!isoString) return ''
  return isoString.split('T')[0]
}

const extractTimePart = (isoString) => {
  if (!isoString || !isoString.includes('T')) return ''
  return isoString.split('T')[1].substring(0, 5)
}

const formatDisplayDate = (isoString) => {
  if (!isoString) return '-'
  const date = new Date(isoString)
  const timeString = extractTimePart(isoString)
  if (timeString === '00:00') {
    return date.toLocaleDateString(undefined, { year: 'numeric', month: '2-digit', day: '2-digit' })
  } else {
    return date.toLocaleString(undefined, { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' })
  }
}

const resetForm = () => {
  formData.value = { 
    name: '', category: null, description: '', location: null,
    event_start: '', event_start_time: '', 
    event_end: '', event_end_time: '', 
    page_groups: [] 
  }
}

const populateForm = (item) => {
  formData.value = {
    name: item.name,
    category: item.category,
    description: item.description || '',
    location: item.location || null,
    event_start: extractDatePart(item.event_start),
    event_start_time: extractTimePart(item.event_start),
    event_end: extractDatePart(item.event_end),
    event_end_time: extractTimePart(item.event_end),
    page_groups: item.page_groups || []
  }
}

const loadData = async () => {
  try {
    const [eventsRes, catRes, pgRes, locRes] = await Promise.all([
      api.get('events/'),
      api.get('category/event-categories/'),
      api.get('page-groups/'),
      api.get('locations/')
    ])
    items.value = eventsRes.data
    categories.value = catRes.data
    pageGroups.value = pgRes.data
    locations.value = locRes.data
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

  const payload = { ...formData.value }
  
  if (payload.event_start) {
    const time = payload.event_start_time || '00:00'
    payload.event_start = `${payload.event_start}T${time}:00Z`
  } else {
    payload.event_start = null
  }

  if (payload.event_end) {
    const time = payload.event_end_time || '00:00'
    payload.event_end = `${payload.event_end}T${time}:00Z`
  } else {
    payload.event_end = null
  }
  
  delete payload.event_start_time
  delete payload.event_end_time

  try {
    if (crud.isEditing.value) {
      await api.put(`events/${crud.editingId.value}/`, payload)
      crud.notifySuccess('updated', t)
    } else {
      await api.post('events/', payload)
      crud.notifySuccess('created', t)
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
    crud.notifySuccess('deleted', t)
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
<template>
  <div class="category-manager">
    <CrudHeader 
      :title="$t('nav.playlists')" 
      v-model="crud.showIdColumn.value" 
      @add="crud.openAddDialog(resetForm)" 
    />

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-if="crud.showIdColumn.value" class="id-column">{{ $t('common.id') }}</th>
            <th style="width: 50%;">
              <ColumnHeaderFilter 
                :title="$t('common.name')" 
                v-model="columnFilters.name" 
                :placeholder="$t('common.search')" 
              />
            </th>
            <th>Items in Playlist</th>
            <th class="actions-column">{{ $t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredItems.length === 0">
            <td :colspan="crud.showIdColumn.value ? 4 : 3" class="empty-state">{{ $t('common.no_data') }}</td>
          </tr>
          <tr v-for="item in filteredItems" :key="item.id">
            <td v-if="crud.showIdColumn.value" class="id-column">{{ item.id }}</td>
            <td><strong>{{ item.name }}</strong></td>
            <td>{{ item.stimuli ? item.stimuli.length : 0 }} Items</td>
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
        
        <div class="form-group">
          <label>Assigned Stimuli (Click to Add / Remove)</label>
          <div class="shuffle-container">
            <div class="shuffle-box">
              <div class="shuffle-header">
                {{ $t('views.playlist.available_stimuli') }}
                <input type="text" v-model="searchAvailable" :placeholder="$t('views.playlist.search_placeholder')" class="shuffle-search" />
              </div>
              <ul class="shuffle-list">
                <li v-for="s in filteredAvailable" :key="s.id" @click="addStimulus(s.id)">
                  <span>{{ s.name }}</span>
                  <span class="add-btn">+</span>
                </li>
              </ul>
            </div>

            <div class="shuffle-box">
              <div class="shuffle-header">
                {{ $t('views.playlist.selected_items') }}
                <input type="text" v-model="searchSelected" :placeholder="$t('views.playlist.search_placeholder')" class="shuffle-search" />
              </div>
              <ul class="shuffle-list">
                <li v-for="item in mappedSelected" :key="'selected-' + item.originalIndex" 
                    class="draggable-item"
                    :class="{ 'is-dragging': draggedItemIndex === item.originalIndex }"
                    draggable="true"
                    @dragstart="onDragStart($event, item.originalIndex)"
                    @dragover.prevent
                    @dragenter.prevent
                    @drop="onDrop($event, item.originalIndex)"
                    @dragend="onDragEnd"
                    @click="removeStimulus(item.originalIndex)">
                  <div style="display: flex; align-items: center; gap: 10px;">
                    <span class="drag-handle" @click.stop>☰</span>
                    <span>{{ item.originalIndex + 1 }}. {{ item.name }}</span>
                  </div>
                  <span class="remove-btn">×</span>
                </li>
                <li v-if="formData.stimuli.length === 0" class="shuffle-empty">-</li>
              </ul>
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
import ConfirmDeleteModal from '@/components/ConfirmDeleteModal.vue'
import WarningModal from '@/components/WarningModal.vue'
import ColumnHeaderFilter from '@/components/ColumnHeaderFilter.vue'
import CrudHeader from '@/components/CrudHeader.vue'
import TableActionButtons from '@/components/TableActionButtons.vue'

const { t } = useI18n()
const items = ref([])
const allStimuli = ref([])
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

const formData = ref({ name: '', stimuli: [] })

const resetForm = () => { 
  formData.value = { name: '', stimuli: [] } 
  searchAvailable.value = ''; searchSelected.value = '';
}

const populateForm = (item) => { 
  formData.value = { name: item.name, stimuli: item.stimuli ? [...item.stimuli] : [] }
  searchAvailable.value = ''; searchSelected.value = '';
}

const loadData = async () => {
  try {
    const [resPlaylists, resStimuli] = await Promise.all([
      api.get('playlists/'),
      api.get('stimuli/')
    ])
    items.value = resPlaylists.data
    allStimuli.value = resStimuli.data
  } catch (error) { 
    warningMessage.value = crud.parseApiError(error, t, 'errors.load_failed')
    showWarningModal.value = true
  }
}

const getStimulusName = (id) => {
  const s = allStimuli.value.find(st => st.id === id)
  return s ? s.name : `Unknown (ID: ${id})`
}

const addStimulus = (id) => { formData.value.stimuli.push(id) }
const removeStimulus = (index) => { formData.value.stimuli.splice(index, 1) }

const draggedItemIndex = ref(null)

const onDragStart = (event, index) => {
  draggedItemIndex.value = index
  event.dataTransfer.effectAllowed = 'move'
  if (event.dataTransfer) event.dataTransfer.setData('text/plain', index.toString())
}

const onDrop = (event, targetIndex) => {
  if (draggedItemIndex.value === null || draggedItemIndex.value === targetIndex) return
  const list = formData.value.stimuli
  const [movedItem] = list.splice(draggedItemIndex.value, 1)
  list.splice(targetIndex, 0, movedItem)
  draggedItemIndex.value = null
}

const onDragEnd = () => { draggedItemIndex.value = null }

const searchAvailable = ref('')
const searchSelected = ref('')

const filteredAvailable = computed(() => {
  if (!searchAvailable.value) return allStimuli.value
  const q = searchAvailable.value.toLowerCase()
  return allStimuli.value.filter(s => s.name.toLowerCase().includes(q))
})

const mappedSelected = computed(() => {
  let mapped = formData.value.stimuli.map((id, index) => ({ id: id, originalIndex: index, name: getStimulusName(id) }))
  if (searchSelected.value) {
    const q = searchSelected.value.toLowerCase()
    mapped = mapped.filter(item => item.name.toLowerCase().includes(q))
  }
  return mapped
})

const saveRecord = async () => {
  crud.clearErrors()

  if (!formData.value.name || formData.value.name.trim() === '') {
    crud.fieldErrors.value.name = t('errors.required_field')
    return
  }

  try {
    if (crud.isEditing.value) await api.put(`playlists/${crud.editingId.value}/`, formData.value)
    else await api.post('playlists/', formData.value)
    crud.closeDialog()
    loadData()
  } catch (error) { 
    crud.handleFormError(error, t, 'errors.save_failed')
  }
}

const executeDelete = async () => {
  try {
    await api.delete(`playlists/${crud.itemToDelete.value}/`)
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
.shuffle-container { display: flex; gap: 15px; }
.shuffle-box { flex: 1; border: 1px solid #ddd; border-radius: 4px; height: 250px; overflow-y: auto; background: #fdfdfd; }
.shuffle-header { padding: 10px; background: #f4f7f6; border-bottom: 1px solid #ddd; font-weight: bold; position: sticky; top: 0; display: flex; flex-direction: column; gap: 8px; z-index: 2; }
.shuffle-list { list-style: none; padding: 0; margin: 0; }
.shuffle-list li { padding: 10px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
.shuffle-list li:hover { background: #e9ecef; }
.shuffle-empty { text-align: center; color: #aaa; font-style: italic; cursor: default !important; }
.shuffle-empty:hover { background: none !important; }
.add-btn { color: #2ecc71; font-weight: bold; font-size: 1.2rem; }
.remove-btn { color: #e74c3c; font-weight: bold; font-size: 1.2rem; }
.shuffle-search { padding: 6px; border: 1px solid #ccc; border-radius: 4px; font-weight: normal; font-size: 0.85rem; width: 100%; }
.draggable-item { cursor: grab; transition: background-color 0.2s; }
.draggable-item:active { cursor: grabbing; }
.draggable-item.is-dragging { opacity: 0.4; background-color: #f1f2f6 !important; border: 1px dashed #3498db; }
.drag-handle { color: #bdc3c7; cursor: grab; font-size: 1.2rem; user-select: none; }
.drag-handle:hover { color: #7f8c8d; }
</style>
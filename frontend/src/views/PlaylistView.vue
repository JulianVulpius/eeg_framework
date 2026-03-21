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
          <PlaylistShuffle 
            :availableItems="allStimuli"
            :categories="stimulusCategories"
            v-model="formData.stimuli"
          />
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
import PlaylistShuffle from '@/components/PlaylistShuffle.vue'

const { t } = useI18n()
const items = ref([])
const allStimuli = ref([])
const stimulusCategories = ref([])
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
}

const populateForm = (item) => { 
  formData.value = { name: item.name, stimuli: item.stimuli ? [...item.stimuli] : [] }
}

const loadData = async () => {
  try {
    const [resPlaylists, resStimuli, resCats] = await Promise.all([
      api.get('playlists/'),
      api.get('stimuli/'),
      api.get('category/stimulus-categories/')
    ])
    items.value = resPlaylists.data
    allStimuli.value = resStimuli.data
    stimulusCategories.value = resCats.data
  } catch (error) { 
    warningMessage.value = crud.parseApiError(error, t, 'errors.load_failed')
    showWarningModal.value = true
  }
}

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
<template>
  <div class="category-manager">
    <CrudHeader 
      :title="$t('nav.trigger_groups')" 
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
            <th style="width: 30%;">
              <ColumnHeaderFilter 
                :title="$t('common.description')" 
                v-model="columnFilters.description" 
                :placeholder="$t('common.search')" 
              />
            </th>
            <th>Triggers & Hotkeys</th>
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
            <td>{{ item.description }}</td>
            <td>{{ item.triggers ? item.triggers.length : 0 }} Assigned</td>
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
      :errorMessage="crud.errorMessage.value"
      @close="crud.closeDialog"
    >
      <form @submit.prevent="saveRecord(false)">
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
          <label>Triggers & Hotkeys</label>
          <TriggerShuffle 
            :allOptions="allTriggerDefs"
            :triggerPairs="allTriggerPairs"
            v-model:selectedIds="formData.triggers"
            v-model:hotkeyMap="formData.hotkeys"
          />
        </div>

        <div class="modal-actions">
          <button type="button" class="btn-secondary" @click="crud.closeDialog">{{ $t('actions.cancel') }}</button>
          <button type="submit" class="btn-primary">{{ $t('actions.save') }}</button>
        </div>
      </form>
    </BaseModal>

    <WarningModal 
      :isOpen="isWarningOpen" 
      :title="$t('common.warning')"
      :message="$t('errors.empty_hotkey_warning')"
      :hideCancel="false"
      @cancel="isWarningOpen = false"
      @confirm="confirmSaveWithWarning"
    />

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
import api from '@/services/api'
import { useCrud } from '@/composables/useCrud'
import { useI18n } from 'vue-i18n'

import BaseModal from '@/components/BaseModal.vue'
import BaseInputError from '@/components/BaseInputError.vue'
import ConfirmDeleteModal from '@/components/ConfirmDeleteModal.vue'
import WarningModal from '@/components/WarningModal.vue'
import ColumnHeaderFilter from '@/components/ColumnHeaderFilter.vue'
import CrudHeader from '@/components/CrudHeader.vue'
import TableActionButtons from '@/components/TableActionButtons.vue'
import TriggerShuffle from '@/components/TriggerShuffle.vue'

const { t } = useI18n()
const items = ref([])
const allTriggerDefs = ref([])
const allTriggerPairs = ref([])
const allHotkeys = ref([])
const crud = useCrud()

const showWarningModal = ref(false)
const warningMessage = ref('')

const columnFilters = ref({
  name: '',
  description: ''
})

const filteredItems = computed(() => {
  return items.value.filter(item => {
    if (columnFilters.value.name) {
      const q = columnFilters.value.name.toLowerCase()
      if (!item.name.toLowerCase().includes(q)) return false
    }
    if (columnFilters.value.description) {
      const q = columnFilters.value.description.toLowerCase()
      if (!item.description || !item.description.toLowerCase().includes(q)) return false
    }
    return true
  })
})

const formData = ref({ name: '', description: '', triggers: [], hotkeys: {} })
const isWarningOpen = ref(false)

const resetForm = () => { 
  formData.value = { name: '', description: '', triggers: [], hotkeys: {} } 
}

const populateForm = (item) => {
  const hotkeysDict = {}
  const existingHotkeys = allHotkeys.value.filter(hk => hk.group === item.id)
  existingHotkeys.forEach(hk => { hotkeysDict[hk.definition] = hk.key_code })

  formData.value = { 
    name: item.name, 
    description: item.description,
    triggers: item.triggers ? [...item.triggers] : [],
    hotkeys: hotkeysDict
  }
}

const loadData = async () => {
  try {
    const [resGroups, resDefs, resHotkeys, resPairs] = await Promise.all([
      api.get('triggers/groups/'),
      api.get('triggers/definitions/'),
      api.get('triggers/hotkeys/'),
      api.get('triggers/pairs/') 
    ])
    items.value = resGroups.data
    allTriggerDefs.value = resDefs.data
    allHotkeys.value = resHotkeys.data
    allTriggerPairs.value = resPairs.data 
  } catch (error) { 
    warningMessage.value = crud.parseApiError(error, t, 'errors.load_failed')
    showWarningModal.value = true
  }
}

const saveRecord = async (skipWarning = false) => {
  crud.clearErrors()

  if (!formData.value.name || formData.value.name.trim() === '') {
    crud.fieldErrors.value.name = t('errors.required_field')
    return
  }

  const hotkeyValues = []
  for (const triggerId of formData.value.triggers) {
    const key = formData.value.hotkeys[triggerId]?.trim()
    if (key) {
      if (hotkeyValues.includes(key.toLowerCase())) {
        crud.errorMessage.value = t('errors.duplicate_hotkey', { key: key })
        return 
      }
      hotkeyValues.push(key.toLowerCase())
    }
  }

  if (!skipWarning) {
    const hasEmptyHotkeys = formData.value.triggers.some(tId => {
      const key = formData.value.hotkeys[tId]
      return !key || key.trim() === ""
    })

    if (hasEmptyHotkeys) {
      isWarningOpen.value = true
      return
    }
  }

  try {
    let groupId = crud.editingId.value
    const groupPayload = { 
      name: formData.value.name, 
      description: formData.value.description, 
      triggers: formData.value.triggers 
    }
    
    if (crud.isEditing.value) {
      await api.put(`triggers/groups/${groupId}/`, groupPayload)
    } else {
      const res = await api.post('triggers/groups/', groupPayload)
      groupId = res.data.id
    }

    const existingHotkeys = allHotkeys.value.filter(hk => hk.group === groupId)
    for (const hk of existingHotkeys) {
      await api.delete(`triggers/hotkeys/${hk.id}/`)
    }

    for (const triggerId of formData.value.triggers) {
      const keyCode = formData.value.hotkeys[triggerId]
      if (keyCode && keyCode.trim() !== "") {
        await api.post('triggers/hotkeys/', { 
          group: groupId, 
          definition: triggerId, 
          key_code: keyCode.trim() 
        })
      }
    }

    isWarningOpen.value = false
    crud.closeDialog()
    loadData()
  } catch (error) { 
    crud.handleFormError(error, t, 'errors.save_failed')
  }
}

const confirmSaveWithWarning = () => {
  saveRecord(true)
}

const executeDelete = async () => {
  try {
    await api.delete(`triggers/groups/${crud.itemToDelete.value}/`)
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
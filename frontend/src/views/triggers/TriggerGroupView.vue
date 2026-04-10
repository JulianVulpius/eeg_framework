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
            <th style="width: 20%;">
              <ColumnHeaderFilter :title="$t('common.name')" v-model="columnFilters.name" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 15%;">
              <ColumnHeaderFilter :title="$t('master_data.category')" v-model="columnFilters.category" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 25%;">
              <ColumnHeaderFilter :title="$t('common.description')" v-model="columnFilters.description" :placeholder="$t('common.search')" />
            </th>
            <th style="width: 15%;">Triggers & Hotkeys</th>
            <th style="width: 15%;">
              <ColumnHeaderFilter :title="$t('common.creator')" v-model="columnFilters.creator" :placeholder="$t('common.search')" />
            </th>
            <th class="actions-column">{{ $t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredItems.length === 0">
            <td :colspan="crud.showIdColumn.value ? 7 : 6" class="empty-state">{{ $t('common.no_data') }}</td>
          </tr>
          <tr v-for="item in filteredItems" :key="item.id">
            <td v-if="crud.showIdColumn.value" class="id-column">{{ item.id }}</td>
            <td><strong>{{ item.name }}</strong></td>
            <td><span class="badge category-badge">{{ getCategoryName(item.category) }}</span></td>
            <td>{{ item.description }}</td>
            <td>{{ item.triggers ? item.triggers.length : 0 }} Assigned</td>
            <td>{{ item.creator || '-' }}</td>
            <TableActionButtons @edit="crud.openEditDialog(item.id, () => populateForm(item))" @delete="confirmAndDelete(item.id)" />
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
      <form @submit.prevent="saveRecord(false)">
        <div class="form-group">
          <label>{{ $t('common.name') }} *</label>
          <input type="text" v-model="formData.name" class="form-control" :class="{ 'input-invalid': crud.fieldErrors.value.name }" />
          <BaseInputError :message="crud.fieldErrors.value.name" />
        </div>
        
        <BaseSearchSelect 
          v-model="formData.category"
          :options="categories"
          :label="$t('master_data.category')"
          :nullLabel="$t('master_data.none')"
          :error="crud.fieldErrors.value.category"
        />

        <div class="form-group" style="margin-bottom: 15px;">
          <label>{{ $t('common.description') }}</label>
          <textarea v-model="formData.description" class="form-control" rows="2"></textarea>
        </div>
        
        <div class="form-group">
          <label>Triggers & Hotkeys</label>
          <div class="info-banner" style="margin-bottom: 15px; font-size: 0.9rem;">
            {{ $t('views.triggers.hotkey_info') }}
          </div>
          <TriggerShuffle 
            :allOptions="allTriggerDefs"
            :triggerPairs="allTriggerPairs"
            v-model:selectedIds="formData.triggers"
            :hotkeyMap="formData.hotkeys"
            @update:hotkeyMap="sanitizeHotkeys"
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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import { useCrud } from '@/composables/useCrud'
import { useGlobalModal } from '@/composables/useGlobalModal'
import { useI18n } from 'vue-i18n'

import BaseModal from '@/components/ui/BaseModal.vue'
import BaseInputError from '@/components/ui/BaseInputError.vue'
import WarningModal from '@/components/ui/WarningModal.vue'
import CrudHeader from '@/components/ui/CrudHeader.vue'
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'

import ColumnHeaderFilter from '@/components/table/ColumnHeaderFilter.vue'
import TableActionButtons from '@/components/table/TableActionButtons.vue'

import TriggerShuffle from '@/components/domain/TriggerShuffle.vue'

const { t } = useI18n()
const items = ref([])
const categories = ref([])
const allTriggerDefs = ref([])
const allTriggerPairs = ref([])
const allHotkeys = ref([])
const crud = useCrud()
const { requireConfirmation, showWarning } = useGlobalModal()

const columnFilters = ref({ name: '', category: '', description: '', creator: '' })

const getCategoryName = (id) => {
  const cat = categories.value.find(c => c.id === id)
  return cat ? cat.name : '-'
}

const filteredItems = computed(() => {
  return items.value.filter(item => {
    if (columnFilters.value.name && !item.name.toLowerCase().includes(columnFilters.value.name.toLowerCase())) return false
    
    if (columnFilters.value.category) {
      const cName = getCategoryName(item.category).toLowerCase()
      if (!cName.includes(columnFilters.value.category.toLowerCase())) return false
    }

    if (columnFilters.value.description && (!item.description || !item.description.toLowerCase().includes(columnFilters.value.description.toLowerCase()))) return false
    
    if (columnFilters.value.creator) {
      const creatorName = item.creator ? item.creator.toLowerCase() : ''
      if (!creatorName.includes(columnFilters.value.creator.toLowerCase())) return false
    }
    
    return true
  })
})

const formData = ref({ name: '', category: null, description: '', triggers: [], hotkeys: {} })
const isWarningOpen = ref(false)

const sanitizeHotkeys = (newMap) => {
  for (const triggerId in newMap) {
    if (newMap[triggerId]) {
      newMap[triggerId] = newMap[triggerId]
        .toLowerCase()
        .replace(/[^a-z0-9]/g, '')
        .substring(0, 1)
    }
  }
  formData.value.hotkeys = newMap
}

const resetForm = () => { formData.value = { name: '', category: null, description: '', triggers: [], hotkeys: {} } }

const populateForm = (item) => {
  const hotkeysDict = {}
  const existingHotkeys = allHotkeys.value.filter(hk => hk.group === item.id)
  existingHotkeys.forEach(hk => { hotkeysDict[hk.definition] = hk.key_code })

  formData.value = { 
    name: item.name, 
    category: item.category || null,
    description: item.description,
    triggers: item.triggers ? [...item.triggers] : [],
    hotkeys: hotkeysDict
  }
}

const loadData = async () => {
  try {
    const [resGroups, resCats, resDefs, resHotkeys, resPairs] = await Promise.all([
      api.get('triggers/groups/'),
      api.get('category/trigger-group/'),
      api.get('triggers/definitions/'),
      api.get('triggers/hotkeys/'),
      api.get('triggers/pairs/') 
    ])
    items.value = resGroups.data
    categories.value = resCats.data
    allTriggerDefs.value = resDefs.data
    allHotkeys.value = resHotkeys.data
    allTriggerPairs.value = resPairs.data 
  } catch (error) { 
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
        showWarning(t('errors.duplicate_hotkey', { key: key }), t('common.error'))
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
      category: formData.value.category,
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
    crud.handleFormError(error, t)
  }
}

const confirmSaveWithWarning = () => { saveRecord(true) }

const confirmAndDelete = (id) => {
  requireConfirmation(async () => {
    try {
      await api.delete(`triggers/groups/${id}/`)
      loadData()
    } catch (error) {}
  })
}

onMounted(loadData)
</script>
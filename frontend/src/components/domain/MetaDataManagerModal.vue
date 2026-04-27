<template>
  <BaseModal 
    :isOpen="isOpen" 
    :title="modalTitle"
    customClass="large-modal"
    @close="closeModal"
  >
    <div class="metadata-manager" v-if="!isLoading">
      
      <div class="sticky-header">
        <button class="modal-sticky-close" @click="closeModal" :title="$t('metadata_tool.close')">✖</button>
      </div>
      
      <div class="mode-toggle" v-if="hasAnyData">
        <button class="btn-secondary" :class="{ active: currentMode === 'view' }" @click="currentMode = 'view'">
          🏷️ {{ $t('metadata_tool.view') }}
        </button>
        <button class="btn-secondary" :class="{ active: currentMode === 'edit' }" @click="currentMode = 'edit'">
          📝 {{ $t('metadata_tool.edit') }}
        </button>
      </div>

      <div v-if="currentMode === 'view'" class="view-mode">
        <div v-if="attachedInstances.length === 0" class="empty-state">
          <p>{{ $t('common.no_data') }}</p>
          <button v-if="tableSupportsMetadata" class="btn-primary mt-2" @click="currentMode = 'edit'">
            + {{ $t('metadata_tool.add_new') }}
          </button>
        </div>

        <div v-else class="metadata-groups">
          <div v-for="instance in processedInstances" :key="instance.id" class="metadata-card">
            <div class="card-header">
              <h4>{{ getGroupName(instance.group) }}</h4>
              <span v-if="instance.creation_source === 'COMPONENT'" class="badge badge-info">{{ $t('metadata_tool.system') }}</span>
              <span v-if="instance.isLegacy" class="badge badge-warning">{{ $t('metadata_tool.legacy') }}</span>
            </div>
            <table class="data-table small-table">
              <tbody>
                <tr v-for="val in getCompleteValues(instance)" :key="val.definition">
                  <td style="width: 40%"><strong>{{ getDefName(val.definition) }}</strong></td>
                  <td :class="{ 'text-muted': val.value === '' }">{{ formatValue(val.value, val.definition) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="currentMode === 'edit'" class="edit-mode">
        
        <div class="add-section" v-if="tableSupportsMetadata">
          <h3>{{ $t('metadata_tool.add_new') }}</h3>
          
          <div class="form-row flex-gap" v-if="!draftGroup">
            <div class="form-group" style="flex: 1;">
              <label>{{ $t('metadata_tool.select_category') }}</label>
              <BaseSearchSelect 
                v-model="selectedCategory" 
                :options="availableCategoryOptions" 
                :nullLabel="$t('common.all')"
                @update:modelValue="draftGroup = null"
              />
            </div>

            <div class="form-group" style="flex: 1;">
              <label>{{ $t('metadata_tool.select_group') }}</label>
              <BaseSearchSelect 
                v-model="draftGroup" 
                :options="filteredUnassignedGroups" 
                :nullLabel="$t('master_data.none')"
                @update:modelValue="initializeDraft"
              />
            </div>
          </div>

          <div v-if="draftGroup" class="draft-form-card">
            <div class="draft-header">
              <h4>{{ $t('metadata_tool.draft') }} {{ getGroupName(draftGroup) }}</h4>
              <button class="btn-icon" @click="cancelDraft">✖</button>
            </div>
            
            <div class="draft-fields">
              <div v-for="def in activeDraftDefinitions" :key="def.id" class="form-group">
                <label>{{ def.name }}</label>
                <input 
                  v-if="def.expected_data_type === 'STRING' || def.expected_data_type === 'INTEGER'"
                  :type="def.expected_data_type === 'INTEGER' ? 'number' : 'text'"
                  v-model="draftValues[def.id]"
                  class="form-control"
                />
                <select v-else-if="def.expected_data_type === 'BOOLEAN'" v-model="draftValues[def.id]" class="form-control">
                  <option :value="null">-- {{ $t('common.select') }} --</option>
                  <option value="true">{{ $t('common.yes') }}</option>
                  <option value="false">{{ $t('common.no') }}</option>
                </select>
                <textarea v-else v-model="draftValues[def.id]" class="form-control" rows="2"></textarea>
              </div>
            </div>

            <div class="modal-actions" style="margin-top: 1rem">
              <button class="btn-secondary" @click="cancelDraft">{{ $t('metadata_tool.cancel') }}</button>
              <button class="btn-primary" @click="saveDraft">{{ $t('metadata_tool.save') }}</button>
            </div>
          </div>
          <hr />
        </div>

        <div class="existing-management" v-if="processedInstances.length > 0">
          <h3>{{ $t('metadata_tool.attached_data') }}</h3>
          
          <div v-for="instance in processedInstances" :key="instance.id" class="metadata-card manage-card">
            <div class="card-header manage-header">
              <div class="card-info">
                <h4>{{ getGroupName(instance.group) }}</h4>
                <span v-if="instance.creation_source === 'COMPONENT'" class="text-muted">({{ $t('metadata_tool.readonly_session_data') }})</span>
                <span v-if="instance.isLegacy" class="badge badge-warning text-small">{{ $t('metadata_tool.archived_category') }}</span>
              </div>
              
              <div class="card-actions">
                <div v-if="deleteConfirmId === instance.id" class="inline-confirm">
                  <span class="text-danger"><strong>{{ $t('common.are_you_sure') }}</strong></span>
                  <button class="btn-danger btn-sm" @click="executeDelete(instance.id)">{{ $t('common.yes') }}</button>
                  <button class="btn-secondary btn-sm" @click="deleteConfirmId = null">{{ $t('common.no') }}</button>
                </div>
                <button 
                  v-else-if="!instance.isReadOnly" 
                  class="btn-icon text-danger" 
                  :title="$t('metadata_tool.delete')"
                  @click="deleteConfirmId = instance.id"
                >
                  🗑️
                </button>
              </div>
            </div>
            
            <div class="draft-fields" v-if="!instance.isReadOnly && editValues[instance.id]">
              <div v-for="val in getCompleteValues(instance)" :key="val.definition" class="form-group">
                <label>{{ getDefName(val.definition) }}</label>
                <input 
                  v-if="getDefType(val.definition) === 'STRING' || getDefType(val.definition) === 'INTEGER'"
                  :type="getDefType(val.definition) === 'INTEGER' ? 'number' : 'text'"
                  v-model="editValues[instance.id][val.definition]"
                  class="form-control"
                />
                <select v-else-if="getDefType(val.definition) === 'BOOLEAN'" v-model="editValues[instance.id][val.definition]" class="form-control">
                  <option :value="null">-- {{ $t('common.select') }} --</option>
                  <option value="true">{{ $t('common.yes') }}</option>
                  <option value="false">{{ $t('common.no') }}</option>
                </select>
                <textarea v-else v-model="editValues[instance.id][val.definition]" class="form-control" rows="2"></textarea>
              </div>
              <button class="btn-primary mt-2" @click="saveExistingEdits(instance.id)">{{ $t('metadata_tool.save') }}</button>
            </div>
          </div>
        </div>

        <div v-if="!tableSupportsMetadata && processedInstances.length === 0" class="empty-state">
          <p>{{ $t('metadata_tool.table_not_configured') }}</p>
        </div>

      </div>
    </div>
    
    <div v-else class="loading-state">
      <p>{{ $t('common.loading') }}</p>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useMetadataRegistry } from '@/composables/useMetadataRegistry'
import api from '@/services/api'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'

const { t } = useI18n()

const props = defineProps({
  isOpen: Boolean,
  initialMode: { type: String, default: 'view' },
  contentTypeId: Number,
  objectId: Number,
  objectName: String,
  tableSupportsMetadata: Boolean
})

const emit = defineEmits(['close', 'updated'])

const { 
  isLoading, loadAttachedMetadata, getAvailableGroupsForTable, 
  saveManualMetadataDraft, updateManualMetadata, deleteManualInstance, checkLegacyStatus 
} = useMetadataRegistry()

const currentMode = ref('view')
const attachedInstances = ref([])
const availableGroups = ref([])
const allGroups = ref([]) 
const allDefinitions = ref([]) 
const allCategories = ref([]) 

const selectedCategory = ref(null)
const deleteConfirmId = ref(null)

const draftGroup = ref(null)
const draftValues = ref({})
const activeDraftDefinitions = ref([])

const editValues = ref({})

// NEU: Greift jetzt ebenfalls strikt auf das metadata-JSON zu
const modalTitle = computed(() => {
  const prefix = currentMode.value === 'view' ? t('metadata_tool.title_view') : t('metadata_tool.title_manage')
  return `${prefix} ${props.objectName || `ID ${props.objectId}`}`
})

const hasAnyData = computed(() => attachedInstances.value.length > 0)

const processedInstances = computed(() => {
  return checkLegacyStatus(attachedInstances.value, availableGroups.value)
})

const unassignedGroupsRaw = computed(() => {
  return availableGroups.value.filter(g => !attachedInstances.value.some(i => i.group === g.id))
})

const availableCategoryOptions = computed(() => {
  const groupCatIds = [...new Set(unassignedGroupsRaw.value.map(g => g.category))]
  return allCategories.value.filter(c => groupCatIds.includes(c.id))
})

const filteredUnassignedGroups = computed(() => {
  if (!selectedCategory.value) return unassignedGroupsRaw.value
  return unassignedGroupsRaw.value.filter(g => g.category === selectedCategory.value)
})

const getGroupName = (id) => allGroups.value.find(g => g.id === id)?.name || id
const getDefName = (id) => allDefinitions.value.find(d => d.id === id)?.name || id
const getDefType = (id) => allDefinitions.value.find(d => d.id === id)?.expected_data_type || 'STRING'

const getCompleteValues = (instance) => {
  const group = allGroups.value.find(g => g.id === instance.group)
  if (!group || !group.assigned_definitions) return []
  
  return group.assigned_definitions.map(defId => {
    const existingVal = instance.values.find(v => v.definition === defId)
    return {
      definition: defId,
      value: existingVal ? existingVal.value : ''
    }
  })
}

const formatValue = (val, defId) => {
  if (val === '' || val === null || val === undefined) return '-'
  if (getDefType(defId) === 'BOOLEAN') {
    return val === 'true' ? t('common.yes') : t('common.no')
  }
  return val
}

const initEditState = () => {
  editValues.value = {}
  processedInstances.value.forEach(instance => {
    if (!instance.isReadOnly) {
      editValues.value[instance.id] = {}
      getCompleteValues(instance).forEach(v => {
        editValues.value[instance.id][v.definition] = v.value
      })
    }
  })
}

const loadData = async () => {
  if (!props.contentTypeId || !props.objectId) return
  
  const [instances, available, allGroupsRes, defs, cats] = await Promise.all([
    loadAttachedMetadata(props.contentTypeId, props.objectId),
    getAvailableGroupsForTable(props.contentTypeId),
    api.get('metadata/groups/').then(res => res.data).catch(() => []), 
    api.get('metadata/definitions/').then(res => res.data).catch(() => []),
    api.get('category/metadata-group/').then(res => res.data).catch(() => [])
  ])
  
  attachedInstances.value = instances
  availableGroups.value = available
  allGroups.value = allGroupsRes
  allDefinitions.value = defs
  allCategories.value = cats
  
  initEditState()
  currentMode.value = props.initialMode
}

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    deleteConfirmId.value = null
    selectedCategory.value = null
    cancelDraft()
    loadData()
  }
})

const initializeDraft = (groupId) => {
  if (!groupId) return cancelDraft()
  const group = allGroups.value.find(g => g.id === groupId)
  if (group && group.assigned_definitions) {
    activeDraftDefinitions.value = group.assigned_definitions.map(id => allDefinitions.value.find(d => d.id === id)).filter(Boolean)
    draftValues.value = {}
  }
}

const cancelDraft = () => {
  draftGroup.value = null
  draftValues.value = {}
  activeDraftDefinitions.value = []
}

const saveDraft = async () => {
  const valuesArray = Object.keys(draftValues.value).map(defId => ({
    definition: parseInt(defId),
    value: draftValues.value[defId] !== null && draftValues.value[defId] !== undefined ? String(draftValues.value[defId]) : ''
  }))

  const result = await saveManualMetadataDraft(props.contentTypeId, props.objectId, draftGroup.value, valuesArray)
  if (result) {
    cancelDraft()
    await loadData()
    emit('updated') 
  }
}

const saveExistingEdits = async (instanceId) => {
  const instanceData = editValues.value[instanceId]
  const valuesArray = Object.keys(instanceData).map(defId => ({
    definition: parseInt(defId),
    value: instanceData[defId] !== null && instanceData[defId] !== undefined ? String(instanceData[defId]) : ''
  }))
  
  const success = await updateManualMetadata(instanceId, valuesArray)
  if (success) await loadData()
}

const executeDelete = async (instanceId) => {
  const success = await deleteManualInstance(instanceId)
  if (success) {
    deleteConfirmId.value = null
    await loadData()
    emit('updated')
  }
}

const closeModal = () => emit('close')
</script>

<style scoped>
.metadata-manager { position: relative; overflow: visible !important; }

.sticky-header {
  position: sticky;
  top: 0px;
  right: 0px;
  z-index: 1100;
  display: flex;
  justify-content: flex-end;
  pointer-events: none;
}
.modal-sticky-close {
  pointer-events: auto;
  background: var(--bg-primary, #fff);
  border: 1px solid var(--border-color);
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.4rem;
  cursor: pointer;
  color: var(--text-muted);
  box-shadow: 0 4px 10px rgba(0,0,0,0.15);
  margin-top: 5px;
  margin-right: -10px;
  transition: all 0.2s ease;
}
.modal-sticky-close:hover { color: var(--danger-color); border-color: var(--danger-color); transform: scale(1.15); }

.flex-gap { display: flex; gap: 1rem; }

.mode-toggle { display: flex; gap: 0.5rem; margin-bottom: 1.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; margin-top: -30px; }
.mode-toggle button { opacity: 0.6; }
.mode-toggle button.active { opacity: 1; border-bottom: 2px solid var(--primary-color); border-radius: 0; }

.metadata-card { background: var(--bg-secondary); border-radius: 8px; padding: 1rem; margin-bottom: 1rem; }
.card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.5rem; }
.card-header h4 { margin: 0; color: var(--primary-color); }

.manage-card { display: flex; flex-direction: column; }
.manage-header { border-bottom: none; padding-bottom: 0; margin-bottom: 1rem; }
.inline-confirm { display: flex; gap: 0.5rem; align-items: center; background: #ffebee; padding: 0.25rem 0.5rem; border-radius: 4px; }
.btn-sm { padding: 0.2rem 0.5rem; font-size: 0.85rem; }

.draft-form-card { border: 2px dashed var(--primary-color); border-radius: 8px; padding: 1rem; margin-top: 1rem; }
.draft-header { display: flex; justify-content: space-between; margin-bottom: 1rem; }
.text-small { font-size: 0.8rem; }
.text-muted { opacity: 0.6; }
.mt-2 { margin-top: 1rem; }
</style>
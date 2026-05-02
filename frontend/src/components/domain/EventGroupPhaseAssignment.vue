<template>
  <div class="phase-assignment-container">
    
    <div class="group-selector">
      <label class="section-label">1. {{ $t('views.events.select_event_group') }}</label>
      <select v-model="selectedGroupId" class="form-control select-box" @change="loadPhaseConfigs">
        <option :value="null">{{ $t('actions.select')}}</option>
        <option v-for="grp in eventGroups" :key="grp.id" :value="grp.id">
          {{ grp.name }}
        </option>
      </select>
    </div>

    <div v-if="selectedGroup" class="page-group-radios fade-in">
      <label class="section-label">2. {{ $t('views.events.assign_phases_title') }}</label>
      <div v-if="pageGroups.length === 0" class="no-data">
        ⚠️ {{ $t('views.events.no_phases_available') }}
      </div>
      <div class="radio-list">
        <label v-for="pg in pageGroups" :key="pg.id" class="radio-item">
          <input type="checkbox" :value="pg.id" v-model="selectedGroup.page_groups" @change="onSelectionChange" />
          <span class="checkbox-custom"></span>
          <span class="radio-label">{{ pg.name }}</span>
        </label>
      </div>
    </div>

    <div v-if="selectedGroup && selectedGroup.page_groups.length > 0" class="device-config-section fade-in">
      <label class="section-label" style="border-top: 2px dashed #3498db; padding-top: 20px; margin-top: 10px;">
        3. {{ $t('views.events.configure_phase_devices')}}
      </label>

      <div v-for="pgId in selectedGroup.page_groups" :key="pgId" class="phase-card">
        <div class="phase-header">
          <h4>{{ getPageGroupName(pgId) }}</h4>
          <button class="btn-secondary btn-sm" @click="openDeviceAssignModal(pgId)">
            <i class="fas fa-plus"></i> {{ $t('views.events.assign_device')}}
          </button>
        </div>

        <div v-if="getConfigsForPhase(pgId).length === 0" class="text-muted" style="margin-top: 10px; font-size: 0.9rem;">
          Noch keine Geräte zugewiesen.
        </div>

        <div class="config-accordion" v-for="config in getConfigsForPhase(pgId)" :key="config.id" :class="{ 'is-archived': config.is_archived }">
          
          <div class="accordion-header" @click="toggleAccordion(config.id)">
            <div class="header-title">
              <strong>{{ config.device_name }}</strong>
              <span v-if="config.is_locked" class="badge warning-badge">🔒 Locked</span>
              <span v-if="config.is_archived" class="badge default-badge">{{ $t('views.events.archived_badge') }}</span>
            </div>
            <div style="display: flex; align-items: center; gap: 15px;">
              <button class="btn-danger btn-sm" @click.stop="deleteConfig(config)" v-if="!config.is_archived">
                <i class="fas fa-trash"></i> {{ $t('common.remove')}}
              </button>
              <i :class="expandedConfigs.includes(config.id) ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
            </div>
          </div>

          <div v-if="expandedConfigs.includes(config.id)" class="accordion-body fade-in">
            <div v-if="config.is_locked" class="lock-warning">
              ⚠️ {{ $t('views.events.is_locked_warning') }}
            </div>

            <div class="form-group">
              <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
              <label style="margin: 0;">{{ $t('views.events.expected_channels')}}</label>
              
              <button 
                v-if="!config.is_locked && !config.is_archived"
                class="btn-secondary btn-sm" 
                style="padding: 2px 8px; font-size: 0.8rem;"
                @click="resetChannels(config)"
              >
                <i class="fas fa-undo"></i> {{ $t('common.reset') }}
              </button>
            </div>
              
              <div v-if="getAvailableChannelsForConfig(config).length === 0" class="text-muted">
                {{ $t('views.events.no_channels_defined')}}
              </div>
              
             <div v-else class="channel-grid">
                <span 
                  v-for="ch in config.expected_channels" 
                  :key="ch" 
                  class="channel-tag" 
                  :class="{ 'disabled': config.is_locked || config.is_archived }"
                >
                  {{ ch }}
                  <button 
                    v-if="!config.is_locked && !config.is_archived"
                    class="btn-icon text-danger remove-channel-btn" 
                    @click="removeChannel(config, ch)"
                    :title="$t('common.remove')"
                  >
                    ✖
                  </button>
                </span>
              </div>
            </div>

            <div style="margin-top: 15px;">
              <button class="btn-primary btn-sm" @click="$emit('edit-metadata', config)" :disabled="config.is_archived">
                <i class="fas fa-sliders-h"></i> {{ $t('views.events.edit_settings')}}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <BaseModal :isOpen="isAssignModalOpen" :title="$t('views.events.assign_device')" @close="isAssignModalOpen = false">
      <div v-if="eventDevicePool.length === 0" class="no-data">
        {{ $t('views.events.device_pool_empty') }}
      </div>
      <div v-else>
        
        <div class="filter-bar">
          <input 
            type="text" 
            v-model="modalSearchName" 
            class="form-control" 
            :placeholder="$t('common.search')" 
            style="flex: 1;"
          />
          <div style="flex: 1;">
            <BaseSearchSelect 
              v-model="modalSearchCategory" 
              :options="uniqueCategoriesAsOptions" 
              :placeholder="$t('common.all_categories')"
              :nullLabel="$t('common.all_categories')"
            />
          </div>
        </div>

        <div class="device-list">
          <div v-for="poolDev in filteredModalDevices" :key="poolDev.id" class="device-list-item">
            <div>
              <strong>{{ poolDev.device_name }}</strong>
              <div class="text-muted" style="font-size: 0.85rem;" v-if="poolDev.category">
                {{ getCategoryName(poolDev.category) }}
              </div>
            </div>
            
            <div>
              <button class="btn-primary btn-sm" :disabled="isSaving" @click="confirmDeviceAssignment(poolDev)">
                {{ $t('views.events.assign')}}
              </button>
            </div>
          </div>
          
          <div v-if="filteredModalDevices.length === 0" class="text-center text-muted" style="padding: 20px;">
            Alle verfügbaren Geräte sind dieser Phase bereits zugewiesen oder entsprechen nicht dem Filter.
          </div>
        </div>

      </div>
    </BaseModal>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import api from '@/services/api'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'
import { useGlobalModal } from '@/composables/useGlobalModal'

const props = defineProps({
  eventGroups: { type: Array, required: true },
  pageGroups: { type: Array, required: true },
  eventDevicePool: { type: Array, required: false, default: () => [] },
  deviceCategories: { type: Array, required: false, default: () => [] }
})

const emit = defineEmits(['update-assignment', 'edit-metadata'])
const { requireConfirmation } = useGlobalModal()

const selectedGroupId = ref(null)
const phaseConfigs = ref([]) 
const expandedConfigs = ref([])

const isAssignModalOpen = ref(false)
const targetPageGroupId = ref(null)
const isSaving = ref(false)
const modalSearchName = ref('')
const modalSearchCategory = ref(null)

const selectedGroup = computed(() => props.eventGroups.find(g => g.id === selectedGroupId.value))

const removeChannel = async (config, channelToRemove) => {
  if (config.is_locked || config.is_archived) return

  config.expected_channels = config.expected_channels.filter(ch => ch !== channelToRemove);
  await updateConfig(config);
}

const resetChannels = async (config) => {
  if (config.is_locked || config.is_archived) return
  
  const poolDevice = props.eventDevicePool.find(d => d.device_model_id === config.device_model_id)
  
  if (poolDevice && poolDevice.channels) {
    let originalChannels = poolDevice.channels
    if (typeof originalChannels === 'string') {
      originalChannels = originalChannels.split(',').map(s => s.trim())
    }

    config.expected_channels = [...originalChannels]
    
    await updateConfig(config)
  }
}

const getPageGroupName = (id) => {
  const pg = props.pageGroups.find(p => p.id === id)
  return pg ? pg.name : `Phase ${id}`
}

const getConfigsForPhase = (pgId) => phaseConfigs.value.filter(c => c.page_group_id === pgId)

const toggleAccordion = (id) => {
  if (expandedConfigs.value.includes(id)) {
    expandedConfigs.value = expandedConfigs.value.filter(e => e !== id)
  } else {
    expandedConfigs.value.push(id)
  }
}

const getCategoryName = (catId) => {
  if (!catId) return '';
  const cat = props.deviceCategories.find(c => c.id === catId);
  return cat ? String(cat.name) : String(catId);
}

const getAvailableChannelsForConfig = (config) => {
  const poolDevice = props.eventDevicePool.find(d => d.device_name === config.device_name);
  return poolDevice ? poolDevice.channels : (config.expected_channels || []);
}

const isDeviceAlreadyAssigned = (poolDev) => {
  const configsInCurrentPhase = getConfigsForPhase(targetPageGroupId.value);
  
  return configsInCurrentPhase.some(c => 
    c.device_model_id === poolDev.device_model_id
  );
}
const uniqueCategoriesAsOptions = computed(() => {
  const catIds = [...new Set(props.eventDevicePool.map(d => d.category).filter(Boolean))];
  
  return catIds.map(id => ({
    id: id,
    name: getCategoryName(id)
  }));
});

const filteredModalDevices = computed(() => {
  return props.eventDevicePool.filter(d => {
    if (isDeviceAlreadyAssigned(d)) return false;
    
    if (modalSearchName.value && !d.device_name.toLowerCase().includes(modalSearchName.value.toLowerCase())) {
      return false;
    }
    
    if (modalSearchCategory.value && d.category !== modalSearchCategory.value) {
      return false;
    }
    
    return true;
  });
});

const loadPhaseConfigs = async () => {
  if (!selectedGroupId.value) {
    phaseConfigs.value = []
    return
  }
  try {
    const res = await api.get(`event-management/phase-device-configs/?phase__event_group=${selectedGroupId.value}`)
    phaseConfigs.value = res.data
  } catch (error) {
    console.error("Backend Error Response:", error.response?.data || error)
  }
}

const onSelectionChange = () => {
  if (selectedGroup.value) emit('update-assignment', selectedGroup.value)
}

const openDeviceAssignModal = (pgId) => {
  targetPageGroupId.value = pgId
  modalSearchName.value = ''
  modalSearchCategory.value = null
  isAssignModalOpen.value = true
}

const confirmDeviceAssignment = async (poolDevice) => {
  if (!poolDevice || !targetPageGroupId.value) return
  isSaving.value = true

  try {
    const payload = {
      event_group_id: selectedGroupId.value,
      target_page_group_id: targetPageGroupId.value,
      master_device_id: poolDevice.device_model_id,
      expected_channels: poolDevice.channels || [] 
    }

    await api.post('event-management/phase-device-configs/', payload)
    
    isAssignModalOpen.value = false
    await loadPhaseConfigs() 
  } catch (error) {
  } finally {
    isSaving.value = false
  }
}

const updateConfig = async (config) => {
  if (config.is_locked || config.is_archived) return
  try {
    await api.patch(`event-management/phase-device-configs/${config.id}/`, {
      expected_channels: config.expected_channels
    })
  } catch (error) {
  }
}

const deleteConfig = (config) => {
  requireConfirmation(async () => {
    try {
      await api.delete(`event-management/phase-device-configs/${config.id}/`)
      await loadPhaseConfigs()
    } catch (error) {
    }
  })
}
</script>

<style scoped>
.phase-assignment-container { background: #fdfdfd; padding: 25px; border: 1px solid #e0e0e0; border-radius: 8px; box-shadow: inset 0 2px 4px rgba(0,0,0,0.02); }
.section-label { display: block; font-weight: bold; color: #2c3e50; margin-bottom: 10px; font-size: 1.1rem; }
.select-box { max-width: 400px; border: 2px solid #3498db; }
.page-group-radios { margin-top: 30px; padding-top: 20px; border-top: 1px dashed #ccc; }
.radio-list { display: flex; flex-direction: column; gap: 12px; margin-top: 15px; }
.radio-item { display: flex; align-items: center; cursor: pointer; padding: 10px 15px; background: white; border: 1px solid #ddd; border-radius: 6px; transition: all 0.2s; max-width: 400px; }
.radio-item:hover { border-color: #3498db; background: #f0f8ff; }
.radio-item input[type="checkbox"] { margin-right: 12px; transform: scale(1.2); cursor: pointer; }
.radio-label { font-size: 1.05rem; font-weight: 500; color: #333; }
.no-data { color: #e74c3c; background: #fadbd8; padding: 15px; border-radius: 6px; font-weight: 500; }
.fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }

.device-config-section { margin-top: 40px; }
.phase-card { background: white; border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; margin-bottom: 15px; }
.phase-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding-bottom: 10px; margin-bottom: 15px; }
.phase-header h4 { margin: 0; color: #2980b9; }

.config-accordion { border: 1px solid #dcdde1; border-radius: 6px; margin-bottom: 10px; overflow: hidden; }
.config-accordion.is-archived { opacity: 0.6; background: #f8f9fa; }
.accordion-header { background: #f1f2f6; padding: 12px 15px; display: flex; justify-content: space-between; align-items: center; cursor: pointer; transition: background 0.2s; }
.accordion-header:hover { background: #eccc68; color: #2f3542; }
.header-title { display: flex; align-items: center; gap: 10px; }
.accordion-body { padding: 15px; background: white; border-top: 1px solid #dcdde1; }
.lock-warning { background: #fff3cd; color: #856404; padding: 10px; border-radius: 4px; margin-bottom: 15px; font-size: 0.9rem; }
.channel-grid { display: flex; flex-wrap: wrap; gap: 8px; }
.channel-tag { background: #ecf0f1; padding: 5px 10px; border-radius: 15px; font-size: 0.85rem; display: flex; align-items: center; gap: 5px; cursor: pointer; border: 1px solid transparent; }
.channel-tag:hover:not(.disabled) { border-color: #3498db; }
.channel-tag.disabled { cursor: not-allowed; opacity: 0.7; }

.filter-bar { display: flex; gap: 15px; margin-bottom: 20px; align-items: center; }
.device-list { display: flex; flex-direction: column; gap: 10px; max-height: 400px; overflow-y: auto; }
.device-list-item { display: flex; justify-content: space-between; align-items: center; padding: 15px; border: 1px solid #e0e0e0; border-radius: 6px; background: #fff; }

.remove-channel-btn {
  background: none;
  border: none;
  color: #e74c3c;
  font-size: 0.8rem;
  margin-left: 5px;
  cursor: pointer;
  padding: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.remove-channel-btn:hover {
  color: #c0392b;
}
</style>
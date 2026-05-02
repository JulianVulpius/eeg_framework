<template>
  <BaseModal 
    :isOpen="isOpen" 
    :title="$t('views.runner.configure_device') + (phaseConfig ? ' - ' + phaseConfig.device_name : '')"
    @close="$emit('close')"
    customClass="large-modal"
  >
    <div v-if="isLoading" class="loading-state text-center p-4">
      {{ $t('common.loading') }}...
    </div>

    <div v-else-if="phaseConfig" class="device-instance-form">
      
      <div class="info-banner mb-4 p-3" style="background: #e8f4f8; border-left: 4px solid #3498db; border-radius: 4px;">
        <h4 style="margin-top: 0; color: #2980b9; font-size: 1.1rem;">Neue Aufnahme-Instanz</h4>
        <p style="margin-bottom: 0; font-size: 0.9rem; color: #34495e;">
          Bitte überprüfe die Kanalqualität und die Geräteeinstellungen für diese spezifische Aufnahme.
        </p>
      </div>

      <form @submit.prevent="saveInstance">
        
        <!-- KANAL QUALITÄT -->
        <div class="channels-section mb-4">
          <h4 style="border-bottom: 1px solid #eee; padding-bottom: 8px; margin-bottom: 15px;">
            Kanal-Qualität
          </h4>
          
          <div v-if="!phaseConfig.expected_channels || phaseConfig.expected_channels.length === 0" class="text-muted italic">
            Keine spezifischen Kanäle für dieses Gerät geplant.
          </div>
          
          <div v-else class="channel-quality-grid">
            <div v-for="ch in phaseConfig.expected_channels" :key="ch" class="channel-quality-item form-group">
              <label style="font-weight: 600; color: #2c3e50; margin-bottom: 4px;">{{ ch }}</label>
              <select v-model="channelStatuses[ch]" class="form-control select-sm">
                <option value="GOOD">🟢 Good</option>
                <option value="NOISY">🟡 Noisy</option>
                <option value="DISCONNECTED">🔴 Disconnected</option>
              </select>
            </div>
          </div>
        </div>

        <!-- METADATEN OVERWRITE -->
        <div class="metadata-section mb-4" v-if="metadataDefinitions.length > 0">
          <h4 style="border-bottom: 1px solid #eee; padding-bottom: 8px; margin-bottom: 15px;">
            Geräte-Einstellungen (Overwrite)
          </h4>
          
          <div v-for="def in metadataDefinitions" :key="def.id" class="form-group" style="margin-bottom: 15px;">
            <label>{{ def.name }} <span v-if="def.is_required">*</span></label>
            
            <input 
              v-if="def.expected_data_type === 'STRING'" 
              type="text" 
              v-model="metadataValues[def.id]" 
              class="form-control" 
              :required="def.is_required" 
            />
            
            <input 
              v-else-if="def.expected_data_type === 'INTEGER'" 
              type="number" step="1" 
              v-model="metadataValues[def.id]" 
              class="form-control" 
              :required="def.is_required" 
            />
            
            <input 
              v-else-if="def.expected_data_type === 'FLOAT'" 
              type="number" step="any" 
              v-model="metadataValues[def.id]" 
              class="form-control" 
              :required="def.is_required" 
            />
            
            <!-- Konsistente Checkbox für Booleans -->
            <label v-else-if="def.expected_data_type === 'BOOLEAN'" class="checkbox-label" style="display: flex; align-items: center; gap: 10px; font-weight: normal; cursor: pointer; margin-top: 5px;">
              <input type="checkbox" v-model="metadataValues[def.id]" style="width: 18px; height: 18px;" /> {{ $t('common.yes') }}
            </label>
            
            <textarea 
              v-else-if="def.expected_data_type === 'JSON'" 
              v-model="metadataValues[def.id]" 
              rows="3" 
              class="form-control" 
              :required="def.is_required">
            </textarea>

            <small class="text-muted" v-if="def.description" style="display: block; margin-top: 4px;">{{ def.description }}</small>
          </div>
        </div>

        <div class="modal-actions" style="margin-top: 30px; display: flex; justify-content: flex-end; gap: 10px; border-top: 1px solid #eee; padding-top: 20px;">
          <button type="button" class="btn-secondary" @click="$emit('close')">
            {{ $t('actions.cancel') }}
          </button>
          <button type="submit" class="btn-primary" :disabled="isSaving">
            {{ isSaving ? $t('common.saving') : 'Instanz speichern & Verwenden' }}
          </button>
        </div>
      </form>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, watch } from 'vue'
import api from '@/services/api'
import BaseModal from '@/components/ui/BaseModal.vue'

const props = defineProps({
  isOpen: { type: Boolean, default: false },
  sessionId: { type: [String, Number], required: true },
  phaseConfig: { type: Object, default: null } // EventGroupPageGroupDevice
})

const emit = defineEmits(['close', 'saved'])

const isLoading = ref(false)
const isSaving = ref(false)

const channelStatuses = ref({})
const metadataDefinitions = ref([])
const metadataValues = ref({})
const originalMetadataInstanceId = ref(null)

const initForm = async () => {
  channelStatuses.value = {}
  metadataDefinitions.value = []
  metadataValues.value = {}
  originalMetadataInstanceId.value = null

  if (!props.phaseConfig) return

  // 1. Initialisiere Kanäle
  if (props.phaseConfig.expected_channels) {
    props.phaseConfig.expected_channels.forEach(ch => {
      channelStatuses.value[ch] = 'GOOD'
    })
  }

  // 2. Lade Tier-3-Metadaten (falls vorhanden) als Basis für das Overwrite-Formular
  if (props.phaseConfig.metadata_instance) {
    isLoading.value = true
    try {
      const res = await api.get(`metadata-instances/${props.phaseConfig.metadata_instance}/`)
      originalMetadataInstanceId.value = res.data.id
      
      const groupRes = await api.get(`metadata/groups/${res.data.group}/`)
      metadataDefinitions.value = groupRes.data.full_definitions || []

      const initialVals = {}
      metadataDefinitions.value.forEach(def => {
        const existingVal = res.data.values.find(v => v.definition === def.id || v.definition_id === def.id)
        let val = existingVal ? existingVal.value : ''
        if (def.expected_data_type === 'BOOLEAN') {
          val = (val === 'true' || val === true)
        }
        initialVals[def.id] = val
      })
      metadataValues.value = initialVals
    } catch (e) {
      console.error("Fehler beim Laden der Tier-3-Metadaten:", e)
    } finally {
      isLoading.value = false
    }
  }
}

watch(() => props.isOpen, (newVal) => {
  if (newVal) initForm()
})

const saveInstance = async () => {
  if (!props.phaseConfig) return
  isSaving.value = true

  try {
    // Formatiere die Metadaten für das Backend
    const formattedMetadata = Object.keys(metadataValues.value).map(defId => ({
      definition: parseInt(defId),
      value: metadataValues.value[defId] !== null && metadataValues.value[defId] !== undefined ? String(metadataValues.value[defId]) : ''
    }))

    const payload = {
      session: props.sessionId,
      device_model: props.phaseConfig.device_model_id || props.phaseConfig.device_from_pool,
      phase_config: props.phaseConfig.id,
      final_channels: channelStatuses.value,
      // Wir schicken die überschriebenen Metadatenwerte mit an das Backend
      metadata_overwrite_values: formattedMetadata 
    }

    const res = await api.post('device-instances/', payload)
    emit('saved', res.data)
    emit('close')
  } catch (error) {
    console.error("Fehler beim Erstellen der Device Instance:", error)
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
.channel-quality-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 15px;
}
.channel-quality-item {
  background: #fdfdfd;
  border: 1px solid #e0e0e0;
  padding: 10px;
  border-radius: 6px;
  text-align: center;
}
.select-sm {
  padding: 4px 8px;
  font-size: 0.85rem;
  height: auto;
}
</style>
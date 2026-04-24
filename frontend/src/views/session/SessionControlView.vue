<template>
  <div class="category-manager" style="padding-bottom: 40px;">
    
    <div class="page-header" style="margin-bottom: 20px;">
      <h1 style="margin: 0;">{{ $t('views.session_control.title') }}</h1>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 25px;">
      
      <div style="display: flex; flex-direction: column; gap: 20px;">
        <div class="card">
          <h3 style="margin-top: 0; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">{{ $t('views.session_control.config') }}</h3>
          
          <div class="form-group">
            <BaseSearchSelect v-model="selectedPlaylist" :options="playlists" :label="$t('views.session_control.select_playlist')" :nullLabel="$t('views.session_control.no_playlist')" :disabled="isRunning" />
          </div>

          <div class="form-group" style="margin-top: 15px;">
            <BaseSearchSelect v-model="selectedGroup" :options="triggerGroups" :label="$t('views.session_control.select_group')" :nullLabel="$t('views.session_control.no_hotkeys')" :disabled="isRunning" />
          </div>

          <div class="form-group" style="margin-top: 15px;">
            <label>{{ $t('views.session_control.transition_time') }}</label>
            <input type="number" v-model="transitionTime" min="0" :disabled="isRunning" class="form-control" />
          </div>
        </div>

        <div class="card">
          <h3 style="margin-top: 0; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">{{ $t('views.session_control.active_hotkeys') }}</h3>
          
          <div style="margin-bottom: 10px;" v-if="activeHotkeys.length > 0">
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
              <input type="checkbox" v-model="hotkeysEnabled" />
              <strong>{{ $t('views.session_control.enable_hotkeys') }}</strong>
            </label>
          </div>

          <ul style="list-style: none; padding: 0; margin: 0;" v-if="activeHotkeys.length > 0">
            <li v-for="hk in activeHotkeys" :key="hk.id" :style="{ opacity: hotkeysEnabled ? 1 : 0.5, padding: '8px 0', borderBottom: '1px dashed var(--border-light)' }">
              <kbd style="background: #eee; padding: 2px 6px; border-radius: 4px; border: 1px solid #ccc;">{{ hk.key_code.toUpperCase() }}</kbd> ➔ {{ hk.triggerName }} (Value: {{ hk.triggerChar }})
            </li>
          </ul>
          <p v-else style="color: #7f8c8d; font-style: italic; margin: 0;">{{ $t('views.session_control.no_hotkeys_loaded') }}</p>
        </div>
      </div>

      <div style="display: flex; flex-direction: column; gap: 20px;">
        
        <div class="card" style="display: flex; gap: 15px; padding: 20px;">
          <button class="btn btn-primary" style="flex: 1; padding: 15px; font-size: 1.1rem;" :disabled="isRunning || !selectedPlaylist" @click="startEngine">
            ▶ START
          </button>
          <button class="btn btn-warning" style="flex: 1; padding: 15px; font-size: 1.1rem; color: white;" :disabled="!isRunning" @click="togglePause">
            {{ isPaused ? '▶ RESUME' : '⏸ PAUSE' }}
          </button>
          <button class="btn btn-danger" style="flex: 1; padding: 15px; font-size: 1.1rem;" :disabled="!isRunning" @click="stopEngine">
            ⏹ STOP
          </button>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
          <div :class="statusBadgeClass">
            Status: <strong>{{ engineStatus }}</strong>
          </div>
          <div class="card metric-card" style="margin: 0; padding: 10px;">
            <span class="metric-label" style="margin-bottom: 5px;">Duration</span>
            <div class="metric-value" style="font-size: 2rem;">
              {{ formatDuration(sessionDuration) }}
            </div>
          </div>
        </div>

        <div class="terminal-card" style="flex-grow: 1;">
          <div class="terminal-header">
            <h3>{{ $t('views.session_control.live_log') }}</h3>
            <button class="btn btn-danger" style="padding: 4px 10px; font-size: 0.8rem;" @click="clearLog">{{ $t('actions.clear') }}</button>
          </div>
          
          <div class="terminal-body">
            <div v-for="(log, index) in logs" :key="index" class="terminal-line">
              <span class="terminal-time">[{{ log.time }}]</span>
              <span class="terminal-msg" style="color: #ecf0f1;">{{ log.msg }}</span>
            </div>
            <div v-if="logs.length === 0" class="terminal-empty">{{ $t('views.session_control.waiting_events') }}</div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import engineApi from '@/services/engineApi'
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'
import { useFormatters } from '@/composables/useFormatters'

const { t } = useI18n()
const { formatDuration } = useFormatters()

const playlists = ref([])
const triggerGroups = ref([])
const triggerDefinitions = ref([])
const hotkeyMappings = ref([])

const selectedPlaylist = ref(null)
const selectedGroup = ref(null)
const transitionTime = ref(15)
const hotkeysEnabled = ref(false)

const isRunning = ref(false)
const isPaused = ref(false)
const logs = ref([])

const sessionDuration = ref(0)
let timerInterval = null

const engineStatus = computed(() => {
  if (!isRunning.value) return 'Ready'
  if (isPaused.value) return 'Paused'
  return 'Running'
})

const statusBadgeClass = computed(() => {
  if (!isRunning.value) return 'badge-ready'
  if (isPaused.value) return 'badge-paused'
  return 'badge-running'
})

const activeHotkeys = computed(() => {
  if (!selectedGroup.value) return []
  const groupMappings = hotkeyMappings.value.filter(m => m.group === selectedGroup.value)
  return groupMappings.map(mapping => {
    const def = triggerDefinitions.value.find(d => d.id === mapping.definition)
    return { ...mapping, triggerName: def ? def.name : 'Unknown', triggerChar: def ? def.trigger_character : '?' }
  })
})

const allStimuli = ref([]) 

const loadDjangoData = async () => {
  try {
    const [resPlaylists, resGroups, resDefs, resHotkeys, resStimuli] = await Promise.all([
      api.get('playlists/'), api.get('triggers/groups/'), api.get('triggers/definitions/'),
      api.get('triggers/hotkeys/'), api.get('stimuli/') 
    ])
    playlists.value = resPlaylists.data; triggerGroups.value = resGroups.data;
    triggerDefinitions.value = resDefs.data; hotkeyMappings.value = resHotkeys.data;
    allStimuli.value = resStimuli.data 
  } catch (error) { 
    console.error("Error loading setup data:", error) 
  }
}

const addLog = (msg) => {
  const time = new Date().toLocaleTimeString()
  logs.value.unshift({ time, msg })
  if (logs.value.length > 100) logs.value.pop()
}
const clearLog = () => { logs.value = [] }

const startTimer = () => {
  clearInterval(timerInterval)
  timerInterval = setInterval(() => { sessionDuration.value++ }, 1000)
}

const startEngine = async () => {
  try {
    const playlist = playlists.value.find(p => p.id === selectedPlaylist.value)
    if (!playlist || !playlist.stimuli || playlist.stimuli.length === 0) { 
      addLog(t('views.session_control.log_error_empty'))
      return 
    }

    const realSongs = playlist.stimuli.map(stimulusId => {
      const stimulusData = allStimuli.value.find(s => s.id === stimulusId)
      return { name: stimulusData.name, duration: stimulusData.duration, audio_file: stimulusData.source }
    })

    await engineApi.post('/start', { transition_time: transitionTime.value, songs: realSongs })
    isRunning.value = true; 
    isPaused.value = false;
    sessionDuration.value = 0;
    startTimer();
    addLog(t('views.session_control.log_started', { name: playlist.name }))
  } catch (error) { 
    addLog(t('views.session_control.log_error_start', { msg: error.message })) 
  }
}

const togglePause = async () => {
  try {
    if (isPaused.value) { 
      await engineApi.post('/resume'); 
      isPaused.value = false; 
      startTimer();
      addLog(t('views.session_control.log_resumed')) 
    } else { 
      await engineApi.post('/pause'); 
      isPaused.value = true; 
      clearInterval(timerInterval);
      addLog(t('views.session_control.log_paused')) 
    }
  } catch (error) { 
    addLog(t('views.session_control.log_error_pause', { msg: error.message })) 
  }
}

const stopEngine = async () => {
  try {
    await engineApi.post('/stop')
    isRunning.value = false; 
    isPaused.value = false;
    clearInterval(timerInterval);
    addLog(t('views.session_control.log_stopped'))
  } catch (error) { 
    addLog(t('views.session_control.log_error_stop', { msg: error.message })) 
  }
}

const handleKeydown = (event) => {
  if (!hotkeysEnabled.value || !isRunning.value || isPaused.value) return
  const hotkey = activeHotkeys.value.find(h => h.key_code.toLowerCase() === event.key.toLowerCase())
  if (hotkey) {
    event.preventDefault()
    engineApi.post('/manual-trigger', { trigger_value: hotkey.triggerChar, description: hotkey.triggerName })
      .catch(err => addLog(t('views.session_control.log_error_send', { msg: err.message })))
    addLog(t('views.session_control.log_manual_trigger', { name: hotkey.triggerName, val: hotkey.triggerChar }))
  }
}

onMounted(() => { loadDjangoData(); window.addEventListener('keydown', handleKeydown) })
onUnmounted(() => { 
  window.removeEventListener('keydown', handleKeydown); 
  clearInterval(timerInterval);
  if (isRunning.value) stopEngine(); 
})
</script>

<style scoped>
</style>
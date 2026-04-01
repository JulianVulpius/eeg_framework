<template>
  <div class="category-manager">
    <div class="page-header">
      <h1>{{ $t('views.session_control.title') }}</h1>
    </div>

    <div class="control-grid">
      <div class="setup-panel">
        <div class="panel-section">
          <h3>{{ $t('views.session_control.config') }}</h3>
          
          <div class="form-group">
            <BaseSearchSelect 
              v-model="selectedPlaylist"
              :options="playlists"
              :label="$t('views.session_control.select_playlist')"
              :nullLabel="$t('views.session_control.no_playlist')"
              :disabled="isRunning"
            />
          </div>

          <div class="form-group" style="margin-top: 15px;">
            <BaseSearchSelect 
              v-model="selectedGroup"
              :options="triggerGroups"
              :label="$t('views.session_control.select_group')"
              :nullLabel="$t('views.session_control.no_hotkeys')"
              :disabled="isRunning"
            />
          </div>

          <div class="form-group" style="margin-top: 15px;">
            <label>{{ $t('views.session_control.transition_time') }}</label>
            <input type="number" v-model="transitionTime" min="0" :disabled="isRunning" class="form-control" />
          </div>
        </div>

        <div class="panel-section">
          <h3>{{ $t('views.session_control.active_hotkeys') }}</h3>
          
          <div style="margin-bottom: 10px;" v-if="activeHotkeys.length > 0">
            <label style="display: flex; align-items: center; gap: 8px; cursor: pointer;">
              <input type="checkbox" v-model="hotkeysEnabled" />
              <strong>{{ $t('views.session_control.enable_hotkeys') }}</strong>
            </label>
          </div>

          <ul class="hotkey-list" v-if="activeHotkeys.length > 0">
            <li v-for="hk in activeHotkeys" :key="hk.id" :style="{ opacity: hotkeysEnabled ? 1 : 0.5 }">
              <kbd>{{ hk.key_code.toUpperCase() }}</kbd> ➔ {{ hk.triggerName }} (Value: {{ hk.triggerChar }})
            </li>
          </ul>
          <p class="empty-state" v-else>{{ $t('views.session_control.no_hotkeys_loaded') }}</p>
        </div>
      </div>

      <div class="execution-panel">
        <div class="engine-controls">
          <button class="btn-start" :disabled="isRunning || !selectedPlaylist" @click="startEngine">
            ▶ START
          </button>
          <button class="btn-pause" :disabled="!isRunning" @click="togglePause">
            {{ isPaused ? '▶ RESUME' : '⏸ PAUSE' }}
          </button>
          <button class="btn-stop" :disabled="!isRunning" @click="stopEngine">
            ⏹ STOP
          </button>
        </div>

        <div class="status-box" :class="{ 'is-running': isRunning, 'is-paused': isPaused }">
          Status: <strong>{{ engineStatus }}</strong>
        </div>

        <div class="panel-section log-section">
          <h3>{{ $t('views.session_control.live_log') }}</h3>
          <button class="btn-clear" @click="clearLog">{{ $t('actions.clear') }}</button>
          <div class="log-container">
            <div v-for="(log, index) in logs" :key="index" class="log-entry">
              <span class="log-time">[{{ log.time }}]</span> {{ log.msg }}
            </div>
            <div v-if="logs.length === 0" class="empty-state">{{ $t('views.session_control.waiting_events') }}</div>
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

const { t } = useI18n()

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

const engineStatus = computed(() => {
  if (!isRunning.value) return 'Ready'
  if (isPaused.value) return 'Paused'
  return 'Running'
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
    isRunning.value = true; isPaused.value = false;
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
      addLog(t('views.session_control.log_resumed')) 
    } else { 
      await engineApi.post('/pause'); 
      isPaused.value = true; 
      addLog(t('views.session_control.log_paused')) 
    }
  } catch (error) { 
    addLog(t('views.session_control.log_error_pause', { msg: error.message })) 
  }
}

const stopEngine = async () => {
  try {
    await engineApi.post('/stop')
    isRunning.value = false; isPaused.value = false;
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
onUnmounted(() => { window.removeEventListener('keydown', handleKeydown); if (isRunning.value) stopEngine() })
</script>

<style scoped>
.control-grid { display: grid; grid-template-columns: 1fr 2fr; gap: 20px; margin-top: 20px; }
.setup-panel, .execution-panel { display: flex; flex-direction: column; gap: 20px; }

.panel-section { background: var(--sidebar-bg); padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.panel-section h3 { margin-top: 0; border-bottom: 1px solid var(--border-color); padding-bottom: 10px; color: var(--text-main); }

.hotkey-list { list-style: none; padding: 0; margin: 0; }
.hotkey-list li { padding: 8px 0; border-bottom: 1px dashed var(--border-light); font-size: 0.95rem; }

.engine-controls { display: flex; gap: 15px; }
.engine-controls button { flex: 1; padding: 15px; font-size: 1.1rem; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; transition: opacity 0.2s, transform 0.1s; }
.engine-controls button:disabled { opacity: 0.5; cursor: not-allowed; }
.engine-controls button:not(:disabled):active { transform: scale(0.98); }

.btn-start { background-color: var(--success-color); color: white; }
.btn-pause { background-color: var(--warning-color); color: white; }
.btn-stop { background-color: var(--danger-color); color: white; }

.status-box { padding: 15px; border-radius: 8px; background-color: var(--bg-color); border-left: 5px solid var(--border-color); font-size: 1.1rem; }
.status-box.is-running { border-color: var(--success-color); background-color: rgba(46, 204, 113, 0.1); }
.status-box.is-paused { border-color: var(--warning-color); background-color: rgba(243, 156, 18, 0.1); }

.log-section { flex-grow: 1; display: flex; flex-direction: column; position: relative; }
.btn-clear { position: absolute; top: 15px; right: 20px; background: none; border: 1px solid var(--border-color); border-radius: 4px; cursor: pointer; padding: 4px 8px; font-size: 0.8rem; }
.log-container { background: var(--text-main); color: var(--bg-color); font-family: 'Consolas', monospace; font-size: 0.9rem; padding: 10px; border-radius: 4px; height: 300px; overflow-y: auto; margin-top: 10px; }
.log-entry { margin-bottom: 4px; }
.log-time { color: var(--text-muted); margin-right: 8px; }
</style>
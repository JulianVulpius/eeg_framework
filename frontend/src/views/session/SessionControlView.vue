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

        <div class="card" v-if="activePlaylistItems.length > 0 && !isRunning">
          <h3 style="margin-top: 0; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">Playlist Preview</h3>
          <ul style="list-style: none; padding: 0; margin: 0; max-height: 250px; overflow-y: auto;">
            <li v-for="(item, idx) in activePlaylistItems" :key="idx" style="padding: 8px 0; border-bottom: 1px solid var(--border-light); font-size: 0.9rem;">
              <strong>{{ idx + 1 }}. {{ item.name }}</strong> ({{ item.type }})
              <span v-if="item.duration" style="float: right;">{{ formatDuration(item.duration) }}</span>
              <span v-else style="float: right; color: #7f8c8d; font-style: italic;">Untimed</span>
            </li>
          </ul>
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
          <button class="btn btn-primary" style="flex: 1; padding: 15px; font-size: 1.1rem;" :disabled="isRunning || !selectedPlaylist || isCompleted" @click="startEngine">
            ▶ START
          </button>
          <button class="btn btn-warning" style="flex: 1; padding: 15px; font-size: 1.1rem; color: white;" :disabled="!isRunning || isCompleted" @click="togglePause">
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

        <div v-if="isRunning || isCompleted" class="presentation-container card">
          <div v-if="isCompleted" class="complete-message">
            <h2>Session Completed</h2>
            <button class="btn btn-primary" @click="resetSession" style="margin-top: 15px;">Reset</button>
          </div>
          <div v-else-if="isTransitioning" class="transition-message">
            <h2>Transitioning...</h2>
          </div>
          <div v-else-if="currentItem" class="media-wrapper">
            <img v-if="currentItem.type === 'IMAGE'" :src="currentItem.file" class="media-element" />
            <video v-else-if="currentItem.type === 'VIDEO'" :src="currentItem.file" autoplay class="media-element" @playing="onVideoPlaying" @ended="onMediaEnded"></video>
            <div v-else-if="currentItem.type === 'CUSTOM'" class="custom-text">{{ currentItem.description }}</div>
            <div v-else-if="currentItem.type === 'AUDIO'" class="audio-placeholder">🎵 Playing Audio: {{ currentItem.name }}</div>

            <button v-if="needsManualNext" class="btn btn-primary btn-next" @click="onMediaEnded">Next ➔</button>
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
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import engineApi, { connectEngineWS, sendWSTrigger } from '@/services/engineApi'
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'
import { useFormatters } from '@/composables/useFormatters'

const { t } = useI18n()
const { formatDuration } = useFormatters()

const playlists = ref([])
const triggerGroups = ref([])
const triggerDefinitions = ref([])
const hotkeyMappings = ref([])
const allStimuli = ref([])

const selectedPlaylist = ref(null)
const selectedGroup = ref(null)
const transitionTime = ref(15)
const hotkeysEnabled = ref(false)

const isRunning = ref(false)
const isPaused = ref(false)
const isCompleted = ref(false)
const isTransitioning = ref(false)
const logs = ref([])

const sessionDuration = ref(0)
let timerInterval = null

const currentIndex = ref(0)
const needsManualNext = ref(false)
let activeTimer = null
let lastFrameTime = 0
let currentTimerStartTime = 0
let timerDurationRemaining = 0

const activePlaylistItems = computed(() => {
  if (!selectedPlaylist.value) return []
  const playlist = playlists.value.find(p => p.id === selectedPlaylist.value)
  if (!playlist || !playlist.stimuli) return []
  return playlist.stimuli.map(id => allStimuli.value.find(s => s.id === id)).filter(Boolean)
})

const currentItem = computed(() => {
  if (currentIndex.value >= 0 && currentIndex.value < activePlaylistItems.value.length) {
    return activePlaylistItems.value[currentIndex.value]
  }
  return null
})

const engineStatus = computed(() => {
  if (isCompleted.value) return 'Completed'
  if (!isRunning.value) return 'Ready'
  if (isPaused.value) return 'Paused'
  return 'Running'
})

const statusBadgeClass = computed(() => {
  if (isCompleted.value) return 'badge-completed'
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

const loadDjangoData = async () => {
  try {
    const [resPlaylists, resGroups, resDefs, resHotkeys, resStimuli] = await Promise.all([
      api.get('playlists/'), api.get('triggers/groups/'), api.get('triggers/definitions/'),
      api.get('triggers/hotkeys/'), api.get('stimuli/')
    ])
    playlists.value = resPlaylists.data
    triggerGroups.value = resGroups.data
    triggerDefinitions.value = resDefs.data
    hotkeyMappings.value = resHotkeys.data
    allStimuli.value = resStimuli.data
  } catch (error) {}
}

const addLog = (msg) => {
  const time = new Date().toLocaleTimeString()
  logs.value.unshift({ time, msg })
  if (logs.value.length > 100) logs.value.pop()
}

const clearLog = () => { logs.value = [] }

const startGlobalTimer = () => {
  clearInterval(timerInterval)
  timerInterval = setInterval(() => { sessionDuration.value++ }, 1000)
}

const preloadMedia = () => {
  activePlaylistItems.value.forEach(item => {
    if (item.type === 'IMAGE' && item.file) {
      const img = new Image()
      img.src = item.file
    } else if (item.type === 'VIDEO' && item.file) {
      const vid = document.createElement('video')
      vid.preload = 'auto'
      vid.src = item.file
    }
  })
}

const startEngine = () => {
  if (activePlaylistItems.value.length === 0) {
    addLog(t('views.session_control.log_error_empty'))
    return
  }
  preloadMedia()
  isRunning.value = true
  isPaused.value = false
  isCompleted.value = false
  sessionDuration.value = 0
  currentIndex.value = 0
  startGlobalTimer()
  addLog(t('views.session_control.log_started', { name: playlists.value.find(p => p.id === selectedPlaylist.value).name }))
  runCurrentStimulus()
}

const runCurrentStimulus = async () => {
  if (currentIndex.value >= activePlaylistItems.value.length) {
    completeSession()
    return
  }
  const item = currentItem.value
  
  if (item.type === 'AUDIO') {
    sendWSTrigger('1', `Start: ${item.name}`)
    addLog(`Started: ${item.name}`)
    await engineApi.post('/play-single', { audio_file: item.file.split('/').pop() })
    if (item.duration) {
      startRAF(item.duration)
    } else {
      needsManualNext.value = true
    }
  } else if (item.type === 'IMAGE' || item.type === 'CUSTOM') {
    sendWSTrigger('1', `Start: ${item.name}`)
    addLog(`Displayed: ${item.name}`)
    if (item.duration && item.duration > 0) {
      startRAF(item.duration)
    } else {
      needsManualNext.value = true
    }
  }
}

const onVideoPlaying = () => {
  sendWSTrigger('1', `Start: ${currentItem.value.name}`)
  addLog(`Video Playing: ${currentItem.value.name}`)
}

const startRAF = (durationSeconds) => {
  timerDurationRemaining = durationSeconds * 1000
  lastFrameTime = performance.now()
  const tick = (now) => {
    if (!isRunning.value) return
    if (!isPaused.value) {
      const delta = now - lastFrameTime
      timerDurationRemaining -= delta
      if (timerDurationRemaining <= 0) {
        onMediaEnded()
        return
      }
    }
    lastFrameTime = now
    activeTimer = requestAnimationFrame(tick)
  }
  activeTimer = requestAnimationFrame(tick)
}

const onMediaEnded = async () => {
  if (activeTimer) cancelAnimationFrame(activeTimer)
  needsManualNext.value = false
  
  const item = currentItem.value
  sendWSTrigger('2', `End: ${item.name}`)
  
  if (item.type === 'AUDIO') {
    await engineApi.post('/stop-audio')
  }
  
  if (transitionTime.value > 0 && currentIndex.value < activePlaylistItems.value.length - 1) {
    isTransitioning.value = true
    sendWSTrigger('9', `Trans Start`)
    await new Promise(r => setTimeout(r, transitionTime.value * 1000))
    sendWSTrigger('10', `Trans End`)
    isTransitioning.value = false
  }
  
  currentIndex.value++
  runCurrentStimulus()
}

const completeSession = () => {
  isRunning.value = false
  isCompleted.value = true
  clearInterval(timerInterval)
  addLog("Session Completed Successfully.")
}

const resetSession = () => {
  isCompleted.value = false
  currentIndex.value = 0
  sessionDuration.value = 0
  clearLog()
}

const togglePause = async () => {
  if (isPaused.value) {
    if (currentItem.value?.type === 'AUDIO') await engineApi.post('/resume')
    const videos = document.querySelectorAll('.media-element')
    videos.forEach(v => { if (v.play) v.play() })
    isPaused.value = false
    lastFrameTime = performance.now()
    startGlobalTimer()
    addLog(t('views.session_control.log_resumed'))
  } else {
    if (currentItem.value?.type === 'AUDIO') await engineApi.post('/pause')
    const videos = document.querySelectorAll('.media-element')
    videos.forEach(v => { if (v.pause) v.pause() })
    isPaused.value = true
    clearInterval(timerInterval)
    addLog(t('views.session_control.log_paused'))
  }
}

const stopEngine = async () => {
  isRunning.value = false
  isPaused.value = false
  isCompleted.value = false
  isTransitioning.value = false
  needsManualNext.value = false
  clearInterval(timerInterval)
  if (activeTimer) cancelAnimationFrame(activeTimer)
  await engineApi.post('/stop-audio')
  addLog(t('views.session_control.log_stopped'))
}

const handleKeydown = (event) => {
  if (!hotkeysEnabled.value || !isRunning.value || isPaused.value || isTransitioning.value) return
  const hotkey = activeHotkeys.value.find(h => h.key_code.toLowerCase() === event.key.toLowerCase())
  if (hotkey) {
    event.preventDefault()
    sendWSTrigger(hotkey.triggerChar, hotkey.triggerName)
    addLog(t('views.session_control.log_manual_trigger', { name: hotkey.triggerName, val: hotkey.triggerChar }))
  }
}

onMounted(() => {
  loadDjangoData()
  connectEngineWS()
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
  clearInterval(timerInterval)
  if (activeTimer) cancelAnimationFrame(activeTimer)
  if (isRunning.value) stopEngine()
})
</script>

<style scoped>
.presentation-container {
  width: 100%;
  height: 400px;
  background: #111;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}
.media-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}
.media-element {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}
.custom-text {
  color: #fff;
  font-size: 2rem;
  text-align: center;
  padding: 20px;
}
.audio-placeholder {
  color: #fff;
  font-size: 1.5rem;
  font-style: italic;
}
.transition-message {
  color: #bdc3c7;
  font-size: 1.5rem;
}
.complete-message {
  text-align: center;
  color: #2ecc71;
}
.btn-next {
  position: absolute;
  bottom: 20px;
  right: 20px;
  font-size: 1.2rem;
  padding: 10px 20px;
  z-index: 10;
  box-shadow: 0 4px 6px rgba(0,0,0,0.3);
}
.badge-completed {
  background-color: #2ecc71;
  color: white;
  padding: 10px;
  border-radius: 4px;
  text-align: center;
  font-size: 1.2rem;
}
</style>
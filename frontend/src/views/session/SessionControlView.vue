<template>
  <div class="category-manager" style="padding-bottom: 40px;">
    <div class="page-header" style="margin-bottom: 20px;">
      <h1 style="margin: 0;">{{ $t('views.session_control.title') }}</h1>
    </div>

    <div style="display: grid; grid-template-columns: 1fr 2fr; gap: 25px;">
      
      <div style="display: flex; flex-direction: column; gap: 20px;">
        
        <div v-if="isRunning" style="background-color: #e2f3f5; color: #0c5460; padding: 12px; border-radius: 6px; border-left: 4px solid #17a2b8; font-size: 0.9rem; line-height: 1.4;">
          <strong>{{ $t('views.session_control.config_locked') }}</strong><br/>
          {{ $t('views.session_control.config_locked_info') }}
        </div>

        <div class="card" :style="{ opacity: isRunning ? 0.7 : 1, pointerEvents: isRunning ? 'none' : 'auto' }">
          <h3 style="margin-top: 0; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">{{ $t('views.session_control.setup') }}</h3>
          
          <div class="form-group">
            <BaseSearchSelect v-model="selectedPlaylist" :options="playlists" :label="$t('views.session_control.select_playlist')" :nullLabel="$t('views.session_control.no_playlist')" />
          </div>
          
          <div class="form-group" style="margin-top: 15px;">
            <BaseSearchSelect v-model="selectedGroup" :options="triggerGroups" :label="$t('views.session_control.select_group')" :nullLabel="$t('views.session_control.no_hotkeys')" />
          </div>
          
          <div style="margin-top: 20px; display: flex; flex-direction: column; gap: 12px;">
            <label style="display: flex; align-items: flex-start; gap: 8px; cursor: pointer;">
              <input type="checkbox" v-model="configAutoTransition" style="margin-top: 4px;" />
              <div>
                <strong>{{ $t('views.session_control.auto_transition') }}</strong>
                <p style="margin: 0; font-size: 0.8rem; color: #7f8c8d;">{{ $t('views.session_control.auto_transition_info') }}</p>
              </div>
            </label>

            <div class="form-group" style="margin-top: 5px; margin-left: 25px;" v-if="configAutoTransition">
              <label>{{ $t('views.session_control.transition_time') }}</label>
              <input type="number" v-model="transitionTime" min="0" class="form-control" />
            </div>

            <label style="display: flex; align-items: flex-start; gap: 8px; cursor: pointer;">
              <input type="checkbox" v-model="configBlackscreen" style="margin-top: 4px;" />
              <div>
                <strong>{{ $t('views.session_control.blackscreen_mode') }}</strong>
                <p style="margin: 0; font-size: 0.8rem; color: #7f8c8d;">{{ $t('views.session_control.blackscreen_info') }}</p>
              </div>
            </label>

            <label style="display: flex; align-items: flex-start; gap: 8px; cursor: pointer;">
              <input type="checkbox" v-model="configPhotodiode" style="margin-top: 4px;" />
              <div>
                <strong>{{ $t('views.session_control.photodiode') }}</strong>
                <p style="margin: 0; font-size: 0.8rem; color: #7f8c8d;">{{ $t('views.session_control.photodiode_info') }}</p>
              </div>
            </label>

            <label style="display: flex; align-items: flex-start; gap: 8px; cursor: pointer;">
              <input type="checkbox" v-model="configPauseEnabled" style="margin-top: 4px;" />
              <div>
                <strong>{{ $t('views.session_control.pause_enabled') }}</strong>
                <p style="margin: 0; font-size: 0.8rem; color: #7f8c8d;">{{ $t('views.session_control.pause_info') }}</p>
              </div>
            </label>
          </div>
        </div>

        <div class="card" v-if="activePlaylistItems.length > 0 && !isRunning">
          <h3 style="margin-top: 0; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">
            {{ $t('views.session_control.playlist_preview') }}
            <span style="display: block; font-size: 0.85rem; color: #7f8c8d; font-weight: normal; margin-top: 5px;">
              {{ $t('views.session_control.total_duration') }}: {{ playlistPreviewData.totalExpected }}
            </span>
          </h3>
          <ul style="list-style: none; padding: 0; margin: 0; max-height: 350px; overflow-y: auto;">
            <li v-for="(item, idx) in playlistPreviewData.items" :key="idx" style="padding: 10px 0; border-bottom: 1px solid var(--border-light); font-size: 0.85rem;">
              <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <strong>{{ idx + 1 }}. {{ item.name }} <span style="color: #3498db;">[{{ item.isUntimed ? '∞' : formatDuration(item.duration) }}]</span></strong>
                <span>{{ item.isUntimed ? $t('views.session_control.manual') : formatDuration(item.duration) }}</span>
              </div>
              
              <div v-if="item.hasOverlapWarning" style="color: #e67e22; font-size: 0.75rem; margin-bottom: 5px; font-weight: bold;">
                ⚠️ {{ $t('views.session_control.overlap_warning', { time: item.effectiveTransS }) }}
              </div>

              <div style="display: grid; grid-template-columns: 1fr 1fr; color: #7f8c8d; font-size: 0.8rem; gap: 4px;">
                <div style="color: #2ecc71;">▶ Start: {{ item.startStr }}</div>
                <div v-if="configAutoTransition && !configBlackscreen">⇥ Trans In: {{ item.transEndStr }}</div>
                <div v-if="configAutoTransition && !configBlackscreen">↦ Trans Out: {{ item.transStartStr }}</div>
                <div style="color: #e74c3c;">⏹ End: {{ item.endStr }}</div>
              </div>
            </li>
          </ul>
        </div>

        <div class="card" :style="{ opacity: isRunning ? 0.7 : 1, pointerEvents: isRunning ? 'none' : 'auto' }">
          <h3 style="margin-top: 0; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">{{ $t('views.session_control.trigger_roles') }}</h3>
          
          <div v-if="!selectedGroup" style="color: #c0392b; font-size: 0.9rem; margin-bottom: 10px;">
            {{ $t('views.session_control.no_group_warning') }}
          </div>

          <template v-else>
            <div class="form-group">
              <BaseSearchSelect v-model="roleStart" :options="triggerDefOptions" :label="$t('views.session_control.role_start')" />
            </div>
            <div class="form-group" style="margin-top: 10px;">
              <BaseSearchSelect v-model="roleEnd" :options="triggerDefOptions" :label="$t('views.session_control.role_end')" />
            </div>
            
            <template v-if="configAutoTransition && !configBlackscreen">
              <div class="form-group" style="margin-top: 10px;">
                <BaseSearchSelect v-model="roleTransStart" :options="triggerDefOptions" :label="$t('views.session_control.role_trans_start')" />
              </div>
              <div class="form-group" style="margin-top: 10px;">
                <BaseSearchSelect v-model="roleTransEnd" :options="triggerDefOptions" :label="$t('views.session_control.role_trans_end')" />
              </div>
            </template>

            <template v-if="configPauseEnabled">
              <div class="form-group" style="margin-top: 10px;">
                <BaseSearchSelect v-model="rolePauseStart" :options="triggerDefOptions" :label="$t('views.session_control.role_pause_start')" />
              </div>
              <div class="form-group" style="margin-top: 10px;">
                <BaseSearchSelect v-model="rolePauseEnd" :options="triggerDefOptions" :label="$t('views.session_control.role_pause_end')" />
              </div>
            </template>
          </template>
        </div>

        <div class="card" :style="{ opacity: isRunning ? 0.7 : 1 }">
          <h3 style="margin-top: 0; border-bottom: 1px solid var(--border-color); padding-bottom: 10px;">{{ $t('views.session_control.manual_hotkeys') }}</h3>
          
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
          <p v-else style="color: #7f8c8d; font-style: italic; margin: 0; font-size: 0.9rem;">
            {{ $t('views.session_control.all_triggers_used') }}
          </p>
        </div>
      </div>

      <div style="display: flex; flex-direction: column; gap: 20px;">
        
        <div class="card preflight-card" v-if="!isRunning && !isCompleted">
          <h3 style="margin-top: 0;">{{ $t('views.session_control.preflight_title') }}</h3>
          <div class="preflight-grid">
            <div class="pf-item" :class="{ 'pf-ok': selectedPlaylist, 'pf-err': !selectedPlaylist }">
              <span class="pf-icon">{{ selectedPlaylist ? '✓' : '✗' }}</span> {{ $t('views.session_control.preflight_playlist') }}
            </div>
            <div class="pf-item" :class="{ 'pf-ok': selectedGroup, 'pf-err': !selectedGroup }">
              <span class="pf-icon">{{ selectedGroup ? '✓' : '✗' }}</span> {{ $t('views.session_control.preflight_group') }}
            </div>
            <div class="pf-item" :class="{ 'pf-ok': areTriggersAssigned, 'pf-err': !areTriggersAssigned }">
              <span class="pf-icon">{{ areTriggersAssigned ? '✓' : '✗' }}</span> {{ $t('views.session_control.preflight_roles') }}
            </div>
            <div class="pf-item" :class="{ 'pf-ok': preloadedMedia, 'pf-err': !preloadedMedia }">
              <span class="pf-icon">{{ preloadedMedia ? '✓' : '⧖' }}</span> 
              {{ $t('views.session_control.preflight_media', { loaded: preloadLoaded, total: preloadTotal }) }}
            </div>
          </div>
        </div>

        <div class="card" style="display: flex; gap: 15px; padding: 20px;">
          <button class="btn btn-primary" style="flex: 1; padding: 15px; font-size: 1.1rem;" :disabled="!isReadyToStart || !preloadedMedia || isRunning || isCompleted" @click="startEngine">
            ▶ {{ $t('actions.start') }}
          </button>
          
          <button v-if="configPauseEnabled" class="btn btn-warning" style="flex: 1; padding: 15px; font-size: 1.1rem; color: white;" :disabled="!isRunning || isCompleted" @click="togglePause">
            {{ isPaused ? `▶ ${$t('actions.resume')}` : `⏸ ${$t('actions.pause')}` }}
          </button>
          
          <button class="btn btn-danger" style="flex: 1; padding: 15px; font-size: 1.1rem;" :disabled="!isRunning" @click="stopEngine">
            ⏹ {{ $t('actions.stop') }}
          </button>
        </div>

        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
          <div :class="statusBadgeClass">
            {{ $t('views.session_control.status') }}: <strong>{{ engineStatus }}</strong>
          </div>
          <div class="card metric-card" style="margin: 0; padding: 10px;">
            <span class="metric-label" style="margin-bottom: 5px;">{{ $t('views.session_control.elapsed_time') }}</span>
            <div class="metric-value" style="font-size: 2rem;">
              {{ formatDuration(sessionDuration) }}
            </div>
          </div>
        </div>

        <div ref="presentationContainer" v-if="isRunning || isCompleted" class="presentation-container card" :class="{ 'is-fullscreen': isFullscreen }">
          
          <button v-if="!isFullscreen" class="btn btn-secondary btn-fullscreen" @click="toggleFullscreen">
            {{ $t('views.session_control.btn_fullscreen') }}
          </button>
          <button v-if="isFullscreen" class="btn btn-secondary btn-fullscreen exit-fullscreen" @click="toggleFullscreen">
            {{ $t('views.session_control.btn_exit_fullscreen') }}
          </button>

          <div v-if="showPhotodiode" class="photodiode-sync"></div>

          <div v-if="isCompleted" class="complete-message">
            <h2>{{ $t('views.session_control.session_completed') }}</h2>
            <button class="btn btn-primary" @click="resetSession" style="margin-top: 15px;">{{ $t('views.session_control.btn_reset') }}</button>
          </div>
          
          <div v-else-if="isBlackscreenActive" class="blackscreen-wrapper">
             <button class="btn btn-primary btn-next" @click="onManualNext">{{ $t('views.session_control.next_stimulus') }}</button>
          </div>

          <div v-else-if="currentItem" class="media-wrapper">
            <img v-if="currentItem.type === 'IMAGE'" :src="currentItem.file" class="media-element" />
            <video v-else-if="currentItem.type === 'VIDEO'" :src="currentItem.file" autoplay playsinline class="media-element" @playing="onMediaPlaying"></video>
            <div v-else-if="currentItem.type === 'CUSTOM'" class="custom-text">{{ currentItem.description }}</div>
            
            <div v-else-if="currentItem.type === 'AUDIO'" class="audio-wrapper">
              <div class="audio-placeholder">{{ $t('views.session_control.playing_audio', { name: currentItem.name }) }}</div>
              <audio :src="currentItem.file" autoplay @playing="onMediaPlaying" style="display: none;"></audio>
            </div>

            <button v-if="needsManualNext && !configBlackscreen" class="btn btn-primary btn-next" :disabled="isManualTransitioning" @click="onManualNext">
              {{ isManualTransitioning ? $t('views.session_control.transitioning') : $t('views.session_control.next_stimulus') }}
            </button>
          </div>
        </div>

        <div class="terminal-card" style="flex-grow: 1;">
          <div class="terminal-header">
            <h3>{{ $t('views.session_control.live_log') }}</h3>
            <div>
              <button class="btn btn-secondary" style="padding: 4px 10px; font-size: 0.8rem; margin-right: 10px;" @click="exportLog">{{ $t('views.session_control.export_txt') }}</button>
              <button class="btn btn-danger" style="padding: 4px 10px; font-size: 0.8rem;" @click="clearLog">{{ $t('actions.clear') }}</button>
            </div>
          </div>
          <div class="terminal-body">
            <div v-for="(log, index) in logs" :key="index" class="terminal-line">
              <span class="terminal-time">[{{ log.time }} | {{ log.sessionDur }}]</span>
              <span class="terminal-msg" :style="{ color: log.isWarning ? '#e74c3c' : '#ecf0f1' }">{{ log.msg }}</span>
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
import { connectEngineWS, sendWSTrigger } from '@/services/engineApi'
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
const configPhotodiode = ref(false)
const configBlackscreen = ref(false)
const configPauseEnabled = ref(false)
const configAutoTransition = ref(false)

const roleStart = ref(null)
const roleEnd = ref(null)
const roleTransStart = ref(null)
const roleTransEnd = ref(null)
const rolePauseStart = ref(null)
const rolePauseEnd = ref(null)

watch(selectedGroup, () => {
  roleStart.value = null; roleEnd.value = null
  roleTransStart.value = null; roleTransEnd.value = null
  rolePauseStart.value = null; rolePauseEnd.value = null
})

const isRunning = ref(false)
const isPaused = ref(false)
const isCompleted = ref(false)
const logs = ref([])
const sessionDuration = ref(0)
let timerInterval = null

const presentationContainer = ref(null)
const isFullscreen = ref(false)

const currentIndex = ref(0)
const needsManualNext = ref(false)
const isManualTransitioning = ref(false)
const isBlackscreenActive = ref(false)
const showPhotodiode = ref(false)

const preloadedMedia = ref(false)
const preloadTotal = ref(0)
const preloadLoaded = ref(0)

let activeTimer = null
let lastFrameTime = 0
let stimulusStartTime = 0
let manualTransitionStartTime = 0

let hasSentTransEnd = false
let hasSentTransStart = false
let hasMediaStarted = false

const triggerDefOptions = computed(() => {
  if (!selectedGroup.value) return []
  const group = triggerGroups.value.find(g => g.id === selectedGroup.value)
  let validIds = group && group.triggers && group.triggers.length > 0 
                 ? group.triggers 
                 : hotkeyMappings.value.filter(m => m.group === selectedGroup.value).map(m => m.definition)
  
  return triggerDefinitions.value
    .filter(td => validIds.includes(td.id))
    .map(td => ({ id: td.id, name: `${td.name} (${td.trigger_character})` }))
})

const activeHotkeys = computed(() => {
  if (!selectedGroup.value) return []
  const groupMappings = hotkeyMappings.value.filter(m => m.group === selectedGroup.value)
  const usedRoles = [roleStart.value, roleEnd.value, roleTransStart.value, roleTransEnd.value, rolePauseStart.value, rolePauseEnd.value].filter(Boolean)

  return groupMappings
    .filter(mapping => !usedRoles.includes(mapping.definition))
    .map(mapping => {
      const def = triggerDefinitions.value.find(d => d.id === mapping.definition)
      return { ...mapping, triggerName: def ? def.name : 'Unknown', triggerChar: def ? def.trigger_character : '?' }
    })
})

const getTriggerChar = (id) => {
  const tDef = triggerDefinitions.value.find(d => d.id === id)
  return tDef ? tDef.trigger_character : '0'
}

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

const playlistPreviewData = computed(() => {
  let cumulativeS = 0;
  let isManualEncountered = false;
  let totalPlaylistDuration = 0;
  const transS = (configAutoTransition.value && !configBlackscreen.value) ? (transitionTime.value || 0) : 0;

  const items = activePlaylistItems.value.map((item) => {
    const durS = item.duration || 0;
    const isUntimed = durS <= 0;
    
    let startStr, transEndStr, transStartStr, endStr;
    let hasOverlapWarning = false;
    let effectiveTransS = transS;

    if (isManualEncountered) {
      startStr = transEndStr = transStartStr = endStr = t('views.session_control.depends_on_click');
    } else {
      startStr = formatDuration(cumulativeS);
      
      effectiveTransS = isUntimed ? transS : Math.min(transS, durS / 2);
      if (effectiveTransS < transS && !isUntimed) hasOverlapWarning = true;
      
      transEndStr = effectiveTransS > 0 ? formatDuration(cumulativeS + effectiveTransS) : '-';
      
      if (isUntimed) {
        transStartStr = configBlackscreen.value ? "-" : `Klick + 0s`;
        endStr = configBlackscreen.value ? `Klick + 0s` : `Klick + ${effectiveTransS}s`;
        isManualEncountered = true;
      } else {
        transStartStr = effectiveTransS > 0 ? formatDuration(cumulativeS + durS - effectiveTransS) : '-';
        endStr = formatDuration(cumulativeS + durS);
        cumulativeS += durS;
      }
    }
    
    totalPlaylistDuration += durS;

    return { ...item, startStr, transEndStr, transStartStr, endStr, isUntimed, hasOverlapWarning, effectiveTransS };
  });

  return {
    items,
    totalExpected: isManualEncountered ? `${formatDuration(totalPlaylistDuration)}+ (${t('views.session_control.manual')})` : formatDuration(totalPlaylistDuration)
  };
});

const areTriggersAssigned = computed(() => {
  const requiresTrans = configAutoTransition.value && !configBlackscreen.value
  
  const baseAssigned = requiresTrans 
    ? (!!roleStart.value && !!roleEnd.value && !!roleTransStart.value && !!roleTransEnd.value)
    : (!!roleStart.value && !!roleEnd.value)

  return configPauseEnabled.value ? (baseAssigned && !!rolePauseStart.value && !!rolePauseEnd.value) : baseAssigned
})

const isReadyToStart = computed(() => { return selectedPlaylist.value && selectedGroup.value && areTriggersAssigned.value })

const engineStatus = computed(() => {
  if (isCompleted.value) return t('views.session_control.status_completed')
  if (!isRunning.value) return t('views.session_control.status_ready')
  if (isPaused.value) return t('views.session_control.status_paused')
  if (isBlackscreenActive.value) return t('views.session_control.status_hold')
  return t('views.session_control.status_running')
})

const statusBadgeClass = computed(() => {
  if (isCompleted.value) return 'badge-completed'
  if (!isRunning.value) return 'badge-ready'
  if (isPaused.value) return 'badge-paused'
  if (isBlackscreenActive.value) return 'badge-hold'
  return 'badge-running'
})

const loadDjangoData = async () => {
  try {
    const [resPlaylists, resGroups, resDefs, resHotkeys, resStimuli] = await Promise.all([
      api.get('playlists/'), api.get('triggers/groups/'), api.get('triggers/definitions/'),
      api.get('triggers/hotkeys/'), api.get('stimuli/')
    ])
    playlists.value = resPlaylists.data; triggerGroups.value = resGroups.data;
    triggerDefinitions.value = resDefs.data; hotkeyMappings.value = resHotkeys.data;
    allStimuli.value = resStimuli.data
  } catch (error) {}
}

const addLog = (msg, isWarning = false) => {
  const time = new Date().toLocaleTimeString()
  const sessionDur = formatDuration(sessionDuration.value)
  logs.value.unshift({ time, sessionDur, msg, isWarning })
  if (logs.value.length > 200) logs.value.pop()
}

const clearLog = () => { logs.value = [] }

const exportLog = () => {
  if (logs.value.length === 0) return
  const pName = playlists.value.find(p => p.id === selectedPlaylist.value)?.name || 'Unknown'
  const dateStr = new Date().toISOString().slice(0,10)
  
  let content = `EEG Session Export\nDate: ${dateStr}\nPlaylist: ${pName}\n\n[TIME | SESSION_DUR] - [EVENT]\n`
  content += "---------------------------------------------------\n"
  
  const chronologicalLogs = [...logs.value].reverse()
  chronologicalLogs.forEach(l => { content += `[${l.time} | ${l.sessionDur}] ${l.isWarning ? 'WARNING: ' : ''}${l.msg}\n` })

  const blob = new Blob([content], { type: "text/plain;charset=utf-8" })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a'); a.href = url; a.download = `EEG_Log_${dateStr}_${pName.replace(/\s+/g, '_')}.txt`; a.click(); URL.revokeObjectURL(url)
}

watch(selectedPlaylist, () => {
  preloadedMedia.value = false
  preloadTotal.value = 0
  preloadLoaded.value = 0
  if (selectedPlaylist.value) preloadMedia()
})

const preloadMedia = () => {
  const mediaItems = activePlaylistItems.value.filter(i => ['IMAGE', 'VIDEO', 'AUDIO'].includes(i.type) && i.file)
  preloadTotal.value = mediaItems.length
  preloadLoaded.value = 0
  preloadedMedia.value = false

  if (preloadTotal.value === 0) {
    preloadedMedia.value = true
    return
  }

  const checkDone = () => {
    preloadLoaded.value++
    if (preloadLoaded.value >= preloadTotal.value) { preloadedMedia.value = true }
  }

  mediaItems.forEach(item => {
    if (item.type === 'IMAGE') {
      const img = new Image(); img.onload = checkDone; img.onerror = checkDone; img.src = item.file
    } else {
      const media = document.createElement(item.type === 'VIDEO' ? 'video' : 'audio')
      media.oncanplaythrough = checkDone; media.onerror = checkDone; media.preload = 'auto'; media.src = item.file
    }
  })
}

const toggleFullscreen = () => {
  if (!document.fullscreenElement) {
    presentationContainer.value?.requestFullscreen().catch(err => addLog(`Fullscreen Error: ${err.message}`, true))
  } else { document.exitFullscreen() }
}
const handleFullscreenChange = () => { isFullscreen.value = !!document.fullscreenElement }

const startGlobalTimer = () => {
  clearInterval(timerInterval); timerInterval = setInterval(() => { sessionDuration.value++ }, 1000)
}

const sendFormattedTrigger = (code, descMsg) => {
  sendWSTrigger(code, descMsg)
  addLog(t('views.session_control.log_trigger_sent', { code, desc: descMsg }))
}

const triggerStimulusStart = (item) => {
  const startCode = getTriggerChar(roleStart.value)
  sendFormattedTrigger(startCode, `Start: ${item.name}`)

  if (configPhotodiode.value) {
    showPhotodiode.value = true; setTimeout(() => { showPhotodiode.value = false }, 100)
  }
  startPlaybackTimer(item)
}

const onMediaPlaying = () => {
  if (!hasMediaStarted) {
    hasMediaStarted = true
    triggerStimulusStart(currentItem.value)
  }
}

const startEngine = () => {
  isRunning.value = true; isPaused.value = false; isCompleted.value = false; isBlackscreenActive.value = false
  sessionDuration.value = 0; currentIndex.value = 0
  
  startGlobalTimer()
  addLog(t('views.session_control.log_started', { name: playlists.value.find(p => p.id === selectedPlaylist.value).name }))
  runCurrentStimulus()
}

const runCurrentStimulus = () => {
  if (currentIndex.value >= activePlaylistItems.value.length) { completeSession(); return }
  
  const item = currentItem.value
  hasSentTransEnd = false; hasSentTransStart = false; hasMediaStarted = false
  isManualTransitioning.value = false; isBlackscreenActive.value = false
  
  needsManualNext.value = (!item.duration || item.duration <= 0)

  if (item.type !== 'VIDEO' && item.type !== 'AUDIO') {
    triggerStimulusStart(item)
  }
}

const startPlaybackTimer = (item) => {
  const durMs = (item.duration || 0) * 1000
  const transMs = (configBlackscreen.value || !configAutoTransition.value) ? 0 : (transitionTime.value * 1000)
  const isUntimed = needsManualNext.value
  
  const effectiveTransMs = isUntimed ? transMs : Math.min(transMs, durMs / 2)

  lastFrameTime = performance.now()
  stimulusStartTime = lastFrameTime

  const tick = (now) => {
    if (!isRunning.value) return
    const delta = now - lastFrameTime

    if (delta > 50 && !isPaused.value) {
      addLog(t('views.session_control.log_frame_drop', { lag: Math.round(delta) }), true)
    }

    if (isPaused.value || isBlackscreenActive.value) {
      stimulusStartTime += delta
      if (isManualTransitioning.value) manualTransitionStartTime += delta
      lastFrameTime = now; activeTimer = requestAnimationFrame(tick); return
    }

    const elapsed = now - stimulusStartTime
    lastFrameTime = now

    if (!hasSentTransEnd && effectiveTransMs > 0 && elapsed >= effectiveTransMs) {
      const code = getTriggerChar(roleTransEnd.value)
      sendFormattedTrigger(code, `Trans End: ${item.name}`)
      hasSentTransEnd = true
    } 

    if (!isUntimed) {
      if (!configBlackscreen.value && !hasSentTransStart && elapsed >= (durMs - effectiveTransMs) && effectiveTransMs > 0 && currentIndex.value < activePlaylistItems.value.length - 1) {
        const code = getTriggerChar(roleTransStart.value)
        sendFormattedTrigger(code, `Trans Start Next`)
        hasSentTransStart = true
      }
      if (elapsed >= durMs) { onMediaEnded(); return }
    } else {
      if (isManualTransitioning.value && !configBlackscreen.value) {
        if ((now - manualTransitionStartTime) >= effectiveTransMs) { onMediaEnded(); return }
      }
    }

    activeTimer = requestAnimationFrame(tick)
  }
  activeTimer = requestAnimationFrame(tick)
}

const onManualNext = () => {
  if (isBlackscreenActive.value) {
    isBlackscreenActive.value = false; currentIndex.value++; runCurrentStimulus(); return
  }
  if (isManualTransitioning.value) return
  if (configBlackscreen.value || !configAutoTransition.value) { onMediaEnded(); return }

  const effectiveTransMs = transitionTime.value * 1000
  if (!hasSentTransEnd && effectiveTransMs > 0) {
    const code = getTriggerChar(roleTransEnd.value)
    sendFormattedTrigger(code, `Trans End (Forced)`)
    hasSentTransEnd = true
  }

  if (effectiveTransMs > 0 && currentIndex.value < activePlaylistItems.value.length - 1) {
    const code = getTriggerChar(roleTransStart.value)
    sendFormattedTrigger(code, `Trans Start Next (Manual)`)
    isManualTransitioning.value = true
    manualTransitionStartTime = performance.now()
  } else {
    onMediaEnded()
  }
}

const onMediaEnded = () => {
  if (activeTimer) cancelAnimationFrame(activeTimer)
  needsManualNext.value = false

  const item = currentItem.value
  const isLast = (currentIndex.value === activePlaylistItems.value.length - 1)
  const desc = isLast ? `End: ${item.name} (Playlist End)` : `End: ${item.name}`
  const endCode = getTriggerChar(roleEnd.value)

  sendFormattedTrigger(endCode, desc)

  if (configBlackscreen.value && !isLast) {
    isBlackscreenActive.value = true
  } else {
    currentIndex.value++
    runCurrentStimulus()
  }
}

const completeSession = () => {
  isRunning.value = false; isCompleted.value = true; clearInterval(timerInterval)
  addLog(t('views.session_control.session_completed'))
}

const resetSession = () => {
  isCompleted.value = false; currentIndex.value = 0; sessionDuration.value = 0; clearLog()
}

const togglePause = () => {
  if (isPaused.value) {
    if (configPauseEnabled.value) {
      const code = getTriggerChar(rolePauseEnd.value); sendFormattedTrigger(code, `Pause End`)
    }
    const media = document.querySelectorAll('.media-element, audio'); media.forEach(m => { if (m.play) m.play() })
    isPaused.value = false; lastFrameTime = performance.now(); startGlobalTimer()
    addLog(t('views.session_control.log_resumed'))
  } else {
    if (configPauseEnabled.value) {
      const code = getTriggerChar(rolePauseStart.value); sendFormattedTrigger(code, `Pause Start`)
    }
    const media = document.querySelectorAll('.media-element, audio'); media.forEach(m => { if (m.pause) m.pause() })
    isPaused.value = true; clearInterval(timerInterval)
    addLog(t('views.session_control.log_paused'))
  }
}

const stopEngine = () => {
  isRunning.value = false; isPaused.value = false; isCompleted.value = false; isBlackscreenActive.value = false
  needsManualNext.value = false; isManualTransitioning.value = false; clearInterval(timerInterval)
  if (activeTimer) cancelAnimationFrame(activeTimer)
  const media = document.querySelectorAll('.media-element, audio'); media.forEach(m => { if (m.pause) { m.pause(); m.currentTime = 0; } })
  if (document.fullscreenElement) document.exitFullscreen()
  addLog(t('views.session_control.log_stopped'))
}

const handleKeydown = (event) => {
  if (!hotkeysEnabled.value || !isRunning.value || isPaused.value || isManualTransitioning.value || isBlackscreenActive.value) return
  const hotkey = activeHotkeys.value.find(h => h.key_code.toLowerCase() === event.key.toLowerCase())
  if (hotkey) {
    event.preventDefault(); sendFormattedTrigger(hotkey.triggerChar, `Manual: ${hotkey.triggerName}`)
  }
}

onMounted(() => {
  loadDjangoData(); connectEngineWS(); window.addEventListener('keydown', handleKeydown)
  document.addEventListener('fullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown); document.removeEventListener('fullscreenchange', handleFullscreenChange)
  clearInterval(timerInterval); if (activeTimer) cancelAnimationFrame(activeTimer)
  if (isRunning.value) stopEngine()
})
</script>

<style scoped>
.preflight-card { background-color: #f8f9fa; border-left: 5px solid #3498db; }
.preflight-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px; }
.pf-item { display: flex; align-items: center; gap: 8px; font-size: 0.95rem; padding: 8px; border-radius: 4px; background: #fff; border: 1px solid #ddd; }
.pf-ok { color: #27ae60; border-color: #2ecc71; background: #eaeff2; }
.pf-err { color: #c0392b; border-color: #e74c3c; background: #fadbd8; }
.pf-icon { font-weight: bold; font-size: 1.1rem; }

.presentation-container {
  width: 100%; height: 450px; background: #000; display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; border-radius: 8px; box-shadow: inset 0 0 20px rgba(0,0,0,0.5);
}
.presentation-container:-webkit-full-screen { width: 100vw; height: 100vh; border-radius: 0; }
.presentation-container:fullscreen { width: 100vw; height: 100vh; border-radius: 0; }

.btn-fullscreen { position: absolute; top: 10px; right: 10px; z-index: 100; opacity: 0.5; transition: opacity 0.3s; }
.btn-fullscreen:hover { opacity: 1; }
.exit-fullscreen { opacity: 0.8; }

.media-wrapper, .blackscreen-wrapper, .audio-wrapper { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; position: relative; }
.media-element { max-width: 100%; max-height: 100%; object-fit: contain; }
.custom-text { color: #fff; font-size: 2.5rem; text-align: center; padding: 40px; }
.audio-placeholder { color: #fff; font-size: 1.5rem; font-style: italic; }

.photodiode-sync { position: absolute; bottom: 0; right: 0; width: 80px; height: 80px; background-color: #ffffff; z-index: 100; }

.complete-message { text-align: center; color: #2ecc71; }
.btn-next { position: absolute; bottom: 20px; right: 20px; font-size: 1.2rem; padding: 12px 25px; z-index: 10; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }

.badge-hold { background-color: #8e44ad; color: white; padding: 10px; border-radius: 4px; text-align: center; font-size: 1.2rem; }
.badge-completed { background-color: #2ecc71; color: white; padding: 10px; border-radius: 4px; text-align: center; font-size: 1.2rem; }
.badge-ready { background-color: #bdc3c7; color: white; padding: 10px; border-radius: 4px; text-align: center; font-size: 1.2rem; }
.badge-running { background-color: #e74c3c; color: white; padding: 10px; border-radius: 4px; text-align: center; font-size: 1.2rem; }
.badge-paused { background-color: #f1c40f; color: white; padding: 10px; border-radius: 4px; text-align: center; font-size: 1.2rem; }
</style>
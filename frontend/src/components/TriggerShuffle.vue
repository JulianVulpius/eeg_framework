<template>
  <div class="shuffle-container">
    <div class="shuffle-box">
      <div class="shuffle-header-wrapper">
        <div class="shuffle-header" style="display: flex; justify-content: space-between; align-items: center;">
          {{ $t('views.triggers.available') }}
          <button type="button" class="btn-secondary btn-small" @click="isPairModalOpen = true">
            {{ $t('views.triggers.add_pair') }}
          </button>
        </div>
        <input 
          type="text" 
          v-model="availableSearch" 
          :placeholder="$t('common.search')" 
          class="shuffle-search"
        />
      </div>
      <ul class="shuffle-list">
        <li v-for="t in filteredAvailableOptions" :key="t.id" @click="addTrigger(t.id)">
          <span>{{ t.name }}</span>
          <span class="add-btn">+</span>
        </li>
        <li v-if="filteredAvailableOptions.length === 0" class="shuffle-empty">-</li>
      </ul>
    </div>

    <div class="shuffle-box">
      <div class="shuffle-header-wrapper">
        <div class="shuffle-header">{{ $t('views.triggers.selected') }}</div>
        <input 
          type="text" 
          v-model="selectedSearch" 
          :placeholder="$t('common.search')" 
          class="shuffle-search"
        />
      </div>
      <ul class="shuffle-list">
        <li v-for="t in filteredSelectedOptions" :key="t.id" class="selected-item">
          <span>{{ t.name }}</span>
          <div style="display: flex; align-items: center; gap: 10px;">
            <input 
              type="text" 
              :value="hotkeyMap[t.id]" 
              @input="updateHotkey(t.id, $event.target.value)"
              placeholder="Key (e.g. x)" 
              maxlength="10"
              class="hotkey-input"
            />
            <span class="remove-btn" @click="removeTrigger(t.id)">×</span>
          </div>
        </li>
        <li v-if="filteredSelectedOptions.length === 0" class="shuffle-empty">-</li>
      </ul>
    </div>

    <BaseModal 
      :isOpen="isPairModalOpen" 
      :title="$t('views.triggers.add_pair')"
      @close="isPairModalOpen = false"
    >
      <input 
        type="text" 
        v-model="pairSearch" 
        :placeholder="$t('common.search')" 
        class="search-input" 
        style="width: 100%; margin-bottom: 15px; padding: 8px;" 
      />
      
      <ul class="shuffle-list pair-list">
        <li v-for="pair in filteredPairs" :key="pair.id" @click="addPair(pair)">
          <div>
            <strong>{{ pair.name }}</strong>
            <div style="font-size: 0.85rem; color: #666; margin-top: 4px;">
              {{ getTriggerName(pair.start_trigger) }} &rarr; {{ getTriggerName(pair.end_trigger) }}
            </div>
          </div>
          <span class="add-btn">+</span>
        </li>
        <li v-if="filteredPairs.length === 0" class="shuffle-empty">{{ $t('views.triggers.no_more_pairs') }}</li>
      </ul>
      
      <div class="modal-actions">
        <button type="button" class="btn-secondary" @click="isPairModalOpen = false">{{ $t('actions.cancel') }}</button>
      </div>
    </BaseModal>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import BaseModal from './BaseModal.vue'

const props = defineProps({
  allOptions: {
    type: Array,
    required: true
  },
  triggerPairs: {
    type: Array,
    default: () => []
  },
  selectedIds: {
    type: Array,
    default: () => []
  },
  hotkeyMap: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['update:selectedIds', 'update:hotkeyMap'])

const availableSearch = ref('')
const selectedSearch = ref('')
const pairSearch = ref('')
const isPairModalOpen = ref(false)

const filteredAvailableOptions = computed(() => {
  let options = props.allOptions.filter(opt => !props.selectedIds.includes(opt.id))
  if (availableSearch.value) {
    const query = availableSearch.value.toLowerCase()
    options = options.filter(opt => opt.name.toLowerCase().includes(query))
  }
  return options
})

const filteredSelectedOptions = computed(() => {
  let options = props.allOptions.filter(opt => props.selectedIds.includes(opt.id))
  if (selectedSearch.value) {
    const query = selectedSearch.value.toLowerCase()
    options = options.filter(opt => opt.name.toLowerCase().includes(query))
  }
  return options
})

const filteredPairs = computed(() => {
  let availablePairs = props.triggerPairs.filter(pair => {
    const isStartAssigned = props.selectedIds.includes(pair.start_trigger)
    const isEndAssigned = props.selectedIds.includes(pair.end_trigger)
    
    return !(isStartAssigned && isEndAssigned)
  })

  if (pairSearch.value) {
    const query = pairSearch.value.toLowerCase()
    availablePairs = availablePairs.filter(pair => pair.name.toLowerCase().includes(query))
  }

  return availablePairs
})

const getTriggerName = (id) => {
  const trigger = props.allOptions.find(opt => opt.id === id)
  return trigger ? trigger.name : `ID: ${id}`
}

const addTrigger = (id) => {
  const newSelected = [...props.selectedIds, id]
  const newHotkeys = { ...props.hotkeyMap, [id]: "" }
  emit('update:selectedIds', newSelected)
  emit('update:hotkeyMap', newHotkeys)
}

const addPair = (pair) => {
  let newSelected = [...props.selectedIds]
  let newHotkeys = { ...props.hotkeyMap }
  
  if (!newSelected.includes(pair.start_trigger)) {
    newSelected.push(pair.start_trigger)
    newHotkeys[pair.start_trigger] = ""
  }
  
  if (!newSelected.includes(pair.end_trigger)) {
    newSelected.push(pair.end_trigger)
    newHotkeys[pair.end_trigger] = ""
  }
  
  emit('update:selectedIds', newSelected)
  emit('update:hotkeyMap', newHotkeys)
  isPairModalOpen.value = false
}

const removeTrigger = (id) => {
  const newSelected = props.selectedIds.filter(t => t !== id)
  const newHotkeys = { ...props.hotkeyMap }
  delete newHotkeys[id]
  emit('update:selectedIds', newSelected)
  emit('update:hotkeyMap', newHotkeys)
}

const updateHotkey = (id, val) => {
  const newHotkeys = { ...props.hotkeyMap, [id]: val }
  emit('update:hotkeyMap', newHotkeys)
}
</script>

<style scoped>
.shuffle-container { display: flex; gap: 15px; }
.shuffle-box { flex: 1; border: 1px solid #ddd; border-radius: 4px; height: 300px; overflow-y: auto; background: #fdfdfd; }

.shuffle-header-wrapper {
  position: sticky;
  top: 0;
  background: #f4f7f6;
  border-bottom: 1px solid #ddd;
  z-index: 10;
  padding-bottom: 10px;
}

.shuffle-header { padding: 10px; font-weight: bold; }

.shuffle-search {
  width: calc(100% - 20px);
  margin: 0 10px;
  padding: 6px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 0.9rem;
  box-sizing: border-box;
}
.shuffle-search:focus { outline: none; border-color: #3498db; }

.shuffle-list { list-style: none; padding: 0; margin: 0; }
.shuffle-list li { padding: 10px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
.shuffle-list li:hover { background: #e9ecef; }
.shuffle-empty { text-align: center; color: #aaa; font-style: italic; cursor: default !important; }
.shuffle-empty:hover { background: none !important; }

.add-btn { color: #2ecc71; font-weight: bold; font-size: 1.2rem; }
.remove-btn { color: #e74c3c; font-weight: bold; font-size: 1.2rem; cursor: pointer; }
.hotkey-input { width: 80px !important; padding: 4px 8px !important; text-align: center; font-family: monospace;}
.selected-item { cursor: default !important; }
.selected-item:hover { background: transparent !important; }

.btn-small { padding: 4px 8px; font-size: 0.8rem; }
.pair-list { max-height: 250px; overflow-y: auto; border: 1px solid #ddd; border-radius: 4px; }
</style>
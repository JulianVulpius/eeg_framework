<template>
  <div class="shuffle-container">
    <div class="shuffle-box">
      <label>{{ leftTitle }}</label>
      <slot name="left-filters"></slot>
      <input 
        type="text" 
        v-model="searchLeft" 
        :placeholder="searchPlaceholder" 
        class="shuffle-search" 
      />
      <select multiple v-model="selectedLeft" class="shuffle-list">
        <option v-for="opt in leftOptions" :key="opt.id" :value="opt.id">
          {{ opt.name }}
        </option>
      </select>
    </div>

    <div class="shuffle-controls">
      <button type="button" class="btn-shuffle" @click="moveRight" :disabled="!selectedLeft.length">🡒</button>
      <button type="button" class="btn-shuffle" @click="moveLeft" :disabled="!selectedRight.length">🡐</button>
    </div>

    <div class="shuffle-box">
      <label>{{ rightTitle }}</label>
      <slot name="right-filters"></slot>
      <input 
        type="text" 
        v-model="searchRight" 
        :placeholder="searchPlaceholder" 
        class="shuffle-search full-width" 
      />
      
      <div class="list-with-controls">
        <select multiple v-model="selectedRight" class="shuffle-list">
          <option v-for="opt in rightOptions" :key="opt.id" :value="opt.id">
            {{ opt.name }}
          </option>
        </select>
        <div class="order-controls" v-if="enableOrdering">
          <button type="button" class="btn-order" @click="moveUp" :disabled="!selectedRight.length">↑</button>
          <button type="button" class="btn-order" @click="moveDown" :disabled="!selectedRight.length">↓</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    required: true
  },
  options: {
    type: Array,
    required: true
  },
  leftTitle: {
    type: String,
    required: true
  },
  rightTitle: {
    type: String,
    required: true
  },
  searchPlaceholder: {
    type: String,
    default: 'Search...'
  },
  enableOrdering: {
    type: Boolean,
    default: false
  },
  leftFilterFn: {
    type: Function,
    default: () => true
  }
})

const emit = defineEmits(['update:modelValue'])

const searchLeft = ref('')
const searchRight = ref('')
const selectedLeft = ref([])
const selectedRight = ref([])

const leftOptions = computed(() => {
  return props.options.filter(opt => {
    if (props.modelValue.includes(opt.id)) return false
    if (!props.leftFilterFn(opt)) return false
    if (searchLeft.value && !opt.name.toLowerCase().includes(searchLeft.value.toLowerCase())) return false
    return true
  })
})

const rightOptions = computed(() => {
  let items = props.modelValue.map(id => props.options.find(o => o.id === id)).filter(Boolean)
  return items.filter(opt => {
    if (searchRight.value && !opt.name.toLowerCase().includes(searchRight.value.toLowerCase())) return false
    return true
  })
})

const moveRight = () => {
  emit('update:modelValue', [...props.modelValue, ...selectedLeft.value])
  selectedLeft.value = []
}

const moveLeft = () => {
  emit('update:modelValue', props.modelValue.filter(id => !selectedRight.value.includes(id)))
  selectedRight.value = []
}

const moveUp = () => {
  const arr = [...props.modelValue]
  const selected = [...selectedRight.value].sort((a, b) => arr.indexOf(a) - arr.indexOf(b))
  selected.forEach(id => {
    const idx = arr.indexOf(id)
    if (idx > 0) {
      const temp = arr[idx - 1]
      arr[idx - 1] = id
      arr[idx] = temp
    }
  })
  emit('update:modelValue', arr)
}

const moveDown = () => {
  const arr = [...props.modelValue]
  const selected = [...selectedRight.value].sort((a, b) => arr.indexOf(b) - arr.indexOf(a))
  selected.forEach(id => {
    const idx = arr.indexOf(id)
    if (idx < arr.length - 1 && idx !== -1) {
      const temp = arr[idx + 1]
      arr[idx + 1] = id
      arr[idx] = temp
    }
  })
  emit('update:modelValue', arr)
}
</script>

<style scoped>
.shuffle-container { display: flex; justify-content: space-between; align-items: stretch; gap: 15px; margin-top: 10px; }
.shuffle-box { flex: 1; display: flex; flex-direction: column; gap: 10px; }
.shuffle-box label { font-size: 0.9rem; margin: 0; color: #7f8c8d; font-weight: 600;}
.shuffle-search { padding: 6px; border: 1px solid #ddd; border-radius: 4px; font-size: 0.85rem; width: 100%; box-sizing: border-box; }
.shuffle-list { height: 250px; width: 100%; padding: 5px; border: 1px solid #ddd; border-radius: 4px; font-family: inherit; }
.shuffle-controls { display: flex; flex-direction: column; justify-content: center; gap: 10px; }
.btn-shuffle { background: #ecf0f1; border: 1px solid #bdc3c7; border-radius: 4px; padding: 10px; cursor: pointer; font-weight: bold; transition: 0.2s; }
.btn-shuffle:hover:not(:disabled) { background: #bdc3c7; }
.btn-shuffle:disabled { opacity: 0.4; cursor: not-allowed; }
.list-with-controls { display: flex; gap: 10px; align-items: stretch; }
.order-controls { display: flex; flex-direction: column; justify-content: center; gap: 10px; }
.btn-order { background: #fdfefe; border: 1px solid #d0d3d4; color: #34495e; border-radius: 4px; padding: 8px; cursor: pointer; font-weight: bold; font-size: 1.1rem; transition: 0.2s; }
.btn-order:hover:not(:disabled) { background: #e5e8e8; }
.btn-order:disabled { opacity: 0.4; cursor: not-allowed; }
</style>
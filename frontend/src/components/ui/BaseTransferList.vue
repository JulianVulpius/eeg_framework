<template>
  <div class="shuffle-container">
    <div class="shuffle-box">
      <label>{{ leftTitle }}</label>
      <slot name="left-filters"></slot>
      <input type="text" v-model="searchLeft" :placeholder="searchPlaceholder" class="shuffle-search" />
      
      <div class="shuffle-list custom-list">
        <div 
          v-for="opt in leftOptions" 
          :key="opt.id" 
          class="custom-option"
          :class="{ selected: selectedLeft.includes(opt.id) }"
          @click="toggleSelect(opt.id, 'left')"
        >
          <slot name="list-item" :item="opt">
            {{ opt.name }}
          </slot>
        </div>
      </div>
    </div>

    <div class="shuffle-controls">
      <button type="button" class="btn-shuffle" @click="moveRight" :disabled="!selectedLeft.length" :title="$t('actions.move_selected')">🡒</button>
      <button type="button" class="btn-shuffle" @click="moveAllRight" :disabled="!leftOptions.length" :title="$t('actions.move_all')">🡒🡒</button>
      <button type="button" class="btn-shuffle" @click="moveLeft" :disabled="!selectedRight.length" :title="$t('actions.move_selected')">🡐</button>
      <button type="button" class="btn-shuffle" @click="moveAllLeft" :disabled="!rightOptions.length" :title="$t('actions.move_all')">🡐🡐</button>
    </div>

    <div class="shuffle-box">
      <label>{{ rightTitle }}</label>
      <slot name="right-filters"></slot>
      <input type="text" v-model="searchRight" :placeholder="searchPlaceholder" class="shuffle-search full-width" />
      <div class="list-with-controls">
        
        <div class="shuffle-list custom-list">
          <div 
            v-for="opt in rightOptions" 
            :key="opt.id" 
            class="custom-option"
            :class="{ selected: selectedRight.includes(opt.id) }"
            @click="toggleSelect(opt.id, 'right')"
          >
            <slot name="list-item" :item="opt">
              {{ opt.name }}
            </slot>
          </div>
        </div>

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
  modelValue: { type: Array, required: true },
  options: { type: Array, required: true },
  leftTitle: { type: String, required: true },
  rightTitle: { type: String, required: true },
  searchPlaceholder: { type: String, default: 'Search...' },
  enableOrdering: { type: Boolean, default: false },
  leftFilterFn: { type: Function, default: () => true },
  rightFilterFn: { type: Function, default: () => true }
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
    if (!props.rightFilterFn(opt)) return false
    if (searchRight.value && !opt.name.toLowerCase().includes(searchRight.value.toLowerCase())) return false
    return true
  })
})

const toggleSelect = (id, side) => {
  const targetArray = side === 'left' ? selectedLeft.value : selectedRight.value;
  const index = targetArray.indexOf(id);
  if (index > -1) {
    targetArray.splice(index, 1);
  } else {
    targetArray.push(id);
  }
}

const moveRight = () => {
  emit('update:modelValue', [...props.modelValue, ...selectedLeft.value])
  selectedLeft.value = []
}

const moveAllRight = () => {
  const allLeftIds = leftOptions.value.map(o => o.id)
  emit('update:modelValue', [...props.modelValue, ...allLeftIds])
  selectedLeft.value = []
}

const moveLeft = () => {
  emit('update:modelValue', props.modelValue.filter(id => !selectedRight.value.includes(id)))
  selectedRight.value = []
}

const moveAllLeft = () => {
  const allRightIds = rightOptions.value.map(o => o.id)
  emit('update:modelValue', props.modelValue.filter(id => !allRightIds.includes(id)))
  selectedRight.value = []
}

const moveUp = () => {
  const arr = [...props.modelValue]
  const selected = [...selectedRight.value].sort((a, b) => arr.indexOf(a) - arr.indexOf(b))
  selected.forEach(id => {
    const idx = arr.indexOf(id)
    if (idx > 0) { const temp = arr[idx - 1]; arr[idx - 1] = id; arr[idx] = temp }
  })
  emit('update:modelValue', arr)
}

const moveDown = () => {
  const arr = [...props.modelValue]
  const selected = [...selectedRight.value].sort((a, b) => arr.indexOf(b) - arr.indexOf(a))
  selected.forEach(id => {
    const idx = arr.indexOf(id)
    if (idx < arr.length - 1 && idx !== -1) { const temp = arr[idx + 1]; arr[idx + 1] = id; arr[idx] = temp }
  })
  emit('update:modelValue', arr)
}
</script>

<style scoped>
.custom-list {
  background: #fff;
  border: 1px solid #dcdde1;
  border-radius: 4px;
  overflow-y: auto;
  min-height: 200px;
  max-height: 300px;
}

.custom-option {
  padding: 8px 12px;
  cursor: pointer;
  user-select: none;
  border-bottom: 1px solid #f1f2f6;
  transition: background-color 0.1s;
}

.custom-option:last-child {
  border-bottom: none;
}

.custom-option:hover {
  background: #f8f9fa;
}

.custom-option.selected {
  background: #e8f4f8;
  color: #2c3e50;
  font-weight: 500;
}
</style>
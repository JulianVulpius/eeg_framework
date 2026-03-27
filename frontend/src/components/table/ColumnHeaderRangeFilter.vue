<template>
  <div class="column-header-range-filter">
    <div class="th-content" @click="toggleDropdown">
      <span>{{ title }}</span>
      <button class="icon-btn" :class="{ 'has-filter': hasFilter }" :title="$t('common.search')">
        🔻
      </button>
    </div>

    <div v-if="isExpanded" class="filter-dropdown" @click.stop>
      <div class="dropdown-header">
        <span class="filter-title">{{ filterTitle }}</span>
        <button class="clear-btn" v-if="hasFilter" @click="clearFilter">✕</button>
      </div>
      
      <div class="range-inputs">
        <input 
          type="number" 
          min="0" 
          step="0.1" 
          v-model="localMin" 
          @input="emitValue"
          @change="enforceRules"
          placeholder="Min" 
          class="form-control" 
        />
        <span class="separator">-</span>
        <input 
          type="number" 
          min="0" 
          step="0.1" 
          v-model="localMax" 
          @input="emitValue"
          @change="enforceRules"
          placeholder="Max" 
          class="form-control" 
        />
      </div>
    </div>

    <div v-if="isExpanded" class="click-outside-overlay" @click="closeDropdown"></div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  modelValue: { type: Object, default: () => ({ min: null, max: null }) },
  filterTitle: { type: String, default: 'Filter' }
})

const emit = defineEmits(['update:modelValue'])

const isExpanded = ref(false)

const localMin = ref(props.modelValue.min)
const localMax = ref(props.modelValue.max)

const hasFilter = computed(() => {
  return (props.modelValue.min !== null && props.modelValue.min !== '') || 
         (props.modelValue.max !== null && props.modelValue.max !== '')
})

watch(() => props.modelValue, (newVal) => {
  localMin.value = newVal.min
  localMax.value = newVal.max
}, { deep: true })

const toggleDropdown = () => {
  isExpanded.value = !isExpanded.value
}

const closeDropdown = () => {
  isExpanded.value = false
}

const clearFilter = () => {
  localMin.value = null
  localMax.value = null
  emitValue()
}

const emitValue = () => {
  emit('update:modelValue', {
    min: localMin.value === '' ? null : Number(localMin.value),
    max: localMax.value === '' ? null : Number(localMax.value)
  })
}

const enforceRules = () => {
  if (localMin.value !== null && localMin.value < 0) localMin.value = 0
  if (localMax.value !== null && localMax.value < 0) localMax.value = 0

  const minVal = Number(localMin.value)
  const maxVal = Number(localMax.value)

  if (localMin.value !== null && localMin.value !== '' && localMax.value !== null && localMax.value !== '') {
    if (maxVal < minVal) {
      localMax.value = minVal // auto-correct max to be at least min
    }
  }
  emitValue()
}
</script>

<style scoped>
.column-header-range-filter {
  position: relative;
  display: flex;
  flex-direction: column;
}

.th-content {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}

.icon-btn {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 0.9rem;
  opacity: 0.5;
  transition: opacity 0.2s;
  padding: 0 4px;
}

.icon-btn:hover, .icon-btn.has-filter {
  opacity: 1;
  color: #3498db;
}

.filter-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  z-index: 100;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 12px;
  box-shadow: 0 4px 15px rgba(0,0,0,0.1);
  width: 240px;
  margin-top: 8px;
  cursor: default;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.filter-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: #7f8c8d;
}

.clear-btn {
  background: none;
  border: none;
  color: #e74c3c;
  cursor: pointer;
  font-size: 0.85rem;
  padding: 2px 6px;
  font-weight: bold;
  border-radius: 4px;
}

.clear-btn:hover {
  background-color: #fdeaea;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}

.range-inputs input {
  width: 100%;
  padding: 6px;
  font-size: 0.9rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.range-inputs input:focus {
  outline: none;
  border-color: #3498db;
}

.separator {
  color: #7f8c8d;
  font-weight: bold;
}

.click-outside-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 99;
}
</style>
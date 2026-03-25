<template>
  <div class="column-header-filter">
    <div class="th-content" @click="toggleSearch">
      <span>{{ title }}</span>
      <button class="icon-btn" :class="{ 'has-filter': modelValue }" :title="placeholder">
        🔻
      </button>
    </div>
    
    <div v-show="isExpanded || modelValue" class="filter-wrapper">
      <select 
        ref="selectRef"
        :value="modelValue" 
        @change="$emit('update:modelValue', $event.target.value)"
        class="column-search-input"
        @click.stop
      >
        <option value="">{{ placeholder || '...' }}</option>
        <option v-for="opt in options" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>
      
      <button v-if="modelValue" class="clear-btn select-clear-btn" @click.stop="clearSearch">✕</button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick } from 'vue'

defineProps({
  title: { type: String, required: true },
  modelValue: { type: String, default: '' },
  options: { type: Array, required: true }, // expects array of { value, label }
  placeholder: { type: String, default: 'Search...' }
})

const emit = defineEmits(['update:modelValue'])

const isExpanded = ref(false)
const selectRef = ref(null)

const toggleSearch = async () => {
  isExpanded.value = !isExpanded.value
  if (isExpanded.value) {
    await nextTick()
    selectRef.value?.focus()
  }
}

const clearSearch = () => {
  emit('update:modelValue', '')
  isExpanded.value = false
}
</script>

<style scoped>
.column-header-filter {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
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

.filter-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.column-search-input {
  width: 100%;
  padding: 4px 24px 4px 8px; 
  font-size: 0.85rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-weight: normal; 
  background-color: white;
  appearance: auto; 
}

.column-search-input:focus {
  outline: none;
  border-color: #3498db;
}

.clear-btn {
  position: absolute;
  right: 4px;
  background: none;
  border: none;
  color: #999;
  cursor: pointer;
  font-size: 0.8rem;
  padding: 0 4px;
}

.select-clear-btn {
  right: 22px; 
}

.clear-btn:hover {
  color: #e74c3c;
}
</style>
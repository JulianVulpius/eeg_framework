<template>
  <div class="column-header-search-select-filter">
    <div class="th-content" @click="toggleDropdown">
      <span>{{ title }}</span>
      <button class="icon-btn" :class="{ 'has-filter': modelValue }" :title="$t('common.search')">
        🔻
      </button>
    </div>

    <div v-if="isExpanded" class="filter-dropdown" @click.stop>
      <div class="dropdown-header">
        <span class="filter-title">{{ filterTitle || $t('common.search') }}</span>
        <button class="clear-btn" v-if="modelValue" @click="clearFilter">✕</button>
      </div>
      
      <BaseSearchSelect 
        :modelValue="modelValue"
        @update:modelValue="onSelectUpdate"
        :options="options"
        :placeholder="placeholder || $t('common.search')"
        :nullLabel="$t('master_data.none')"
      />
    </div>

    <div v-if="isExpanded" class="click-outside-overlay" @click="closeDropdown"></div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import BaseSearchSelect from '../ui/BaseSearchSelect.vue'

defineProps({
  title: { type: String, required: true },
  modelValue: { type: [String, Number], default: null }, 
  options: { type: Array, required: true }, 
  placeholder: { type: String, default: '' },
  filterTitle: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])

const isExpanded = ref(false)

const toggleDropdown = () => {
  isExpanded.value = !isExpanded.value
}

const closeDropdown = () => {
  isExpanded.value = false
}

const clearFilter = () => {
  emit('update:modelValue', null)
}

const onSelectUpdate = (val) => {
  emit('update:modelValue', val)
  closeDropdown()
}
</script>

<style scoped>
.column-header-search-select-filter {
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
  width: 260px; /* Breit genug für die Sucheingabe */
  margin-top: 8px;
  cursor: default; 
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
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

.click-outside-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 99;
}
</style>
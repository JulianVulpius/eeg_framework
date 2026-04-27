<template>
  <div class="subject-info-filter">
    <div class="filter-select-wrapper">
      <BaseSearchSelect
        v-model="selectedDropdownValue"
        :options="availableCategoryOptions"
        :placeholder="$t('master_data.select_category')"
        @update:modelValue="handleCategorySelect"
      />
    </div>

    <div v-if="modelValue.length > 0" class="active-filters">
      <div v-for="catId in modelValue" :key="catId" class="filter-tag">
        <span>{{ getCategoryName(catId) }}</span>
        <button type="button" class="remove-btn" @click="removeCategory(catId)">✕</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'

const props = defineProps({
  categories: { type: Array, required: true },
  modelValue: { type: Array, required: true } 
})

const emit = defineEmits(['update:modelValue'])
const selectedDropdownValue = ref(null)

const availableCategoryOptions = computed(() => {
  return props.categories
    .filter(cat => !props.modelValue.includes(cat.id))
    .map(cat => ({ value: cat.id, label: cat.name }))
})

const getCategoryName = (id) => {
  const cat = props.categories.find(c => c.id === id)
  return cat ? cat.name : ''
}

const handleCategorySelect = (newValue) => {
  if (newValue) {
    emit('update:modelValue', [...props.modelValue, newValue])
    selectedDropdownValue.value = null
  }
}

const removeCategory = (idToRemove) => {
  emit('update:modelValue', props.modelValue.filter(id => id !== idToRemove))
}
</script>

<style scoped>
.subject-info-filter {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.filter-select-wrapper {
  max-width: 300px;
}
.active-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.filter-tag {
  background-color: #dcf8c6;
  color: #075e54;
  padding: 4px 10px;
  border-radius: 16px;
  font-size: 0.85rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 6px;
  border: 1px solid #c4e8ab;
}
.remove-btn {
  background: none;
  border: none;
  color: #075e54;
  cursor: pointer;
  font-size: 0.9rem;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}
.remove-btn:hover {
  opacity: 0.7;
}
</style>
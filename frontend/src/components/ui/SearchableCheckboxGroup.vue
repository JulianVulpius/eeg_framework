<template>
  <div class="searchable-checkbox-group">
    <input 
      type="text" 
      v-model="searchQuery" 
      :placeholder="searchPlaceholder || $t('common.search')" 
      class="form-control search-input" 
    />
    <div class="checkbox-list">
      <div v-for="opt in filteredOptions" :key="opt.id" class="checkbox-item">
        <label>
          <input 
            type="checkbox" 
            :value="opt.id" 
            :checked="modelValue.includes(opt.id)"
            @change="toggleSelection(opt.id)"
          />
          {{ opt.name }}
        </label>
      </div>
      <div v-if="filteredOptions.length === 0" class="no-results">
        {{ $t('common.no_data') }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: { type: Array, required: true },
  options: { type: Array, required: true },
  searchPlaceholder: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])
const searchQuery = ref('')

const filteredOptions = computed(() => {
  if (!searchQuery.value) return props.options
  const q = searchQuery.value.toLowerCase()
  return props.options.filter(opt => opt.name.toLowerCase().includes(q))
})

const toggleSelection = (id) => {
  const current = [...props.modelValue]
  const index = current.indexOf(id)
  if (index === -1) {
    current.push(id)
  } else {
    current.splice(index, 1)
  }
  emit('update:modelValue', current)
}
</script>

<style scoped>
.searchable-checkbox-group { border: 1px solid #ddd; border-radius: 4px; display: flex; flex-direction: column; }
.search-input { border: none; border-bottom: 1px solid #ddd; border-radius: 4px 4px 0 0; width: 100%; box-sizing: border-box; }
.search-input:focus { box-shadow: none; border-bottom: 1px solid #3498db; }
.checkbox-list { max-height: 200px; overflow-y: auto; padding: 10px; background: #fafafa; }
.checkbox-item { margin-bottom: 5px; }
.checkbox-item label { font-weight: 400; cursor: pointer; display: flex; align-items: center; gap: 8px; margin: 0; color: #2c3e50; }
.no-results { color: #7f8c8d; font-size: 0.9rem; text-align: center; padding: 10px 0; }
</style>
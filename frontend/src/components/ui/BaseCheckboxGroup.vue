<template>
  <div class="checkbox-group-wrapper">
    <div v-if="searchable" class="checkbox-search">
      <input 
        type="text" 
        v-model="searchQuery" 
        :placeholder="searchPlaceholder || $t('common.search')" 
        class="form-control"
      />
    </div>

    <div class="checkbox-grid-container">
      <label v-for="option in filteredOptions" :key="option.id" class="checkbox-item">
        <span class="item-name">{{ option.name }}</span>
        <input 
          type="checkbox" 
          :value="option.id"
          :checked="modelValue.includes(option.id)"
          @change="onChange($event, option.id)"
        />
      </label>
      
      <div v-if="filteredOptions.length === 0" class="no-results">
        {{ $t('common.no_data') }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  options: {
    type: Array,
    required: true
  },
  searchable: {
    type: Boolean,
    default: false
  },
  searchPlaceholder: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const searchQuery = ref('')

const filteredOptions = computed(() => {
  if (!searchQuery.value) return props.options
  const q = searchQuery.value.toLowerCase()
  return props.options.filter(opt => opt.name.toLowerCase().includes(q))
})

const onChange = (event, id) => {
  const isChecked = event.target.checked
  let newValue = [...props.modelValue]
  
  if (isChecked) {
    newValue.push(id)
  } else {
    newValue = newValue.filter(val => val !== id)
  }
  
  emit('update:modelValue', newValue)
}
</script>

<style scoped>
.checkbox-group-wrapper {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.checkbox-search input {
  width: 100%;
  padding: 6px 10px;
  font-size: 0.85rem;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.checkbox-search input:focus {
  outline: none;
  border-color: #3498db;
}

.checkbox-grid-container {
  display: grid;
  grid-template-columns: 1fr 1fr; 
  gap: 0.5rem 1rem;
  max-height: 200px; 
  overflow-y: auto;
  border: 1px solid var(--color-border, #ccc);
  padding: 10px;
  border-radius: 4px;
  background-color: var(--color-background-soft, #f9f9f9);
}

.checkbox-item {
  display: grid;
  grid-template-columns: 1fr 25px; 
  align-items: center; 
  gap: 10px; 
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.checkbox-item:hover {
  background-color: var(--color-background-mute, #e5e5e5);
}

.item-name {
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.checkbox-item input[type="checkbox"] {
  justify-self: end;
  margin: 0;
  cursor: pointer;
  width: 16px;
  height: 16px;
}

.no-results {
  grid-column: 1 / -1;
  text-align: center;
  color: #999;
  font-size: 0.85rem;
  padding: 10px 0;
  font-style: italic;
}
</style>
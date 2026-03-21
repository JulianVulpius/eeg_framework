<template>
  <div class="checkbox-grid-container">
    <label v-for="option in options" :key="option.id" class="checkbox-item">
      <span class="item-name">{{ option.name }}</span>
      <input 
        type="checkbox" 
        :value="option.id"
        :checked="modelValue.includes(option.id)"
        @change="onChange($event, option.id)"
      />
    </label>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  },
  options: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

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
.checkbox-grid-container {
  display: grid;
  grid-template-columns: 1fr 1fr; /* 2 equal columns */
  gap: 0.5rem 1rem;
  max-height: 200px; /* Scrolling */
  overflow-y: auto;
  border: 1px solid var(--color-border, #ccc);
  padding: 10px;
  border-radius: 4px;
  background-color: var(--color-background-soft, #f9f9f9);
}

.checkbox-item {
  display: grid;
  /* Columns: Text takes all space (1fr), Checkbox has fixed width (25px) */
  grid-template-columns: 1fr 25px; 
  align-items: center; /* Vertically center */
  gap: 10px; /* Space between text and checkbox area */
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
  /* Truncate text if it's too long for the column */
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Ensure checkbox is right-aligned in its 25px grid cell */
.checkbox-item input[type="checkbox"] {
  justify-self: end;
  margin: 0;
  cursor: pointer;
  width: 16px;
  height: 16px;
}
</style>
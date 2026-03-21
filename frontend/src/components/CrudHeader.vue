<template>
  <div class="page-header">
    <h1>{{ title }}</h1>
    <div class="header-actions">
      <label class="toggle-label">
        <input 
          type="checkbox" 
          :checked="modelValue" 
          @change="$emit('update:modelValue', $event.target.checked)" 
        /> 
        {{ $t('common.show_id') }}
      </label>
      <button class="btn-primary" @click="$emit('add')">
        {{ addText || $t('actions.add_new') }}
      </button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  // this acts as v-model for the 'show id' toggle
  modelValue: {
    type: Boolean,
    default: false
  },
  addText: {
    type: String,
    default: ''
  }
})

defineEmits(['update:modelValue', 'add'])
</script>
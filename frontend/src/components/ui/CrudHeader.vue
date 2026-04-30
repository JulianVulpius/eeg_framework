<template>
  <div class="crud-header" style="display: flex; align-items: center; width: 100%; margin-bottom: 20px;">
    <!-- Titel links verankert -->
    <h2 class="page-title" style="margin: 0;">{{ title }}</h2>
    
    <!-- Aktions-Container nach rechts geschoben durch margin-left: auto -->
    <div class="header-actions" style="margin-left: auto; display: flex; align-items: center; gap: 20px;">
      
      <!-- Slot für zusätzliche Toggles (z.B. Archiviert) -->
      <slot></slot>

      <!-- Standard Show ID Toggle -->
      <label class="header-toggle-wrapper">
        <input 
          type="checkbox" 
          :checked="modelValue" 
          @change="$emit('update:modelValue', $event.target.checked)" 
        />
        {{ $t('common.show_id') }}
      </label>

      <!-- Haupt-Aktionsbutton (Add) -->
      <button class="btn-primary" @click="$emit('add')" style="margin-left: 10px;">
        <i class="fas fa-plus"></i> {{ $t('actions.add_new') }}
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
  // acts as v-model for the 'show id' toggle
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
<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content" :class="customClass">
      
      <div class="modal-header">
        <h2>{{ title }}</h2>
        <button class="modal-close-x" @click="$emit('close')" title="Schließen">✕</button>
      </div>
      
      <div v-if="errorMessage" class="error-box">
        <strong>Backend Error:</strong> {{ errorMessage }}
      </div>
      
      <div class="modal-body">
        <slot></slot>
      </div>

      <div v-if="$slots.actions" class="modal-actions">
        <slot name="actions"></slot>
      </div>

    </div>
  </div>
</template>

<script setup>
defineProps({
  isOpen: Boolean,
  title: String,
  errorMessage: { type: String, default: '' },
  customClass: { type: String, default: '' }
})
defineEmits(['close'])
</script>
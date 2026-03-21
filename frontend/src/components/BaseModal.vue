<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content" :class="customClass">
      <h2>{{ title }}</h2>
      
      <div v-if="errorMessage" class="error-box">
        <strong>Backend Error:</strong> {{ errorMessage }}
      </div>
      
      <slot></slot>
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
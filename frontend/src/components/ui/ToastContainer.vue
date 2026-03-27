<template>
  <div class="toast-container">
    <div 
      v-for="toast in toasts" 
      :key="toast.id" 
      class="toast"
      :class="toast.type"
    >
      <span v-if="toast.type === 'success'">✅</span>
      <span v-if="toast.type === 'error'">🗑️</span>
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { useToast } from '@/composables/useToast'

const { toasts } = useToast()
</script>
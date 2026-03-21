<template>
  <p v-if="message" class="inline-error-message" role="alert">
    <span>⚠️</span> {{ message }}
  </p>
</template>

<script setup>
defineProps({
  message: {
    type: String,
    default: ''
  }
})
</script>
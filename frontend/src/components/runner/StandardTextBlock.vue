<template>
  <div class="text-block-card">
    <div class="content" v-html="sanitizedContent"></div>
    
    </div>
</template>

<script setup>
import { computed } from 'vue'
import DOMPurify from 'dompurify'

const props = defineProps({
  parameters: { type: Object, default: () => ({}) }
})

const sanitizedContent = computed(() => {
  const rawText = props.parameters.text || props.parameters.content || '...'
  return DOMPurify.sanitize(rawText)
})

// necessary dummy
const submit = async () => {
  return true
}

defineExpose({ submit })
</script>

<style scoped>
.text-block-card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.content { font-size: 1.1rem; line-height: 1.6; color: #2c3e50; } 
</style>
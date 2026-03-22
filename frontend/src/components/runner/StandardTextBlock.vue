<template>
  <div class="text-block-card">
    <div class="content" v-html="parameters.text || parameters.content || '...'"></div>
    <div class="action-footer">
      <button class="btn-secondary" @click="$emit('go-back')" style="margin-right: 15px;">{{ $t('actions.back') }}</button>
      <button class="btn-primary" @click="$emit('completed')">{{ $t('actions.continue') }}</button>
    </div>
  </div>
</template>

<script setup>
defineProps({
  parameters: { type: Object, default: () => ({}) }
})
defineEmits(['completed'])
</script>

<style scoped>
.text-block-card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.content { font-size: 1.1rem; line-height: 1.6; margin-bottom: 30px; color: #2c3e50; }
.action-footer { display: flex; justify-content: flex-end; }
</style>
<template>
  <BaseModal 
    :isOpen="isOpen" 
    :title="$t('modal.confirm_delete_title')" 
    @close="$emit('cancel')"
  >
    <div class="danger-content">
      <div class="danger-icon-wrapper">🗑️</div>
      <p class="danger-message">{{ $t('modal.confirm_delete_desc') }}</p>
    </div>
    
    <div class="modal-actions">
      <button class="btn-secondary" @click="$emit('cancel')">
        {{ $t('actions.cancel') }}
      </button>
      <button class="btn-danger" @click="$emit('confirm')">
        {{ $t('modal.yes_delete') }}
      </button>
    </div>
  </BaseModal>
</template>

<script setup>
import BaseModal from './BaseModal.vue'

defineProps({ isOpen: Boolean })
defineEmits(['cancel', 'confirm'])
</script>

<style scoped>
.danger-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background-color: #fdeaea;
  border-radius: 8px;
  border-left: 4px solid var(--danger-color);
  margin-bottom: 1.5rem;
}

.danger-icon-wrapper {
  font-size: 2rem;
  line-height: 1;
}

.danger-message {
  font-size: 1.05rem;
  color: var(--text-main);
  line-height: 1.5;
  margin: 0;
  flex: 1;
}
</style>
<template>
  <BaseModal 
    :isOpen="isOpen" 
    :title="title || $t('common.warning')" 
    @close="handleClose"
  >
    <div class="warning-content">
      <div class="warning-icon-wrapper">⚠️</div>
      <p class="warning-message">{{ message }}</p>
    </div>
    
    <div class="modal-actions right-actions">
      <button 
        v-if="!hideCancel" 
        type="button" 
        class="btn-secondary" 
        @click="handleClose"
      >
        {{ cancelText || $t('actions.cancel') }}
      </button>
      <button 
        type="button" 
        class="btn-primary warning-btn" 
        @click="handleConfirm"
      >
        {{ confirmText || 'OK' }}
      </button>
    </div>
  </BaseModal>
</template>

<script setup>
import BaseModal from './BaseModal.vue'

defineProps({
  isOpen: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    default: ''
  },
  message: {
    type: String,
    required: true
  },
  cancelText: {
    type: String,
    default: ''
  },
  confirmText: {
    type: String,
    default: ''
  },
  // hide the cancel button by default to use it as a simple error alert
  hideCancel: {
    type: Boolean,
    default: true 
  }
})

const emit = defineEmits(['cancel', 'confirm', 'close'])

const handleClose = () => {
  emit('cancel')
  emit('close')
}

const handleConfirm = () => {
  emit('confirm')
  emit('close')
}
</script>

<style scoped>
/* highlighted box for the warning text */
.warning-content {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem;
  background-color: #fdf5e6;
  border-radius: 8px;
  border-left: 4px solid #f39c12;
  margin-bottom: 1.5rem;
}

.warning-icon-wrapper {
  font-size: 2rem;
  line-height: 1;
}

.warning-message {
  font-size: 1.05rem;
  color: #2c3e50;
  line-height: 1.5;
  margin: 0;
  flex: 1;
}

.right-actions {
  justify-content: flex-end;
}

.warning-btn {
  background-color: #f39c12; 
  border-color: #e67e22;
  color: white;
}

.warning-btn:hover {
  background-color: #d68910;
}
</style>
<template>
  <BaseModal :isOpen="isOpen" :title="$t('views.stimulus.delete_warning_title')" @close="$emit('cancel')">
    <div style="padding: 10px 0;">
      <p style="margin-bottom: 15px; font-size: 0.95rem; color: #2c3e50;">
        {{ $t('views.stimulus.delete_warning_desc') }}
      </p>
      
      <ul style="background: #fdf5f5; border-left: 4px solid #e74c3c; padding: 10px 10px 10px 30px; margin-bottom: 20px; border-radius: 4px;">
        <li v-for="playlist in affectedPlaylists" :key="playlist.id" style="font-weight: bold; color: #c0392b; margin-bottom: 5px;">
          {{ playlist.name }}
        </li>
      </ul>
      
      <p style="font-weight: bold; font-size: 0.95rem;">
        {{ $t('views.stimulus.delete_warning_confirm') }}
      </p>
    </div>
    
    <div class="modal-actions">
      <button type="button" class="btn-secondary" @click="$emit('cancel')">{{ $t('actions.cancel') }}</button>
      <button type="button" class="btn-primary" style="background-color: #e74c3c; border-color: #c0392b;" @click="$emit('confirm')">
        {{ $t('modal.yes_delete') }}
      </button>
    </div>
  </BaseModal>
</template>

<script setup>
import BaseModal from '@/components/ui/BaseModal.vue'

defineProps({
  isOpen: Boolean,
  affectedPlaylists: {
    type: Array,
    default: () => []
  }
})

defineEmits(['cancel', 'confirm'])
</script>
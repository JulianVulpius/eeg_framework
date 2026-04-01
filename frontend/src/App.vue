<template>
  <ToastContainer />
  
  <WarningModal 
    :isOpen="isWarningOpen" 
    :title="$t(warningTitle || 'common.warning')" 
    :message="warningMessage" 
    @close="closeWarning" 
  />
  
  <ConfirmDeleteModal 
    :isOpen="isConfirmOpen" 
    @confirm="confirm" 
    @cancel="cancelConfirm" 
  />

  <router-view />
</template>

<script setup>
import ToastContainer from '@/components/ui/ToastContainer.vue'
import WarningModal from '@/components/ui/WarningModal.vue'
import ConfirmDeleteModal from '@/components/ui/ConfirmDeleteModal.vue'
import { useGlobalModal } from '@/composables/useGlobalModal'

const { 
  isWarningOpen, warningTitle, warningMessage, closeWarning,
  isConfirmOpen, confirm, cancelConfirm 
} = useGlobalModal()
</script>
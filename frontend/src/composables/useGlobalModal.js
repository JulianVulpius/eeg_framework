import { ref } from 'vue'

const isWarningOpen = ref(false)
const warningTitle = ref('')
const warningMessage = ref('')

const isConfirmOpen = ref(false)
let confirmActionCallback = null

export function useGlobalModal() {
  const showWarning = (message, title = 'common.warning') => {
    warningTitle.value = title
    warningMessage.value = message
    isWarningOpen.value = true
  }

  const closeWarning = () => {
    isWarningOpen.value = false
  }

  const requireConfirmation = (actionCallback) => {
    confirmActionCallback = actionCallback
    isConfirmOpen.value = true
  }

  const confirm = async () => {
    if (confirmActionCallback) {
      await confirmActionCallback()
    }
    isConfirmOpen.value = false
    confirmActionCallback = null
  }

  const cancelConfirm = () => {
    isConfirmOpen.value = false
    confirmActionCallback = null
  }

  return {
    isWarningOpen, warningTitle, warningMessage, showWarning, closeWarning,
    isConfirmOpen, requireConfirmation, confirm, cancelConfirm
  }
}
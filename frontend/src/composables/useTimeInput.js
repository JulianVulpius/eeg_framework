import { ref } from 'vue'

export function useTimeInput() {
  const timeError = ref('')

  const initializeTime = (timeRef, defaultTime = '00:00') => {
    if (!timeRef.value) {
      timeRef.value = defaultTime
      timeError.value = ''
    }
  }

  const validateTime = (timeValue, errorMessage = 'Enter valid time') => {
    timeError.value = ''
    
    if (!timeValue) {
      timeError.value = errorMessage
      return false
    }

    const timeRegex = /^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$/
    if (!timeRegex.test(timeValue)) {
      timeError.value = errorMessage
      return false
    }

    return true
  }

  const clearTimeError = () => {
    timeError.value = ''
  }

  const parseApiTime = (apiDateString) => {
    if (!apiDateString) return ''
    
    const date = new Date(apiDateString)
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    
    return `${hours}:${minutes}`
  }

  const buildApiPayload = (dateString, timeString) => {
    if (!dateString || !timeString) return null

    const localDateTime = new Date(`${dateString}T${timeString}:00`)
    
    return localDateTime.toISOString()
  }

  return {
    timeError,
    initializeTime,
    validateTime,
    clearTimeError,
    parseApiTime,
    buildApiPayload
  }
}
import { ref, computed } from 'vue'

export function useCrud() {
  const showIdColumn = ref(false)
  const searchQuery = ref('')
  const isDialogOpen = ref(false)
  const isEditing = ref(false)
  const editingId = ref(null)
  const isConfirmOpen = ref(false)
  const itemToDelete = ref(null)
  const errorMessage = ref('') 
  const fieldErrors = ref({}) 

  // clear all errors
  const clearErrors = () => {
    errorMessage.value = ''
    fieldErrors.value = {}
  }

  // open add dialog
  const openAddDialog = (resetFormCallback) => {
    clearErrors() 
    isEditing.value = false
    editingId.value = null
    if (resetFormCallback) resetFormCallback()
    isDialogOpen.value = true
  }

  // open edit dialog
  const openEditDialog = (id, populateFormCallback) => {
    clearErrors() 
    isEditing.value = true
    editingId.value = id
    if (populateFormCallback) populateFormCallback()
    isDialogOpen.value = true
  }

  // close dialog
  const closeDialog = () => { 
    isDialogOpen.value = false 
  }

  // request delete confirm
  const requestDelete = (id) => {
    itemToDelete.value = id
    isConfirmOpen.value = true
  }

  // cancel delete
  const cancelDelete = () => {
    isConfirmOpen.value = false
    itemToDelete.value = null
  }

  // generic search filter
  const createSearchFilter = (itemsRef, searchFields) => {
    return computed(() => {
      if (!searchQuery.value) return itemsRef.value
      const query = searchQuery.value.toLowerCase()
      return itemsRef.value.filter(item => {
        return searchFields.some(field => {
          const val = item[field]
          return val && String(val).toLowerCase().includes(query)
        })
      })
    })
  }

  // parse string errors from api response
  const parseApiError = (error, t, fallbackKey) => {
    if (error.response?.data) {
      const data = error.response.data
      if (data.detail) return data.detail
    }
    return t ? t(fallbackKey) : fallbackKey
  }

  // smartly map backend validation errors to form fields or global error
  const handleFormError = (error, t, fallbackKey = 'errors.save_failed') => {
    if (error.response?.data) {
      const serverData = error.response.data
      
      // check if we got field-specific errors (drf format)
      if (typeof serverData === 'object' && !serverData.detail) {
        for (const field in serverData) {
          // get the first string message
          const msg = Array.isArray(serverData[field]) ? serverData[field][0] : serverData[field]
          
          // map common database unique errors to our translations
          if (msg && msg.toLowerCase().includes('unique')) {
            fieldErrors.value[field] = t('errors.duplicate_entry')
          } else {
            fieldErrors.value[field] = msg
          }
        }
        return // exit if we mapped field errors
      }
    }
    // fallback to global error message inside the modal
    errorMessage.value = parseApiError(error, t, fallbackKey)
  }

  return {
    showIdColumn, searchQuery, isDialogOpen, isEditing, editingId,
    isConfirmOpen, itemToDelete, errorMessage, fieldErrors,
    openAddDialog, openEditDialog, closeDialog, requestDelete, cancelDelete,
    clearErrors, createSearchFilter, parseApiError, handleFormError
  }
}
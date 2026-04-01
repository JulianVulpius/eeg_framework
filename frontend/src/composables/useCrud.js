import { ref, computed } from 'vue'

export function useCrud() {
  const showIdColumn = ref(false)
  const searchQuery = ref('')
  const isDialogOpen = ref(false)
  const isEditing = ref(false)
  const editingId = ref(null)
  const fieldErrors = ref({}) 

  const clearErrors = () => {
    fieldErrors.value = {}
  }

  const openAddDialog = (resetFormCallback) => {
    clearErrors() 
    isEditing.value = false
    editingId.value = null
    if (resetFormCallback) resetFormCallback()
    isDialogOpen.value = true
  }

  const openEditDialog = (id, populateFormCallback) => {
    clearErrors() 
    isEditing.value = true
    editingId.value = id
    if (populateFormCallback) populateFormCallback()
    isDialogOpen.value = true
  }

  const closeDialog = () => { 
    isDialogOpen.value = false 
  }

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

  const handleFormError = (error, t) => {
    if (error.response?.data) {
      const serverData = error.response.data
      if (typeof serverData === 'object' && !serverData.detail) {
        for (const field in serverData) {
          const msg = Array.isArray(serverData[field]) ? serverData[field][0] : serverData[field]
          if (msg && msg.toLowerCase().includes('unique')) {
            fieldErrors.value[field] = t('errors.duplicate_entry')
          } else {
            fieldErrors.value[field] = msg
          }
        }
      }
    }
  }

  return {
    showIdColumn, searchQuery, isDialogOpen, isEditing, editingId, fieldErrors,
    openAddDialog, openEditDialog, closeDialog, clearErrors, createSearchFilter, handleFormError
  }
}
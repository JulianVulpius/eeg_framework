import { ref } from 'vue'

const activeMockUser = ref('admin')

export function useMockAuth() {
  const mockUsers = [
    { id: 'admin', name: 'Admin (All Rights)', roles: ['admin'] },
    { id: 'assistant_a', name: 'Assistant A', roles: ['assistant'] },
    { id: 'photographer', name: 'Photographer', roles: ['photographer'] }
  ]

  const setMockUser = (userId) => {
    activeMockUser.value = userId
  }

  const hasPermission = (permission) => {
    if (activeMockUser.value === 'admin') return true
    if (activeMockUser.value === 'photographer' && permission === 'upload_images') return true
    if (activeMockUser.value === 'assistant_a' && ['view_subjects', 'add_subjects'].includes(permission)) return true
    return false
  }

  return { 
    activeMockUser, 
    mockUsers, 
    setMockUser, 
    hasPermission 
  }
}
import axios from 'axios'
import { useToast } from '@/composables/useToast'
import { useGlobalModal } from '@/composables/useGlobalModal'
import i18n from '@/i18n'

const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  }
})

api.interceptors.response.use(
  (response) => {
    const method = response.config.method.toLowerCase()
    const { showToast } = useToast()
    const t = i18n.global.t

    if (method === 'post') {
      showToast(t('toast.created') || 'Erfolgreich erstellt', 'success')
    } else if (['put', 'patch'].includes(method)) {
      showToast(t('toast.updated') || 'Erfolgreich aktualisiert', 'success')
    } else if (method === 'delete') {
      showToast(t('toast.deleted') || 'Erfolgreich gelöscht', 'error')
    }

    return response
  },
  (error) => {
    const { showWarning } = useGlobalModal()
    const t = i18n.global.t

    if (error.response && error.response.status === 400) {
      return Promise.reject(error)
    }

    let errorMsg = t('errors.save_failed') || 'Ein Fehler ist aufgetreten.'
    if (error.response?.data) {
      errorMsg = error.response.data.detail || error.response.data.message || errorMsg
    }

    showWarning(errorMsg, t('common.error') || 'Fehler')
    
    return Promise.reject(error)
  }
)

export default api
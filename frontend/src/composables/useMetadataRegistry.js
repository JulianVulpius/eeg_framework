import { ref } from 'vue'
import api from '@/services/api'
import { useGlobalModal } from '@/composables/useGlobalModal'
import { useI18n } from 'vue-i18n'

export function useMetadataRegistry() {
  const { showWarning } = useGlobalModal()
  const { t } = useI18n()
  
  const isLoading = ref(false)
  const error = ref(null)

  const loadAttachedMetadata = async (contentTypeId, objectId) => {
    isLoading.value = true
    try {
      const response = await api.get('metadata-instances/', {
        params: { content_type: contentTypeId, object_id: objectId }
      })
      return response.data
    } catch (err) {
      showWarning(t('common.error'), t('errors.load_failed'))
      return []
    } finally {
      isLoading.value = false
    }
  }

  const getAvailableGroupsForTable = async (contentTypeId) => {
    try {
      const response = await api.get('metadata/groups/available-for-table/', {
        params: { content_type: contentTypeId }
      })
      return response.data
    } catch (err) {
      showWarning(t('common.error'), t('errors.load_failed'))
      return []
    }
  }

  const saveManualMetadataDraft = async (contentTypeId, objectId, groupId, valuesArray) => {
    try {
      const payload = {
        content_type: contentTypeId,
        object_id: objectId,
        group: groupId,
        values: valuesArray
      }
      const response = await api.post('metadata-instances/save-manual-instance/', payload)
      return response.data
    } catch (err) {
      showWarning(t('common.error'), t('errors.save_failed'))
      return null
    }
  }

  const updateManualMetadata = async (instanceId, valuesArray) => {
    try {
      await api.put(`metadata-instances/${instanceId}/update-manual-instance/`, { values: valuesArray })
      return true
    } catch (err) {
      showWarning(t('common.error'), t('errors.save_failed'))
      return false
    }
  }

  const deleteManualInstance = async (instanceId) => {
    try {
      await api.delete(`metadata-instances/${instanceId}/`)
      return true
    } catch (err) {
      showWarning(t('common.error'), t('errors.delete_failed'))
      return false
    }
  }

  const checkLegacyStatus = (attachedInstances, availableGroups) => {
    const allowedGroupIds = availableGroups.map(g => g.id)
    return attachedInstances.map(instance => {
      if (instance.creation_source === 'COMPONENT') {
        return { ...instance, isLegacy: false, isReadOnly: true }
      }
      const isStillAllowed = allowedGroupIds.includes(instance.group)
      return { ...instance, isLegacy: !isStillAllowed, isReadOnly: false }
    })
  }

const bulkCheckMetadata = async (contentTypeId, objectIdsArray) => {
    if (!objectIdsArray || objectIdsArray.length === 0) return {}
    try {
      const response = await api.post('metadata-instances/bulk-check/', 
        {
          content_type: contentTypeId,
          object_ids: objectIdsArray
        }, 
        {
          hideToast: true 
        }
      )
      return response.data
    } catch (err) {
      return {}
    }
  }

  return {
    isLoading,
    error,
    loadAttachedMetadata,
    getAvailableGroupsForTable,
    saveManualMetadataDraft,
    updateManualMetadata,
    deleteManualInstance,
    checkLegacyStatus,
    bulkCheckMetadata
  }
}
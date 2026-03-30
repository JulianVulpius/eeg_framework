<template>
  <div class="event-detail-view">
    <div class="header-area">
      <div style="width: 100%;">
        <BaseBreadcrumb :items="breadcrumbItems" />
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 5px;">
          <h2>{{ $t('views.events.detail_title') }}: {{ eventData.name }}</h2>
        </div>
      </div>
    </div>

    <div class="tabs">
      <button :class="['tab-btn', { active: activeTab === 'general' }]" @click="activeTab = 'general'">
        {{ $t('views.events.tab_general') }}
      </button>
      <button :class="['tab-btn', { active: activeTab === 'page_groups' }]" @click="activeTab = 'page_groups'">
        {{ $t('nav.page_groups') }}
      </button>
      
      <button :class="['tab-btn', { active: activeTab === 'phases' }]" @click="activeTab = 'phases'">
        {{ $t('views.events.tab_phases') }}
      </button>

      <button :class="['tab-btn', { active: activeTab === 'groups' }]" @click="activeTab = 'groups'">
        {{ $t('views.events.tab_groups') }}
      </button>
      <button :class="['tab-btn', { active: activeTab === 'roles' }]" @click="activeTab = 'roles'" v-if="hasPermission('admin')">
        {{ $t('views.events.tab_roles') }}
      </button>
      <button :class="['tab-btn', { active: activeTab === 'staff' }]" @click="activeTab = 'staff'">
        {{ $t('views.events.tab_staff') }}
      </button>
      <button :class="['tab-btn', { active: activeTab === 'subjects' }]" @click="activeTab = 'subjects'">
        {{ $t('views.events.tab_subjects') }}
      </button>
    </div>

    <div class="tab-content">

      <div v-if="activeTab === 'general'" class="panel">
        <div class="panel-header">
          <h3>{{ $t('views.events.tab_general') }}</h3>
          <button @click="saveGeneral" class="btn-primary" v-if="hasPermission('admin')">
            {{ $t('actions.save') }}
          </button>
        </div>

        <div class="form-group" style="max-width: 600px; margin-bottom: 20px;">
          <label>{{ $t('common.name') }} *</label>
          <input v-model="eventData.name" type="text" class="form-control" />
        </div>

        <div class="form-row" style="display: flex; gap: 1rem; max-width: 600px; margin-bottom: 20px;">
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('views.events.start') }}</label>
            <div style="display: flex; gap: 10px;">
              <input type="date" v-model="eventData.event_start_date" class="form-control" />
              <input 
                type="time" 
                v-model="eventData.event_start_time" 
                class="form-control" 
                style="max-width: 130px;" 
                :class="{ 'input-invalid': timeErrors.start_time || fieldErrors.start_time }"
                @focus="initializeTimeField(eventData, 'event_start_time')"
                @blur="validateTimeField(eventData.event_start_time, 'start_time', $t('errors.invalid_time', 'Enter valid time'))"
              />
            </div>
            <BaseInputError :message="timeErrors.start_time || fieldErrors.start_time" />
          </div>
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('views.events.end') }}</label>
            <div style="display: flex; gap: 10px;">
              <input type="date" v-model="eventData.event_end_date" class="form-control" />
              <input 
                type="time" 
                v-model="eventData.event_end_time" 
                class="form-control" 
                style="max-width: 130px;" 
                :class="{ 'input-invalid': timeErrors.end_time || fieldErrors.end_time }"
                @focus="initializeTimeField(eventData, 'event_end_time')"
                @blur="validateTimeField(eventData.event_end_time, 'end_time', $t('errors.invalid_time', 'Enter valid time'))"
              />
            </div>
            <BaseInputError :message="timeErrors.end_time || fieldErrors.end_time" />
          </div>
        </div>

        <div class="form-group" style="max-width: 600px; margin-bottom: 20px;">
          <label>{{ $t('common.description') }}</label>
          <textarea v-model="eventData.description" class="form-control" rows="4"></textarea>
        </div>
      </div>

      <div v-if="activeTab === 'page_groups'" class="panel">
        <div class="panel-header">
          <h3>{{ $t('nav.page_groups') }}</h3>
          <button @click="savePageGroups" class="btn-primary" v-if="hasPermission('admin')">{{ $t('actions.save') }}</button>
        </div>
        <BaseTransferList
          v-model="assignedPageGroups"
          :options="availablePageGroups"
          :leftTitle="$t('views.events.available_groups')"
          :rightTitle="$t('views.events.selected_groups')"
          :enableOrdering="true"
          :disabled="!hasPermission('admin')"
          :leftFilterFn="filterAvailableLogic"
          :rightFilterFn="filterSelectedLogic"
        >
          <template #left-filters>
            <BaseSearchSelect v-model="filterAvailablePG" :options="pageGroupCategories" :placeholder="$t('views.metadata.search_category')" />
          </template>
          <template #right-filters>
            <BaseSearchSelect v-model="filterSelectedPG" :options="pageGroupCategories" :placeholder="$t('views.metadata.search_category')" />
          </template>
        </BaseTransferList>
      </div>

      <div v-if="activeTab === 'phases'" class="panel">
        <div class="panel-header">
          <h3>{{ $t('views.events.assigned_phases') }}</h3>
        </div>
        <p style="margin-bottom: 20px; color: #555;">
          {{ $t('views.events.phases_description') }}
        </p>
        
        <EventGroupPhaseAssignment 
          :eventGroups="eventGroups"
          :pageGroups="resolvedAssignedPageGroups"
          @update-assignment="saveEventGroupPhase"
        />
      </div>

      <div v-if="activeTab === 'groups'" class="panel">
        <div class="panel-header">
          <h3>{{ $t('views.events.tab_groups') }}</h3>
          <button @click="openModal('group')" class="btn-primary" v-if="hasPermission('admin')">{{ $t('actions.add_new') }}</button>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>{{ $t('views.events.group_name') }}</th>
              <th>{{ $t('views.events.assigned_phase') }}</th>
              <th>{{ $t('actions.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="grp in eventGroups" :key="grp.id">
              <td>{{ grp.name }}</td>
              <td>
                <div v-if="grp.page_groups && grp.page_groups.length > 0" style="display: flex; gap: 5px; flex-wrap: wrap;">
                  <span v-for="pgId in grp.page_groups" :key="pgId" class="badge category-badge">
                    {{ getEntityName(availablePageGroups, pgId) }}
                  </span>
                </div>
                <span v-else class="text-muted">{{ $t('views.events.no_phases_assigned') }}</span>
              </td>
              <td>
                <TableActionButtons @edit="openModal('group', grp)" @delete="deleteEntity('event-management/groups', grp.id, loadGroups)" v-if="hasPermission('admin')" />
              </td>
            </tr>
            <tr v-if="!eventGroups.length"><td colspan="3" class="text-center">{{ $t('common.no_data') }}</td></tr>
          </tbody>
        </table>
      </div>

      <div v-if="activeTab === 'roles'" class="panel">
        <div class="panel-header">
          <h3>{{ $t('views.events.tab_roles') }}</h3>
          <button @click="openModal('role')" class="btn-primary">{{ $t('actions.add_new') }}</button>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>{{ $t('common.name') }}</th>
              <th>{{ $t('views.events.permissions') }}</th>
              <th>{{ $t('actions.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="role in eventRoles" :key="role.id">
              <td>{{ role.name }}</td>
              <td>{{ role.permissions ? role.permissions.join(', ') : '-' }}</td>
              <td>
                <TableActionButtons @edit="openModal('role', role)" @delete="deleteEntity('event-management/roles', role.id, loadRoles)" />
              </td>
            </tr>
            <tr v-if="!eventRoles.length"><td colspan="3" class="text-center">{{ $t('common.no_data') }}</td></tr>
          </tbody>
        </table>
      </div>

      <div v-if="activeTab === 'staff'" class="panel">
        <div class="panel-header">
          <h3>{{ $t('views.events.tab_staff') }}</h3>
          <button @click="openModal('staff')" class="btn-primary" v-if="hasPermission('admin')">{{ $t('views.events.assign_staff') }}</button>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>{{ $t('views.events.user') }}</th>
              <th>{{ $t('views.events.role') }}</th>
              <th>{{ $t('views.events.target_group') }}</th>
              <th>{{ $t('actions.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="staff in staffAssignments" :key="staff.id">
              <td>{{ getMockUserName(staff.user) }}</td>
              <td>{{ getEntityName(eventRoles, staff.role) }}</td>
              <td>{{ getEntityName(eventGroups, staff.target_group) || $t('views.events.global_all_groups') }}</td>
              <td>
                <TableActionButtons @edit="openModal('staff', staff)" @delete="deleteEntity('event-management/staff-assignments', staff.id, loadStaff)" v-if="hasPermission('admin')" />
              </td>
            </tr>
            <tr v-if="!staffAssignments.length"><td colspan="4" class="text-center">{{ $t('common.no_data') }}</td></tr>
          </tbody>
        </table>
      </div>

      <div v-if="activeTab === 'subjects'" class="panel">
        <div class="panel-header">
          <h3>{{ $t('views.events.tab_subjects') }}</h3>
          <button @click="openModal('subject')" class="btn-primary" v-if="hasPermission('add_subjects') || hasPermission('admin')"> {{ $t('views.events.assign_subject') }}</button>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>{{ $t('views.events.subject') }} ID</th>
              <th>{{ $t('views.events.target_group') }}</th>
              <th>{{ $t('actions.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sub in subjectAssignments" :key="sub.id">
              <td>{{ getEntityName(realSubjects, sub.subject, 'identifier') || getEntityName(realSubjects, sub.subject, 'subject_id') }}</td>
              <td>{{ getEntityName(eventGroups, sub.group) || $t('views.events.no_group') }}</td>
              <td>
                <TableActionButtons @edit="openModal('subject', sub)" @delete="deleteEntity('event-management/subject-assignments', sub.id, loadSubjects)" v-if="hasPermission('admin') || hasPermission('add_subjects')" />
              </td>
            </tr>
            <tr v-if="!subjectAssignments.length"><td colspan="3" class="text-center">{{ $t('common.no_data') }}</td></tr>
          </tbody>
        </table>
      </div>
    </div>

    <BaseModal :isOpen="modals.group" :title="editingId ? $t('actions.edit') : $t('actions.add_new')" @close="closeModal('group')">
      <div class="form-group">
        <label>{{ $t('views.events.group_name') }} *</label>
        <input v-model="forms.group.name" type="text" class="form-control" />
      </div>
      <div class="form-group">
        <label>{{ $t('common.description') }}</label>
        <textarea v-model="forms.group.description" class="form-control"></textarea>
      </div>
      <div class="modal-actions">
        <button @click="closeModal('group')" class="btn-secondary">{{ $t('actions.cancel') }}</button>
        <button @click="saveEntity('event-management/groups', forms.group, loadGroups, 'group')" class="btn-primary">{{ $t('actions.save') }}</button>
      </div>
    </BaseModal>

    <BaseModal :isOpen="modals.subject" :title="editingId ? $t('actions.edit') : $t('views.events.assign_subject')" @close="closeModal('subject')">
      <div class="form-group">
        <label>{{ $t('views.events.subject') }} *</label>
        
        <SubjectSearchSelect
          v-model="forms.subject.subject"
          :subjects="realSubjects"
          :assignedIds="assignedSubjectIds"
          :placeholder="$t('views.events.search_subject')"
        />

      </div>
      <div class="form-group">
        <label>{{ $t('views.events.target_group') }}</label>
        <select v-model="forms.subject.group" class="form-control">
          <option :value="null">{{ $t('views.events.no_group') }}</option>
          <option v-for="g in eventGroups" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
      </div>
      <div class="modal-actions">
        <button @click="closeModal('subject')" class="btn-secondary">{{ $t('actions.cancel') }}</button>
        <button @click="saveEntity('event-management/subject-assignments', forms.subject, loadSubjects, 'subject')" class="btn-primary">{{ $t('actions.save') }}</button>
      </div>
    </BaseModal>

    <ConfirmDeleteModal 
      :isOpen="deleteModal.isOpen" 
      @cancel="cancelDelete" 
      @confirm="executeDelete" 
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useMockAuth } from '@/composables/useMockAuth'
import { useCrud } from '@/composables/useCrud'
import { useTimeInput } from '@/composables/useTimeInput'

import BaseBreadcrumb from '@/components/ui/BaseBreadcrumb.vue'
import BaseTransferList from '@/components/ui/BaseTransferList.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'
import TableActionButtons from '@/components/table/TableActionButtons.vue'
import EventGroupPhaseAssignment from '@/components/domain/EventGroupPhaseAssignment.vue'
import BaseInputError from '@/components/ui/BaseInputError.vue'
import ConfirmDeleteModal from '@/components/ui/ConfirmDeleteModal.vue'
import SubjectSearchSelect from '@/components/domain/SubjectSearchSelect.vue'

const route = useRoute()
const { t } = useI18n()
const { hasPermission, mockUsers } = useMockAuth()
const crudHelper = useCrud() 
const { initializeTime, validateTime, parseApiTime, buildApiPayload } = useTimeInput()

const eventId = route.params.id
const activeTab = ref('general')
const eventData = ref({})

const availablePageGroups = ref([])
const assignedPageGroups = ref([])
const eventGroups = ref([])
const eventRoles = ref([])
const staffAssignments = ref([])
const subjectAssignments = ref([])
const realSubjects = ref([])

const pageGroupCategories = ref([])
const filterAvailablePG = ref(null)
const filterSelectedPG = ref(null)

const assignedSubjectIds = computed(() => {
  return subjectAssignments.value.map(assignment => assignment.subject)
})

const filterAvailableLogic = (opt) => !filterAvailablePG.value || opt.category === filterAvailablePG.value
const filterSelectedLogic = (opt) => !filterSelectedPG.value || opt.category === filterSelectedPG.value

const breadcrumbItems = computed(() => [
  { label: t('nav.events'), route: '/events' },
  { label: eventData.value.name || t('common.loading') }
])

const resolvedAssignedPageGroups = computed(() => {
  const assignedIds = assignedPageGroups.value.map(val => typeof val === 'object' ? val.id : val)
  return availablePageGroups.value.filter(pg => assignedIds.includes(pg.id))
})

const modals = reactive({ group: false, role: false, staff: false, subject: false })
const editingId = ref(null)

const defaultForms = {
  group: { event: eventId, name: '', description: '', page_groups: [] },
  role: { event: eventId, name: '', permissions: [] },
  staff: { user: null, role: null, event_group: null },
  subject: { event: eventId, subject: null, group: null }
}
const forms = reactive(JSON.parse(JSON.stringify(defaultForms)))

const fieldErrors = reactive({
  start_time: '',
  end_time: ''
})

const timeErrors = reactive({
  start_time: '',
  end_time: ''
})

const initializeTimeField = (dataObj, key) => {
  const tempRef = ref(dataObj[key])
  initializeTime(tempRef, '00:00')
  dataObj[key] = tempRef.value
}

const validateTimeField = (val, key, errorMsg) => {
  timeErrors[key] = ''
  if (!val) return true 
  
  const isValid = validateTime(val, errorMsg)
  if (!isValid) {
    timeErrors[key] = errorMsg
  }
  return isValid
}

const deleteModal = reactive({
  isOpen: false,
  endpoint: '',
  id: null,
  reloadFn: null
})

const getEntityName = (list, id, key = 'name') => {
  if (!id) return null
  const item = list.find(i => i.id === id)
  return item ? item[key] : id
}

const getMockUserName = (id) => {
  const u = mockUsers.find(x => x.id === id)
  return u ? u.name : id
}

const extractDatePart = (isoString) => {
  if (!isoString) return ''
  const d = new Date(isoString)
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0')
}

const loadEventBaseData = async () => {
  try {
    const res = await api.get(`events/${eventId}/`)
    eventData.value = res.data
    
    eventData.value.event_start_date = extractDatePart(res.data.event_start)
    eventData.value.event_start_time = parseApiTime(res.data.event_start) 
    eventData.value.event_end_date = extractDatePart(res.data.event_end)
    eventData.value.event_end_time = parseApiTime(res.data.event_end)

    assignedPageGroups.value = res.data.page_groups || []
  } catch (err) { console.error(err) }
}

const loadPageGroupsAndCategories = async () => {
  try {
    const [pgRes, catRes] = await Promise.all([
      api.get('page-groups/'),
      api.get('category/page-group-categories/')
    ])
    availablePageGroups.value = pgRes.data
    pageGroupCategories.value = catRes.data
  } catch (err) { console.error(err) }
}

const loadGroups = async () => {
  try {
    const res = await api.get(`event-management/groups/?event=${eventId}`)
    eventGroups.value = res.data
  } catch (err) { console.error(err) }
}

const loadRoles = async () => {
  try {
    const res = await api.get(`event-management/roles/?event=${eventId}`)
    eventRoles.value = res.data
  } catch (err) { console.error(err) }
}

const loadStaff = async () => {
  try {
    const res = await api.get(`event-management/staff-assignments/?event=${eventId}`)
    staffAssignments.value = res.data
  } catch (err) { console.error(err) }
}

const loadSubjects = async () => {
  try {
    const [subRes, assignmentRes] = await Promise.all([
      api.get('subjects/'),
      api.get(`event-management/subject-assignments/?event=${eventId}`)
    ])
    
    realSubjects.value = subRes.data 
    
    subjectAssignments.value = assignmentRes.data
  } catch (err) { console.error(err) }
}

const saveGeneral = async () => {
  fieldErrors.start_time = ''
  fieldErrors.end_time = ''
  let hasError = false

  if (eventData.value.event_start_time && !eventData.value.event_start_date) {
    fieldErrors.start_time = t('errors.time_without_date')
    hasError = true
  }
  if (eventData.value.event_end_time && !eventData.value.event_end_date) {
    fieldErrors.end_time = t('errors.time_without_date')
    hasError = true
  }

  if (eventData.value.event_start_time && !validateTimeField(eventData.value.event_start_time, 'start_time', t('errors.invalid_time', 'Enter valid time'))) {
    hasError = true
  }
  if (eventData.value.event_end_time && !validateTimeField(eventData.value.event_end_time, 'end_time', t('errors.invalid_time', 'Enter valid time'))) {
    hasError = true
  }

  if (hasError) return

  try {
    const payload = { ...eventData.value }

    if (payload.event_start_date) {
      const time = payload.event_start_time || '00:00'
      payload.event_start = buildApiPayload(payload.event_start_date, time)
    } else {
      payload.event_start = null
    }

    if (payload.event_end_date) {
      const time = payload.event_end_time || '00:00'
      payload.event_end = buildApiPayload(payload.event_end_date, time)
    } else {
      payload.event_end = null
    }

    delete payload.event_start_date
    delete payload.event_start_time
    delete payload.event_end_date
    delete payload.event_end_time

    await api.put(`events/${eventId}/`, payload)
    crudHelper.notifySuccess('updated', t)
  } catch (error) { 
    crudHelper.parseApiError(error, t, 'errors.save_failed') 
  }
}

const savePageGroups = async () => {
  try {
    const payload = { ...eventData.value, page_groups: assignedPageGroups.value }
    delete payload.event_start_date
    delete payload.event_start_time
    delete payload.event_end_date
    delete payload.event_end_time

    await api.put(`events/${eventId}/`, payload)
    crudHelper.notifySuccess('updated', t)
  } catch (error) { 
    crudHelper.parseApiError(error, t, 'errors.save_failed') 
  }
}

const saveEventGroupPhase = async (updatedGroup) => {
  try {
    await api.put(`event-management/groups/${updatedGroup.id}/`, updatedGroup)
    crudHelper.notifySuccess('updated', t)
    loadGroups() 
  } catch (err) {
    crudHelper.parseApiError(err, t, 'errors.save_failed')
  }
}

const openModal = (type, item = null) => {
  editingId.value = item ? item.id : null
  if (item) {
    forms[type] = { ...item }
    if (type === 'role' && !forms[type].permissions) forms[type].permissions = []
  } else {
    forms[type] = JSON.parse(JSON.stringify(defaultForms[type]))
  }
  modals[type] = true
}

const closeModal = (type) => {
  modals[type] = false
  editingId.value = null
}

const saveEntity = async (endpoint, payload, reloadFn, modalType) => {
  try {
    if (editingId.value) {
      await api.put(`${endpoint}/${editingId.value}/`, payload)
    } else {
      await api.post(`${endpoint}/`, payload)
    }
    crudHelper.notifySuccess(editingId.value ? 'updated' : 'created', t)
    closeModal(modalType)
    reloadFn()
  } catch (error) {
    alert(crudHelper.parseApiError(error, t, 'errors.save_failed'))
  }
}

const deleteEntity = (endpoint, id, reloadFn) => {
  deleteModal.endpoint = endpoint
  deleteModal.id = id
  deleteModal.reloadFn = reloadFn
  deleteModal.isOpen = true
}

const cancelDelete = () => {
  deleteModal.isOpen = false
}

const executeDelete = async () => {
  try {
    await api.delete(`${deleteModal.endpoint}/${deleteModal.id}/`)
    crudHelper.notifySuccess('deleted', t)
    if (deleteModal.reloadFn) deleteModal.reloadFn() 
  } catch (error) {
    alert(crudHelper.parseApiError(error, t, 'errors.delete_failed'))
  } finally {
    deleteModal.isOpen = false 
  }
}

onMounted(() => {
  loadEventBaseData()
  loadPageGroupsAndCategories()
  loadGroups()
  loadRoles()
  loadStaff()
  loadSubjects()
})
</script>

<style scoped>
.event-detail-view { display: flex; flex-direction: column; gap: 20px; }
.header-area { background: white; padding: 15px 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.header-area h2 { margin: 0; color: #2c3e50; }
.tabs { display: flex; gap: 10px; border-bottom: 2px solid #e0e0e0; padding-bottom: 0; }
.tab-btn { background: transparent; border: none; border-bottom: 3px solid transparent; padding: 10px 20px; font-size: 1rem; font-weight: 600; color: #7f8c8d; cursor: pointer; transition: all 0.2s; }
.tab-btn:hover { color: #3498db; }
.tab-btn.active { color: #3498db; border-bottom: 3px solid #3498db; }
.panel { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); min-height: 400px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
.panel-header h3 { margin: 0; color: #2c3e50; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 25px; padding-top: 15px; border-top: 1px solid #eee; }
</style>
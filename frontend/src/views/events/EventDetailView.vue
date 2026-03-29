<template>
  <div class="event-detail-view">
    <div class="header-area">
      <div style="width: 100%;">
        <BaseBreadcrumb :items="breadcrumbItems" />
        <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 5px;">
          <h2>{{ $t('views.events.detail_title') }}: {{ eventData.name || '...' }}</h2>
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
        Phasen
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
          <button @click="saveGeneral" class="btn-primary" v-if="hasPermission('admin')">{{ $t('actions.save') }}</button>
        </div>
        <div class="form-group" style="max-width: 600px; margin-bottom: 20px;">
          <label>{{ $t('common.name') }} *</label>
          <input v-model="eventData.name" type="text" class="form-control" />
        </div>
        <div class="form-group" style="max-width: 600px;">
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
            <BaseSearchSelect v-model="filterAvailablePG" :options="pageGroupCategories" placeholder="Kategorie filtern..." />
          </template>
          <template #right-filters>
            <BaseSearchSelect v-model="filterSelectedPG" :options="pageGroupCategories" placeholder="Kategorie filtern..." />
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
          <button @click="openModal('group')" class="btn-primary" v-if="hasPermission('admin')">+ {{ $t('actions.add_new') }}</button>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th>{{ $t('views.events.group_name') }}</th>
              <th>Zugewiesene Phase</th>
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
          <button @click="openModal('role')" class="btn-primary">+ {{ $t('actions.add_new') }}</button>
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
          <button @click="openModal('staff')" class="btn-primary" v-if="hasPermission('admin')">+ Personal zuweisen</button>
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
              <td>{{ getEntityName(eventGroups, staff.target_group) || 'Global (Alle Gruppen)' }}</td>
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
          <button @click="openModal('subject')" class="btn-primary" v-if="hasPermission('add_subjects') || hasPermission('admin')">+ Proband zuweisen</button>
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
              <td>{{ getEntityName(eventGroups, sub.group) || 'Keine Gruppe' }}</td>
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

    <BaseModal :isOpen="modals.role" :title="editingId ? $t('actions.edit') : $t('actions.add_new')" @close="closeModal('role')">
      <div class="form-group">
        <label>{{ $t('common.name') }} *</label>
        <input v-model="forms.role.name" type="text" class="form-control" />
      </div>
      <div class="form-group" style="margin-top: 15px;">
        <label>{{ $t('views.events.permissions') }} (JSON Array Flags)</label>
        <BaseCheckboxGroup
          v-model="forms.role.permissions"
          :options="permissionOptions"
        />
      </div>
      <div class="modal-actions">
        <button @click="closeModal('role')" class="btn-secondary">{{ $t('actions.cancel') }}</button>
        <button @click="saveEntity('event-management/roles', forms.role, loadRoles, 'role')" class="btn-primary">{{ $t('actions.save') }}</button>
      </div>
    </BaseModal>

    <BaseModal :isOpen="modals.staff" :title="editingId ? $t('actions.edit') : 'Personal zuweisen'" @close="closeModal('staff')">
      <div class="form-group">
        <label>{{ $t('views.events.user') }} *</label>
        <select v-model="forms.staff.user" class="form-control">
          <option v-for="u in mockUsers" :key="u.id" :value="u.id">{{ u.name }}</option>
        </select>
      </div>
      <div class="form-group">
        <label>{{ $t('views.events.role') }} *</label>
        <select v-model="forms.staff.role" class="form-control">
          <option v-for="r in eventRoles" :key="r.id" :value="r.id">{{ r.name }}</option>
        </select>
      </div>
      <div class="form-group">
        <label>{{ $t('views.events.target_group') }}</label>
        <select v-model="forms.staff.target_group" class="form-control">
          <option :value="null">Global (Alle Gruppen)</option>
          <option v-for="g in eventGroups" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
      </div>
      <div class="modal-actions">
        <button @click="closeModal('staff')" class="btn-secondary">{{ $t('actions.cancel') }}</button>
        <button @click="saveEntity('event-management/staff-assignments', forms.staff, loadStaff, 'staff')" class="btn-primary">{{ $t('actions.save') }}</button>
      </div>
    </BaseModal>

    <BaseModal :isOpen="modals.subject" :title="editingId ? $t('actions.edit') : 'Proband zuweisen'" @close="closeModal('subject')">
      <div class="form-group">
        <label>{{ $t('views.events.subject') }} *</label>
        <BaseSearchSelect
          v-model="forms.subject.subject"
          :options="realSubjects"
          labelKey="identifier"
          valueKey="id"
          placeholder="Proband suchen..."
        />
      </div>
      <div class="form-group">
        <label>{{ $t('views.events.target_group') }}</label>
        <select v-model="forms.subject.group" class="form-control">
          <option :value="null">Keine Gruppe</option>
          <option v-for="g in eventGroups" :key="g.id" :value="g.id">{{ g.name }}</option>
        </select>
      </div>
      <div class="modal-actions">
        <button @click="closeModal('subject')" class="btn-secondary">{{ $t('actions.cancel') }}</button>
        <button @click="saveEntity('event-management/subject-assignments', forms.subject, loadSubjects, 'subject')" class="btn-primary">{{ $t('actions.save') }}</button>
      </div>
    </BaseModal>

  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useMockAuth } from '@/composables/useMockAuth'
import { useCrud } from '@/composables/useCrud'

import BaseBreadcrumb from '@/components/ui/BaseBreadcrumb.vue'
import BaseTransferList from '@/components/ui/BaseTransferList.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'
import BaseCheckboxGroup from '@/components/ui/BaseCheckboxGroup.vue'
import TableActionButtons from '@/components/table/TableActionButtons.vue'
import EventGroupPhaseAssignment from '@/components/domain/EventGroupPhaseAssignment.vue' // <-- NEW IMPORT

const router = useRouter()
const route = useRoute()
const { t } = useI18n()
const { hasPermission, mockUsers } = useMockAuth()
const crudHelper = useCrud() 

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
  staff: { event: eventId, user: null, role: null, target_group: null },
  subject: { event: eventId, subject: null, group: null }
}
const forms = reactive(JSON.parse(JSON.stringify(defaultForms)))

const permissionOptions = [
  { value: 'can_start_session', label: 'Start Session' },
  { value: 'can_add_subjects', label: 'Add Subjects' },
  { value: 'can_view_reports', label: 'View Reports' },
  { value: 'can_upload_media', label: 'Upload Media' },
  { value: 'admin', label: 'Full Admin' }
]

const getEntityName = (list, id, key = 'name') => {
  if (!id) return null
  const item = list.find(i => i.id === id)
  return item ? item[key] : id
}
const getMockUserName = (id) => {
  const u = mockUsers.find(x => x.id === id)
  return u ? u.name : id
}

const loadEventBaseData = async () => {
  try {
    const res = await api.get(`events/${eventId}/`)
    eventData.value = res.data
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
  try {
    await api.put(`events/${eventId}/`, eventData.value)
    crudHelper.notifySuccess('updated', t)
  } catch (error) { crudHelper.parseApiError(error, t, 'errors.save_failed') }
}

const savePageGroups = async () => {
  try {
    const payload = { ...eventData.value, page_groups: assignedPageGroups.value }
    await api.put(`events/${eventId}/`, payload)
    crudHelper.notifySuccess('updated', t)
  } catch (error) { crudHelper.parseApiError(error, t, 'errors.save_failed') }
}

const saveEventGroupPhase = async (updatedGroup) => {
  try {
    await api.put(`event-management/groups/${updatedGroup.id}/`, updatedGroup)
    crudHelper.notifySuccess('updated', t)
    loadGroups() // Reload the list so the table updates
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

const deleteEntity = async (endpoint, id, reloadFn) => {
  if (!confirm(t('actions.confirm_delete_text') || 'Wirklich löschen?')) return
  try {
    await api.delete(`${endpoint}/${id}/`)
    crudHelper.notifySuccess('deleted', t)
    reloadFn()
  } catch (error) {
    alert(crudHelper.parseApiError(error, t, 'errors.delete_failed'))
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
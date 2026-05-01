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
      
      <button :class="['tab-btn', { active: activeTab === 'media' }]" @click="activeTab = 'media'">
        {{ $t('views.events.tab_media') || 'Logo & Poster' }}
      </button>

      <button :class="['tab-btn', { active: activeTab === 'gallery' }]" @click="activeTab = 'gallery'">
        {{ $t('views.events.tab_gallery') || 'Media Gallery' }}
      </button>

      <button :class="['tab-btn', { active: activeTab === 'page_groups' }]" @click="activeTab = 'page_groups'">
        {{ $t('nav.page_groups') }}
      </button>
      
      <button :class="['tab-btn', { active: activeTab === 'devices' }]" @click="activeTab = 'devices'">
        {{ $t('views.events.tab_device_pool') }}
      </button>

      <button :class="['tab-btn', { active: activeTab === 'groups' }]" @click="activeTab = 'groups'">
        {{ $t('views.events.tab_groups') }}
      </button>
      <button :class="['tab-btn', { active: activeTab === 'phases' }]" @click="activeTab = 'phases'">
        {{ $t('views.events.tab_phases') }}
      </button>
      <button :class="['tab-btn', { active: activeTab === 'subjects' }]" @click="activeTab = 'subjects'">
        {{ $t('views.events.tab_subjects') }}
      </button>
      <button :class="['tab-btn', { active: activeTab === 'staff' }]" @click="activeTab = 'staff'">
        {{ $t('views.events.tab_staff') }}
      </button>
      <button :class="['tab-btn', { active: activeTab === 'roles' }]" @click="activeTab = 'roles'" v-if="hasPermission('admin')">
        {{ $t('views.events.tab_roles') }}
      </button>
    </div>

    <div class="tab-content">
      
      <div v-if="activeTab === 'general'" class="panel">
        <div class="panel-header">
          <h3>{{ $t('views.events.tab_general') }}</h3>
          <button @click="saveGeneral" class="btn-primary" v-if="hasPermission('admin')">{{ $t('actions.save') }}</button>
        </div>
        <div class="form-row" style="display: flex; gap: 1rem; max-width: 600px; margin-bottom: 20px;">
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('common.name') }} *</label>
            <input v-model="eventData.name" type="text" class="form-control" />
          </div>
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('master_data.category') }}</label>
            <BaseSearchSelect v-model="eventData.category" :options="categories" :placeholder="$t('views.events.select_category')" :nullLabel="$t('master_data.none')" />
          </div>
        </div>
        <div class="form-group" style="max-width: 600px; margin-bottom: 20px;">
          <label>{{ $t('nav.locations') }}</label>
          <BaseSearchSelect v-model="eventData.location" :options="locations" :placeholder="$t('common.search')" :nullLabel="$t('master_data.none')" />
        </div>
        <div class="form-row" style="display: flex; gap: 1rem; max-width: 600px; margin-bottom: 20px;">
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('views.events.start') }}</label>
            <div style="display: flex; gap: 10px;">
              <input type="date" v-model="eventData.event_start_date" class="form-control" />
              <input type="time" v-model="eventData.event_start_time" class="form-control" style="max-width: 130px;" :class="{ 'input-invalid': timeErrors.start_time || fieldErrors.start_time }" @focus="initializeTimeField(eventData, 'event_start_time')" @blur="validateTimeField(eventData.event_start_time, 'start_time', $t('errors.invalid_time', 'Enter valid time'))"/>
            </div>
            <BaseInputError :message="timeErrors.start_time || fieldErrors.start_time" />
          </div>
          <div class="form-group" style="flex: 1;">
            <label>{{ $t('views.events.end') }}</label>
            <div style="display: flex; gap: 10px;">
              <input type="date" v-model="eventData.event_end_date" class="form-control" />
              <input type="time" v-model="eventData.event_end_time" class="form-control" style="max-width: 130px;" :class="{ 'input-invalid': timeErrors.end_time || fieldErrors.end_time }" @focus="initializeTimeField(eventData, 'event_end_time')" @blur="validateTimeField(eventData.event_end_time, 'end_time', $t('errors.invalid_time', 'Enter valid time'))"/>
            </div>
            <BaseInputError :message="timeErrors.end_time || fieldErrors.end_time" />
          </div>
        </div>
        <div class="form-group" style="max-width: 600px; margin-bottom: 20px;">
          <label>{{ $t('common.description') }}</label>
          <textarea v-model="eventData.description" class="form-control" rows="4"></textarea>
        </div>
      </div>

      <div v-if="activeTab === 'media'" class="panel">
        <div class="panel-header">
          <h3>{{ $t('views.events.tab_media')}}</h3>
        </div>
        <p style="margin-bottom: 30px; color: #7f8c8d;">{{ $t('views.events.media_desc')}}</p>
        
        <div class="media-management-grid">
          
          <div class="media-slot">
            <h4 style="color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-bottom: 15px;">
              {{ $t('views.events.tab_logo') }}
            </h4>
            <div class="slot-content">
              <div class="upload-section">
                <p style="font-size: 0.85rem; color: #7f8c8d; margin-bottom: 10px; font-style: italic;">
                  {{ eventData.logo ? ($t('views.events.replace_image')) : $t('actions.select_image') }}
                </p>
                <ImageUploadBox :eventName="eventData.name" @success="(newId) => handleMediaReplace('logo', newId)" />
              </div>

              <div class="preview-section" v-if="eventData.logo">
                <p style="font-size: 0.85rem; color: #7f8c8d; margin-bottom: 10px; font-style: italic;">
                   {{ $t('views.events.tab_logo') }}
                </p>
                <ImagePreview 
                  :assetId="eventData.logo" 
                  :mediaCategories="mediaCategories"
                  @deleted="savePartialEvent({ logo: null })" 
                />
              </div>
            </div>
          </div>

          <div class="media-slot">
            <h4 style="color: #2c3e50; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-bottom: 15px;">
              {{ $t('views.events.tab_poster') }}
            </h4>
            <div class="slot-content">
              <div class="upload-section">
                <p style="font-size: 0.85rem; color: #7f8c8d; margin-bottom: 10px; font-style: italic;">
                  {{ eventData.poster ? ($t('views.events.replace_image')) : $t('actions.select_image') }}
                </p>
                <ImageUploadBox :eventName="eventData.name" @success="(newId) => handleMediaReplace('poster', newId)" />
              </div>

              <div class="preview-section" v-if="eventData.poster">
                <p style="font-size: 0.85rem; color: #7f8c8d; margin-bottom: 10px; font-style: italic;">
                   {{ $t('views.events.tab_poster') }}
                </p>
                <ImagePreview 
                  :assetId="eventData.poster" 
                  :mediaCategories="mediaCategories"
                  @deleted="savePartialEvent({ poster: null })" 
                />
              </div>
            </div>
          </div>

        </div>
      </div>

      <div v-if="activeTab === 'gallery'" class="panel">
        <div class="panel-header">
          <h3>{{ $t('views.events.tab_gallery')}}</h3>
        </div>
        <p style="margin-bottom: 25px; color: #7f8c8d;">{{ $t('views.events.gallery_desc')}}</p>
        
        <EventMediaGallery :eventId="eventId" :eventName="eventData.name" />
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
          :enableOrdering="false" 
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

      <div v-if="activeTab === 'devices'" class="panel">
        <div class="panel-header">
          <h3>{{ $t('views.events.tab_device_pool') }}</h3>
          <button @click="saveDevicePool" class="btn-primary" v-if="hasPermission('admin')">{{ $t('actions.save') }}</button>
        </div>
        <p style="margin-bottom: 25px; color: #7f8c8d;">
          {{ $t('views.events.device_pool_desc') }}
        </p>
        
        <BaseTransferList
          v-model="eventData.devices"
          :options="allMasterDevices"
          :leftTitle="$t('views.events.available_devices')"
          :rightTitle="$t('views.events.selected_devices')"
          :searchPlaceholder="$t('views.events.search_devices')"
          :enableOrdering="false"
          :disabled="!hasPermission('admin')"
          :leftFilterFn="filterAvailableDeviceLogic"
          :rightFilterFn="filterSelectedDeviceLogic"
        >
          <template #left-filters>
            <BaseSearchSelect v-model="filterAvailableDevice" :options="deviceCategories" :placeholder="$t('views.metadata.search_category')" />
          </template>
          <template #right-filters>
            <BaseSearchSelect v-model="filterSelectedDevice" :options="deviceCategories" :placeholder="$t('views.metadata.search_category')" />
          </template>
        </BaseTransferList>
      </div>

      <div v-if="activeTab === 'groups'" class="panel">
        <div class="panel-header">
          <h3>{{ $t('views.events.tab_groups') }}</h3>
          <button @click="openModal('group')" class="btn-primary" v-if="hasPermission('admin')">{{ $t('actions.add_new') }}</button>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th style="width: 25%;"><ColumnHeaderFilter :title="$t('views.events.group_name')" v-model="groupFilters.name" :placeholder="$t('common.search')" /></th>
              <th style="width: 35%;"><ColumnHeaderFilter :title="$t('common.description')" v-model="groupFilters.description" :placeholder="$t('common.search')" /></th>
              <th style="width: 25%;">{{ $t('views.events.assigned_phase') }}</th>
              <th class="actions-column">{{ $t('actions.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="grp in filteredGroups" :key="grp.id">
              <td><strong>{{ grp.name }}</strong></td>
              <td>{{ grp.description || '-' }}</td>
              <td>
                <div v-if="grp.page_groups && grp.page_groups.length > 0" style="display: flex; gap: 5px; flex-wrap: wrap;">
                  <span v-for="pgId in grp.page_groups" :key="pgId" class="badge category-badge">
                    {{ getEntityName(availablePageGroups, pgId) }}
                  </span>
                </div>
                <span v-else class="text-muted">{{ $t('views.events.no_phases_assigned') }}</span>
              </td>
              <TableActionButtons @edit="openModal('group', grp)" @delete="deleteEntity('event-management/groups', grp.id, loadGroups)" v-if="hasPermission('admin')" />
            </tr>
            <tr v-if="!filteredGroups.length"><td colspan="4" class="text-center">{{ $t('common.no_data') }}</td></tr>
          </tbody>
        </table>
      </div>

      <div v-if="activeTab === 'phases'" class="panel">
        <div class="panel-header">
          <h3>{{ $t('views.events.assigned_phases') }}</h3>
        </div>
        <p style="margin-bottom: 20px; color: #555;">{{ $t('views.events.phases_description') }}</p>
        <EventGroupPhaseAssignment 
          :eventGroups="eventGroups" 
          :pageGroups="resolvedAssignedPageGroups" 
          :eventDevicePool="resolvedDevicePool"
          :deviceCategories="deviceCategories"
          @update-assignment="saveEventGroupPhase" 
          @edit-metadata="openPhaseMetadataModal"
        />
      </div>

      <div v-if="activeTab === 'subjects'" class="panel">
        <div class="panel-header">
          <h3>{{ $t('views.events.tab_subjects') }}</h3>
          <div style="display: flex; gap: 10px;">
            <button @click="modals.randomizer = true" class="btn-primary" style="background-color: #9b59b6; border-color: #8e44ad;" v-if="hasPermission('add_subjects') || hasPermission('admin')">
              🎲 {{ $t('views.events.randomize') }}
            </button>
            <button @click="modals.quickAssign = true" class="btn-secondary" v-if="hasPermission('add_subjects') || hasPermission('admin')">
              ⚡ {{ $t('views.events.quick_assign') }}
            </button>
            <button @click="openModal('subject')" class="btn-primary" v-if="hasPermission('add_subjects') || hasPermission('admin')">
              + {{ $t('views.events.assign_subject') }}
            </button>
          </div>
        </div>
        <table class="data-table">
          <thead>
            <tr>
              <th><ColumnHeaderFilter :title="$t('views.events.subject') + ' ID'" v-model="subjectFilters.id" :placeholder="$t('common.search')" /></th>
              <th><ColumnHeaderFilter :title="$t('master_data.firstname')" v-model="subjectFilters.firstname" :placeholder="$t('common.search')" /></th>
              <th><ColumnHeaderFilter :title="$t('master_data.lastname')" v-model="subjectFilters.lastname" :placeholder="$t('common.search')" /></th>
              <th><ColumnHeaderFilter :title="$t('views.events.target_group')" v-model="subjectFilters.group" :placeholder="$t('common.search')" /></th>
              <th class="actions-column">{{ $t('actions.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="sub in filteredSubjects" :key="sub.subject">
              <td><strong>{{ getEntityName(realSubjects, sub.subject, 'identifier') || getEntityName(realSubjects, sub.subject, 'subject_id') }}</strong></td>
              <td>{{ getEntityName(realSubjects, sub.subject, 'firstname') || '-' }}</td>
              <td>{{ getEntityName(realSubjects, sub.subject, 'lastname') || '-' }}</td>
              <td>
                <span v-if="sub.groups.length === 0" class="text-muted">{{ $t('views.events.no_group') }}</span>
                <span v-else>{{ sub.groups.map(gId => getEntityName(eventGroups, gId)).join(', ') }}</span>
              </td>
              <TableActionButtons @edit="openModal('subject', sub)" @delete="deleteSubjectGroup(sub)" v-if="hasPermission('admin') || hasPermission('add_subjects')" />
            </tr>
            <tr v-if="!filteredSubjects.length"><td colspan="5" class="text-center">{{ $t('common.no_data') }}</td></tr>
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
              <th><ColumnHeaderFilter :title="$t('views.events.user')" v-model="staffFilters.user" :placeholder="$t('common.search')" /></th>
              <th><ColumnHeaderFilter :title="$t('views.events.role')" v-model="staffFilters.role" :placeholder="$t('common.search')" /></th>
              <th><ColumnHeaderFilter :title="$t('views.events.target_group')" v-model="staffFilters.group" :placeholder="$t('common.search')" /></th>
              <th class="actions-column">{{ $t('actions.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="staff in filteredStaff" :key="staff.id">
              <td><strong>{{ getMockUserName(staff.user) }}</strong></td>
              <td>{{ getEntityName(eventRoles, staff.role) }}</td>
              <td>{{ getEntityName(eventGroups, staff.target_group) || $t('views.events.global_all_groups') }}</td>
              <TableActionButtons @edit="openModal('staff', staff)" @delete="deleteEntity('event-management/staff-assignments', staff.id, loadStaff)" v-if="hasPermission('admin')" />
            </tr>
            <tr v-if="!filteredStaff.length"><td colspan="4" class="text-center">{{ $t('common.no_data') }}</td></tr>
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
              <th><ColumnHeaderFilter :title="$t('common.name')" v-model="roleFilters.name" :placeholder="$t('common.search')" /></th>
              <th><ColumnHeaderFilter :title="$t('views.events.permissions')" v-model="roleFilters.permissions" :placeholder="$t('common.search')" /></th>
              <th class="actions-column">{{ $t('actions.actions') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="role in filteredRoles" :key="role.id">
              <td><strong>{{ role.name }}</strong></td>
              <td>{{ role.permissions ? role.permissions.join(', ') : '-' }}</td>
              <TableActionButtons @edit="openModal('role', role)" @delete="deleteEntity('event-management/roles', role.id, loadRoles)" />
            </tr>
            <tr v-if="!filteredRoles.length"><td colspan="3" class="text-center">{{ $t('common.no_data') }}</td></tr>
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
          :disabled="!!editingId" 
        />
      </div>
      <div class="form-group">
        <label>{{ $t('views.events.target_group') }} ({{ $t('views.events.multiple') }})</label>
        <SearchableCheckboxGroup 
          v-model="forms.subject.groups" 
          :options="eventGroups" 
          :searchPlaceholder="$t('views.events.search_groups')"
        />
      </div>
      <div class="modal-actions">
        <button @click="closeModal('subject')" class="btn-secondary">{{ $t('actions.cancel') }}</button>
        <button @click="saveSubjectAssignments" class="btn-primary">{{ $t('actions.save') }}</button>
      </div>
    </BaseModal>

    <EventGroupQuickAssignModal 
      :isOpen="modals.quickAssign"
      :eventId="eventId"
      :eventGroups="eventGroups"
      :subjects="realSubjects"
      :assignments="subjectAssignments"
      @close="modals.quickAssign = false"
      @saved="loadSubjects"
    />

    <EventGroupRandomizerModal 
      :isOpen="modals.randomizer"
      :eventId="eventId"
      :eventGroups="eventGroups"
      :subjects="realSubjects"
      :assignments="subjectAssignments"
      @close="modals.randomizer = false"
      @saved="loadSubjects"
    />

    <PhaseConfigMetadataModal 
      :isOpen="isPhaseMetadataModalOpen"
      :instanceId="editingPhaseConfig?.metadata_instance"
      :configName="editingPhaseConfig?.device_name"
      @close="isPhaseMetadataModalOpen = false"
    />

  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import { useMockAuth } from '@/composables/useMockAuth'
import { useCrud } from '@/composables/useCrud'
import { useGlobalModal } from '@/composables/useGlobalModal'
import { useTimeInput } from '@/composables/useTimeInput'

import BaseBreadcrumb from '@/components/ui/BaseBreadcrumb.vue'
import BaseTransferList from '@/components/ui/BaseTransferList.vue'
import BaseModal from '@/components/ui/BaseModal.vue'
import BaseSearchSelect from '@/components/ui/BaseSearchSelect.vue'
import TableActionButtons from '@/components/table/TableActionButtons.vue'
import ColumnHeaderFilter from '@/components/table/ColumnHeaderFilter.vue'
import EventGroupPhaseAssignment from '@/components/domain/EventGroupPhaseAssignment.vue'
import BaseInputError from '@/components/ui/BaseInputError.vue'
import SubjectSearchSelect from '@/components/domain/SubjectSearchSelect.vue'
import SearchableCheckboxGroup from '@/components/ui/SearchableCheckboxGroup.vue'
import EventGroupQuickAssignModal from '@/components/domain/EventGroupQuickAssignModal.vue'
import EventGroupRandomizerModal from '@/components/domain/EventGroupRandomizerModal.vue'
import ImagePreview from '@/components/ui/ImagePreview.vue'
import ImageUploadBox from '@/components/ui/ImageUploadBox.vue'
import EventMediaGallery from '@/components/domain/EventMediaGallery.vue'
import PhaseConfigMetadataModal from '@/components/domain/PhaseConfigMetadataModal.vue'

const route = useRoute()
const { t } = useI18n()
const { hasPermission, mockUsers } = useMockAuth()
const crudHelper = useCrud() 
const { requireConfirmation, showWarning } = useGlobalModal()
const { initializeTime, validateTime, parseApiTime, buildApiPayload } = useTimeInput()

const eventId = route.params.id
const activeTab = ref('general')
const eventData = ref({})

const availablePageGroups = ref([])
const assignedPageGroups = ref([])
const allMasterDevices = ref([]) 
const eventGroups = ref([])
const eventRoles = ref([])
const staffAssignments = ref([])
const subjectAssignments = ref([])
const realSubjects = ref([])

const pageGroupCategories = ref([])
const deviceCategories = ref([]) 
const categories = ref([])
const locations = ref([])
const mediaCategories = ref([])

const groupFilters = ref({ name: '', description: '' })
const subjectFilters = ref({ id: '', firstname: '', lastname: '', group: '' })
const staffFilters = ref({ user: '', role: '', group: '' })
const roleFilters = ref({ name: '', permissions: '' })

const filterAvailablePG = ref(null)
const filterSelectedPG = ref(null)
const filterAvailableLogic = (opt) => !filterAvailablePG.value || opt.category === filterAvailablePG.value
const filterSelectedLogic = (opt) => !filterSelectedPG.value || opt.category === filterSelectedPG.value

const filterAvailableDevice = ref(null)
const filterSelectedDevice = ref(null)
const filterAvailableDeviceLogic = (opt) => !filterAvailableDevice.value || opt.category === filterAvailableDevice.value
const filterSelectedDeviceLogic = (opt) => !filterSelectedDevice.value || opt.category === filterSelectedDevice.value

const breadcrumbItems = computed(() => [
  { label: t('nav.events'), route: '/events' },
  { label: eventData.value.name || t('common.loading') }
])

const isPhaseMetadataModalOpen = ref(false)
const editingPhaseConfig = ref(null)

const openPhaseMetadataModal = (config) => {
  editingPhaseConfig.value = config
  isPhaseMetadataModalOpen.value = true
}

const resolvedDevicePool = computed(() => {
  if (!eventData.value.devices || eventData.value.devices.length === 0) return [];
  
  return eventData.value.devices.map(deviceId => {
    const id = typeof deviceId === 'object' ? deviceId.id : deviceId;
    const master = allMasterDevices.value.find(d => d.id === id);
    
    if (master) {
      return {
        id: master.id, 
        device_model_id: master.id,
        device_name: master.name || 'Unbekanntes Gerät',
        category: master.category,
        channels: master.channel_names || master.channels || []
      };
    }
    return null;
  }).filter(Boolean);
});

const getEntityName = (list, id, key = 'name') => {
  if (!id) return null
  const item = list.find(i => i.id === id)
  return item ? item[key] : id
}
const getMockUserName = (id) => {
  const u = mockUsers.find(x => x.id === id)
  return u ? u.name : id
}

const filteredGroups = computed(() => {
  return eventGroups.value.filter(g => {
    if (groupFilters.value.name && !g.name.toLowerCase().includes(groupFilters.value.name.toLowerCase())) return false
    if (groupFilters.value.description && (!g.description || !g.description.toLowerCase().includes(groupFilters.value.description.toLowerCase()))) return false
    return true
  })
})

const filteredRoles = computed(() => {
  return eventRoles.value.filter(r => {
    if (roleFilters.value.name && !r.name.toLowerCase().includes(roleFilters.value.name.toLowerCase())) return false
    const perms = r.permissions ? r.permissions.join(', ') : ''
    if (roleFilters.value.permissions && !perms.toLowerCase().includes(roleFilters.value.permissions.toLowerCase())) return false
    return true
  })
})

const filteredStaff = computed(() => {
  return staffAssignments.value.filter(s => {
    const userName = getMockUserName(s.user) || ''
    const roleName = getEntityName(eventRoles.value, s.role) || ''
    const targetGroup = getEntityName(eventGroups.value, s.target_group) || t('views.events.global_all_groups')
    if (staffFilters.value.user && !userName.toLowerCase().includes(staffFilters.value.user.toLowerCase())) return false
    if (staffFilters.value.role && !roleName.toLowerCase().includes(staffFilters.value.role.toLowerCase())) return false
    if (staffFilters.value.group && !targetGroup.toLowerCase().includes(staffFilters.value.group.toLowerCase())) return false
    return true
  })
})

const resolvedAssignedPageGroups = computed(() => {
  const assignedIds = assignedPageGroups.value.map(val => typeof val === 'object' ? val.id : val)
  return availablePageGroups.value.filter(pg => assignedIds.includes(pg.id))
})

const assignedSubjectIds = computed(() => {
  return [...new Set(subjectAssignments.value.map(a => a.subject))]
})

const groupedSubjectAssignments = computed(() => {
  const map = new Map()
  subjectAssignments.value.forEach(a => {
    if (!map.has(a.subject)) {
      map.set(a.subject, {
        subject: a.subject,
        groups: [],
        assignmentIds: [] 
      })
    }
    const entry = map.get(a.subject)
    if (a.group && !entry.groups.includes(a.group)) {
      entry.groups.push(a.group)
    }
    entry.assignmentIds.push(a.id)
  })
  return Array.from(map.values())
})

const filteredSubjects = computed(() => {
  return groupedSubjectAssignments.value.filter(sub => {
    const sId = getEntityName(realSubjects.value, sub.subject, 'identifier') || getEntityName(realSubjects.value, sub.subject, 'subject_id') || ''
    const fn = getEntityName(realSubjects.value, sub.subject, 'firstname') || ''
    const ln = getEntityName(realSubjects.value, sub.subject, 'lastname') || ''
    const groupsStr = sub.groups.map(gId => getEntityName(eventGroups.value, gId)).join(', ') || t('views.events.no_group')
    
    if (subjectFilters.value.id && !sId.toLowerCase().includes(subjectFilters.value.id.toLowerCase())) return false
    if (subjectFilters.value.firstname && !fn.toLowerCase().includes(subjectFilters.value.firstname.toLowerCase())) return false
    if (subjectFilters.value.lastname && !ln.toLowerCase().includes(subjectFilters.value.lastname.toLowerCase())) return false
    if (subjectFilters.value.group && !groupsStr.toLowerCase().includes(subjectFilters.value.group.toLowerCase())) return false
    return true
  })
})

const modals = reactive({ group: false, role: false, staff: false, subject: false, quickAssign: false, randomizer: false })
const editingId = ref(null)

const defaultForms = {
  group: { event: eventId, name: '', description: '', page_groups: [] },
  role: { event: eventId, name: '', permissions: [] },
  staff: { user: null, role: null, target_group: null }, 
  subject: { event: eventId, subject: null, groups: [] } 
}
const forms = reactive(JSON.parse(JSON.stringify(defaultForms)))

const fieldErrors = reactive({ start_time: '', end_time: '' })
const timeErrors = reactive({ start_time: '', end_time: '' })

const initializeTimeField = (dataObj, key) => {
  const tempRef = ref(dataObj[key])
  initializeTime(tempRef, '00:00')
  dataObj[key] = tempRef.value
}
const validateTimeField = (val, key, errorMsg) => {
  timeErrors[key] = ''
  if (!val) return true 
  const isValid = validateTime(val, errorMsg)
  if (!isValid) timeErrors[key] = errorMsg
  return isValid
}

const extractDatePart = (isoString) => {
  if (!isoString) return ''
  const d = new Date(isoString)
  return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0')
}

const loadEventBaseData = async () => {
  try {
    const res = await api.get(`events/${eventId}/`)
    
    if (!res.data.devices) {
      res.data.devices = []
    }
    
    eventData.value = res.data
    eventData.value.event_start_date = extractDatePart(res.data.event_start)
    eventData.value.event_start_time = parseApiTime(res.data.event_start) 
    eventData.value.event_end_date = extractDatePart(res.data.event_end)
    eventData.value.event_end_time = parseApiTime(res.data.event_end) 
    assignedPageGroups.value = res.data.page_groups || []
  } catch (err) {}
}

const loadPageGroupsAndCategories = async () => {
  try {
    const [pgRes, catRes, evCatRes, locRes, mediaCatRes, deviceRes, deviceCatRes] = await Promise.all([
      api.get('page-groups/'), api.get('category/page-group/'),
      api.get('category/event/'), api.get('locations/'),
      api.get('category/media-asset/'), api.get('device-models/'),
      api.get('category/device-model/')
    ])
    availablePageGroups.value = pgRes.data; pageGroupCategories.value = catRes.data
    categories.value = evCatRes.data; locations.value = locRes.data
    mediaCategories.value = mediaCatRes.data
    deviceCategories.value = deviceCatRes.data
    
    allMasterDevices.value = deviceRes.data.filter(d => !d.is_archived).map(dev => ({
      ...dev, 
      id: dev.id,
      name: dev.name + (dev.manufacturer_name ? ` (${dev.manufacturer_name})` : ''),
      category: dev.category 
    }))
  } catch (err) {}
}

const loadGroups = async () => { try { const res = await api.get(`event-management/groups/?event=${eventId}`); eventGroups.value = res.data } catch (err) {} }
const loadRoles = async () => { try { const res = await api.get(`event-management/roles/?event=${eventId}`); eventRoles.value = res.data } catch (err) {} }
const loadStaff = async () => { try { const res = await api.get(`event-management/staff-assignments/?event=${eventId}`); staffAssignments.value = res.data } catch (err) {} }
const loadSubjects = async () => {
  try {
    const [subRes, assignmentRes] = await Promise.all([ api.get('subjects/'), api.get(`event-management/subject-assignments/?event=${eventId}`) ])
    realSubjects.value = subRes.data; subjectAssignments.value = assignmentRes.data
  } catch (err) {}
}

const saveGeneral = async () => {
  fieldErrors.start_time = ''; fieldErrors.end_time = ''
  let hasError = false
  if (eventData.value.event_start_time && !eventData.value.event_start_date) { fieldErrors.start_time = t('errors.time_without_date'); hasError = true }
  if (eventData.value.event_end_time && !eventData.value.event_end_date) { fieldErrors.end_time = t('errors.time_without_date'); hasError = true }
  if (eventData.value.event_start_time && !validateTimeField(eventData.value.event_start_time, 'start_time', t('errors.invalid_time', 'Enter valid time'))) hasError = true
  if (eventData.value.event_end_time && !validateTimeField(eventData.value.event_end_time, 'end_time', t('errors.invalid_time', 'Enter valid time'))) hasError = true
  if (hasError) return

  try {
    const payload = { ...eventData.value }
    if (payload.event_start_date) payload.event_start = buildApiPayload(payload.event_start_date, payload.event_start_time || '00:00')
    else payload.event_start = null
    if (payload.event_end_date) payload.event_end = buildApiPayload(payload.event_end_date, payload.event_end_time || '00:00')
    else payload.event_end = null

    delete payload.event_start_date; delete payload.event_start_time; delete payload.event_end_date; delete payload.event_end_time
    await api.put(`events/${eventId}/`, payload)
  } catch (error) { crudHelper.handleFormError(error, t) }
}

const savePartialEvent = async (payload) => {
  try {
    await api.patch(`events/${eventId}/`, payload)
    await loadEventBaseData() 
  } catch (error) {
    showWarning(t('common.error_saving'), t('common.error'))
  }
}

const saveDevicePool = async () => {
  try {
    await api.patch(`events/${eventId}/`, {
      devices: eventData.value.devices
    })
    await loadEventBaseData()
  } catch (error) {
    crudHelper.handleFormError(error, t)
  }
}

const handleMediaReplace = async (field, newAssetId) => {
  try {
    const oldAssetId = eventData.value[field]
    await api.patch(`events/${eventId}/`, { [field]: newAssetId })

    if (oldAssetId && oldAssetId !== newAssetId) {
      try {
        await api.delete(`media/assets/${oldAssetId}/`)
      } catch (e) { console.warn("old image couldnt be deleted", e) }
    }
    await loadEventBaseData() 
  } catch (error) {
    showWarning(t('common.error_saving'), t('common.error'))
  }
}

const savePageGroups = async () => {
  try {
    const payload = { ...eventData.value, page_groups: assignedPageGroups.value }
    delete payload.event_start_date; delete payload.event_start_time; delete payload.event_end_date; delete payload.event_end_time
    await api.put(`events/${eventId}/`, payload)
  } catch (error) {}
}

const saveEventGroupPhase = async (updatedGroup) => { try { await api.put(`event-management/groups/${updatedGroup.id}/`, updatedGroup); loadGroups() } catch (err) {} }

const openModal = (type, item = null) => {
  editingId.value = item ? (item.id || 'multi') : null 
  if (type === 'subject') {
    if (item) {
      forms.subject.subject = item.subject
      forms.subject.groups = subjectAssignments.value.filter(a => a.subject === item.subject).map(a => a.group).filter(Boolean) 
    } else { forms.subject = JSON.parse(JSON.stringify(defaultForms.subject)) }
  } else {
    if (item) {
      forms[type] = { ...item }
      if (type === 'role' && !forms[type].permissions) forms[type].permissions = []
    } else { forms[type] = JSON.parse(JSON.stringify(defaultForms[type])) }
  }
  modals[type] = true
}

const closeModal = (type) => { modals[type] = false; editingId.value = null }

const saveSubjectAssignments = async () => {
  try {
    const existing = subjectAssignments.value.filter(a => a.subject === forms.subject.subject)
    const selectedGroups = forms.subject.groups || []
    if (existing.length > 0) { await Promise.all(existing.map(a => api.delete(`event-management/subject-assignments/${a.id}/`))) }
    const postPromises = []
    if (selectedGroups.length === 0) {
      postPromises.push(api.post(`event-management/subject-assignments/`, { event: eventId, subject: forms.subject.subject, group: null }))
    } else {
      for (const gId of selectedGroups) { postPromises.push(api.post(`event-management/subject-assignments/`, { event: eventId, subject: forms.subject.subject, group: gId })) }
    }
    await Promise.all(postPromises)
    closeModal('subject'); loadSubjects()
  } catch (error) {}
}

const saveEntity = async (endpoint, payload, reloadFn, modalType) => {
  try {
    if (editingId.value) await api.put(`${endpoint}/${editingId.value}/`, payload)
    else await api.post(`${endpoint}/`, payload)
    closeModal(modalType); reloadFn()
  } catch (error) {}
}

const deleteEntity = (endpoint, id, reloadFn) => { requireConfirmation(async () => { try { await api.delete(`${endpoint}/${id}/`); reloadFn() } catch (error) {} }) }
const deleteSubjectGroup = (sub) => { requireConfirmation(async () => { try { const promises = sub.assignmentIds.map(id => api.delete(`event-management/subject-assignments/${id}/`)); await Promise.all(promises); loadSubjects() } catch (error) {} }) }

onMounted(async () => { await loadPageGroupsAndCategories(); await loadEventBaseData(); loadGroups(); loadRoles(); loadStaff(); loadSubjects() })
</script>

<style scoped>
.event-detail-view { display: flex; flex-direction: column; gap: 20px; }
.header-area { background: white; padding: 15px 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
.header-area h2 { margin: 0; color: #2c3e50; }
.tabs { display: flex; gap: 10px; border-bottom: 2px solid #e0e0e0; padding-bottom: 0; flex-wrap: wrap; }
.tab-btn { background: transparent; border: none; border-bottom: 3px solid transparent; padding: 10px 20px; font-size: 1rem; font-weight: 600; color: #7f8c8d; cursor: pointer; transition: all 0.2s; }
.tab-btn:hover { color: #3498db; }
.tab-btn.active { color: #3498db; border-bottom: 3px solid #3498db; }
.panel { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); min-height: 400px; }
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px; }
.panel-header h3 { margin: 0; color: #2c3e50; }
.modal-actions { display: flex; justify-content: flex-end; gap: 10px; margin-top: 25px; padding-top: 15px; border-top: 1px solid #eee; }

.media-management-grid { 
  display: grid; 
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr)); 
  gap: 40px; 
  width: 100%; 
}
.media-slot { 
  min-width: 0; 
}
.media-slot h4 { 
  color: #2c3e50; 
  border-bottom: 1px solid #eee; 
  padding-bottom: 5px; 
  margin-bottom: 15px; 
}
.slot-content { 
  display: flex; 
  gap: 20px; 
  align-items: stretch; 
  flex-wrap: wrap; 
  min-width: 0;
}
.upload-section, .preview-section {
  flex: 1 1 200px;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
</style>
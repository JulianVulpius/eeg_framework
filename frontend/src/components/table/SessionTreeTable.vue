<template>
  <table class="data-table tree-table">
    <thead>
      <tr>
        <th style="width: 30%;">
          <ColumnHeaderFilter 
            :title="$t('views.history.study_event')" 
            v-model="columnFilters.event" 
            :placeholder="$t('common.search')" 
          />
        </th>
        <th style="width: 25%;">
          <ColumnHeaderFilter 
            :title="$t('views.history.subject')" 
            v-model="columnFilters.subject" 
            :placeholder="$t('common.search')" 
          />
        </th>
        <th style="width: 20%;">
          <ColumnHeaderFilter 
            :title="$t('views.history.event_creator')" 
            v-model="columnFilters.creator" 
            :placeholder="$t('common.search')" 
          />
        </th>
        <th class="actions-column">{{ $t('actions.actions') }}</th>
      </tr>
    </thead>
    
    <tbody v-if="groupedData.length === 0">
      <tr>
        <td colspan="4" class="empty-state" style="text-align: center; padding: 30px; color: #7f8c8d;">
          {{ $t('common.no_data') }}
        </td>
      </tr>
    </tbody>

    <tbody v-else v-for="group in groupedData" :key="group.id" class="group-body">
      <tr class="root-row" @click="toggleGroup(group.id)">
        <td>
          <span class="expand-icon">{{ expandedGroups.includes(group.id) ? '▼' : '▶' }}</span>
          <strong>{{ group.eventName }}</strong>
        </td>
        <td><strong>{{ group.subjectName }}</strong></td>
        <td>{{ group.eventCreator }}</td>
        <td class="actions-cell" @click.stop>
          <button class="btn-primary btn-sm" @click="$emit('combined-report', group.eventId, group.subjectId)">
            {{ $t('views.history.btn_combined') }}
          </button>
        </td>
      </tr>

      <template v-if="expandedGroups.includes(group.id)">
        <tr v-for="sess in group.sessions" :key="sess.id" class="child-row">
          <td class="child-indent">
            <span class="child-connector">└─</span> 
            <span style="margin-right: 12px;">{{ sess.pageGroupName }}</span>
            <button class="btn-primary" style="background-color: #709aca; border-color: #16a085; padding: 2px 8px; font-size: 0.75rem; border-radius: 4px;" @click="$emit('pagegroup-report', group.eventId, sess.pageGroupId)">
              {{ $t('views.history.btn_pagegroup') }}
            </button>
          </td>
          <td class="timestamp-cell">{{ sess.displayDate }}</td>
          <td>
            <span v-if="sess.locationName" class="badge location-badge">
              📍 {{ sess.locationName }}
            </span>
            <span v-else>-</span>
          </td>
          <td class="actions-cell">
            <button class="btn-secondary btn-sm" @click="$emit('single-report', sess.id, group.eventId, group.subjectId)">
              {{ $t('views.history.btn_single') }}
            </button>
          </td>
        </tr>
      </template>
    </tbody>
  </table>
</template>

<script setup>
import { ref } from 'vue'
import ColumnHeaderFilter from './ColumnHeaderFilter.vue'

defineProps({
  groupedData: {
    type: Array,
    required: true
  },
  columnFilters: {
    type: Object,
    required: true
  }
})

defineEmits(['combined-report', 'single-report', 'pagegroup-report'])

const expandedGroups = ref([])

const toggleGroup = (groupId) => {
  const index = expandedGroups.value.indexOf(groupId)
  if (index > -1) {
    expandedGroups.value.splice(index, 1)
  } else {
    expandedGroups.value.push(groupId)
  }
}
</script>

<style scoped>
.tree-table { border-collapse: collapse; }
.group-body { border-bottom: 2px solid #e0e0e0; }
.root-row { cursor: pointer; background-color: #f8fafc; transition: background-color 0.2s; }
.root-row:hover { background-color: #f1f5f9; }
.expand-icon { display: inline-block; width: 20px; font-size: 0.8rem; color: #64748b; }
.child-row { background-color: #ffffff; }
.child-row:hover { background-color: #f8fafc; }
.child-indent { padding-left: 2rem !important; color: #475569; }
.child-connector { color: #cbd5e1; margin-right: 8px; }
.timestamp-cell { font-family: monospace; color: #64748b; }
.actions-cell { text-align: right; }
.btn-sm { padding: 5px 10px; font-size: 0.85rem; }
.location-badge { background-color: #e2e8f0; color: #334155; }
</style>
<template>
  <div class="session-history">
    
    <div class="page-header">
      <h1>{{ $t('nav.session_history') }}</h1>
      <div class="header-actions">
        <label class="toggle-label">
          <input 
            type="checkbox" 
            v-model="showIdColumn" 
          /> 
          {{ $t('common.show_id') }}
        </label>
      </div>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-if="showIdColumn" class="id-column">{{ $t('common.id') }}</th>
            <th style="width: 30%;">
              <ColumnHeaderFilter 
                :title="$t('views.report.event')" 
                v-model="columnFilters.event" 
                :placeholder="$t('common.search')" 
              />
            </th>
            <th style="width: 30%;">
              <ColumnHeaderFilter 
                :title="$t('views.report.subject')" 
                v-model="columnFilters.subject" 
                :placeholder="$t('common.search')" 
              />
            </th>
            <th style="width: 25%;">
              <ColumnHeaderDateFilter 
                :title="$t('views.report.date')" 
                v-model="columnFilters.date" 
              />
            </th>
            <th class="actions-column">{{ $t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredSessions.length === 0">
            <td :colspan="showIdColumn ? 5 : 4" class="empty-state">{{ $t('common.no_data') }}</td>
          </tr>
          <tr v-for="session in filteredSessions" :key="session.id">
            <td v-if="showIdColumn" class="id-column">{{ session.id }}</td>
            <td><strong>{{ getEventName(session.event) }}</strong></td>
            <td>{{ getSubjectName(session.subject) }}</td>
            <td>{{ formatDisplayDate(session.start_datetime) }}</td>
            <td class="actions-cell">
              <router-link :to="'/session/report/' + session.id" class="btn-primary" style="text-decoration: none; padding: 6px 12px; font-size: 0.85rem;">
                📊 {{ $t('nav.report') }}
              </router-link>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'
import ColumnHeaderFilter from '@/components/ColumnHeaderFilter.vue'
import ColumnHeaderDateFilter from '@/components/ColumnHeaderDateFilter.vue'

const showIdColumn = ref(false)
const sessions = ref([])
const events = ref([])
const subjects = ref([])

const columnFilters = ref({
  event: '',
  subject: '',
  date: ''
})

const loadData = async () => {
  try {
    const [sessRes, evRes, subRes] = await Promise.all([
      api.get('sessions/'),
      api.get('events/'),
      api.get('subjects/')
    ])
    sessions.value = sessRes.data
    events.value = evRes.data
    subjects.value = subRes.data
  } catch (error) {
    console.error("Failed to load history", error)
  }
}

const getEventName = (id) => {
  const ev = events.value.find(e => e.id === id)
  return ev ? ev.name : id
}

const getSubjectName = (id) => {
  const sub = subjects.value.find(s => s.id === id)
  if (!sub) return id
  
  const fullName = `${sub.first_name || ''} ${sub.last_name || ''}`.trim()
  return fullName || sub.identifier
}

const formatDisplayDate = (isoString) => {
  if (!isoString) return '-'
  const date = new Date(isoString)
  return date.toLocaleString(undefined, { 
    year: 'numeric', 
    month: '2-digit', 
    day: '2-digit', 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const filteredSessions = computed(() => {
  return sessions.value.filter(s => {
    
    if (columnFilters.value.event) {
      const q = columnFilters.value.event.toLowerCase()
      const eName = getEventName(s.event).toLowerCase()
      if (!eName.includes(q)) return false
    }

    if (columnFilters.value.subject) {
      const q = columnFilters.value.subject.toLowerCase()
      const sName = getSubjectName(s.subject).toLowerCase()
      if (!sName.includes(q)) return false
    }

    if (columnFilters.value.date) {
      if (!s.start_datetime || !s.start_datetime.startsWith(columnFilters.value.date)) return false
    }

    return true
  })
})

onMounted(loadData)
</script>
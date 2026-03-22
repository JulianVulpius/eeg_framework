<template>
  <div class="session-history">
    <div class="page-header">
      <h1>{{ $t('nav.session_history') }}</h1>
    </div>

    <div class="table-container">
      <div class="filters" style="padding: 15px; background: #f8f9fa; border-bottom: 1px solid #e0e0e0; display: flex; gap: 15px;">
        <input type="text" v-model="searchSubject" :placeholder="$t('views.report.subject') + ' ' + $t('common.search')" class="form-control" style="max-width: 250px;" />
      </div>

      <table class="data-table">
        <thead>
          <tr>
            <th class="id-column">{{ $t('common.id') }}</th>
            <th>{{ $t('views.report.date') }}</th>
            <th>{{ $t('views.report.event') }}</th>
            <th>{{ $t('views.report.subject') }}</th>
            <th class="actions-column">{{ $t('actions.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="filteredSessions.length === 0">
            <td colspan="5" class="empty-state">{{ $t('common.no_data') }}</td>
          </tr>
          <tr v-for="session in filteredSessions" :key="session.id">
            <td class="id-column">{{ session.id }}</td>
            <td>{{ new Date(session.start_datetime).toLocaleString() }}</td>
            <td><strong>{{ getEventName(session.event) }}</strong></td>
            <td>{{ getSubjectName(session.subject) }}</td>
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

const sessions = ref([])
const events = ref([])
const subjects = ref([])
const searchSubject = ref('')

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
  return sub ? `${sub.identifier} (${sub.first_name || ''} ${sub.last_name || ''})`.trim() : id
}

const filteredSessions = computed(() => {
  if (!searchSubject.value) return sessions.value
  const query = searchSubject.value.toLowerCase()
  return sessions.value.filter(s => {
    const subjectName = getSubjectName(s.subject).toLowerCase()
    return subjectName.includes(query)
  })
})

onMounted(loadData)
</script>
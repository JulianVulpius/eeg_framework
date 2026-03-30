<template>
  <div class="session-history">
    <div class="page-header" style="margin-bottom: 20px;">
      <h1>{{ $t('nav.session_history') }}</h1>
    </div>

    <div class="table-container">
      <SessionTreeTable 
        :groupedData="groupedSessions"
        :columnFilters="columnFilters"
        @combined-report="goToCombinedReport"
        @single-report="goToSingleReport"
        @pagegroup-report="goToPageGroupReport"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

import SessionTreeTable from '@/components/table/SessionTreeTable.vue'

const router = useRouter()

const sessions = ref([])
const events = ref([])
const subjects = ref([])
const pageGroups = ref([])
const locations = ref([])

const columnFilters = ref({ event: '', subject: '', creator: '' })

const loadData = async () => {
  try {
    const [sessRes, evRes, subRes, pgRes, locRes] = await Promise.all([
      api.get('sessions/'), api.get('events/'), api.get('subjects/'),
      api.get('page-groups/'), api.get('locations/')
    ])
    sessions.value = sessRes.data; events.value = evRes.data
    subjects.value = subRes.data; pageGroups.value = pgRes.data
    locations.value = locRes.data
  } catch (error) {
    console.error('failed to load history data', error)
  }
}

const getEvent = (id) => events.value.find(e => e.id === id) || {}
const getSubject = (id) => subjects.value.find(s => s.id === id) || {}
const getPageGroup = (id) => pageGroups.value.find(p => p.id === id) || {}
const getLocation = (id) => locations.value.find(l => l.id === id) || {}

const formatDisplayDate = (isoString) => {
  if (!isoString) return '-'
  return new Date(isoString).toLocaleString(undefined, { 
    year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' 
  })
}

const groupedSessions = computed(() => {
  const map = new Map()
  
  const searchEv = columnFilters.value.event.toLowerCase()
  const searchSub = columnFilters.value.subject.toLowerCase()
  const searchCreator = columnFilters.value.creator.toLowerCase()
  
  sessions.value.forEach(session => {
    const ev = getEvent(session.event)
    const sub = getSubject(session.subject)
    
    const eventName = ev.name || `Event ${session.event}`
    const eventCreator = ev.creator || '-'
    const subjectName = `${sub.identifier || ''} ${sub.first_name ? `(${sub.first_name} ${sub.last_name})` : ''}`.trim() || `Subject ${session.subject}`
    
    if (searchEv && !eventName.toLowerCase().includes(searchEv)) return
    if (searchSub && !subjectName.toLowerCase().includes(searchSub)) return
    if (searchCreator && !eventCreator.toLowerCase().includes(searchCreator)) return

    const key = `${session.event}_${session.subject}`
    
    if (!map.has(key)) {
      map.set(key, {
        id: key, eventId: session.event, subjectId: session.subject,
        eventName, eventCreator, subjectName, sessions: []
      })
    }
    
    map.get(key).sessions.push({
      id: session.id,
      pageGroupId: session.page_group,
      pageGroupName: getPageGroup(session.page_group).name || `Group ${session.page_group}`,
      locationName: session.location ? getLocation(session.location).name : null,
      displayDate: formatDisplayDate(session.start_datetime)
    })
  })
  
  return Array.from(map.values())
})

const goToSingleReport = (sessionId, eventId, subjectId) => {
  router.push({ path: '/sessions/reports/single', query: { sessionId, eventId, subjectId } })
}
const goToCombinedReport = (eventId, subjectId) => {
  router.push({ path: '/sessions/reports/combined', query: { eventId, subjectId } })
}
const goToPageGroupReport = (eventId, pageGroupId) => {
  router.push({ path: '/sessions/reports/page-groups', query: { eventId, pageGroupId } })
}
onMounted(loadData)
</script>
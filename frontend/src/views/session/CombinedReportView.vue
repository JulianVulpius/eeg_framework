<template>
  <div class="session-report" style="padding-bottom: 40px;">
    <BaseBreadcrumb :items="breadcrumbItems" />

    <div class="page-header" style="margin-bottom: 20px;">
      <h1 style="font-size: 1.8rem; color: #2c3e50; margin: 0;">{{ $t('views.report.combined_title') }}</h1>
    </div>

    <div v-if="isLoading" class="loading-state">{{ $t('common.loading') }}</div>

    <div v-else class="report-content">
      <div v-if="combinedReports.length === 0" class="card empty-state">
        {{ $t('views.report.no_data') }}
      </div>

      <SessionReportDisplay 
        v-for="report in combinedReports" 
        :key="report.session_id" 
        :report="report" 
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import BaseBreadcrumb from '@/components/ui/BaseBreadcrumb.vue'
import SessionReportDisplay from '@/components/domain/SessionReportDisplay.vue'

const route = useRoute()
const { t } = useI18n()

const eventId = route.query.eventId
const subjectId = route.query.subjectId
const combinedReports = ref([])
const isLoading = ref(true)

const breadcrumbItems = computed(() => [
  { label: t('nav.session_history'), route: '/sessions/history' },
  { label: t('breadcrumb.history_combined_report'), route: null }
])

const loadCombinedReport = async () => {
  try {
    const [sessionsRes, locRes] = await Promise.all([
      api.get(`sessions/?event=${eventId}&subject=${subjectId}`),
      api.get('locations/')
    ])
    
    let sessions = sessionsRes.data
    sessions.sort((a, b) => new Date(a.start_datetime) - new Date(b.start_datetime))

    const reportPromises = sessions.map(session => api.get(`sessions/${session.id}/report/`))
    const reportsResponses = await Promise.all(reportPromises)
    
    combinedReports.value = reportsResponses.map((res, index) => {
      const originalSession = sessions[index]
      const locName = locRes.data.find(l => l.id === originalSession.location)?.name || '-'

      return {
        ...res.data,
        start_time: originalSession.start_datetime,
        location_name: locName
      }
    })
  } catch (error) {
    console.error('failed to load combined report', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(loadCombinedReport)
</script>
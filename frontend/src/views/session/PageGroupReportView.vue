<template>
  <div class="session-report">
    <BaseBreadcrumb :items="breadcrumbItems" />

    <div class="page-header" style="margin-bottom: 20px;">
      <h1 v-if="pageGroupReports.length > 0">
        {{ pageGroupReports[0].page_group_name }}
      </h1>
      <h1 v-else>
        {{ $t('views.report.pagegroup_title') }}
      </h1>
    </div>

    <div v-if="isLoading" class="loading-state">
      {{ $t('common.loading') }}
    </div>

    <div v-else class="report-content">
      <div v-if="pageGroupReports.length === 0" class="card empty-state">
        {{ $t('views.report.no_data') }}
      </div>

      <div v-for="report in pageGroupReports" :key="report.session_id" style="margin-bottom: 40px;">
        
        <div class="card meta-card">
          <div class="meta-grid">
            <div><label>{{ $t('views.report.session_id') }}</label><div class="val">{{ report.session_id }}</div></div>
            <div><label>{{ $t('views.report.event') }}</label><div class="val">{{ report.event_name }}</div></div>
            <div><label>{{ $t('views.report.subject') }}</label><div class="val">{{ report.subject_identifier }}</div></div>
            <div><label>{{ $t('views.report.date') }}</label><div class="val">{{ formatDate(report.start_time) }}</div></div>
            <div v-if="report.location_name"><label>{{ $t('views.report.location') }}</label><div class="val">{{ report.location_name }}</div></div>
          </div>
        </div>

        <div v-if="report.metadata_groups.length === 0" class="card empty-state" style="margin-top: -10px;">
           {{ $t('views.report.no_data') }}
        </div>

        <div v-for="(group, idx) in report.metadata_groups" :key="idx" class="card group-card">
          <h3>{{ group.group_name }}</h3>
          <table class="report-table">
            <thead>
              <tr>
                <th style="width: 50%;">{{ $t('views.report.question') }}</th>
                <th style="width: 50%;">{{ $t('views.report.answer') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(ans, aIdx) in group.answers" :key="aIdx">
                <td>{{ ans.question }}</td>
                <td>
                  <span v-if="ans.type === 'BOOLEAN'" class="badge" :class="ans.answer === 'true' ? 'badge-yes' : 'badge-no'">
                    {{ ans.answer === 'true' ? $t('common.yes') : $t('common.no') }}
                  </span>
                  <span v-else><strong>{{ ans.answer }}</strong></span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import BaseBreadcrumb from '@/components/ui/BaseBreadcrumb.vue'

const route = useRoute()

const eventId = route.query.eventId
const pageGroupId = route.query.pageGroupId

const { t } = useI18n()

const pageGroupReports = ref([])
const isLoading = ref(true)

const breadcrumbItems = computed(() => [
  { label: t('nav.session_history'), route: '/sessions/history' },
  { label: t('breadcrumb.history_page_group_report'), route: null }
])

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString(undefined, {
    year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'
  })
}

const loadPageGroupReport = async () => {
  try {
    const [sessionsRes, locRes] = await Promise.all([
      api.get(`sessions/?event=${eventId}&page_group=${pageGroupId}`),
      api.get('locations/')
    ])
    
    let sessions = sessionsRes.data
    const locations = locRes.data

    sessions.sort((a, b) => new Date(a.start_datetime) - new Date(b.start_datetime))

    const reportPromises = sessions.map(session => api.get(`sessions/${session.id}/report/`))
    const reportsResponses = await Promise.all(reportPromises)
    
    pageGroupReports.value = reportsResponses.map((res, index) => {
      const reportData = res.data
      const originalSession = sessions[index]
      
      let locName = '-'
      if (originalSession.location) {
        const loc = locations.find(l => l.id === originalSession.location)
        if (loc) locName = loc.name
      }

      return {
        ...reportData,
        start_time: originalSession.start_datetime,
        location_name: locName
      }
    })
  } catch (error) {
    console.error('failed to load page group report', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(loadPageGroupReport)
</script>
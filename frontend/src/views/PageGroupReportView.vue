<template>
  <div class="session-report">
    <div class="page-header" style="margin-bottom: 20px;">
      <h1>{{ $t('views.report.pagegroup_title') }}</h1>
      <button class="btn-secondary" @click="router.push('/session-history')">{{ $t('actions.back') }}</button>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const props = defineProps({
  eventId: { type: [String, Number], required: true },
  pageGroupId: { type: [String, Number], required: true }
})

const router = useRouter()
const pageGroupReports = ref([])
const isLoading = ref(true)

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString(undefined, {
    year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit'
  })
}

const loadPageGroupReport = async () => {
  try {
    const [sessionsRes, locRes] = await Promise.all([
      api.get(`sessions/?event=${props.eventId}&page_group=${props.pageGroupId}`),
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

<style scoped>
.card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #e0e0e0; }
.meta-card { background: #f8f9fa; border-left: 4px solid #1abc9c; }
.meta-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
.meta-grid label { font-size: 0.85rem; color: #7f8c8d; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 5px; display: block;}
.meta-grid .val { font-size: 1.1rem; font-weight: bold; color: #2c3e50; }
.group-card h3 { margin-top: 0; color: #2c3e50; border-bottom: 2px solid #f4f7f6; padding-bottom: 10px; margin-bottom: 15px; }
.report-table { width: 100%; border-collapse: collapse; }
.report-table th { text-align: left; padding: 10px; background: #f4f7f6; color: #7f8c8d; font-size: 0.9rem; }
.report-table td { padding: 12px 10px; border-bottom: 1px solid #eee; }
.badge { padding: 4px 8px; border-radius: 4px; font-size: 0.85rem; font-weight: bold; }
.badge-yes { background: #d5f5e3; color: #27ae60; }
.badge-no { background: #fadbd8; color: #c0392b; }
</style>
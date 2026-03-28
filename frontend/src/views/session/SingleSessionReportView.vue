<template>
  <div class="session-report">
    <BaseBreadcrumb :items="breadcrumbItems" />

    <div class="page-header" style="margin-bottom: 20px;">
      <h1>{{ $t('views.report.title') }}</h1>
    </div>

    <div v-if="isLoading" class="loading-state">{{ $t('common.loading') }}</div>
    
    <div v-else-if="reportData" class="report-content">
      <div class="card meta-card">
        <div class="meta-grid">
          <div><label>{{ $t('views.report.session_id') }}</label><div class="val">{{ reportData.session_id }}</div></div>
          <div><label>{{ $t('views.report.event') }}</label><div class="val">{{ reportData.event_name }}</div></div>
          <div><label>{{ $t('views.report.subject') }}</label><div class="val">{{ reportData.subject_identifier }}</div></div>
          <div><label>{{ $t('views.report.date') }}</label><div class="val">{{ formatDate(reportData.start_time) }}</div></div>
          <div v-if="reportData.location_name"><label>{{ $t('views.report.location') }}</label><div class="val">{{ reportData.location_name }}</div></div>
        </div>
      </div>

      <div v-if="reportData.metadata_groups.length === 0" class="card empty-state">
        {{ $t('views.report.no_data') }}
      </div>

      <div v-for="(group, idx) in reportData.metadata_groups" :key="idx" class="card group-card">
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
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import api from '@/services/api'
import BaseBreadcrumb from '@/components/ui/BaseBreadcrumb.vue'

const props = defineProps({
  id: { type: [String, Number], required: true }
})

const router = useRouter()
const route = useRoute()
const { t } = useI18n()

const reportData = ref(null)
const isLoading = ref(true)

const hasCombinedContext = computed(() => {
  return route.query.eventId && route.query.subjectId
})

const breadcrumbItems = computed(() => {
  const items = [
    { label: t('nav.session_history'), route: '/session-history' }
  ]
  
  items.push({ label: `${t('breadcrumb.history_single_report')} #${props.id}`, route: null })
  
  return items
})

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString(undefined, {
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit'
  })
}

const loadReport = async () => {
  try {
    const [reportRes, sessionRes, locRes] = await Promise.all([
      api.get(`sessions/${props.id}/report/`),
      api.get(`sessions/${props.id}/`),
      api.get('locations/')
    ])
    
    reportData.value = reportRes.data
    const session = sessionRes.data
    const locations = locRes.data
    
    let locName = '-'
    if (session.location) {
      const loc = locations.find(l => l.id === session.location)
      if (loc) locName = loc.name
    }
    
    reportData.value.location_name = locName
    reportData.value.start_time = session.start_datetime
    
  } catch (error) {
    console.error('error loading single report data', error)
  } finally {
    isLoading.value = false
  }
}

onMounted(loadReport)
</script>
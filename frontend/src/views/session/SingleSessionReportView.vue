<template>
  <div class="session-report" style="padding-bottom: 40px;">
    <BaseBreadcrumb :items="breadcrumbItems" />

    <div class="page-header" style="margin-bottom: 20px;">
      <h1 style="font-size: 1.8rem; color: #2c3e50; margin: 0;">{{ $t('views.report.title') }}</h1>
    </div>

    <div v-if="isLoading" class="loading-state">{{ $t('common.loading') }}</div>
    
    <div v-else-if="reportData" class="report-content">
      <SessionReportDisplay :report="reportData" />
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

const sessionId = route.query.sessionId
const reportData = ref(null)
const isLoading = ref(true)

const breadcrumbItems = computed(() => [
  { label: t('nav.session_history'), route: '/sessions/history' },
  { label: `${t('breadcrumb.history_single_report')} #${sessionId}`, route: null }
])

const loadReport = async () => {
  try {
    const response = await api.get(`sessions/${sessionId}/report/`)
    reportData.value = response.data
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

onMounted(loadReport)
</script>
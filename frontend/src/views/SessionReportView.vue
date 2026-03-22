<template>
  <div class="session-report">
    <div class="page-header" style="margin-bottom: 20px;">
      <h1>{{ $t('views.report.title') }}</h1>
      <button class="btn-secondary" @click="router.push('/session-history')">{{ $t('actions.back') }}</button>
    </div>

    <div v-if="isLoading" class="loading-state">
      {{ $t('common.loading') }}
    </div>

    <div v-else-if="reportData" class="report-content">
      
      <div class="card meta-card">
        <div class="meta-grid">
          <div>
            <label>{{ $t('views.report.session_id') }}</label>
            <div class="val">{{ reportData.session_id }}</div>
          </div>
          <div>
            <label>{{ $t('views.report.event') }}</label>
            <div class="val">{{ reportData.event_name }}</div>
          </div>
          <div>
            <label>{{ $t('views.report.subject') }}</label>
            <div class="val">{{ reportData.subject_identifier }}</div>
          </div>
          <div>
            <label>{{ $t('views.report.date') }}</label>
            <div class="val">{{ new Date(reportData.start_time).toLocaleString() }}</div>
          </div>
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
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const props = defineProps({
  id: { type: [String, Number], required: true }
})
const router = useRouter()
const reportData = ref(null)
const isLoading = ref(true)

const loadReport = async () => {
  try {
    const response = await api.get(`sessions/${props.id}/report/`)
    reportData.value = response.data
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

onMounted(loadReport)
</script>

<style scoped>
.card { background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); margin-bottom: 20px; border: 1px solid #e0e0e0; }
.meta-card { background: #f8f9fa; border-left: 4px solid #3498db; }
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
<template>
  <div class="report-display" style="margin-bottom: 40px;">
    
    <div class="card meta-card">
      <div class="meta-grid">
        <div><label>{{ $t('views.report.session_id') }}</label><div class="val">{{ report.session_id }}</div></div>
        <div><label>{{ $t('views.report.event') }}</label><div class="val">{{ report.event_name }}</div></div>
        <div v-if="report.page_group_name"><label>{{ $t('views.report.page_group') }}</label><div class="val">{{ report.page_group_name }}</div></div>
        <div><label>{{ $t('views.report.subject') }}</label><div class="val">{{ report.subject_identifier }}</div></div>
        <div><label>{{ $t('views.report.date') }}</label><div class="val">{{ formatDate(report.start_time) }}</div></div>
        <div v-if="report.location_name"><label>{{ $t('views.report.location') }}</label><div class="val">{{ report.location_name }}</div></div>
      </div>
    </div>

    <div v-if="report.metadata_groups.length === 0 && report.uploaded_files.length === 0" class="card empty-state" style="margin-top: -10px;">
       {{ $t('views.report.no_data') }}
    </div>

    <div v-if="report.uploaded_files && report.uploaded_files.length > 0" class="card group-card">
      <h3>📁 {{ $t('views.report.files_title') }}</h3>
      <table class="report-table">
        <thead>
          <tr>
            <th style="width: 10%;">{{ $t('views.report.file_order') }}</th>
            <th style="width: 15%;">{{ $t('views.report.file_type') }}</th>
            <th style="width: 25%;">{{ $t('views.report.file_name') }}</th>
            <th style="width: 30%;">{{ $t('views.report.file_desc') }}</th>
            <th style="width: 20%;">{{ $t('views.report.file_link') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(file, idx) in report.uploaded_files" :key="idx">
            <td>{{ file.order }}</td>
            <td>
              <span class="badge">{{ file.type }}</span>
              <span v-if="file.category" style="display: block; font-size: 0.75rem; color: #7f8c8d; margin-top: 4px;">{{ file.category }}</span>
            </td>
            <td><strong>{{ file.name || '-' }}</strong></td>
            <td>{{ file.description || '-' }}</td>
            <td>
              <a v-if="file.url" :href="getAbsoluteUrl(file.url)" target="_blank" style="color: #3498db; text-decoration: none; font-size: 0.9rem;">
                {{ file.url.split('/').pop() }}
              </a>
              <span v-else class="text-muted">-</span>
            </td>
          </tr>
        </tbody>
      </table>
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
</template>

<script setup>
import { useFormatters } from '@/composables/useFormatters'

const props = defineProps({
  report: {
    type: Object,
    required: true
  }
})

const { formatDate, getAbsoluteUrl } = useFormatters()
</script>
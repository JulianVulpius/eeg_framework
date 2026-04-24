<template>
  <div class="page-container" style="padding-bottom: 40px;">
    
    <div class="page-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
      <h1 style="margin: 0;">{{ $t('views.heartrate.title') }}</h1>
      <span class="badge" :class="isLive ? 'badge-active' : 'badge-idle'">
        {{ isLive ? $t('views.heartrate.status_connected') : $t('views.heartrate.status_waiting') }}
      </span>
    </div>

    <div class="card metric-card" style="margin-bottom: 30px;">
      <span class="metric-label">{{ $t('views.heartrate.graph_label') }} (Live)</span>
      <div class="metric-value">
        {{ bpmDisplay }} <span style="font-size: 1.2rem; color: var(--text-muted);">BPM</span>
      </div>
    </div>

    <div class="card" style="height: 350px; margin-bottom: 30px; padding: 20px;">
      <Line v-if="hasData" :data="chartData" :options="chartOptions" />
      <div v-else style="text-align: center; padding-top: 130px; color: #bdc3c7; font-style: italic;">
        {{ $t('views.heartrate.placeholder') }}
      </div>
    </div>

    <div class="terminal-card">
      <div class="terminal-header">
        <h3>{{ $t('views.heartrate.dev_log_title') }}</h3>
        <button @click="clearLog" class="btn btn-danger" style="padding: 4px 10px; font-size: 0.8rem;">
           {{ $t('views.heartrate.btn_clear_log') }}
        </button>
      </div>
      
      <div class="terminal-body">
        <div v-for="(entry, index) in dataLog" :key="index" class="terminal-line">
          <span class="terminal-time">[{{ dataLog.length - index }}]</span>
          <code class="terminal-msg">{{ entry }}</code>
        </div>
        <div v-if="dataLog.length === 0" class="terminal-empty">
          {{ $t('views.heartrate.dev_log_empty') }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { Line } from 'vue-chartjs';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler);

const { t, locale } = useI18n();

const isLive = ref(false);
const bpmDisplay = ref('--');
const dataLog = ref([]);
const hasData = computed(() => chartData.value.labels.length > 0);
let ws = null;

const chartData = ref({
  labels: [],
  datasets: [{
    label: t('views.heartrate.graph_label'),
    backgroundColor: 'rgba(231, 76, 60, 0.1)',
    borderColor: '#e74c3c',
    borderWidth: 3,
    pointRadius: 0,
    fill: true,
    tension: 0.4,
    data: []
  }]
});

watch(locale, () => {
  chartData.value.datasets[0].label = t('views.heartrate.graph_label');
  chartData.value = { ...chartData.value };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  animation: false,
  scales: {
    y: { min: 40, max: 180, grid: { color: '#eee' } },
    x: { display: false }
  }
};

const clearLog = () => { dataLog.value = []; };

const connect = () => {
  ws = new WebSocket('ws://localhost:8001/ws/heartrate');

  ws.onmessage = (event) => {
    const payload = JSON.parse(event.data);

    if (payload.action === 'session_start') {
      chartData.value = { ...chartData.value, labels: [], datasets: [{ ...chartData.value.datasets[0], data: [] }] };
      dataLog.value.unshift(JSON.stringify(payload));
      if (dataLog.value.length > 10) dataLog.value.pop();
      return; 
    }

    if (payload.bpm) {
      isLive.value = true;
      bpmDisplay.value = Math.round(payload.bpm);
      dataLog.value.unshift(JSON.stringify(payload));
      if (dataLog.value.length > 10) dataLog.value.pop();

      let currentLabels = [...chartData.value.labels];
      let currentData = [...chartData.value.datasets[0].data];
      currentLabels.push(new Date().toLocaleTimeString());
      currentData.push(payload.bpm);

      if (currentLabels.length > 300) { currentLabels.shift(); currentData.shift(); }

      chartData.value = { ...chartData.value, labels: currentLabels, datasets: [{ ...chartData.value.datasets[0], data: currentData }] };
    }
  };

  ws.onclose = () => { 
    isLive.value = false; 
    setTimeout(connect, 2000); 
  };
};

onMounted(() => connect());

onUnmounted(() => {
  if (ws) {
    ws.onclose = null;
    ws.close();
  }
});
</script>

<style scoped>
.page-container { max-width: 1000px; margin: 0 auto; }
</style>
<template>
  <div class="page-container">
    <div class="header-section">
      <h1>{{ $t('views.heartrate.title') }}</h1>
      <div class="status-indicator" :class="{ 'active': isLive }">
        {{ isLive ? $t('views.heartrate.status_connected') : $t('views.heartrate.status_waiting') }}
      </div>
    </div>

    <div class="main-stats">
      <div class="heart-rate-box">
        <span class="value">{{ bpmDisplay }}</span>
        <span class="unit">BPM</span>
      </div>
    </div>

    <div class="graph-container">
      <Line v-if="hasData" :data="chartData" :options="chartOptions" />
      <div v-else class="placeholder-text">
        {{ $t('views.heartrate.placeholder') }}
      </div>
    </div>

    <div class="dev-log-container">
      <div class="dev-log-header">
        <h3>{{ $t('views.heartrate.dev_log_title') }}</h3>
        <button @click="clearLog" class="btn-clear" v-if="dataLog.length > 0">
           {{ $t('views.heartrate.btn_clear_log') }}
        </button>
      </div>
      
      <div class="log-entries">
        <div v-for="(entry, index) in dataLog" :key="index" class="log-entry">
          <span class="log-index">[{{ dataLog.length - index }}]</span>
          <code class="log-code">{{ entry }}</code>
        </div>
        <div v-if="dataLog.length === 0" class="log-placeholder">
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
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler
} from 'chart.js';

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

const clearLog = () => {
  dataLog.value = [];
};

const connect = () => {
  ws = new WebSocket('ws://localhost:8001/ws/heartrate');

  ws.onmessage = (event) => {
    const payload = JSON.parse(event.data);

    if (payload.action === 'session_start') {
      chartData.value = {
        ...chartData.value,
        labels: [],
        datasets: [{
          ...chartData.value.datasets[0],
          data: []
        }]
      };
      
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

      if (currentLabels.length > 300) {
        currentLabels.shift();
        currentData.shift();
      }

      chartData.value = {
        ...chartData.value,
        labels: currentLabels,
        datasets: [{
          ...chartData.value.datasets[0],
          data: currentData
        }]
      };
    }
  };

  ws.onclose = () => {
    isLive.value = false;
    setTimeout(connect, 2000);
  };
};

onMounted(() => connect());
onUnmounted(() => ws && ws.close());
</script>

<style scoped>
.page-container { padding: 20px; color: #2c3e50; max-width: 1000px; margin: 0 auto; }
.header-section { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
.status-indicator { font-size: 0.8rem; font-weight: bold; color: #95a5a6; border: 1px solid #ddd; padding: 4px 12px; border-radius: 15px; }
.status-indicator.active { color: #e74c3c; border-color: #e74c3c; animation: pulse 2s infinite; }
.main-stats { display: flex; justify-content: center; margin-bottom: 20px; }
.heart-rate-box { background: #fff; border-radius: 15px; padding: 20px 50px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); text-align: center; }
.value { font-size: 60px; font-weight: 800; color: #e74c3c; }
.unit { font-size: 18px; margin-left: 8px; color: #7f8c8d; }
.graph-container { background: #fff; height: 300px; padding: 20px; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); margin-bottom: 30px; }
.placeholder-text { text-align: center; padding-top: 120px; color: #bdc3c7; font-style: italic; }

.dev-log-container { background: #2c3e50; color: #ecf0f1; padding: 15px; border-radius: 10px; font-family: monospace; }
.dev-log-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #444; padding-bottom: 8px; margin-bottom: 8px; }
.dev-log-header h3 { margin: 0; font-size: 0.9rem; color: #bdc3c7; }

.btn-clear { background: #e74c3c; color: white; border: none; padding: 4px 10px; border-radius: 4px; font-size: 0.75rem; cursor: pointer; transition: background 0.2s; font-family: sans-serif; font-weight: bold;}
.btn-clear:hover { background: #c0392b; }

.log-entries { height: 200px; overflow-y: auto; display: flex; flex-direction: column; gap: 5px; }
.log-entry { font-size: 0.85rem; border-bottom: 1px solid #34495e; padding: 2px 0; display: flex; gap: 10px; }
.log-index { color: #f1c40f; min-width: 30px; }
.log-code { color: #2ecc71; }
.log-placeholder { color: #7f8c8d; text-align: center; padding-top: 80px; }

@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
</style>
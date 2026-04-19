<template>
  <div class="page-container">
    <div class="header-section">
      <h1>Session Heartrate</h1>
      <div class="status-indicator" :class="{ 'active': isLive }">
        {{ isLive ? 'CONNECTED' : 'WAITING FOR DATA' }}
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
        Start measurement on Galaxy Watch
      </div>
    </div>

    <div class="dev-log-container">
      <h3>Developer Live Log (Raw JSON)</h3>
      <div class="log-entries">
        <div v-for="(entry, index) in dataLog" :key="index" class="log-entry">
          <span class="log-index">[{{ dataLog.length - index }}]</span>
          <code class="log-code">{{ entry }}</code>
        </div>
        <div v-if="dataLog.length === 0" class="log-placeholder">
          No data packets received yet...
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { Line } from 'vue-chartjs';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Filler);

const isLive = ref(false);
const bpmDisplay = ref('--');
const dataLog = ref([]);
const hasData = computed(() => chartData.value.labels.length > 0);
let ws = null;
let lastMessageTime = 0;

const chartData = ref({
  labels: [],
  datasets: [{
    label: 'Heartrate',
    backgroundColor: 'rgba(231, 76, 60, 0.1)',
    borderColor: '#e74c3c',
    borderWidth: 3,
    pointRadius: 0,
    fill: true,
    tension: 0.4,
    data: []
  }]
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

const connect = () => {
  ws = new WebSocket('ws://localhost:8001/ws/heartrate');

  ws.onmessage = (event) => {
    const payload = JSON.parse(event.data);
    isLive.value = true;
    bpmDisplay.value = Math.round(payload.bpm);

    dataLog.value.unshift(JSON.stringify(payload));
    if (dataLog.value.length > 10) dataLog.value.pop();

    const now = Date.now();
    if (lastMessageTime !== 0 && (now - lastMessageTime > 4000)) {
      chartData.value.labels = [];
      chartData.value.datasets[0].data = [];
    }
    lastMessageTime = now;

    chartData.value.labels.push(new Date().toLocaleTimeString());
    chartData.value.datasets[0].data.push(payload.bpm);

    if (chartData.value.labels.length > 40) {
      chartData.value.labels.shift();
      chartData.value.datasets[0].data.shift();
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
.dev-log-container h3 { margin-top: 0; font-size: 0.9rem; color: #bdc3c7; border-bottom: 1px solid #444; padding-bottom: 8px; }
.log-entries { height: 200px; overflow-y: auto; display: flex; flex-direction: column; gap: 5px; }
.log-entry { font-size: 0.85rem; border-bottom: 1px solid #34495e; padding: 2px 0; display: flex; gap: 10px; }
.log-index { color: #f1c40f; min-width: 30px; }
.log-code { color: #2ecc71; }
.log-placeholder { color: #7f8c8d; text-align: center; padding-top: 80px; }
@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
</style>
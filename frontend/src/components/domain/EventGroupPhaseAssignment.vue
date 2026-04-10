<template>
  <div class="phase-assignment-container">
    <div class="group-selector">
      <label class="section-label">1. {{ $t('views.events.select_event_group') }}</label>
      <select v-model="selectedGroupId" class="form-control select-box">
        <option :value="null">{{ $t('actions.select') || 'Bitte wählen' }}</option>
        <option v-for="grp in eventGroups" :key="grp.id" :value="grp.id">
          {{ grp.name }}
        </option>
      </select>
    </div>

    <div v-if="selectedGroup" class="page-group-radios fade-in">
      <label class="section-label">2. {{ $t('views.events.assign_phases_title') }}</label>
      
      <div v-if="pageGroups.length === 0" class="no-data">
        ⚠️ {{ $t('views.events.no_phases_available') }}
      </div>
      
      <div class="radio-list">
        <label v-for="pg in pageGroups" :key="pg.id" class="radio-item">
          <input
            type="checkbox"
            :value="pg.id"
            v-model="selectedGroup.page_groups"
            @change="onSelectionChange"
          />
          <span class="checkbox-custom"></span>
          <span class="radio-label">{{ pg.name }}</span>
        </label>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  eventGroups: { type: Array, required: true },
  pageGroups: { type: Array, required: true }
})

const emit = defineEmits(['update-assignment'])
const selectedGroupId = ref(null)

const selectedGroup = computed(() => {
  return props.eventGroups.find(g => g.id === selectedGroupId.value)
})

const onSelectionChange = () => {
  if (selectedGroup.value) {
    emit('update-assignment', selectedGroup.value)
  }
}
</script>

<style scoped>
.phase-assignment-container {
  background: #fdfdfd;
  padding: 25px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.02);
}
.section-label {
  display: block;
  font-weight: bold;
  color: #2c3e50;
  margin-bottom: 10px;
  font-size: 1.1rem;
}
.select-box { max-width: 400px; border: 2px solid #3498db; }
.page-group-radios { margin-top: 30px; padding-top: 20px; border-top: 1px dashed #ccc; }
.radio-list { display: flex; flex-direction: column; gap: 12px; margin-top: 15px; }
.radio-item {
  display: flex; align-items: center; cursor: pointer; padding: 10px 15px;
  background: white; border: 1px solid #ddd; border-radius: 6px;
  transition: all 0.2s; max-width: 400px;
}
.radio-item:hover { border-color: #3498db; background: #f0f8ff; }
.radio-item input[type="checkbox"] { margin-right: 12px; transform: scale(1.2); cursor: pointer; }
.radio-label { font-size: 1.05rem; font-weight: 500; color: #333; }
.no-data { color: #e74c3c; background: #fadbd8; padding: 15px; border-radius: 6px; font-weight: 500; }
.fade-in { animation: fadeIn 0.3s ease-in-out; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }
</style>
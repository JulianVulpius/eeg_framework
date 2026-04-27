<template>
  <div class="metadata-filter-toolbar" v-if="showToolbar">
    
    <div v-if="filterState.isActive" class="active-filter-badge">
      <span>🔖 {{ $t('metadata_filter.active') }} <strong>{{ filterState.ruleCount }} {{ $t('metadata_filter.rules') }}</strong></span>
      <button class="btn-clear" @click="$emit('clear')" :title="$t('metadata_filter.clear')">✖</button>
    </div>

    <button 
      class="btn-meta-filter" 
      @click="$emit('open')"
    >
      🔖 {{ $t('metadata_filter.button') }}
    </button>

  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  tableSupportsMetadata: {
    type: Boolean,
    default: false
  },
  hasAnyMetadata: {
    type: Boolean,
    default: false
  },
  filterState: {
    type: Object,
    required: true
  }
})

defineEmits(['open', 'clear'])

const showToolbar = computed(() => props.tableSupportsMetadata || props.hasAnyMetadata)
</script>

<style scoped>
.metadata-filter-toolbar {
  display: flex;
  justify-content: flex-end; 
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  width: 100%;
}

.btn-meta-filter {
  background-color: #afb2b4; 
  color: #000000; 
  font-weight: bold;
  border: 2px solid #5a6268;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s ease;
}

.btn-meta-filter:hover {
  background-color: #5a6268;
  transform: translateY(-1px);
}

.active-filter-badge {
  background-color: var(--primary-color, #3498db);
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.95rem;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.btn-clear {
  background: none;
  border: none;
  color: white;
  font-weight: bold;
  cursor: pointer;
  padding: 0;
  font-size: 1.1rem;
}

.btn-clear:hover {
  color: #ffcccc;
}
</style>
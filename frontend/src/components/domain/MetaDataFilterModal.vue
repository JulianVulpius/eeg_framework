<template>
  <BaseModal 
    :isOpen="isOpen" 
    :title="$t('metadata_filter.title')"
    @close="closeModal"
  >
    <div class="metadata-filter-builder" v-if="!isLoading">
      
      <div class="logic-toggle">
        <label>
          <input type="radio" value="AND" v-model="matchType"> 
          {{ $t('metadata_filter.match_and') }}
        </label>
        <label>
          <input type="radio" value="OR" v-model="matchType"> 
          {{ $t('metadata_filter.match_or') }}
        </label>
      </div>

      <hr />

      <div class="rules-container">
        <div v-for="(rule, index) in rules" :key="index" class="rule-row">
          
          <div class="rule-col flex-2">
            <select v-model="rule.definition" class="form-control" @change="rule.value = ''">
              <option :value="null">{{ $t('metadata_filter.select_def') }}</option>
              <optgroup v-for="group in formattedDefinitions" :key="group.groupId" :label="group.groupName">
                <option v-for="def in group.defs" :key="def.id" :value="def.id">
                  {{ def.name }}
                </option>
              </optgroup>
            </select>
          </div>

          <div class="rule-col flex-1">
            <select v-model="rule.operator" class="form-control" :disabled="!rule.definition || getDefType(rule.definition) === 'BOOLEAN'">
              <option value="exact">{{ $t('metadata_filter.op_exact') }}</option>
              <option value="contains">{{ $t('metadata_filter.op_contains') }}</option>
            </select>
          </div>

          <div class="rule-col flex-2">
            <template v-if="rule.definition">
              <select v-if="getDefType(rule.definition) === 'BOOLEAN'" v-model="rule.value" class="form-control">
                <option value="true">{{ $t('common.yes')}}</option>
                <option value="false">{{ $t('common.no')}}</option>
              </select>
              <input 
                v-else
                :type="getDefType(rule.definition) === 'INTEGER' ? 'number' : 'text'"
                v-model="rule.value"
                class="form-control"
                :placeholder="$t('metadata_filter.value')"
              />
            </template>
            <input v-else type="text" class="form-control" disabled />
          </div>

          <button class="btn-icon text-danger" @click="removeRule(index)" title="Remove">🗑️</button>
        </div>
      </div>

      <button class="btn-secondary mt-2" @click="addRule">+ {{ $t('metadata_filter.add_rule') }}</button>

      <div class="modal-actions" style="margin-top: 2rem;">
        <button class="btn-secondary" @click="clearFilter">{{ $t('metadata_filter.clear') }}</button>
        <button class="btn-primary" @click="applyFilter" :disabled="!isValid">{{ $t('metadata_filter.apply') }}</button>
      </div>

    </div>
    <div v-else class="loading-state">
      <p>{{ $t('common.loading') }}</p>
    </div>
  </BaseModal>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import api from '@/services/api'
import BaseModal from '@/components/ui/BaseModal.vue'

const props = defineProps({
  isOpen: Boolean,
  contentTypeId: Number
})

const emit = defineEmits(['close', 'apply', 'clear'])

const isLoading = ref(false)
const matchType = ref('AND')
const rules = ref([])

const allGroups = ref([])
const allDefinitions = ref([])

const isValid = computed(() => {
  return rules.value.length > 0 && rules.value.every(r => r.definition && (r.value !== '' && r.value !== null))
})

const formattedDefinitions = computed(() => {
  const result = []
  allGroups.value.forEach(group => {
    if (group.assigned_definitions && group.assigned_definitions.length > 0) {
      const defs = group.assigned_definitions.map(id => allDefinitions.value.find(d => d.id === id)).filter(Boolean)
      result.push({ groupId: group.id, groupName: group.name, defs })
    }
  })
  return result
})

const getDefType = (id) => allDefinitions.value.find(d => d.id === id)?.expected_data_type || 'STRING'

const loadData = async () => {
  if (!props.contentTypeId) return
  isLoading.value = true
  try {
    const [groupsRes, defsRes] = await Promise.all([
      api.get('metadata/groups/'),
      api.get('metadata/definitions/')
    ])
    allGroups.value = groupsRes.data
    allDefinitions.value = defsRes.data
  } catch (e) {
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

watch(() => props.isOpen, (newVal) => {
  if (newVal && allGroups.value.length === 0) {
    loadData()
  }
  if (newVal && rules.value.length === 0) {
    addRule()
  }
})

const addRule = () => {
  rules.value.push({ definition: null, operator: 'exact', value: '' })
}

const removeRule = (index) => {
  rules.value.splice(index, 1)
  if (rules.value.length === 0) addRule()
}

const applyFilter = () => {
  emit('apply', { matchType: matchType.value, rules: rules.value })
  closeModal()
}

const clearFilter = () => {
  rules.value = []
  emit('clear')
  closeModal()
}

const closeModal = () => emit('close')
</script>

<style scoped>
.logic-toggle { display: flex; gap: 1.5rem; margin-bottom: 1rem; }
.rule-row { display: flex; gap: 0.5rem; margin-bottom: 0.5rem; align-items: center; }
.rule-col { display: flex; flex-direction: column; }
.flex-1 { flex: 1; }
.flex-2 { flex: 2; }
.mt-2 { margin-top: 1rem; }
</style>
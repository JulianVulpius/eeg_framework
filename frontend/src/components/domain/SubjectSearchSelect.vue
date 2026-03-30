<template>
  <div class="form-group custom-select-wrapper" @click.stop style="margin-bottom: 0;">
    <label v-if="label">{{ label }}</label>
    <input 
      type="text" 
      v-model="searchQuery" 
      class="form-control"
      :class="{ 'input-invalid': error }" 
      @focus="onFocus"
      :placeholder="displayPlaceholder" 
    />
    
    <ul v-if="isOpen" class="dropdown-list">
      <li @click="selectOption(null)">{{ nullLabel || $t('master_data.none') }}</li>
      <li v-for="opt in filteredOptions" :key="opt.id" @click="selectOption(opt)">
        {{ opt.identifier }} 
        <span v-if="opt.firstname || opt.lastname" style="color: #888; font-size: 0.85em; margin-left: 5px;">
          ({{ opt.firstname }} {{ opt.lastname }})
        </span>
      </li>
    </ul>
    
    <BaseInputError :message="error" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import BaseInputError from '@/components/ui/BaseInputError.vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: null
  },
  subjects: {
    type: Array,
    required: true
  },
  assignedIds: {
    type: Array,
    default: () => []
  },
  label: { type: String, default: '' },
  error: { type: String, default: '' },
  placeholder: { type: String, default: 'Search...' },
  nullLabel: { type: String, default: '' }
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const searchQuery = ref('')

const displayPlaceholder = computed(() => {
  if (isOpen.value) {
    const selected = props.subjects.find(o => o.id === props.modelValue)
    return selected ? selected.identifier : props.placeholder
  }
  return props.placeholder
})

const onFocus = () => {
  isOpen.value = true
  searchQuery.value = ''
}

const filteredOptions = computed(() => {
  const q = searchQuery.value.toLowerCase()
  
  return props.subjects.filter(opt => {
    const isAlreadyAssigned = props.assignedIds.includes(opt.id)
    const isCurrentlySelected = opt.id === props.modelValue
    
    if (isAlreadyAssigned && !isCurrentlySelected) {
      return false
    }

    const searchString = `${opt.identifier || ''} ${opt.firstname || ''} ${opt.lastname || ''}`.toLowerCase()
    
    return searchString.includes(q)
  })
})

const selectOption = (opt) => {
  if (opt) {
    emit('update:modelValue', opt.id)
    searchQuery.value = opt.identifier
  } else {
    emit('update:modelValue', null)
    searchQuery.value = ''
  }
  isOpen.value = false
}

watch(() => props.modelValue, (newVal) => {
  if (!isOpen.value) {
    if (!newVal) {
      searchQuery.value = ''
    } else {
      const selected = props.subjects.find(o => o.id === newVal)
      if (selected) {
        searchQuery.value = selected.identifier
      }
    }
  }
}, { immediate: true })

const closeDropdown = () => {
  isOpen.value = false
  const selected = props.subjects.find(o => o.id === props.modelValue)
  searchQuery.value = selected ? selected.identifier : ''
}

onMounted(() => document.addEventListener('click', closeDropdown))
onUnmounted(() => document.removeEventListener('click', closeDropdown))
</script>
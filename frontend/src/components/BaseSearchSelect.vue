<template>
  <div class="form-group custom-select-wrapper" @click.stop>
    <label v-if="label">{{ label }}</label>
    <input 
      type="text" 
      v-model="searchQuery" 
      class="form-control"
      :class="{ 'input-invalid': error }" 
      @focus="isOpen = true"
      :placeholder="placeholder || $t('common.search')" 
    />
    
    <ul v-if="isOpen" class="dropdown-list">
      <li @click="selectOption(null)">{{ $t('master_data.none') }}</li>
      <li v-for="opt in filteredOptions" :key="opt.id" @click="selectOption(opt)">
        {{ opt.name }}
      </li>
    </ul>
    
    <BaseInputError :message="error" />
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import BaseInputError from './BaseInputError.vue'

const props = defineProps({
  modelValue: {
    type: [String, Number],
    default: null
  },
  options: {
    type: Array,
    required: true
  },
  label: {
    type: String,
    default: ''
  },
  error: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const searchQuery = ref('')

// filter the options based on the input text
const filteredOptions = computed(() => {
  const q = searchQuery.value.toLowerCase()
  return props.options.filter(opt => opt.name.toLowerCase().includes(q))
})

// update the selected value and close dropdown
const selectOption = (opt) => {
  if (opt) {
    emit('update:modelValue', opt.id)
    searchQuery.value = opt.name
  } else {
    emit('update:modelValue', null)
    searchQuery.value = ''
  }
  isOpen.value = false
}

// keep local search text in sync if parent changes the v-model directly (e.g. on form reset or edit)
watch(() => props.modelValue, (newVal) => {
  if (!newVal) {
    searchQuery.value = ''
  } else {
    const selected = props.options.find(o => o.id === newVal)
    if (selected) {
      searchQuery.value = selected.name
    }
  }
}, { immediate: true })

// close the dropdown when clicking anywhere else on the page
const closeDropdown = () => {
  isOpen.value = false
  
  // if user typed something but didn't click an option, revert text to current selection
  const selected = props.options.find(o => o.id === props.modelValue)
  searchQuery.value = selected ? selected.name : ''
}

onMounted(() => {
  document.addEventListener('click', closeDropdown)
})

onUnmounted(() => {
  document.removeEventListener('click', closeDropdown)
})
</script>
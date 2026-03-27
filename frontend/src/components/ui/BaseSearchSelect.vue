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
  },
  nullLabel: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue'])

const isOpen = ref(false)
const searchQuery = ref('')

const displayPlaceholder = computed(() => {
  if (isOpen.value) {
    const selected = props.options.find(o => o.id === props.modelValue)
    return selected ? selected.name : (props.placeholder || 'Search...')
  }
  return props.placeholder || 'Search...'
})

const onFocus = () => {
  isOpen.value = true
  searchQuery.value = ''
}

const filteredOptions = computed(() => {
  const q = searchQuery.value.toLowerCase()
  return props.options.filter(opt => opt.name.toLowerCase().includes(q))
})

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

watch(() => props.modelValue, (newVal) => {
  if (!isOpen.value) {
    if (!newVal) {
      searchQuery.value = ''
    } else {
      const selected = props.options.find(o => o.id === newVal)
      if (selected) {
        searchQuery.value = selected.name
      }
    }
  }
}, { immediate: true })

const closeDropdown = () => {
  isOpen.value = false
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
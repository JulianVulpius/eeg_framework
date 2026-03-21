<template>
  <div class="shuffle-container">
    <div class="shuffle-box">
      <div class="shuffle-header">
        {{ $t('views.playlist.available_stimuli') }}
        <input type="text" v-model="searchAvailable" :placeholder="$t('views.playlist.search_placeholder')" class="shuffle-search" />
      </div>
      <ul class="shuffle-list">
        <li v-for="s in filteredAvailable" :key="s.id" @click="addStimulus(s.id)">
          <span>{{ s.name }}</span>
          <span class="add-btn">+</span>
        </li>
      </ul>
    </div>

    <div class="shuffle-box">
      <div class="shuffle-header">
        {{ $t('views.playlist.selected_items') }}
        <input type="text" v-model="searchSelected" :placeholder="$t('views.playlist.search_placeholder')" class="shuffle-search" />
      </div>
      <ul class="shuffle-list">
        <li v-for="item in mappedSelected" :key="'selected-' + item.originalIndex" 
            class="draggable-item"
            :class="{ 'is-dragging': draggedItemIndex === item.originalIndex }"
            draggable="true"
            @dragstart="onDragStart($event, item.originalIndex)"
            @dragover.prevent
            @dragenter.prevent
            @drop="onDrop($event, item.originalIndex)"
            @dragend="onDragEnd"
            @click="removeStimulus(item.originalIndex)">
          <div style="display: flex; align-items: center; gap: 10px;">
            <span class="drag-handle" @click.stop>☰</span>
            <span>{{ item.originalIndex + 1 }}. {{ item.name }}</span>
          </div>
          <span class="remove-btn">×</span>
        </li>
        <li v-if="modelValue.length === 0" class="shuffle-empty">-</li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  availableItems: {
    type: Array,
    required: true
  },
  modelValue: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['update:modelValue'])

const searchAvailable = ref('')
const searchSelected = ref('')
const draggedItemIndex = ref(null)

const filteredAvailable = computed(() => {
  if (!searchAvailable.value) return props.availableItems
  const q = searchAvailable.value.toLowerCase()
  return props.availableItems.filter(s => s.name.toLowerCase().includes(q))
})

const getStimulusName = (id) => {
  const s = props.availableItems.find(st => st.id === id)
  return s ? s.name : `Unknown (ID: ${id})`
}

const mappedSelected = computed(() => {
  let mapped = props.modelValue.map((id, index) => ({ id: id, originalIndex: index, name: getStimulusName(id) }))
  if (searchSelected.value) {
    const q = searchSelected.value.toLowerCase()
    mapped = mapped.filter(item => item.name.toLowerCase().includes(q))
  }
  return mapped
})

const addStimulus = (id) => {
  emit('update:modelValue', [...props.modelValue, id])
}

const removeStimulus = (index) => {
  const newList = [...props.modelValue]
  newList.splice(index, 1)
  emit('update:modelValue', newList)
}

const onDragStart = (event, index) => {
  draggedItemIndex.value = index
  event.dataTransfer.effectAllowed = 'move'
  if (event.dataTransfer) event.dataTransfer.setData('text/plain', index.toString())
}

const onDrop = (event, targetIndex) => {
  if (draggedItemIndex.value === null || draggedItemIndex.value === targetIndex) return
  const list = [...props.modelValue]
  const [movedItem] = list.splice(draggedItemIndex.value, 1)
  list.splice(targetIndex, 0, movedItem)
  emit('update:modelValue', list)
  draggedItemIndex.value = null
}

const onDragEnd = () => {
  draggedItemIndex.value = null
}
</script>

<style scoped>
.shuffle-container { display: flex; gap: 15px; }
.shuffle-box { flex: 1; border: 1px solid #ddd; border-radius: 4px; height: 250px; overflow-y: auto; background: #fdfdfd; }
.shuffle-header { padding: 10px; background: #f4f7f6; border-bottom: 1px solid #ddd; font-weight: bold; position: sticky; top: 0; display: flex; flex-direction: column; gap: 8px; z-index: 2; }
.shuffle-list { list-style: none; padding: 0; margin: 0; }
.shuffle-list li { padding: 10px; border-bottom: 1px solid #eee; display: flex; justify-content: space-between; align-items: center; cursor: pointer; }
.shuffle-list li:hover { background: #e9ecef; }
.shuffle-empty { text-align: center; color: #aaa; font-style: italic; cursor: default !important; }
.shuffle-empty:hover { background: none !important; }
.add-btn { color: #2ecc71; font-weight: bold; font-size: 1.2rem; }
.remove-btn { color: #e74c3c; font-weight: bold; font-size: 1.2rem; }
.shuffle-search { padding: 6px; border: 1px solid #ccc; border-radius: 4px; font-weight: normal; font-size: 0.85rem; width: 100%; box-sizing: border-box; }
.draggable-item { cursor: grab; transition: background-color 0.2s; }
.draggable-item:active { cursor: grabbing; }
.draggable-item.is-dragging { opacity: 0.4; background-color: #f1f2f6 !important; border: 1px dashed #3498db; }
.drag-handle { color: #bdc3c7; cursor: grab; font-size: 1.2rem; user-select: none; }
.drag-handle:hover { color: #7f8c8d; }
</style>
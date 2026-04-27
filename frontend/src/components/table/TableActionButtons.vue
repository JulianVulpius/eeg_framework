<template>
  <div class="action-buttons">
    <button v-if="showEdit" @click="$emit('edit', item)" class="btn-icon" title="Edit">
      ✏️
    </button>
    
    <button 
      v-if="hasMetadata" 
      @click="$emit('view-metadata', item)" 
      class="btn-icon btn-view-meta" 
      title="View MetaData"
    >
      🏷️
    </button>

    <button 
      v-if="tableSupportsMetadata || hasMetadata" 
      @click="$emit('edit-metadata', item)" 
      class="btn-icon btn-edit-meta" 
      title="Manage MetaData"
    >
      📝
    </button>

    <button v-if="showDelete" @click="$emit('delete', item)" class="btn-icon text-danger" title="Delete">
      🗑️
    </button>
  </div>
</template>

<script setup>
defineProps({
  item: { type: Object, required: true },
  showEdit: { type: Boolean, default: true },
  showDelete: { type: Boolean, default: true },
  
  tableSupportsMetadata: {
    type: Boolean,
    default: false
  },
  hasMetadata: {
    type: Boolean,
    default: false 
  }
})

defineEmits(['edit', 'delete', 'view-metadata', 'edit-metadata'])
</script>

<style scoped>
.action-buttons {
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
}
.btn-icon {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  font-size: 1.1rem;
  transition: transform 0.2s ease;
}
.btn-icon:hover {
  transform: scale(1.1);
}
.btn-view-meta {
  color: var(--primary-color);
}
.text-danger {
  color: var(--danger-color);
}
</style>
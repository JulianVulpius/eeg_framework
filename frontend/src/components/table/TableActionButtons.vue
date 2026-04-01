<template>
  <td class="actions-cell">
    <button 
      class="btn-icon" 
      @click="$emit('edit')" 
      :title="$t('actions.edit')"
    >
      ✏️
    </button>
    <button 
      class="btn-icon" 
      @click="$emit('delete')" 
      :title="$t('actions.delete')"
    >
      🗑️
    </button>
  </td>
</template>

<script setup>
defineEmits(['edit', 'delete'])
</script>
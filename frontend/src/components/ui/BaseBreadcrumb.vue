<template>
  <nav class="breadcrumb-nav" aria-label="breadcrumb">
    <ol class="breadcrumb-list">
      <li 
        v-for="(item, index) in items" 
        :key="index" 
        class="breadcrumb-item"
        :class="{ 'is-active': index === items.length - 1 }"
      >
        <router-link 
          v-if="index !== items.length - 1 && item.route" 
          :to="item.route"
          class="breadcrumb-link"
        >
          {{ item.label }}
        </router-link>
        
        <span v-else class="breadcrumb-current">
          {{ item.label }}
        </span>

        <span v-if="index !== items.length - 1" class="breadcrumb-separator">/</span>
      </li>
    </ol>
  </nav>
</template>

<script setup>
defineProps({
  items: {
    type: Array,
    required: true,
    default: () => []
  }
})
</script>

<style scoped>
.breadcrumb-nav {
  margin-bottom: 1.5rem;
}

.breadcrumb-list {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  list-style: none;
  padding: 0;
  margin: 0;
  font-size: 0.95rem;
}

.breadcrumb-item {
  display: flex;
  align-items: center;
}

.breadcrumb-link {
  color: #3498db;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.breadcrumb-link:hover {
  color: #2980b9;
  text-decoration: underline;
}

.breadcrumb-current {
  color: #6c757d;
  font-weight: 600;
}

.breadcrumb-separator {
  margin: 0 0.5rem;
  color: #adb5bd;
  font-size: 0.9rem;
}
</style>
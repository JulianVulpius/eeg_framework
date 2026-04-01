<template>
  <div class="dashboard-home">
    <div class="header-banner">
      <h1>{{ $t('nav.title') }} - Dashboard</h1>
      <p>{{ $t('dashboard.welcome_text') }}</p>
    </div>

    <div class="dashboard-grid">
      <div 
        class="dashboard-card" 
        v-for="section in menuStructure" 
        :key="section.id"
      >
        <div class="card-header">
          <h2>{{ $t(section.titleKey) }}</h2>
        </div>
        
        <ul class="card-links">
          <li v-for="item in section.items" :key="item.route">
            <router-link :to="item.route" class="dash-link">
              {{ $t(item.labelKey) }}
            </router-link>
          </li>
        </ul>

        <div class="card-footer">
          <p>{{ $t(section.descKey) }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { menuStructure } from '@/config/menuConfig.js'

const { t } = useI18n()
</script>

<style scoped>
.dashboard-home {
  max-width: 1200px;
  margin: 0 auto;
}

.header-banner {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid var(--border-color);
}

.header-banner h1 {
  font-size: 2rem;
  color: var(--text-main);
  margin-bottom: 0.5rem;
}

.header-banner p {
  color: var(--text-muted);
  font-size: 1.1rem;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
}

.dashboard-card {
  background: var(--sidebar-bg);
  border-radius: 8px;
  border: 1px solid var(--border-color);
  box-shadow: 0 4px 6px rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  transition: transform 0.2s, box-shadow 0.2s;
}

.dashboard-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0,0,0,0.08);
}

.card-header {
  background: var(--bg-color);
  padding: 1rem 1.2rem;
  border-bottom: 1px solid var(--border-color);
  border-radius: 8px 8px 0 0;
}

.card-header h2 {
  margin: 0;
  font-size: 1.15rem;
  color: var(--text-main);
}

.card-links {
  list-style: none;
  padding: 1rem 1.2rem;
  margin: 0;
  flex-grow: 1;
}

.card-links li {
  margin-bottom: 0.5rem;
}

.card-links li:last-child {
  margin-bottom: 0;
}

.dash-link {
  text-decoration: none;
  color: var(--primary-hover);
  font-weight: 500;
  transition: color 0.2s;
}

.dash-link:hover {
  color: var(--primary-color);
  text-decoration: underline;
}

.card-footer {
  padding: 1rem 1.2rem;
  background: var(--sidebar-bg);
  border-top: 1px solid var(--border-light);
  border-radius: 0 0 8px 8px;
}

.card-footer p {
  margin: 0;
  font-size: 0.85rem;
  color: var(--text-muted);
  line-height: 1.4;
}
</style>
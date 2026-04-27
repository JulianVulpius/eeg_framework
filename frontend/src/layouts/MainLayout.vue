<template>
  <div class="layout-wrapper">
    
    <aside :class="['sidebar', { 'sidebar-closed': !isSidebarOpen }]">
      <div class="sidebar-header">
        <router-link to="/" class="app-brand-link">
          <h2>{{ $t('nav.title') }}</h2>
        </router-link>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-section action-section">
          <router-link to="/sessions/control" class="btn-play-sync" active-class="btn-active">
            <span class="play-icon">▶</span> Unicorn Play & Sync
          </router-link>

          <router-link to="/sessions/launcher" class="btn-play-sync btn-launcher" active-class="btn-active">
            ▶ {{ $t('nav.session_launcher') }}
          </router-link>
          
          <router-link to="/sessions/heartrate" class="btn-play-sync btn-heartrate" active-class="btn-active">
            ▶ {{ $t('nav.heartrate_live') }}
          </router-link>
          
          <router-link to="/sessions/history" class="btn-play-sync btn-history" active-class="btn-active">
            📊 {{ $t('nav.session_history') }}
          </router-link>
        </div>

        <div class="nav-section" v-for="section in menuStructure" :key="section.id">
          <button class="section-toggle" @click="toggleSection(section.id)">
            {{ $t(section.titleKey) }}
            <span class="chevron">{{ openSections[section.id] ? '▼' : '▶' }}</span>
          </button>
          
          <div class="section-links" v-show="openSections[section.id]">
            <router-link 
              v-for="item in section.items" 
              :key="item.route" 
              :to="item.route" 
              class="nav-link"
              active-class="active-nav-link"
            >
              {{ $t(item.labelKey) }}
            </router-link>
          </div>
        </div>
      </nav>
    </aside>

    <div class="main-content">
      <header class="top-bar">
        <button @click="toggleSidebar" class="hamburger-btn">☰</button>
        <div class="header-actions">
          <div class="mock-auth-switcher">
            <label>{{ $t('views.events.mock_user') }}</label>
            <select :value="activeMockUser" @change="setMockUser($event.target.value)" class="lang-toggle-btn mock-user-select">
              <option v-for="u in mockUsers" :key="u.id" :value="u.id">{{ u.name }}</option>
            </select>
          </div>

          <LanguageSwitcher />
        </div>
      </header>

      <main class="page-container">
        <router-view :key="$route.fullPath" />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { menuStructure } from '@/config/menuConfig.js'
import LanguageSwitcher from '@/components/ui/LanguageSwitcher.vue'

import { useMockAuth } from '@/composables/useMockAuth'
const { activeMockUser, mockUsers, setMockUser } = useMockAuth()

const route = useRoute()
const isSidebarOpen = ref(true)

const initialSections = {}
menuStructure.forEach(sec => initialSections[sec.id] = false)
const openSections = reactive(initialSections)

const toggleSidebar = () => { isSidebarOpen.value = !isSidebarOpen.value }
const toggleSection = (sectionId) => { openSections[sectionId] = !openSections[sectionId] }

const openActiveSection = () => {
  menuStructure.forEach(section => {
    const hasActiveItem = section.items.some(item => route.path.startsWith(item.route))
    if (hasActiveItem) {
      openSections[section.id] = true
    }
  })
}

onMounted(() => {
  openActiveSection()
})

watch(() => route.path, () => {
  openActiveSection()
})
</script>

<style scoped>
.layout-wrapper { display: flex; height: 100vh; width: 100vw; overflow: hidden; }
.sidebar { width: 260px; background-color: var(--sidebar-bg); color: var(--text-dark); border-right: 1px solid var(--border-color); transition: width 0.3s ease, padding 0.3s ease, opacity 0.3s ease; display: flex; flex-direction: column; white-space: nowrap; overflow: hidden; }
.sidebar-closed { width: 0px; border-right: none; opacity: 0; }
.sidebar-header { height: 60px; display: flex; align-items: center; justify-content: center; background-color: #f8f9fa; border-bottom: 1px solid var(--border-color); color: var(--text-dark); flex-shrink: 0; }
.sidebar-header h2 { font-size: 1.2rem; margin: 0; font-weight: 700; }

.app-brand-link { text-decoration: none; color: inherit; cursor: pointer; }
.app-brand-link:hover h2 { color: var(--primary-color); }

.sidebar-nav { flex-grow: 1; padding-top: 10px; overflow-y: auto; overflow-x: hidden; }
.nav-section { margin-bottom: 10px; }
.action-section { padding: 10px 20px; }

.section-toggle { width: 100%; display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: none; border: none; font-size: 0.85rem; font-weight: 700; color: var(--text-main); text-transform: uppercase; cursor: pointer; transition: background-color 0.2s; }
.section-toggle:hover { background-color: #f1f3f5; }
.chevron { font-size: 0.7rem; color: var(--text-muted); }

.nav-link { display: block; padding: 10px 20px 10px 30px; color: var(--text-dark); text-decoration: none; font-size: 0.95rem; transition: background 0.2s, font-weight 0.2s; }
.nav-link:hover { background-color: #f1f3f5; }
.active-nav-link { background-color: #e9ecef; font-weight: 600; border-left: 4px solid var(--primary-color); padding-left: 26px; }

.main-content { flex-grow: 1; display: flex; flex-direction: column; background-color: var(--bg-color); min-width: 0; }
.top-bar { height: 60px; background-color: var(--sidebar-bg); border-bottom: 1px solid var(--border-color); display: flex; align-items: center; justify-content: space-between; padding: 0 20px; }
.hamburger-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: var(--text-dark); }

.header-actions { display: flex; gap: 15px; align-items: center; }
.mock-auth-switcher { display: flex; align-items: center; gap: 8px; font-size: 0.9rem; }
.mock-auth-switcher label { color: var(--text-muted); font-weight: bold; }
.mock-user-select { padding: 4px 8px; }

.page-container { padding: 30px; flex-grow: 1; overflow-y: auto; }

.lang-toggle-btn { background: #f1f3f5; border: 1px solid var(--border-light); padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: 600; color: var(--text-main); transition: background 0.2s; }
.lang-toggle-btn:hover { background: #e9ecef; }

.btn-play-sync { display: flex; align-items: center; justify-content: center; gap: 10px; background: linear-gradient(135deg, var(--success-color), var(--success-dark)); color: white; padding: 12px 20px; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 1.05rem; box-shadow: 0 4px 6px rgba(46, 204, 113, 0.3); transition: all 0.2s ease; border: 1px solid var(--success-dark); }
.btn-play-sync:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(46, 204, 113, 0.4); filter: brightness(0.95); }
.btn-play-sync:active { transform: translateY(0); box-shadow: 0 2px 4px rgba(46, 204, 113, 0.3); }
.btn-active { outline: 2px solid var(--text-main); outline-offset: 2px; }
.play-icon { font-size: 1.2rem; }

.btn-launcher { margin-top: 10px; background: linear-gradient(135deg, var(--primary-color), var(--primary-hover)); border-color: var(--primary-hover); box-shadow: 0 4px 6px rgba(52, 152, 219, 0.3); }
.btn-launcher:hover { background: linear-gradient(135deg, var(--primary-hover), var(--primary-color)); box-shadow: 0 6px 12px rgba(52, 152, 219, 0.4); }

.btn-heartrate { margin-top: 10px; background: linear-gradient(135deg, #e74c3c, #c0392b); border-color: #c0392b; box-shadow: 0 4px 6px rgba(231, 76, 60, 0.3); }
.btn-heartrate:hover { background: linear-gradient(135deg, #c0392b, #e74c3c); box-shadow: 0 6px 12px rgba(231, 76, 60, 0.4); }

.btn-history { margin-top: 10px; background: #f1f3f5; color: var(--text-main); border-color: var(--border-light); box-shadow: none; }
.btn-history:hover { background: #e9ecef; box-shadow: none; border-color: var(--border-color); filter: none; transform: none;}
</style>
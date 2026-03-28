<template>
  <div class="layout-wrapper">
    
    <aside :class="['sidebar', { 'sidebar-closed': !isSidebarOpen }]">
      <div class="sidebar-header">
        <router-link to="/" class="app-brand-link">
          <h2>{{ $t('nav.title') }}</h2>
        </router-link>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-section" style="padding: 10px 20px;">
          <router-link to="/session-control" class="btn-play-sync" active-class="btn-active">
            <span class="play-icon">▶</span> Unicorn Play & Sync
          </router-link>

          <router-link to="/launcher" class="btn-play-sync" active-class="btn-active" style="margin-top: 10px; background: linear-gradient(135deg, #3498db, #2980b9); border-color: #2980b9; box-shadow: 0 4px 6px rgba(52, 152, 219, 0.3);">
            ▶ {{ $t('nav.session_launcher') }}
          </router-link>
          
          <router-link to="/session-history" class="btn-play-sync" active-class="btn-active" style="margin-top: 10px; background: #f1f3f5; color: #333; border-color: #ddd; box-shadow: none;">
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
          <button @click="toggleLanguage" class="lang-toggle-btn">
            {{ locale === 'en' ? '🇩🇪 DE' : '🇬🇧 EN' }}
          </button>
        </div>
      </header>

      <main class="page-container">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { menuStructure } from '@/config/menuConfig.js'

const { locale } = useI18n()
const route = useRoute()
const isSidebarOpen = ref(true)

const initialSections = {}
menuStructure.forEach(sec => initialSections[sec.id] = false)
const openSections = reactive(initialSections)

const toggleSidebar = () => { isSidebarOpen.value = !isSidebarOpen.value }
const toggleSection = (sectionId) => { openSections[sectionId] = !openSections[sectionId] }
const toggleLanguage = () => { locale.value = locale.value === 'en' ? 'de' : 'en' }

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
.sidebar { width: 260px; background-color: #ffffff; color: #000000; border-right: 1px solid #e0e0e0; transition: width 0.3s ease, padding 0.3s ease, opacity 0.3s ease; display: flex; flex-direction: column; white-space: nowrap; overflow: hidden; }
.sidebar-closed { width: 0px; border-right: none; opacity: 0; }
.sidebar-header { height: 60px; display: flex; align-items: center; justify-content: center; background-color: #f8f9fa; border-bottom: 1px solid #e0e0e0; color: #000000; flex-shrink: 0; }
.sidebar-header h2 { font-size: 1.2rem; margin: 0; font-weight: 700; }

.app-brand-link { text-decoration: none; color: inherit; cursor: pointer; }
.app-brand-link:hover h2 { color: #3498db; }

.sidebar-nav { flex-grow: 1; padding-top: 10px; overflow-y: auto; overflow-x: hidden; }
.nav-section { margin-bottom: 10px; }
.section-toggle { width: 100%; display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: none; border: none; font-size: 0.85rem; font-weight: 700; color: #333333; text-transform: uppercase; cursor: pointer; transition: background-color 0.2s; }
.section-toggle:hover { background-color: #f1f3f5; }
.chevron { font-size: 0.7rem; color: #888; }
.nav-link { display: block; padding: 10px 20px 10px 30px; color: #000000; text-decoration: none; font-size: 0.95rem; transition: background 0.2s, font-weight 0.2s; }
.nav-link:hover { background-color: #f1f3f5; }

.active-nav-link { background-color: #e9ecef; font-weight: 600; border-left: 4px solid #3498db; padding-left: 26px; }

.btn-active { outline: 2px solid #2c3e50; outline-offset: 2px; }

.main-content { flex-grow: 1; display: flex; flex-direction: column; background-color: #f4f7f6; min-width: 0; }
.top-bar { height: 60px; background-color: #ffffff; border-bottom: 1px solid #e0e0e0; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; }
.hamburger-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #000000; }
.page-container { padding: 30px; flex-grow: 1; overflow-y: auto; }
.lang-toggle-btn { background: #f1f3f5; border: 1px solid #ddd; padding: 6px 12px; border-radius: 4px; cursor: pointer; font-weight: 600; color: #333; transition: background 0.2s; }
.lang-toggle-btn:hover { background: #e9ecef; }
.btn-play-sync { display: flex; align-items: center; justify-content: center; gap: 10px; background: linear-gradient(135deg, #2ecc71, #27ae60); color: white; padding: 12px 20px; border-radius: 8px; text-decoration: none; font-weight: 700; font-size: 1.05rem; box-shadow: 0 4px 6px rgba(46, 204, 113, 0.3); transition: all 0.2s ease; border: 1px solid #27ae60; }
.btn-play-sync:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(46, 204, 113, 0.4); background: linear-gradient(135deg, #27ae60, #219653); }
.btn-play-sync:active { transform: translateY(0); box-shadow: 0 2px 4px rgba(46, 204, 113, 0.3); }
.play-icon { font-size: 1.2rem; }
</style>
<template>
  <div class="layout-wrapper">
    
    <aside :class="['sidebar', { 'sidebar-closed': !isSidebarOpen }]">
      <div class="sidebar-header">
        <h2>{{ $t('nav.title') }}</h2>
      </div>

      <nav class="sidebar-nav">

      <div class="nav-section" style="padding: 10px 20px;">
          <router-link to="/launcher" class="btn-play-sync" style="margin-bottom: 10px; background: linear-gradient(135deg, #3498db, #2980b9); border-color: #2980b9; box-shadow: 0 4px 6px rgba(52, 152, 219, 0.3);">
            ▶ {{ $t('nav.session_launcher') }}
          </router-link>
          
          <router-link to="/session-history" class="btn-play-sync" style="margin-bottom: 10px; background: #f1f3f5; color: #333; border-color: #ddd; box-shadow: none;">
            📊 {{ $t('nav.session_history') }}
          </router-link>

          <router-link to="/session-control" class="btn-play-sync">
            <span class="play-icon">▶</span> {{ $t('nav.unicorn_sync') }}
          </router-link>
        </div>

        <div class="nav-section">
          <button class="section-toggle" @click="toggleSection('studies')">
            {{ $t('nav.events') }}
            <span class="chevron">{{ openSections.studies ? '▼' : '▶' }}</span>
          </button>
          
          <div class="section-links" v-show="openSections.studies">
            <router-link to="/events" class="nav-link">{{ $t('nav.events') }}</router-link>
            <router-link to="/page-groups" class="nav-link">{{ $t('nav.page_groups') }}</router-link>
            <router-link to="/pages" class="nav-link">{{ $t('nav.pages') }}</router-link>
            <router-link to="/components" class="nav-link">{{ $t('nav.components') }}</router-link>
          </div>
        </div>

        <div class="nav-section">
          <button class="section-toggle" @click="toggleSection('stimuli')">
            {{ $t('nav.stimuli_management') }}
            <span class="chevron">{{ openSections.stimuli ? '▼' : '▶' }}</span>
          </button>
          
          <div class="section-links" v-show="openSections.stimuli">
            <router-link to="/stimuli" class="nav-link">{{ $t('nav.stimuli') }}</router-link>
            <router-link to="/playlists" class="nav-link">{{ $t('nav.playlists') }}</router-link>
          </div>
        </div>

        <div class="nav-section">
          <button class="section-toggle" @click="toggleSection('masterData')">
            {{ $t('nav.master_data') }}
            <span class="chevron">{{ openSections.masterData ? '▼' : '▶' }}</span>
          </button>
          
          <div class="section-links" v-show="openSections.masterData">
            <router-link to="/master-data/subjects" class="nav-link">{{ $t('nav.subjects') }}</router-link>
            <router-link to="/master-data/frequency-bands" class="nav-link">{{ $t('nav.frequency_bands') }}</router-link>
            <router-link to="/master-data/device-models" class="nav-link">{{ $t('nav.device_models') }}</router-link>
            <router-link to="/master-data/manufacturers" class="nav-link">{{ $t('nav.manufacturers') }}</router-link>
            <router-link to="/master-data/eeg-channels" class="nav-link">{{ $t('nav.eeg_channels') }}</router-link>
            <router-link to="/component-types" class="nav-link">{{ $t('nav.component_types') }}</router-link>
            <router-link to="/locations" class="nav-link" active-class="active">{{ $t('nav.locations') }}</router-link>
          </div>
        </div>

        <div class="nav-section">
          <button class="section-toggle" @click="toggleSection('triggers')">
            {{ $t('nav.trigger_engine') }}
            <span class="chevron">{{ openSections.triggers ? '▼' : '▶' }}</span>
          </button>
          
          <div class="section-links" v-show="openSections.triggers">
            <router-link to="/triggers/definitions" class="nav-link">{{ $t('nav.trigger_definitions') }}</router-link>
            <router-link to="/triggers/groups" class="nav-link">{{ $t('nav.trigger_groups') }}</router-link>
            <router-link to="/triggers/pairs" class="nav-link">{{ $t('nav.trigger_pairs') }}</router-link>
          </div>
        </div>
        
        <div class="nav-section">
          <button class="section-toggle" @click="toggleSection('categories')">
            {{ $t('nav.categories') }}
            <span class="chevron">{{ openSections.categories ? '▼' : '▶' }}</span>
          </button>
          
          <div class="section-links" v-show="openSections.categories">
            <router-link to="/category/stimulus-categories" class="nav-link">{{ $t('nav.stimulus_categories') }}</router-link>
            <router-link to="/category/component-categories" class="nav-link">{{ $t('nav.component_categories') }}</router-link>
            <router-link to="/category/page-categories" class="nav-link">{{ $t('nav.page_categories') }}</router-link>
            <router-link to="/category/custom-script-categories" class="nav-link">{{ $t('nav.custom_script_categories') }}</router-link>
            <router-link to="/category/data-process-categories" class="nav-link">{{ $t('nav.data_process_categories') }}</router-link>
            <router-link to="/category/data-display-categories" class="nav-link">{{ $t('nav.data_display_categories') }}</router-link>
            <router-link to="/category/device-model-categories" class="nav-link">{{ $t('nav.device_model_categories') }}</router-link>
            <router-link to="/category/page-group-categories" class="nav-link">{{ $t('nav.page_group_categories') }}</router-link>
            <router-link to="/category/event-categories" class="nav-link">{{ $t('nav.event_categories') }}</router-link>
          </div>
        </div>

        <div class="nav-section">
          <button class="section-toggle" @click="toggleSection('metadata')">
            {{ $t('nav.metadata_engine') }}
            <span class="chevron">{{ openSections.metadata ? '▼' : '▶' }}</span>
          </button>
          
          <div class="section-links" v-show="openSections.metadata">
            <router-link to="/metadata/registry" class="nav-link">{{ $t('nav.registry_setup') }}</router-link>
            <router-link to="/metadata/groups" class="nav-link">{{ $t('nav.metadata_groups') }}</router-link>
            <router-link to="/metadata/definitions" class="nav-link">{{ $t('nav.metadata_definitions') }}</router-link>
            <router-link to="/category/metadata-categories" class="nav-link">{{ $t('nav.metadata_categories') }}</router-link>
            <router-link to="/category/metadata-group-categories" class="nav-link">{{ $t('nav.metadata_group_categories') }}</router-link>
          </div>
        </div>
  
      </nav>
    </aside>

    <div class="main-content">
      
      <header class="top-bar">
        <button @click="toggleSidebar" class="hamburger-btn">
          ☰
        </button>
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
import { ref, reactive } from 'vue'
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

const isSidebarOpen = ref(true)

const openSections = reactive({
  masterData: false,
  categories: false,
  metadata: false,
  triggers: false,
  studies: false
})

const toggleSidebar = () => {
  isSidebarOpen.value = !isSidebarOpen.value
}

const toggleSection = (section) => {
  openSections[section] = !openSections[section]
}

const toggleLanguage = () => {
  locale.value = locale.value === 'en' ? 'de' : 'en'
}
</script>

<style scoped>
/* Keep ALL existing CSS from previous MainLayout.vue here! */
.layout-wrapper { display: flex; height: 100vh; width: 100vw; overflow: hidden; }
.sidebar { width: 260px; background-color: #ffffff; color: #000000; border-right: 1px solid #e0e0e0; transition: width 0.3s ease, padding 0.3s ease, opacity 0.3s ease; display: flex; flex-direction: column; white-space: nowrap; overflow: hidden; }
.sidebar-closed { width: 0px; border-right: none; opacity: 0; }
.sidebar-header { height: 60px; display: flex; align-items: center; justify-content: center; background-color: #f8f9fa; border-bottom: 1px solid #e0e0e0; color: #000000; flex-shrink: 0; }
.sidebar-header h2 { font-size: 1.2rem; margin: 0; font-weight: 700; }
.sidebar-nav { flex-grow: 1; padding-top: 10px; overflow-y: auto; overflow-x: hidden; }
.nav-section { margin-bottom: 10px; }
.section-toggle { width: 100%; display: flex; justify-content: space-between; align-items: center; padding: 12px 20px; background: none; border: none; font-size: 0.85rem; font-weight: 700; color: #333333; text-transform: uppercase; cursor: pointer; transition: background-color 0.2s; }
.section-toggle:hover { background-color: #f1f3f5; }
.chevron { font-size: 0.7rem; color: #888; }
.nav-link { display: block; padding: 10px 20px 10px 30px; color: #000000; text-decoration: none; font-size: 0.95rem; transition: background 0.2s, font-weight 0.2s; }
.nav-link:hover { background-color: #f1f3f5; }
.router-link-active { background-color: #e9ecef; font-weight: 600; border-left: 4px solid #3498db; padding-left: 26px; }
.main-content { flex-grow: 1; display: flex; flex-direction: column; background-color: #f4f7f6; min-width: 0; }
.top-bar { height: 60px; background-color: #ffffff; border-bottom: 1px solid #e0e0e0; display: flex; align-items: center; justify-content: space-between; padding: 0 20px; }
.hamburger-btn { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #000000; }
.page-container { padding: 30px; flex-grow: 1; overflow-y: auto; }

/* New CSS for Language Button */
.lang-toggle-btn {
  background: #f1f3f5;
  border: 1px solid #ddd;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 600;
  color: #333;
  transition: background 0.2s;
}
.lang-toggle-btn:hover {
  background: #e9ecef;
}

.btn-play-sync {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: linear-gradient(135deg, #2ecc71, #27ae60);
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 700;
  font-size: 1.05rem;
  box-shadow: 0 4px 6px rgba(46, 204, 113, 0.3);
  transition: all 0.2s ease;
  border: 1px solid #27ae60;
}

.btn-play-sync:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(46, 204, 113, 0.4);
  background: linear-gradient(135deg, #27ae60, #219653);
}

.btn-play-sync:active {
  transform: translateY(0);
  box-shadow: 0 2px 4px rgba(46, 204, 113, 0.3);
}

.play-icon {
  font-size: 1.2rem;
}
</style>
<template>
  <div class="session-runner">
    
    <div class="runner-header">
      <div class="header-left">
        
        <div v-if="blueprint?.event_logo && !logoError" class="logo-wrapper">
          <img 
            :src="getAbsoluteUrl(blueprint.event_logo)" 
            alt="" 
            @error="logoError = true" 
            class="event-logo-img"
          />
        </div>
        
        <div class="breadcrumb">
          <span class="event-name">{{ blueprint?.event_name || '...' }}</span>
          <span class="separator">/</span>
          <span class="group-name">{{ blueprint?.page_group_name || '...' }}</span>
        </div>
      </div>

      <div v-if="blueprint && !isEmptyBlueprint" class="progress">
        {{ $t('views.runner.page') }} {{ currentPageIndex + 1 }} / {{ blueprint.pages.length }}
      </div>
    </div>

    <div class="runner-content">
      <div v-if="isLoading" class="loading-state">
        {{ $t('common.loading') }}
      </div>

      <template v-else-if="blueprint">
        
        <div v-if="isEmptyBlueprint" class="finished-state card">
          <h2>⚠️ {{ $t('views.runner.empty_blueprint') }}</h2>
          <div style="margin-top: 30px; display: flex; justify-content: center; align-items: center;">
            <router-link to="/sessions/launcher" class="btn-secondary" style="text-decoration: none;">
              &larr; {{ $t('actions.back') }}
            </router-link>
          </div>
        </div>

        <div v-else-if="isFinished" class="finished-state card">
          <h2>🎉 {{ $t('views.runner.finished_title') }}</h2>
          <p>{{ $t('views.runner.finished_desc') }}</p>
          
          <div style="margin-top: 30px; display: flex; gap: 15px; justify-content: center; align-items: center;">
            <button class="btn-secondary" @click="goBackFromFinished" style="margin-right: auto;">
              &larr; {{ $t('actions.back') }}
            </button>

            <router-link :to="{ path: '/sessions/reports/single', query: { sessionId: sessionId } }" class="btn-primary" style="text-decoration: none;">
              📊 {{ $t('views.runner.view_report') }}
            </router-link>
            
            <router-link to="/sessions/history" class="btn-secondary" style="text-decoration: none;">
              {{ $t('views.runner.back_home') }}
            </router-link>
          </div>
        </div>

        <div v-else class="page-container-inner">
          <div 
            v-for="(page, index) in blueprint.pages" 
            :key="page.id" 
            v-show="index === currentPageIndex"
          >
            <div v-for="comp in page.components" :key="comp.id" class="component-wrapper">
              
              <StandardTextBlock 
                v-if="comp.type === 'TEXT_BLOCK'" 
                :ref="el => setComponentRef(el, comp.id)"
                :parameters="comp.parameters" 
              />
              
              <StandardMetadataForm 
                v-else-if="comp.type === 'METADATA_FORM'" 
                :ref="el => setComponentRef(el, comp.id)"
                :parameters="comp.parameters" 
                :sessionId="sessionId"
              />

              <StandardRecordingUpload 
                v-else-if="comp.type === 'RECORDING_UPLOAD'" 
                :ref="el => setComponentRef(el, comp.id)"
                :parameters="comp.parameters" 
                :sessionId="sessionId"
                :eventId="blueprint.event_id"
                :pageGroupId="blueprint.page_group_id"
                :eventGroupId="blueprint.event_group_id"
              />
              
              <div v-else class="unknown-component card">
                ⚠️ {{ $t('views.runner.unknown_component') }}: {{ comp.type }}
              </div>
              
            </div>

            <div v-if="page.components.length === 0" class="empty-page card">
              <p>{{ $t('views.runner.empty_page') }}</p>
            </div>
          </div>
        </div>

      </template>
    </div>

    <div class="unified-bottom-bar" v-if="blueprint && !isEmptyBlueprint && !isFinished">
      <div class="bar-content">
        <button class="btn-secondary" @click="prevPage" :disabled="isProcessingNext">
          &larr; {{ $t('actions.back') }}
        </button>
        
        <button class="btn-primary" @click="handleContinue" :disabled="isProcessingNext">
          <template v-if="isProcessingNext">
            {{ $t('common.saving') }}...
          </template>
          <template v-else-if="currentPageIndex === blueprint.pages.length - 1">
            {{ $t('views.runner.finish') || 'Fertigstellen' }} &rarr;
          </template>
          <template v-else>
            {{ $t('actions.continue') }} &rarr;
          </template>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api'

import StandardTextBlock from '@/components/runner/StandardTextBlock.vue'
import StandardMetadataForm from '@/components/runner/StandardMetadataForm.vue'
import StandardRecordingUpload from '@/components/runner/StandardRecordingUpload.vue'

const route = useRoute()
const router = useRouter()

const sessionId = route.query.sessionId
const scope = route.query.scope || 'ALL'

const blueprint = ref(null)
const isLoading = ref(true)
const isFinished = ref(false)
const isEmptyBlueprint = ref(false)
const currentPageIndex = ref(0)
const isProcessingNext = ref(false)
const componentRefs = ref({})

const logoError = ref(false)

const setComponentRef = (el, compId) => {
  if (el) componentRefs.value[compId] = el
}

const getAbsoluteUrl = (path) => {
  if (!path) return ''
  if (path.startsWith('http')) return path
  const baseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000/api/').replace(/\/api\/?$/, '')
  return baseUrl + path
}

const loadBlueprint = async () => {
  try {
    const response = await api.get(`sessions/${sessionId}/blueprint/?scope=${scope}`)
    blueprint.value = response.data
    
    logoError.value = false
    
    if (blueprint.value.pages.length === 0) {
      isEmptyBlueprint.value = true
    }
  } catch (error) { 
    console.error(error) 
  } finally { 
    isLoading.value = false 
  }
}

const handleContinue = async () => {
  isProcessingNext.value = true
  let allValid = true
  const currentPage = blueprint.value.pages[currentPageIndex.value]

  if (currentPage.components.length === 0) {
    nextPage()
    isProcessingNext.value = false
    return
  }

  for (const comp of currentPage.components) {
    const compInstance = componentRefs.value[comp.id]
    
    if (compInstance && typeof compInstance.submit === 'function') {
      try {
        await compInstance.submit()
      } catch (e) {
        console.warn(`Validation or upload failed for component ${comp.id}:`, e)
        allValid = false
        break 
      }
    }
  }

  if (allValid) {
    nextPage()
  }
  
  isProcessingNext.value = false
}

const nextPage = () => {
  if (currentPageIndex.value < blueprint.value.pages.length - 1) {
    currentPageIndex.value++
    window.scrollTo(0, 0)
  } else {
    isFinished.value = true
  }
}

const prevPage = () => {
  if (currentPageIndex.value > 0) {
    currentPageIndex.value--
    window.scrollTo(0, 0)
  } else {
    router.push('/sessions/launcher')
  }
}

const goBackFromFinished = () => {
  isFinished.value = false
}

onMounted(loadBlueprint)
</script>

<style scoped>
.session-runner { 
  padding-bottom: 80px; 
  position: relative;
  min-height: 100%;
}

.runner-header { 
  display: flex; 
  justify-content: space-between; 
  align-items: center; 
  margin-bottom: 20px;
  padding-bottom: 15px; 
  border-bottom: 2px solid #e0e0e0; 
  
  position: sticky; 
  background-color: var(--bg-color, #f4f6f8); 
  z-index: 50; 
}

.header-left {
  display: flex; 
  align-items: center; 
  gap: 15px;
}

/* =========================================
   LOGO GRÖßE HIER ANPASSEN
   ========================================= */
.logo-wrapper {
  height: 90px; 
  border-right: 2px solid #ecf0f1; 
  padding-right: 15px;
}

.event-logo-img {
  height: 100%; 
  max-width: 350px;
  object-fit: contain;
}
/* ========================================= */

.breadcrumb { font-size: 1.2rem; color: #2c3e50; display: flex; align-items: center;}
.event-name { font-weight: bold; }
.separator { margin: 0 10px; color: #bdc3c7; }
.group-name { color: #7f8c8d; }
.progress { font-weight: bold; color: #3498db; background: #e8f4f8; padding: 5px 12px; border-radius: 20px; font-size: 0.9rem; }

.runner-content { position: relative; z-index: 10; }
.component-wrapper { margin-bottom: 20px; }
.finished-state { text-align: center; padding: 60px 20px; }
.empty-page, .unknown-component { text-align: center; color: #7f8c8d; }

.unified-bottom-bar {
  position: absolute; 
  bottom: 0;
  left: -30px; 
  right: -30px; 
  
  background-color: white;
  border-top: 1px solid #dcdde1;
  box-shadow: 0 -4px 10px rgba(0,0,0,0.05);
  padding: 15px 30px;
  z-index: 100;
}

.bar-content {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.unified-bottom-bar button {
  min-width: 150px;
  font-size: 1.1rem;
  padding: 12px 24px;
}
</style>
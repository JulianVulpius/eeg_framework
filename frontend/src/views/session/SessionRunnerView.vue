<template>
  <div class="session-runner">
    
    <div class="runner-header">
      <div class="breadcrumb">
        <span class="event-name">{{ blueprint?.event_name || '...' }}</span>
        <span class="separator">/</span>
        <span class="group-name">{{ blueprint?.page_group_name || '...' }}</span>
      </div>
      <div v-if="blueprint" class="progress">
        {{ $t('views.runner.page') }} {{ currentPageIndex + 1 }} / {{ blueprint.pages.length }}
      </div>
    </div>

    <div v-if="isLoading" class="loading-state">
      {{ $t('common.loading') }}
    </div>

    <template v-else-if="blueprint">
      
      <div v-show="isFinished" class="finished-state card">
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

      <div v-show="!isFinished" class="page-container">
        <div 
          v-for="(page, index) in blueprint.pages" 
          :key="page.id" 
          v-show="index === currentPageIndex"
        >
          <div v-for="comp in page.components" :key="comp.id" class="component-wrapper">
            
            <StandardTextBlock 
              v-if="comp.type === 'TEXT_BLOCK'" 
              :parameters="comp.parameters" 
              @completed="nextPage" 
              @go-back="prevPage"
            />
            
            <StandardMetadataForm 
              v-else-if="comp.type === 'METADATA_FORM'" 
              :parameters="comp.parameters" 
              :sessionId="sessionId"
              @completed="nextPage" 
              @go-back="prevPage"
            />
            
            <div v-else class="unknown-component card">
              ⚠️ {{ $t('views.runner.unknown_component') }}: {{ comp.type }}
            </div>
            
          </div>

          <div v-if="page.components.length === 0" class="empty-page card">
            <p>{{ $t('views.runner.empty_page') }}</p>
            <button class="btn-secondary" @click="prevPage" style="margin-right: 15px;">{{ $t('actions.back') }}</button>
            <button class="btn-primary" @click="nextPage">{{ $t('actions.continue') }}</button>
          </div>
        </div>
      </div>

    </template>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/services/api'

import StandardTextBlock from '@/components/runner/StandardTextBlock.vue'
import StandardMetadataForm from '@/components/runner/StandardMetadataForm.vue'

const route = useRoute()

const sessionId = route.query.sessionId

const blueprint = ref(null)
const isLoading = ref(true)
const isFinished = ref(false)
const currentPageIndex = ref(0)

const loadBlueprint = async () => {
  try {
    const response = await api.get(`sessions/${sessionId}/blueprint/`)
    blueprint.value = response.data
    if (blueprint.value.pages.length === 0) isFinished.value = true
  } catch (error) { 
    console.error(error) 
  } finally { 
    isLoading.value = false 
  }
}

const nextPage = () => {
  if (currentPageIndex.value < blueprint.value.pages.length - 1) currentPageIndex.value++
  else isFinished.value = true
}

const prevPage = () => {
  if (currentPageIndex.value > 0) currentPageIndex.value--
  else router.push('/sessions/launcher')
}

const goBackFromFinished = () => {
  isFinished.value = false;
}

onMounted(loadBlueprint)
</script>

<style scoped>
.runner-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 30px; padding-bottom: 15px; border-bottom: 2px solid #e0e0e0; }
.breadcrumb { font-size: 1.2rem; color: #2c3e50; }
.event-name { font-weight: bold; }
.separator { margin: 0 10px; color: #bdc3c7; }
.group-name { color: #7f8c8d; }
.progress { font-weight: bold; color: #3498db; background: #e8f4f8; padding: 5px 12px; border-radius: 20px; font-size: 0.9rem; }
.component-wrapper { margin-bottom: 20px; }
.finished-state { text-align: center; padding: 60px 20px; }
.empty-page, .unknown-component { text-align: center; color: #7f8c8d; }
</style>
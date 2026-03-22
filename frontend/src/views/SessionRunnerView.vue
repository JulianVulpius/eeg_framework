<template>
  <div class="session-runner">
    
    <div class="runner-header">
      <div class="breadcrumb">
        <span class="event-name">{{ blueprint?.event_name || '...' }}</span>
        <span v-if="currentGroup" class="separator">/</span>
        <span v-if="currentGroup" class="group-name">{{ currentGroup.name }}</span>
      </div>
      <div v-if="currentGroup" class="progress">
        {{ $t('views.runner.page') }} {{ currentPageIndex + 1 }} / {{ currentGroup.pages.length }}
      </div>
    </div>

    <div v-if="isLoading" class="loading-state">
      {{ $t('common.loading') }}
    </div>

    <div v-else-if="isFinished" class="finished-state card">
      <h2>🎉 {{ $t('views.runner.finished_title') }}</h2>
      <p>{{ $t('views.runner.finished_desc') }}</p>
      
      <div style="margin-top: 30px; display: flex; gap: 15px; justify-content: center;">
        <router-link :to="'/session/report/' + id" class="btn-primary" style="text-decoration: none;">
          📊 {{ $t('views.runner.view_report') }}
        </router-link>
        <router-link to="/dashboard" class="btn-secondary" style="text-decoration: none;">
          {{ $t('views.runner.back_home') }}
        </router-link>
      </div>
    </div>

    <div v-else-if="currentPage" class="page-container">
      <div v-for="comp in currentPage.components" :key="comp.id" class="component-wrapper">

        <StandardTextBlock 
          v-if="comp.type === 'TEXT_BLOCK'" 
          :parameters="comp.parameters" 
          @completed="nextPage" 
          @go-back="prevPage"
        />
        <StandardMetadataForm 
          v-else-if="comp.type === 'METADATA_FORM'" 
          :parameters="comp.parameters" 
          :sessionId="id"
          @completed="nextPage" 
          @go-back="prevPage"
        />
        
        <div v-else class="unknown-component card">
          ⚠️ {{ $t('views.runner.unknown_component') }}: {{ comp.type }}
        </div>
        
      </div>

      <div v-if="currentPage.components.length === 0" class="empty-page card">
        <p>{{ $t('views.runner.empty_page') }}</p>
        <button class="btn-secondary" @click="nextPage">{{ $t('actions.continue') }}</button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api'

import StandardTextBlock from '@/components/runner/StandardTextBlock.vue'
import StandardMetadataForm from '@/components/runner/StandardMetadataForm.vue'

const props = defineProps({ id: { type: [String, Number], required: true } })
const router = useRouter()

const blueprint = ref(null)
const isLoading = ref(true)
const isFinished = ref(false)

const currentGroupIndex = ref(0)
const currentPageIndex = ref(0)

const currentGroup = computed(() => {
  if (!blueprint.value || !blueprint.value.page_groups) return null
  return blueprint.value.page_groups[currentGroupIndex.value] || null
})

const currentPage = computed(() => {
  if (!currentGroup.value) return null
  return currentGroup.value.pages[currentPageIndex.value] || null
})

const loadBlueprint = async () => {
  try {
    const response = await api.get(`sessions/${props.id}/blueprint/`)
    blueprint.value = response.data
    
    if (blueprint.value.page_groups.length === 0) {
      isFinished.value = true
    }
  } catch (error) {
    console.error(error)
  } finally {
    isLoading.value = false
  }
}

const nextPage = () => {
  if (!currentGroup.value) return

  if (currentPageIndex.value < currentGroup.value.pages.length - 1) {
    currentPageIndex.value++
  } else {
    if (currentGroupIndex.value < blueprint.value.page_groups.length - 1) {
      currentGroupIndex.value++
      currentPageIndex.value = 0
    } else {
      isFinished.value = true
    }
  }
}

const prevPage = () => {
  if (!currentGroup.value) return

  if (currentPageIndex.value > 0) {
    currentPageIndex.value--
  } else {
    if (currentGroupIndex.value > 0) {
      currentGroupIndex.value--
      currentPageIndex.value = blueprint.value.page_groups[currentGroupIndex.value].pages.length - 1
    } else {
      router.push('/launcher')
    }
  }
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
.card { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
.finished-state { text-align: center; padding: 60px 20px; }
.empty-page, .unknown-component { text-align: center; color: #7f8c8d; }
</style>
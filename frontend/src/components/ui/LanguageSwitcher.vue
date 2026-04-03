<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { supportedLanguages } from '@/config/languageConfig';
import { loadLocaleMessages } from '@/i18n';

const { locale } = useI18n();
const isOpen = ref(false);
const dropdownRef = ref(null);

const isToggleMode = computed(() => supportedLanguages.length === 2);

const otherLanguage = computed(() => {
  return supportedLanguages.find(lang => lang.code !== locale.value) || supportedLanguages[1];
});

const currentLanguage = computed(() => {
  return supportedLanguages.find(lang => lang.code === locale.value) || supportedLanguages[0];
});

const switchLanguage = async (newLocaleCode) => {
  if (locale.value === newLocaleCode) {
    isOpen.value = false;
    return;
  }
  
  await loadLocaleMessages(newLocaleCode);
  isOpen.value = false;
};

const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isOpen.value = false;
  }
};

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<template>
  <div class="language-switcher" ref="dropdownRef">
    
    <button 
      v-if="isToggleMode" 
      @click="switchLanguage(otherLanguage.code)"
      class="switcher-btn toggle-btn"
      :title="`Switch to ${otherLanguage.name}`"
    >
      <span class="emoji">{{ otherLanguage.emoji }}</span>
      <span class="lang-name">{{ otherLanguage.name }}</span>
    </button>

    <div v-else class="dropdown-container">
      <button 
        @click="isOpen = !isOpen" 
        class="switcher-btn dropdown-trigger"
        :class="{ 'is-open': isOpen }"
      >
        <span class="emoji">{{ currentLanguage.emoji }}</span>
        <span class="lang-name">{{ currentLanguage.name }}</span>
        <svg class="chevron" :class="{ 'rotate': isOpen }" viewBox="0 0 24 24" width="16" height="16">
          <path fill="currentColor" d="M7 10l5 5 5-5z"/>
        </svg>
      </button>

      <transition name="fade-slide">
        <ul v-if="isOpen" class="dropdown-menu">
          <li 
            v-for="lang in supportedLanguages" 
            :key="lang.code"
            @click="switchLanguage(lang.code)"
            class="dropdown-item"
            :class="{ 'is-active': lang.code === locale }"
          >
            <span class="emoji">{{ lang.emoji }}</span>
            <span class="lang-name">{{ lang.name }}</span>
            <svg v-if="lang.code === locale" class="check-icon" viewBox="0 0 24 24" width="14" height="14">
              <path fill="currentColor" d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
            </svg>
          </li>
        </ul>
      </transition>
    </div>

  </div>
</template>

<style scoped>
.language-switcher {
  position: relative;
  display: inline-block;
  font-family: inherit;
}

.switcher-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  background-color: transparent;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 14px;
  color: #334155;
  cursor: pointer;
  transition: all 0.2s ease;
}

.switcher-btn:hover, .switcher-btn.is-open {
  background-color: #f8fafc;
  border-color: #cbd5e1;
}

.emoji {
  font-size: 16px;
}

.lang-name {
  font-weight: 500;
}

.chevron {
  transition: transform 0.2s ease;
}
.chevron.rotate {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 4px);
  right: 0;
  background-color: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  min-width: 140px;
  padding: 4px 0;
  margin: 0;
  list-style: none;
  z-index: 50;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  cursor: pointer;
  color: #475569;
  font-size: 14px;
  transition: background-color 0.15s ease;
}

.dropdown-item:hover {
  background-color: #f1f5f9;
}

.dropdown-item.is-active {
  font-weight: 600;
  color: #0f172a;
  background-color: #f8fafc;
}

.check-icon {
  margin-left: auto;
  color: #10b981;
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: opacity 0.2s, transform 0.2s;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-5px);
}
</style>
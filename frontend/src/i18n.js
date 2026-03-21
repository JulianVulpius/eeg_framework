import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import de from './locales/de.json'

// Create i18n instance with options
const i18n = createI18n({
  locale: 'en', // Set default locale to English
  fallbackLocale: 'en', // Fallback if a translation is missing
  messages: {
    en,
    de
  },
  legacy: false // Required for Vue 3 Composition API
})

export default i18n
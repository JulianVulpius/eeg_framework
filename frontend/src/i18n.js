import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import de from './locales/de.json'

// i18n instance with options
const i18n = createI18n({
  locale: 'en', // default 
  fallbackLocale: 'en', 
  messages: {
    en,
    de
  },
  legacy: false
})

export default i18n
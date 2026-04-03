import { createI18n } from 'vue-i18n';
import { defaultLanguage } from './config/languageConfig';

const i18n = createI18n({
  legacy: false,
  locale: defaultLanguage,
  fallbackLocale: 'en',
  messages: {}
});

export async function loadLocaleMessages(locale) {
  try {
    const messages = await import(`./locales/${locale}.json`);
    
    i18n.global.setLocaleMessage(locale, messages.default);
    i18n.global.locale.value = locale;
    
    document.querySelector('html').setAttribute('lang', locale);
    localStorage.setItem('user-locale', locale);
  } catch (error) {
    console.error(`${locale} load error.`, error);
  }
}

export default i18n;
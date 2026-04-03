import './assets/styles/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'

import i18n, { loadLocaleMessages } from './i18n'; 
import { defaultLanguage } from './config/languageConfig';

const app = createApp(App);

app.use(createPinia());
app.use(router);
app.use(i18n);

const initialLocale = localStorage.getItem('user-locale') || defaultLanguage;

loadLocaleMessages(initialLocale).then(() => {
  app.mount('#app');
}).catch(err => {
  console.error("Kritischer Fehler beim Laden der Initialsprache:", err);
  app.mount('#app'); 
});
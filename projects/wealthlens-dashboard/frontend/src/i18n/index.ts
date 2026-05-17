import { createI18n } from 'vue-i18n'
import { getStorageItem } from '@/utils/browserStorage'
import en from './locales/en.json'

const LOCALE_STORAGE_KEY = 'wl-locale'

const savedLocale = getStorageItem(LOCALE_STORAGE_KEY) || 'en'

const i18n = createI18n({
  locale: savedLocale,
  fallbackLocale: 'en',
  legacy: false,
  globalInjection: true,
  messages: {
    en,
  },
})

export { LOCALE_STORAGE_KEY }
export default i18n

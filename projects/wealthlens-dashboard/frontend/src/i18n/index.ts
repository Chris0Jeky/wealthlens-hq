import { createI18n } from 'vue-i18n'
import en from './locales/en.json'

/**
 * Vue I18n instance configured for the WealthLens dashboard.
 *
 * - Composition API mode (legacy: false)
 * - Global injection enabled ($t available in all templates)
 * - English as default and fallback locale
 * - Additional locales can be added to ./locales/ and registered here
 */
const i18n = createI18n({
  locale: 'en',
  fallbackLocale: 'en',
  legacy: false,
  globalInjection: true,
  messages: {
    en,
  },
})

export default i18n

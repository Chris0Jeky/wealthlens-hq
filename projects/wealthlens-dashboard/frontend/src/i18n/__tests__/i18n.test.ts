import { describe, it, expect } from 'vitest'
import { createI18n } from 'vue-i18n'
import en from '../locales/en.json'
import i18n from '../index'

describe('i18n configuration', () => {
  it('creates an i18n instance with English as default locale', () => {
    expect(i18n.global.locale.value).toBe('en')
  })

  it('uses English as the fallback locale', () => {
    expect(i18n.global.fallbackLocale.value).toBe('en')
  })

  it('loads the English locale messages', () => {
    expect(i18n.global.t('nav.home')).toBe('Front page')
    expect(i18n.global.t('nav.data')).toBe('The data')
    expect(i18n.global.t('nav.methodology')).toBe('Methodology')
  })

  it('resolves nested keys correctly', () => {
    expect(i18n.global.t('common.loading')).toBe('Loading...')
    expect(i18n.global.t('common.error')).toBe('Something went wrong')
    expect(i18n.global.t('calculator.title')).toBe('Where Do You Fit in UK Wealth?')
  })

  it('supports named interpolation in messages', () => {
    const result = i18n.global.t('footer.copyright', { year: 2026 })
    expect(result).toBe('© 2026 WealthLens UK')
  })

  it('falls back to English for missing keys in a non-existent locale', () => {
    // Create a separate instance to test fallback behavior
    const testI18n = createI18n({
      locale: 'cy',
      fallbackLocale: 'en',
      legacy: false,
      messages: { en },
    })

    // When locale is 'cy' but no Welsh messages exist, falls back to English
    expect(testI18n.global.t('nav.home')).toBe('Front page')
  })

  it('has all expected top-level namespaces', () => {
    const messages = en as Record<string, unknown>
    expect(messages).toHaveProperty('nav')
    expect(messages).toHaveProperty('home')
    expect(messages).toHaveProperty('common')
    expect(messages).toHaveProperty('calculator')
    expect(messages).toHaveProperty('footer')
  })
})

import { describe, it, expect, beforeEach } from 'vitest'
import { ref } from 'vue'
import { useDocumentTitle } from '@/composables/useDocumentTitle'

describe('useDocumentTitle', () => {
  beforeEach(() => {
    document.title = ''
  })

  it('sets base title when ref is undefined', () => {
    const title = ref<string | undefined>(undefined)
    useDocumentTitle(title)
    expect(document.title).toBe('WealthLens UK')
  })

  it('sets combined title when ref has a value', () => {
    const title = ref<string | undefined>('Wealth Shares')
    useDocumentTitle(title)
    expect(document.title).toBe('Wealth Shares — WealthLens UK')
  })

  it('updates title reactively', async () => {
    const title = ref<string | undefined>('Initial')
    useDocumentTitle(title)
    expect(document.title).toBe('Initial — WealthLens UK')

    title.value = 'Updated'
    await Promise.resolve()
    expect(document.title).toBe('Updated — WealthLens UK')
  })

  it('reverts to base title when cleared', async () => {
    const title = ref<string | undefined>('Page')
    useDocumentTitle(title)
    expect(document.title).toContain('Page')

    title.value = undefined
    await Promise.resolve()
    expect(document.title).toBe('WealthLens UK')
  })
})

import { describe, it, expect, beforeEach } from 'vitest'
import { nextTick } from 'vue'
import { useLocalStorage } from '@/composables/useLocalStorage'

describe('useLocalStorage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('returns default value when key is not stored', () => {
    const val = useLocalStorage('missing', 42)
    expect(val.value).toBe(42)
  })

  it('reads existing stored value', () => {
    localStorage.setItem('test-key', JSON.stringify('hello'))
    const val = useLocalStorage('test-key', 'default')
    expect(val.value).toBe('hello')
  })

  it('persists changes to localStorage', async () => {
    const val = useLocalStorage('persist', 0)
    val.value = 99
    await nextTick()
    expect(JSON.parse(localStorage.getItem('persist')!)).toBe(99)
  })

  it('handles object values', async () => {
    const val = useLocalStorage('obj', { count: 0 })
    val.value = { count: 5 }
    await nextTick()
    expect(JSON.parse(localStorage.getItem('obj')!)).toEqual({ count: 5 })
  })

  it('handles array values', async () => {
    const val = useLocalStorage<string[]>('arr', [])
    val.value = ['a', 'b']
    await nextTick()
    expect(JSON.parse(localStorage.getItem('arr')!)).toEqual(['a', 'b'])
  })

  it('falls back to default if stored JSON is invalid', () => {
    localStorage.setItem('bad', 'not-json{{{')
    const val = useLocalStorage('bad', 'fallback')
    expect(val.value).toBe('fallback')
  })

  it('handles boolean values', async () => {
    const val = useLocalStorage('flag', false)
    val.value = true
    await nextTick()
    expect(JSON.parse(localStorage.getItem('flag')!)).toBe(true)
  })
})

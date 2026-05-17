import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useTheme, _resetForTesting } from '@/composables/useTheme'

describe('useTheme', () => {
  beforeEach(() => {
    _resetForTesting()
    localStorage.clear()

    window.matchMedia = vi.fn().mockImplementation(() => ({
      matches: false,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }))
  })

  it('defaults to light theme', () => {
    const { theme } = useTheme()
    expect(theme.value).toBe('light')
  })

  it('reads from localStorage if set', () => {
    localStorage.setItem('wl-theme', 'dark')
    _resetForTesting(true)

    const { theme } = useTheme()
    expect(theme.value).toBe('dark')
  })

  it('respects prefers-color-scheme when no localStorage value', () => {
    window.matchMedia = vi.fn().mockImplementation(() => ({
      matches: true,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }))

    _resetForTesting(true)

    const { theme } = useTheme()
    expect(theme.value).toBe('dark')
  })

  it('toggleTheme switches and persists', () => {
    const { theme, toggleTheme } = useTheme()
    expect(theme.value).toBe('light')

    toggleTheme()
    expect(theme.value).toBe('dark')
    expect(localStorage.getItem('wl-theme')).toBe('dark')

    toggleTheme()
    expect(theme.value).toBe('light')
    expect(localStorage.getItem('wl-theme')).toBe('light')
  })

  it('sets data-theme attribute on documentElement', () => {
    const { toggleTheme } = useTheme()
    expect(document.documentElement.getAttribute('data-theme')).toBe('light')

    toggleTheme()
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark')

    toggleTheme()
    expect(document.documentElement.getAttribute('data-theme')).toBe('light')
  })
})

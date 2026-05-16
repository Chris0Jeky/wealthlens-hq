import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useDarkMode } from '../useDarkMode'

describe('useDarkMode', () => {
  let matchMediaListeners: Array<(e: MediaQueryListEvent) => void>

  beforeEach(() => {
    // Reset DOM state
    document.documentElement.classList.remove('dark')
    localStorage.clear()

    matchMediaListeners = []

    // Mock matchMedia
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: false,
        media: query,
        addEventListener: vi.fn((event: string, handler: (e: MediaQueryListEvent) => void) => {
          if (event === 'change') matchMediaListeners.push(handler)
        }),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    })
  })

  it('defaults to light mode when no preference is set', () => {
    const { isDark } = useDarkMode()

    expect(isDark.value).toBe(false)
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('toggle switches isDark and adds class to documentElement', () => {
    const { isDark, toggle } = useDarkMode()

    expect(isDark.value).toBe(false)
    expect(document.documentElement.classList.contains('dark')).toBe(false)

    toggle()

    expect(isDark.value).toBe(true)
    expect(document.documentElement.classList.contains('dark')).toBe(true)

    toggle()

    expect(isDark.value).toBe(false)
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('reads from localStorage on init', () => {
    localStorage.setItem('theme', 'dark')

    const { isDark } = useDarkMode()

    expect(isDark.value).toBe(true)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('persists choice to localStorage on toggle', () => {
    const { toggle } = useDarkMode()

    toggle()
    expect(localStorage.getItem('theme')).toBe('dark')

    toggle()
    expect(localStorage.getItem('theme')).toBe('light')
  })

  it('respects system preference when no localStorage value', () => {
    // Mock system preference as dark
    Object.defineProperty(window, 'matchMedia', {
      writable: true,
      value: vi.fn().mockImplementation((query: string) => ({
        matches: true,
        media: query,
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      })),
    })

    const { isDark } = useDarkMode()

    expect(isDark.value).toBe(true)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })
})

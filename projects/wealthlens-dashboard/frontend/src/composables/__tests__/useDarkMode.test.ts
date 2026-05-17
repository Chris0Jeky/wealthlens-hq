import { describe, it, expect, beforeEach, vi } from 'vitest'

// The composable uses module-level singleton state.  We use vi.resetModules()
// + dynamic import so each test gets a fresh module instance.

function mockMatchMedia(prefersDark: boolean) {
  const listeners: Array<(e: MediaQueryListEvent) => void> = []
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query: string) => ({
      matches: prefersDark,
      media: query,
      addEventListener: vi.fn((_event: string, handler: (e: MediaQueryListEvent) => void) => {
        listeners.push(handler)
      }),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  })
  return listeners
}

describe('useDarkMode', () => {
  const localStorageDescriptor = Object.getOwnPropertyDescriptor(window, 'localStorage')

  beforeEach(() => {
    if (localStorageDescriptor) {
      Object.defineProperty(window, 'localStorage', localStorageDescriptor)
    }
    vi.resetModules()
    document.documentElement.classList.remove('dark')
    localStorage.clear()
  })

  it('defaults to light mode when no preference is set', async () => {
    mockMatchMedia(false)
    const { useDarkMode } = await import('../useDarkMode')
    const { isDark } = useDarkMode()

    expect(isDark.value).toBe(false)
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('toggle switches isDark and adds class to documentElement', async () => {
    mockMatchMedia(false)
    const { useDarkMode } = await import('../useDarkMode')
    const { isDark, toggle } = useDarkMode()

    expect(isDark.value).toBe(false)

    toggle()
    expect(isDark.value).toBe(true)
    expect(document.documentElement.classList.contains('dark')).toBe(true)

    toggle()
    expect(isDark.value).toBe(false)
    expect(document.documentElement.classList.contains('dark')).toBe(false)
  })

  it('reads from localStorage on init', async () => {
    mockMatchMedia(false)
    localStorage.setItem('theme', 'dark')

    const { useDarkMode } = await import('../useDarkMode')
    const { isDark } = useDarkMode()

    expect(isDark.value).toBe(true)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('persists choice to localStorage on toggle', async () => {
    mockMatchMedia(false)
    const { useDarkMode } = await import('../useDarkMode')
    const { toggle } = useDarkMode()

    toggle()
    expect(localStorage.getItem('theme')).toBe('dark')

    toggle()
    expect(localStorage.getItem('theme')).toBe('light')
  })

  it('respects system preference when no localStorage value', async () => {
    mockMatchMedia(true)

    const { useDarkMode } = await import('../useDarkMode')
    const { isDark } = useDarkMode()

    expect(isDark.value).toBe(true)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('multiple calls return the same singleton state', async () => {
    mockMatchMedia(false)
    const { useDarkMode } = await import('../useDarkMode')

    const a = useDarkMode()
    const b = useDarkMode()

    expect(a.isDark).toBe(b.isDark)
    a.toggle()
    expect(b.isDark.value).toBe(true)
  })

  it('falls back to system preference when localStorage reads fail', async () => {
    mockMatchMedia(true)
    Object.defineProperty(window, 'localStorage', {
      configurable: true,
      value: {
        getItem: vi.fn(() => {
          throw new DOMException('Storage blocked', 'SecurityError')
        }),
        setItem: vi.fn(),
        removeItem: vi.fn(),
        clear: vi.fn(),
      },
    })

    const { useDarkMode } = await import('../useDarkMode')
    const { isDark } = useDarkMode()

    expect(isDark.value).toBe(true)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('toggles theme when localStorage writes fail', async () => {
    mockMatchMedia(false)
    Object.defineProperty(window, 'localStorage', {
      configurable: true,
      value: {
        getItem: vi.fn(() => null),
        setItem: vi.fn(() => {
          throw new DOMException('Quota exceeded', 'QuotaExceededError')
        }),
        removeItem: vi.fn(),
        clear: vi.fn(),
      },
    })

    const { useDarkMode } = await import('../useDarkMode')
    const { isDark, toggle } = useDarkMode()

    expect(() => toggle()).not.toThrow()
    expect(isDark.value).toBe(true)
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })
})

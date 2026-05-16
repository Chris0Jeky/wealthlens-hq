import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { useMediaQuery } from '@/composables/useMediaQuery'

let listeners: Map<string, ((event: MediaQueryListEvent) => void)[]>
let mockMatches: boolean

function withSetup<T>(composable: () => T): { result: T; unmount: () => void } {
  let result!: T
  const Wrapper = defineComponent({
    setup() {
      result = composable()
      return {}
    },
    template: '<div />',
  })
  const wrapper = mount(Wrapper)
  return { result, unmount: () => wrapper.unmount() }
}

describe('useMediaQuery', () => {
  beforeEach(() => {
    listeners = new Map()
    mockMatches = false

    vi.stubGlobal('matchMedia', (query: string) => ({
      matches: mockMatches,
      media: query,
      addEventListener: (event: string, handler: (e: MediaQueryListEvent) => void) => {
        if (!listeners.has(event)) listeners.set(event, [])
        listeners.get(event)!.push(handler)
      },
      removeEventListener: (event: string, handler: (e: MediaQueryListEvent) => void) => {
        const list = listeners.get(event)
        if (list) {
          const idx = list.indexOf(handler)
          if (idx >= 0) list.splice(idx, 1)
        }
      },
    }))
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  function fireChange(matches: boolean) {
    const handlers = listeners.get('change') ?? []
    for (const handler of handlers) {
      handler({ matches } as MediaQueryListEvent)
    }
  }

  it('returns initial match state', () => {
    mockMatches = true
    const { result } = withSetup(() => useMediaQuery('(min-width: 768px)'))
    expect(result.value).toBe(true)
  })

  it('returns false when query does not match', () => {
    mockMatches = false
    const { result } = withSetup(() => useMediaQuery('(min-width: 1024px)'))
    expect(result.value).toBe(false)
  })

  it('updates when media query changes', () => {
    mockMatches = false
    const { result } = withSetup(() => useMediaQuery('(min-width: 768px)'))
    expect(result.value).toBe(false)
    fireChange(true)
    expect(result.value).toBe(true)
  })

  it('removes listener on unmount', () => {
    const { unmount } = withSetup(() => useMediaQuery('(min-width: 768px)'))
    expect(listeners.get('change')?.length).toBe(1)
    unmount()
    expect(listeners.get('change')?.length).toBe(0)
  })

  it('handles multiple queries independently', () => {
    mockMatches = true
    const { result: mobile } = withSetup(() => useMediaQuery('(max-width: 640px)'))
    mockMatches = false
    const { result: desktop } = withSetup(() => useMediaQuery('(min-width: 1024px)'))
    expect(mobile.value).toBe(true)
    expect(desktop.value).toBe(false)
  })

  it('returns false when matchMedia is unavailable', () => {
    vi.stubGlobal('matchMedia', undefined)
    const { result } = withSetup(() => useMediaQuery('(min-width: 768px)'))
    expect(result.value).toBe(false)
  })
})

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent, h } from 'vue'
import { useColorScheme } from '@/composables/useColorScheme'

function createTestComponent() {
  return defineComponent({
    setup() {
      const { scheme } = useColorScheme()
      return { scheme }
    },
    render() {
      return h('div', this.scheme)
    },
  })
}

describe('useColorScheme', () => {
  let listeners: Array<() => void> = []
  let matches = false

  function setupMatchMedia() {
    window.matchMedia = vi.fn().mockImplementation(() => ({
      get matches() { return matches },
      addEventListener: (_: string, cb: () => void) => { listeners.push(cb) },
      removeEventListener: vi.fn(),
      media: '(prefers-color-scheme: dark)',
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    }))
  }

  beforeEach(() => {
    listeners = []
    matches = false
    setupMatchMedia()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('defaults to light when media query does not match', () => {
    matches = false
    const wrapper = mount(createTestComponent())
    expect(wrapper.text()).toBe('light')
  })

  it('detects dark mode from media query', async () => {
    matches = true
    setupMatchMedia()
    const wrapper = mount(createTestComponent())
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toBe('dark')
  })

  it('registers a change listener', () => {
    mount(createTestComponent())
    expect(listeners).toHaveLength(1)
  })
})

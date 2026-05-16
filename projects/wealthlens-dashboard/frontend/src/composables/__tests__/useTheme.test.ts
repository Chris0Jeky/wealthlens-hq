import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent, nextTick } from 'vue'
import { useTheme, _resetForTesting } from '@/composables/useTheme'

function mountWithTheme() {
  const Comp = defineComponent({
    setup() {
      return useTheme()
    },
    template: '<div />',
  })
  return mount(Comp)
}

describe('useTheme', () => {
  let listeners: Array<() => void>
  let matchesDark: boolean

  beforeEach(() => {
    _resetForTesting()
    listeners = []
    matchesDark = false
    localStorage.clear()
    document.documentElement.classList.remove('dark')

    window.matchMedia = vi.fn().mockImplementation(() => ({
      get matches() {
        return matchesDark
      },
      addEventListener: (_: string, cb: () => void) => listeners.push(cb),
      removeEventListener: vi.fn(),
    }))
  })

  it('defaults to system preference (light)', () => {
    const wrapper = mountWithTheme()
    expect(wrapper.vm.preference).toBe('system')
    expect(wrapper.vm.resolved).toBe('light')
  })

  it('resolves dark when system is dark', () => {
    matchesDark = true
    const wrapper = mountWithTheme()
    expect(wrapper.vm.resolved).toBe('dark')
  })

  it('applies dark class to documentElement', () => {
    matchesDark = true
    mountWithTheme()
    expect(document.documentElement.classList.contains('dark')).toBe(true)
  })

  it('persists user preference to localStorage', () => {
    const wrapper = mountWithTheme()
    wrapper.vm.setPreference('dark')
    expect(localStorage.getItem('wealthlens-theme')).toBe('dark')
  })

  it('removes localStorage key when set to system', () => {
    localStorage.setItem('wealthlens-theme', 'dark')
    const wrapper = mountWithTheme()
    wrapper.vm.setPreference('system')
    expect(localStorage.getItem('wealthlens-theme')).toBeNull()
  })

  it('reads stored preference on mount', () => {
    localStorage.setItem('wealthlens-theme', 'dark')
    const wrapper = mountWithTheme()
    expect(wrapper.vm.preference).toBe('dark')
    expect(wrapper.vm.resolved).toBe('dark')
  })

  it('reacts to system media change', async () => {
    const wrapper = mountWithTheme()
    expect(wrapper.vm.resolved).toBe('light')

    matchesDark = true
    listeners.forEach((cb) => cb())
    await nextTick()
    expect(wrapper.vm.resolved).toBe('dark')
  })
})

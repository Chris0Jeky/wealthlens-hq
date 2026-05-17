import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { _resetForTesting } from '@/composables/useTheme'
import ThemeToggle from '@/components/ThemeToggle.vue'

describe('ThemeToggle', () => {
  beforeEach(() => {
    _resetForTesting()
    localStorage.clear()

    window.matchMedia = vi.fn().mockImplementation(() => ({
      matches: false,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }))
  })

  it('renders a toggle button', () => {
    const wrapper = mount(ThemeToggle)
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('clicking toggles theme', async () => {
    const wrapper = mount(ThemeToggle)
    const btn = wrapper.find('button')

    expect(btn.attributes('aria-pressed')).toBe('false')
    await btn.trigger('click')
    expect(btn.attributes('aria-pressed')).toBe('true')
    await btn.trigger('click')
    expect(btn.attributes('aria-pressed')).toBe('false')
  })

  it('shows correct icon for each state', async () => {
    const wrapper = mount(ThemeToggle)
    const btn = wrapper.find('button')

    // Light mode shows moon (&#9789; = U+2635 crescent moon)
    expect(wrapper.text()).toContain('☽')

    await btn.trigger('click')
    // Dark mode shows sun (&#9728; = U+2600 sun)
    expect(wrapper.text()).toContain('☀')
  })

  it('has correct aria-label and aria-pressed', () => {
    const wrapper = mount(ThemeToggle)
    const btn = wrapper.find('button')

    expect(btn.attributes('aria-label')).toBe('Toggle dark mode')
    expect(btn.attributes('aria-pressed')).toBe('false')
  })
})

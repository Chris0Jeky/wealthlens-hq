import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { _resetForTesting } from '@/composables/useTheme'
import ThemeToggle from '@/components/ThemeToggle.vue'

describe('ThemeToggle', () => {
  beforeEach(() => {
    _resetForTesting()
    localStorage.clear()
    document.documentElement.classList.remove('dark')

    window.matchMedia = vi.fn().mockImplementation(() => ({
      matches: false,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
    }))
  })

  it('renders a button', () => {
    const wrapper = mount(ThemeToggle)
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('has accessible aria-label with current and next theme', () => {
    const wrapper = mount(ThemeToggle)
    const btn = wrapper.find('button')
    const label = btn.attributes('aria-label') ?? ''
    expect(label).toContain('current: System')
    expect(label).toContain('Switch theme to')
  })

  it('cycles through preferences on click', async () => {
    const wrapper = mount(ThemeToggle)
    const btn = wrapper.find('button')

    expect(btn.attributes('aria-label')).toContain('current: System')
    await btn.trigger('click')
    expect(btn.attributes('aria-label')).toContain('current: Light')
    await btn.trigger('click')
    expect(btn.attributes('aria-label')).toContain('current: Dark')
    await btn.trigger('click')
    expect(btn.attributes('aria-label')).toContain('current: System')
  })

  it('has type="button" to prevent form submission', () => {
    const wrapper = mount(ThemeToggle)
    expect(wrapper.find('button').attributes('type')).toBe('button')
  })
})

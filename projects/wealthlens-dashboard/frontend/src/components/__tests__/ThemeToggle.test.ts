import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import ThemeToggle from '@/components/ThemeToggle.vue'

describe('ThemeToggle', () => {
  beforeEach(() => {
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

  it('has accessible aria-label', () => {
    const wrapper = mount(ThemeToggle)
    const btn = wrapper.find('button')
    expect(btn.attributes('aria-label')).toContain('Theme:')
  })

  it('cycles through preferences on click', async () => {
    const wrapper = mount(ThemeToggle)
    const btn = wrapper.find('button')

    expect(btn.attributes('aria-label')).toContain('system')
    await btn.trigger('click')
    expect(btn.attributes('aria-label')).toContain('light')
    await btn.trigger('click')
    expect(btn.attributes('aria-label')).toContain('dark')
    await btn.trigger('click')
    expect(btn.attributes('aria-label')).toContain('system')
  })

  it('has type="button" to prevent form submission', () => {
    const wrapper = mount(ThemeToggle)
    expect(wrapper.find('button').attributes('type')).toBe('button')
  })
})

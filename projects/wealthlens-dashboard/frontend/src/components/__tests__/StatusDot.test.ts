import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatusDot from '@/components/StatusDot.vue'

describe('StatusDot', () => {
  it('renders the dot element', () => {
    const wrapper = mount(StatusDot, { props: { status: 'online' } })
    const dot = wrapper.find('[aria-hidden="true"]')
    expect(dot.exists()).toBe(true)
  })

  it('applies the correct color class for each status', () => {
    const expected: Record<string, string> = {
      online: 'bg-green-500',
      offline: 'bg-red-500',
      warning: 'bg-yellow-500',
      idle: 'bg-gray-400',
    }

    for (const [status, cls] of Object.entries(expected)) {
      const wrapper = mount(StatusDot, { props: { status } })
      const dot = wrapper.find('[aria-hidden="true"]')
      expect(dot.classes()).toContain(cls)
    }
  })

  it('does not show visible label text when label prop is omitted', () => {
    const wrapper = mount(StatusDot, { props: { status: 'online' } })
    const labelSpan = wrapper.find('.text-xs')
    expect(labelSpan.exists()).toBe(false)
  })

  it('shows label text when label prop is provided', () => {
    const wrapper = mount(StatusDot, {
      props: { status: 'offline', label: 'Server' },
    })
    expect(wrapper.text()).toContain('Server')
  })

  it('provides screen-reader text from the label when set', () => {
    const wrapper = mount(StatusDot, {
      props: { status: 'warning', label: 'API' },
    })
    const srOnly = wrapper.find('.sr-only')
    expect(srOnly.text()).toBe('API')
  })

  it('falls back to the status value for screen-reader text', () => {
    const wrapper = mount(StatusDot, { props: { status: 'idle' } })
    const srOnly = wrapper.find('.sr-only')
    expect(srOnly.text()).toBe('idle')
  })

  it('does not pulse by default', () => {
    const wrapper = mount(StatusDot, { props: { status: 'online' } })
    const dot = wrapper.find('[aria-hidden="true"]')
    expect(dot.classes()).not.toContain('motion-safe:animate-pulse')
  })

  it('pulses when pulse prop is true', () => {
    const wrapper = mount(StatusDot, {
      props: { status: 'online', pulse: true },
    })
    const dot = wrapper.find('[aria-hidden="true"]')
    expect(dot.classes()).toContain('motion-safe:animate-pulse')
  })

  it('renders as an inline-flex span', () => {
    const wrapper = mount(StatusDot, { props: { status: 'online' } })
    expect(wrapper.element.tagName).toBe('SPAN')
    expect(wrapper.classes()).toContain('inline-flex')
  })
})

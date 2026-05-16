import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import AlertBanner from '@/components/AlertBanner.vue'

describe('AlertBanner', () => {
  it('renders with role="status" for info variant (default)', () => {
    const wrapper = mount(AlertBanner, { slots: { default: 'Hello' } })
    expect(wrapper.find('[role="status"]').exists()).toBe(true)
  })

  it('uses role="alert" for error variant', () => {
    const wrapper = mount(AlertBanner, {
      props: { variant: 'error' },
      slots: { default: 'err' },
    })
    expect(wrapper.find('[role="alert"]').exists()).toBe(true)
  })

  it('uses role="alert" for warning variant', () => {
    const wrapper = mount(AlertBanner, {
      props: { variant: 'warning' },
      slots: { default: 'warn' },
    })
    expect(wrapper.find('[role="alert"]').exists()).toBe(true)
  })

  it('uses role="status" for success variant', () => {
    const wrapper = mount(AlertBanner, {
      props: { variant: 'success' },
      slots: { default: 'ok' },
    })
    expect(wrapper.find('[role="status"]').exists()).toBe(true)
  })

  it('displays slot content', () => {
    const wrapper = mount(AlertBanner, { slots: { default: 'Data is stale' } })
    expect(wrapper.text()).toContain('Data is stale')
  })

  it('defaults to info variant classes', () => {
    const wrapper = mount(AlertBanner, { slots: { default: 'msg' } })
    const el = wrapper.find('[role="status"]')
    expect(el.classes()).toContain('bg-blue-50')
  })

  it('applies warning variant classes', () => {
    const wrapper = mount(AlertBanner, {
      props: { variant: 'warning' },
      slots: { default: 'warn' },
    })
    expect(wrapper.find('[role="alert"]').classes()).toContain('bg-yellow-50')
  })

  it('applies error variant classes', () => {
    const wrapper = mount(AlertBanner, {
      props: { variant: 'error' },
      slots: { default: 'err' },
    })
    expect(wrapper.find('[role="alert"]').classes()).toContain('bg-red-50')
  })

  it('applies success variant classes', () => {
    const wrapper = mount(AlertBanner, {
      props: { variant: 'success' },
      slots: { default: 'ok' },
    })
    expect(wrapper.find('[role="status"]').classes()).toContain('bg-green-50')
  })

  it('includes sr-only variant label for screen readers', () => {
    const wrapper = mount(AlertBanner, {
      props: { variant: 'warning' },
      slots: { default: 'stale' },
    })
    expect(wrapper.find('.sr-only').text()).toBe('warning:')
  })

  it('does not show dismiss button by default', () => {
    const wrapper = mount(AlertBanner, { slots: { default: 'msg' } })
    expect(wrapper.find('button').exists()).toBe(false)
  })

  it('shows dismiss button when dismissible', () => {
    const wrapper = mount(AlertBanner, {
      props: { dismissible: true },
      slots: { default: 'msg' },
    })
    const btn = wrapper.find('button')
    expect(btn.exists()).toBe(true)
    expect(btn.attributes('aria-label')).toBe('Dismiss alert')
    expect(btn.attributes('type')).toBe('button')
  })

  it('hides alert after dismiss click', async () => {
    const wrapper = mount(AlertBanner, {
      props: { dismissible: true },
      slots: { default: 'msg' },
    })
    await wrapper.find('button').trigger('click')
    expect(wrapper.find('[role="status"]').exists()).toBe(false)
    expect(wrapper.find('[role="alert"]').exists()).toBe(false)
  })

  it('emits dismiss event on close', async () => {
    const wrapper = mount(AlertBanner, {
      props: { dismissible: true },
      slots: { default: 'msg' },
    })
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('dismiss')).toHaveLength(1)
  })

})

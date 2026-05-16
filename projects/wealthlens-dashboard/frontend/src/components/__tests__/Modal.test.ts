import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Modal from '@/components/Modal.vue'

describe('Modal', () => {
  it('does not render when open is false', () => {
    const wrapper = mount(Modal, {
      props: { title: 'Test', open: false },
      global: { stubs: { Teleport: true } },
    })
    expect(wrapper.find('[role="dialog"]').exists()).toBe(false)
  })

  it('renders when open is true', () => {
    const wrapper = mount(Modal, {
      props: { title: 'Test Modal', open: true },
      global: { stubs: { Teleport: true } },
    })
    expect(wrapper.find('[role="dialog"]').exists()).toBe(true)
  })

  it('displays the title', () => {
    const wrapper = mount(Modal, {
      props: { title: 'Dataset Info', open: true },
      global: { stubs: { Teleport: true } },
    })
    expect(wrapper.find('h2').text()).toBe('Dataset Info')
  })

  it('has aria-modal and aria-label', () => {
    const wrapper = mount(Modal, {
      props: { title: 'Details', open: true },
      global: { stubs: { Teleport: true } },
    })
    const dialog = wrapper.find('[role="dialog"]')
    expect(dialog.attributes('aria-modal')).toBe('true')
    expect(dialog.attributes('aria-label')).toBe('Details')
  })

  it('emits close on close button click', async () => {
    const wrapper = mount(Modal, {
      props: { title: 'Test', open: true },
      global: { stubs: { Teleport: true } },
    })
    await wrapper.find('button[aria-label="Close dialog"]').trigger('click')
    expect(wrapper.emitted('close')).toHaveLength(1)
  })

  it('emits close on backdrop click', async () => {
    const wrapper = mount(Modal, {
      props: { title: 'Test', open: true },
      global: { stubs: { Teleport: true } },
    })
    await wrapper.find('[aria-hidden="true"]').trigger('click')
    expect(wrapper.emitted('close')).toHaveLength(1)
  })

  it('emits close on Escape key', async () => {
    const wrapper = mount(Modal, {
      props: { title: 'Test', open: true },
      global: { stubs: { Teleport: true } },
    })
    document.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }))
    expect(wrapper.emitted('close')).toHaveLength(1)
  })

  it('renders slot content', () => {
    const wrapper = mount(Modal, {
      props: { title: 'Test', open: true },
      slots: { default: '<p>Body content</p>' },
      global: { stubs: { Teleport: true } },
    })
    expect(wrapper.text()).toContain('Body content')
  })
})

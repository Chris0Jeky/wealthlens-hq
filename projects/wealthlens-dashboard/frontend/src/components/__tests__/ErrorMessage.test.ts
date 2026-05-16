import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ErrorMessage from '@/components/ErrorMessage.vue'

describe('ErrorMessage', () => {
  it('displays the error message', () => {
    const wrapper = mount(ErrorMessage, {
      props: { message: 'Server unavailable' },
    })
    expect(wrapper.text()).toContain('Server unavailable')
  })

  it('shows default title', () => {
    const wrapper = mount(ErrorMessage, {
      props: { message: 'err' },
    })
    expect(wrapper.text()).toContain('Failed to load data')
  })

  it('allows custom title', () => {
    const wrapper = mount(ErrorMessage, {
      props: { message: 'err', title: 'Connection lost' },
    })
    expect(wrapper.text()).toContain('Connection lost')
  })

  it('has aria-live for screen reader announcement', () => {
    const wrapper = mount(ErrorMessage, {
      props: { message: 'err' },
    })
    expect(wrapper.find('[aria-live="assertive"]').exists()).toBe(true)
  })

  it('hides retry button by default', () => {
    const wrapper = mount(ErrorMessage, {
      props: { message: 'err' },
    })
    expect(wrapper.find('button').exists()).toBe(false)
  })

  it('shows retry button with type=button when retryable', () => {
    const wrapper = mount(ErrorMessage, {
      props: { message: 'err', retryable: true },
    })
    const btn = wrapper.find('button')
    expect(btn.exists()).toBe(true)
    expect(btn.attributes('type')).toBe('button')
  })

  it('emits retry event on button click', async () => {
    const wrapper = mount(ErrorMessage, {
      props: { message: 'err', retryable: true },
    })
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('retry')).toHaveLength(1)
  })
})

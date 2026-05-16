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

  it('has alert role for accessibility', () => {
    const wrapper = mount(ErrorMessage, {
      props: { message: 'err' },
    })
    expect(wrapper.find('[role="alert"]').exists()).toBe(true)
  })

  it('hides retry button by default', () => {
    const wrapper = mount(ErrorMessage, {
      props: { message: 'err' },
    })
    expect(wrapper.find('button').exists()).toBe(false)
  })

  it('shows retry button when retryable', () => {
    const wrapper = mount(ErrorMessage, {
      props: { message: 'err', retryable: true },
    })
    expect(wrapper.find('button').exists()).toBe(true)
    expect(wrapper.find('button').text()).toBe('Try again')
  })

  it('emits retry event on button click', async () => {
    const wrapper = mount(ErrorMessage, {
      props: { message: 'err', retryable: true },
    })
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted('retry')).toHaveLength(1)
  })
})

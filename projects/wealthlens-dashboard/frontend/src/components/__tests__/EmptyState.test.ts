import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import EmptyState from '@/components/EmptyState.vue'

describe('EmptyState', () => {
  it('renders default title', () => {
    const wrapper = mount(EmptyState)
    expect(wrapper.find('h3').text()).toBe('No data available')
  })

  it('renders default message', () => {
    const wrapper = mount(EmptyState)
    expect(wrapper.find('p').text()).toBe('There is nothing to display here yet.')
  })

  it('accepts custom title and message', () => {
    const wrapper = mount(EmptyState, {
      props: { title: 'No datasets', message: 'Run the pipeline first.' },
    })
    expect(wrapper.find('h3').text()).toBe('No datasets')
    expect(wrapper.find('p').text()).toBe('Run the pipeline first.')
  })

  it('hides icon from screen readers', () => {
    const wrapper = mount(EmptyState)
    const icon = wrapper.find('[aria-hidden="true"]')
    expect(icon.exists()).toBe(true)
  })

  it('renders action slot when provided', () => {
    const wrapper = mount(EmptyState, {
      slots: { action: '<button>Retry</button>' },
    })
    expect(wrapper.find('button').text()).toBe('Retry')
  })

  it('does not render action area when no slot', () => {
    const wrapper = mount(EmptyState)
    const buttons = wrapper.findAll('button')
    expect(buttons).toHaveLength(0)
  })
})

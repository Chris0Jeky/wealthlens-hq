import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ChartSkeleton from '@/components/ChartSkeleton.vue'

describe('ChartSkeleton', () => {
  it('renders with default 7 bars', () => {
    const wrapper = mount(ChartSkeleton)
    const bars = wrapper.findAll('[style]')
    expect(bars).toHaveLength(7)
  })

  it('renders custom number of bars', () => {
    const wrapper = mount(ChartSkeleton, { props: { bars: 4 } })
    const barsContainer = wrapper.find('.flex.items-end')
    expect(barsContainer.element.children).toHaveLength(4)
  })

  it('has accessible role and label', () => {
    const wrapper = mount(ChartSkeleton)
    const container = wrapper.find('[role="status"]')
    expect(container.exists()).toBe(true)
    expect(container.attributes('aria-label')).toBe('Loading chart')
  })

  it('has sr-only loading text', () => {
    const wrapper = mount(ChartSkeleton)
    const srOnly = wrapper.find('.sr-only')
    expect(srOnly.text()).toContain('Loading')
  })
})

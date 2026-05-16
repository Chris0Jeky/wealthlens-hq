import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ProgressBar from '@/components/ProgressBar.vue'

describe('ProgressBar', () => {
  it('renders a progressbar role element', () => {
    const wrapper = mount(ProgressBar, { props: { value: 50 } })
    expect(wrapper.find('[role="progressbar"]').exists()).toBe(true)
  })

  it('sets aria-valuenow to the value prop', () => {
    const wrapper = mount(ProgressBar, { props: { value: 42 } })
    expect(wrapper.find('[role="progressbar"]').attributes('aria-valuenow')).toBe('42')
  })

  it('sets aria-valuemax to the max prop', () => {
    const wrapper = mount(ProgressBar, { props: { value: 5, max: 10 } })
    expect(wrapper.find('[role="progressbar"]').attributes('aria-valuemax')).toBe('10')
  })

  it('calculates width percentage correctly', () => {
    const wrapper = mount(ProgressBar, { props: { value: 25, max: 50 } })
    const bar = wrapper.find('[role="progressbar"] > div')
    expect(bar.attributes('style')).toContain('width: 50%')
  })

  it('clamps percentage to 0-100', () => {
    const wrapper = mount(ProgressBar, { props: { value: 200 } })
    const bar = wrapper.find('[role="progressbar"] > div')
    expect(bar.attributes('style')).toContain('width: 100%')
  })

  it('handles zero max gracefully', () => {
    const wrapper = mount(ProgressBar, { props: { value: 5, max: 0 } })
    const bar = wrapper.find('[role="progressbar"] > div')
    expect(bar.attributes('style')).toContain('width: 0%')
  })

  it('shows percentage text when showPercent is true', () => {
    const wrapper = mount(ProgressBar, { props: { value: 75, showPercent: true } })
    expect(wrapper.text()).toContain('75%')
  })

  it('does not show percentage text by default', () => {
    const wrapper = mount(ProgressBar, { props: { value: 75 } })
    expect(wrapper.text()).not.toContain('75%')
  })

  it('shows label when provided', () => {
    const wrapper = mount(ProgressBar, { props: { value: 30, label: 'Loading data' } })
    expect(wrapper.text()).toContain('Loading data')
    expect(wrapper.find('[role="progressbar"]').attributes('aria-label')).toBe('Loading data')
  })

  it('applies size class', () => {
    const wrapper = mount(ProgressBar, { props: { value: 50, size: 'lg' } })
    expect(wrapper.find('[role="progressbar"]').classes()).toContain('h-4')
  })
})

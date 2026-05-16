import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ProgressBar from '@/components/ProgressBar.vue'

describe('ProgressBar', () => {
  it('renders a progressbar role element', () => {
    const wrapper = mount(ProgressBar, { props: { value: 50 } })
    expect(wrapper.find('[role="progressbar"]').exists()).toBe(true)
  })

  it('sets aria-valuenow to clamped value', () => {
    const wrapper = mount(ProgressBar, { props: { value: 42 } })
    expect(wrapper.find('[role="progressbar"]').attributes('aria-valuenow')).toBe('42')
  })

  it('clamps aria-valuenow when value exceeds max', () => {
    const wrapper = mount(ProgressBar, { props: { value: 200, max: 100 } })
    expect(Number(wrapper.find('[role="progressbar"]').attributes('aria-valuenow'))).toBeLessThanOrEqual(100)
  })

  it('clamps aria-valuenow when value is negative', () => {
    const wrapper = mount(ProgressBar, { props: { value: -10, max: 100 } })
    expect(Number(wrapper.find('[role="progressbar"]').attributes('aria-valuenow'))).toBeGreaterThanOrEqual(0)
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

  it('clamps width to 0-100%', () => {
    const wrapper = mount(ProgressBar, { props: { value: 200 } })
    const bar = wrapper.find('[role="progressbar"] > div')
    expect(bar.attributes('style')).toContain('width: 100%')
  })

  it('clamps to 0% when value is negative', () => {
    const wrapper = mount(ProgressBar, { props: { value: -5, max: 100 } })
    const bar = wrapper.find('[role="progressbar"] > div')
    expect(bar.attributes('style')).toContain('width: 0%')
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

  it('uses aria-labelledby when label is provided', () => {
    const wrapper = mount(ProgressBar, { props: { value: 30, label: 'Loading data' } })
    expect(wrapper.text()).toContain('Loading data')
    const bar = wrapper.find('[role="progressbar"]')
    expect(bar.attributes('aria-labelledby')).toBeTruthy()
    expect(bar.attributes('aria-label')).toBeUndefined()
  })

  it('uses aria-label fallback when no label provided', () => {
    const wrapper = mount(ProgressBar, { props: { value: 30 } })
    expect(wrapper.find('[role="progressbar"]').attributes('aria-label')).toBe('Progress')
  })

  it('applies size class', () => {
    const wrapper = mount(ProgressBar, { props: { value: 50, size: 'lg' } })
    expect(wrapper.find('[role="progressbar"]').classes()).toContain('h-4')
  })
})

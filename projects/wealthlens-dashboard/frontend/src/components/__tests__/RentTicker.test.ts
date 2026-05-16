import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import RentTicker from '@/components/RentTicker.vue'

describe('RentTicker', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders the "Live" label', () => {
    const wrapper = mount(RentTicker)
    const label = wrapper.find('.rent-ticker-label')
    expect(label.exists()).toBe(true)
    expect(label.text()).toContain('Live')
    wrapper.unmount()
  })

  it('renders the rent paid amount', () => {
    const wrapper = mount(RentTicker)
    const num = wrapper.find('.rent-ticker-num')
    expect(num.exists()).toBe(true)
    expect(num.text()).toBe('£0')
    wrapper.unmount()
  })

  it('renders the elapsed time', () => {
    const wrapper = mount(RentTicker)
    const text = wrapper.text()
    expect(text).toContain('00:00')
    wrapper.unmount()
  })

  it('updates rent paid after time passes', async () => {
    const wrapper = mount(RentTicker)
    vi.advanceTimersByTime(2000)
    await wrapper.vm.$nextTick()

    const num = wrapper.find('.rent-ticker-num')
    expect(num.text()).not.toBe('£0')
    expect(num.text()).toMatch(/^£[\d,]+$/)
    wrapper.unmount()
  })

  it('displays rate information', () => {
    const wrapper = mount(RentTicker)
    const aside = wrapper.find('.rent-ticker-aside')
    expect(aside.exists()).toBe(true)
    expect(aside.text()).toContain('£85bn')
    expect(aside.text()).toContain('£2,695')
    wrapper.unmount()
  })

  it('has correct section aria-label', () => {
    const wrapper = mount(RentTicker)
    const section = wrapper.find('section')
    expect(section.attributes('aria-label')).toBe('Live rent ticker')
    wrapper.unmount()
  })

  it('mentions "private landlord" in the body text', () => {
    const wrapper = mount(RentTicker)
    const body = wrapper.find('.rent-ticker-body')
    expect(body.text()).toContain("private landlord's pension")
    wrapper.unmount()
  })
})

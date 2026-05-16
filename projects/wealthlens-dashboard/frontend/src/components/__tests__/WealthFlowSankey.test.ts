import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import WealthFlowSankey from '@/components/WealthFlowSankey.vue'

describe('WealthFlowSankey', () => {
  it('renders the SVG visualisation', () => {
    const wrapper = mount(WealthFlowSankey)
    const svg = wrapper.find('svg[role="img"]')
    expect(svg.exists()).toBe(true)
  })

  it('has accessible aria-label on the SVG', () => {
    const wrapper = mount(WealthFlowSankey)
    const svg = wrapper.find('svg[role="img"]')
    expect(svg.attributes('aria-label')).toContain('£57 goes to the top 10')
  })

  it('renders 3 flow groups (bars + ribbons)', () => {
    const wrapper = mount(WealthFlowSankey)
    // Each group has 2 bars (people + money) = 6 bars total
    // Plus ribbons (paths) = 3 paths
    const bars = wrapper.findAll('.flow-bar')
    expect(bars).toHaveLength(6) // 3 groups x 2 bars

    const ribbons = wrapper.findAll('.flow-ribbon')
    expect(ribbons).toHaveLength(3)
  })

  it('renders column headers (100 PEOPLE, £100 OF WEALTH)', () => {
    const wrapper = mount(WealthFlowSankey)
    const text = wrapper.find('svg').text()
    expect(text).toContain('100 PEOPLE')
    expect(text).toContain('£100 OF WEALTH')
  })

  it('renders group labels (Top 10%, Middle 40%, Bottom 50%)', () => {
    const wrapper = mount(WealthFlowSankey)
    const text = wrapper.find('svg').text()
    expect(text).toContain('Top 10%')
    expect(text).toContain('Middle 40%')
    expect(text).toContain('Bottom 50%')
  })

  it('renders per-person share labels', () => {
    const wrapper = mount(WealthFlowSankey)
    const text = wrapper.find('svg').text()
    expect(text).toContain('£5.70 each')
    expect(text).toContain('£0.93 each')
    expect(text).toContain('£0.12 each')
  })

  it('renders the footer punchline', () => {
    const wrapper = mount(WealthFlowSankey)
    const text = wrapper.find('svg').text()
    expect(text).toContain('10 households')
    expect(text).toContain('90')
  })

  it('renders the source citation', () => {
    const wrapper = mount(WealthFlowSankey)
    const text = wrapper.find('svg').text()
    expect(text).toContain('ONS Wealth')
    expect(text).toContain('WID UK')
  })

  it('renders the corner tag', () => {
    const wrapper = mount(WealthFlowSankey)
    const tag = wrapper.find('.flow-corner-tag')
    expect(tag.exists()).toBe(true)
    expect(tag.text()).toContain('100 households')
  })

  it('has an accessible aria-label on the wrapper div', () => {
    const wrapper = mount(WealthFlowSankey)
    const stage = wrapper.find('.hero-lens-stage')
    expect(stage.attributes('aria-label')).toContain('Wealth flow')
  })
})

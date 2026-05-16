import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MissionSection from '@/components/MissionSection.vue'

describe('MissionSection', () => {
  it('renders 4 stat boxes', () => {
    const wrapper = mount(MissionSection)
    const stats = wrapper.findAll('.mission-stat')
    expect(stats).toHaveLength(4)
  })

  it('renders stat values and labels', () => {
    const wrapper = mount(MissionSection)
    const values = wrapper.findAll('.mission-stat-v')
    const labels = wrapper.findAll('.mission-stat-l')

    expect(values.map((v) => v.text())).toEqual(['5', '5', '1820', '100%'])
    expect(labels.map((l) => l.text())).toEqual([
      'Charts published',
      'Primary data sources',
      'Earliest year covered',
      'Source-cited',
    ])
  })

  it('renders the mission quote block', () => {
    const wrapper = mount(MissionSection)
    const quote = wrapper.find('.mission-quote')
    expect(quote.exists()).toBe(true)
    expect(quote.text()).toContain('numbers')
  })

  it('renders the mission body paragraphs', () => {
    const wrapper = mount(MissionSection)
    const bodies = wrapper.findAll('.mission-body')
    expect(bodies.length).toBeGreaterThanOrEqual(2)
    expect(bodies[0].text()).toContain('WealthLens UK')
  })

  it('renders the signature line', () => {
    const wrapper = mount(MissionSection)
    const sig = wrapper.find('.mission-signature')
    expect(sig.exists()).toBe(true)
    expect(sig.text()).toContain('Independent')
    expect(sig.text()).toContain('MIT licensed')
  })

  it('has correct aria-labelledby', () => {
    const wrapper = mount(MissionSection)
    const section = wrapper.find('section')
    expect(section.attributes('aria-labelledby')).toBe('mission-heading')
    expect(wrapper.find('#mission-heading').exists()).toBe(true)
  })
})

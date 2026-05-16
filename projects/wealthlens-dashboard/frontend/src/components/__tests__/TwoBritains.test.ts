import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TwoBritains from '@/components/TwoBritains.vue'

describe('TwoBritains', () => {
  it('renders two side panels', () => {
    const wrapper = mount(TwoBritains)
    const sides = wrapper.findAll('.two-b-side')
    expect(sides).toHaveLength(2)
  })

  it('left panel has "Born to it" label', () => {
    const wrapper = mount(TwoBritains)
    const leftLabel = wrapper.find('.two-b-side--left .two-b-label')
    expect(leftLabel.text()).toContain('Born to it')
    expect(leftLabel.text()).toContain('top decile')
  })

  it('right panel has "Pays for it" label', () => {
    const wrapper = mount(TwoBritains)
    const rightLabel = wrapper.find('.two-b-side--right .two-b-label')
    expect(rightLabel.text()).toContain('Pays for it')
    expect(rightLabel.text()).toContain('bottom')
  })

  it('each side has 3 stat blocks', () => {
    const wrapper = mount(TwoBritains)
    const leftStats = wrapper.findAll('.two-b-side--left .two-b-stat')
    const rightStats = wrapper.findAll('.two-b-side--right .two-b-stat')
    expect(leftStats).toHaveLength(3)
    expect(rightStats).toHaveLength(3)
  })

  it('left side stat values are correct', () => {
    const wrapper = mount(TwoBritains)
    const leftBigs = wrapper.findAll('.two-b-side--left .two-b-stat-big').map((b) => b.text())
    expect(leftBigs).toEqual(['£1.3M', '26%', '£250k'])
  })

  it('right side stat values are correct', () => {
    const wrapper = mount(TwoBritains)
    const rightBigs = wrapper.findAll('.two-b-side--right .two-b-stat-big').map((b) => b.text())
    expect(rightBigs).toEqual(['£12k', '33%', '£3k'])
  })

  it('each side has a 3-item day list', () => {
    const wrapper = mount(TwoBritains)
    const leftItems = wrapper.findAll('.two-b-side--left .two-b-day-list li')
    const rightItems = wrapper.findAll('.two-b-side--right .two-b-day-list li')
    expect(leftItems).toHaveLength(3)
    expect(rightItems).toHaveLength(3)
  })

  it('day list items have question labels', () => {
    const wrapper = mount(TwoBritains)
    const questions = wrapper.findAll('.two-b-day-q')
    expect(questions.length).toBe(6) // 3 per side
    expect(questions[0].text()).toContain('Decides this morning:')
  })

  it('each side has a quote block', () => {
    const wrapper = mount(TwoBritains)
    const quotes = wrapper.findAll('.two-b-quote')
    expect(quotes).toHaveLength(2)
    // Left quote is about inheritance
    expect(quotes[0].text()).toContain('Inheritance')
    // Right quote is about saving for a deposit
    expect(quotes[1].text()).toContain('deposit')
  })

  it('each side has a source attribution', () => {
    const wrapper = mount(TwoBritains)
    const sources = wrapper.findAll('.two-b-quote-who')
    expect(sources).toHaveLength(2)
    expect(sources[0].text()).toContain('Source:')
    expect(sources[1].text()).toContain('Source:')
  })

  it('has correct heading structure', () => {
    const wrapper = mount(TwoBritains)
    const h2 = wrapper.find('h2')
    expect(h2.exists()).toBe(true)
    expect(h2.text()).toContain('Same Tuesday')

    const h3s = wrapper.findAll('h3')
    expect(h3s).toHaveLength(2)
    expect(h3s[0].text()).toContain('Owns the home')
    expect(h3s[1].text()).toContain('Rents the home')
  })

  it('has correct aria-labelledby on section', () => {
    const wrapper = mount(TwoBritains)
    const section = wrapper.find('section')
    expect(section.attributes('aria-labelledby')).toBe('two-b-heading')
    expect(wrapper.find('#two-b-heading').exists()).toBe(true)
  })
})

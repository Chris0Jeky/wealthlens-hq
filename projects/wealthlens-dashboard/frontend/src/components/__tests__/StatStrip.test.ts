import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import StatStrip from '@/components/StatStrip.vue'

const sampleStats = [
  { label: 'The headline', value: '57', unit: '%', description: 'Share of wealth', headline: true },
  { label: 'Top 1%', value: '28', unit: '%', description: 'Their share alone' },
  { label: 'Bottom 50%', value: '5', unit: '%', description: 'Barely any' },
  { label: 'Ratio', value: '11:1', description: 'Top vs bottom' },
]

describe('StatStrip', () => {
  it('renders all stat items with label, value, and description', () => {
    const wrapper = mount(StatStrip, {
      props: { stats: sampleStats },
    })
    const cells = wrapper.findAll('.stat-strip__cell')
    expect(cells).toHaveLength(4)

    expect(cells[0].find('.stat-strip__label').text()).toContain('The headline')
    expect(cells[0].find('.stat-strip__value').text()).toContain('57')
    expect(cells[0].find('.stat-strip__desc').text()).toBe('Share of wealth')
  })

  it('renders the unit as a superscript element', () => {
    const wrapper = mount(StatStrip, {
      props: { stats: sampleStats },
    })
    const firstCell = wrapper.findAll('.stat-strip__cell')[0]
    const sup = firstCell.find('sup')
    expect(sup.exists()).toBe(true)
    expect(sup.text()).toBe('%')
  })

  it('does not render sup when unit is not provided', () => {
    const wrapper = mount(StatStrip, {
      props: { stats: sampleStats },
    })
    // The 4th stat has no unit
    const fourthCell = wrapper.findAll('.stat-strip__cell')[3]
    expect(fourthCell.find('sup').exists()).toBe(false)
  })

  it('applies headline class to the headline stat', () => {
    const wrapper = mount(StatStrip, {
      props: { stats: sampleStats },
    })
    const cells = wrapper.findAll('.stat-strip__cell')
    expect(cells[0].classes()).toContain('stat-strip__cell--headline')
    expect(cells[1].classes()).not.toContain('stat-strip__cell--headline')
  })

  it('handles empty stats array gracefully', () => {
    const wrapper = mount(StatStrip, {
      props: { stats: [] },
    })
    expect(wrapper.findAll('.stat-strip__cell')).toHaveLength(0)
    expect(wrapper.find('.stat-strip').exists()).toBe(true)
  })

  it('has an accessible section with aria-label', () => {
    const wrapper = mount(StatStrip, {
      props: { stats: sampleStats },
    })
    const section = wrapper.find('section[aria-label="Key statistics"]')
    expect(section.exists()).toBe(true)
  })
})

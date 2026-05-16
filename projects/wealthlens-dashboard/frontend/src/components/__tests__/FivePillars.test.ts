import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import FivePillars from '@/components/FivePillars.vue'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div />' } },
    { path: '/charts/:name', component: { template: '<div />' } },
  ],
})

function mountPillars() {
  return mount(FivePillars, {
    global: {
      plugins: [router],
    },
  })
}

describe('FivePillars', () => {
  it('renders 5 pillar cards', () => {
    const wrapper = mountPillars()
    const pillars = wrapper.findAll('.pillar')
    expect(pillars).toHaveLength(5)
  })

  it('renders pillar names', () => {
    const wrapper = mountPillars()
    const names = wrapper.findAll('.pillar-name').map((n) => n.text())
    expect(names).toEqual(['Wealth', 'Housing', 'Tax', 'Inheritance', 'Place'])
  })

  it('renders pillar numbers 01 through 05', () => {
    const wrapper = mountPillars()
    const nums = wrapper.findAll('.pillar-num').map((n) => n.text())
    expect(nums).toEqual(['01', '02', '03', '04', '05'])
  })

  it('each pillar has finding text', () => {
    const wrapper = mountPillars()
    const finds = wrapper.findAll('.pillar-find')
    expect(finds).toHaveLength(5)
    finds.forEach((find) => {
      expect(find.text().length).toBeGreaterThan(10)
    })
  })

  it('finding text renders bold segments safely (not v-html)', () => {
    const wrapper = mountPillars()
    // First pillar finding should have bold text for "top 10%" and "57%"
    const firstFind = wrapper.findAll('.pillar-find')[0]
    const bolds = firstFind.findAll('b')
    expect(bolds.length).toBeGreaterThan(0)
    expect(bolds.map((b) => b.text())).toContain('top 10%')
  })

  it('each pillar links to a chart route', () => {
    const wrapper = mountPillars()
    const pillars = wrapper.findAll('.pillar')
    pillars.forEach((pillar) => {
      // router-link renders an <a> tag
      const link = pillar.element.closest('a')
      expect(link).not.toBeNull()
    })
  })

  it('each pillar has an aria-label', () => {
    const wrapper = mountPillars()
    const pillars = wrapper.findAll('.pillar')
    pillars.forEach((pillar) => {
      const label = pillar.attributes('aria-label')
      expect(label).toMatch(/^Pillar \d{2}: \w+/)
    })
  })

  it('renders mini SVG charts for each pillar', () => {
    const wrapper = mountPillars()
    const charts = wrapper.findAll('.pillar-chart')
    expect(charts).toHaveLength(5)
  })

  it('mini charts are hidden from assistive tech', () => {
    const wrapper = mountPillars()
    const charts = wrapper.findAll('.pillar-chart')
    charts.forEach((chart) => {
      expect(chart.attributes('aria-hidden')).toBe('true')
    })
  })

  it('has section heading with aria-labelledby', () => {
    const wrapper = mountPillars()
    const section = wrapper.find('section')
    expect(section.attributes('aria-labelledby')).toBe('pillars-heading')
    expect(wrapper.find('#pillars-heading').exists()).toBe(true)
  })
})

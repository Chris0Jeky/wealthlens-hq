import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import FeaturedChart from '@/components/FeaturedChart.vue'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div />' } },
    { path: '/charts/:name', component: { template: '<div />' } },
  ],
})

function mountChart() {
  return mount(FeaturedChart, {
    global: {
      plugins: [router],
    },
  })
}

describe('FeaturedChart', () => {
  it('renders the section heading', () => {
    const wrapper = mountChart()
    const h2 = wrapper.find('h2')
    expect(h2.exists()).toBe(true)
    expect(h2.text()).toContain('Two centuries')
  })

  it('renders 4 range buttons', () => {
    const wrapper = mountChart()
    const buttons = wrapper.findAll('.chart-range')
    expect(buttons).toHaveLength(4)
    expect(buttons.map((b) => b.text())).toEqual(['200y', '100y', '50y', '25y'])
  })

  it('100y range is active by default', () => {
    const wrapper = mountChart()
    const activeBtn = wrapper.find('.chart-range--active')
    expect(activeBtn.exists()).toBe(true)
    expect(activeBtn.text()).toBe('100y')
  })

  it('clicking a range button changes the active range', async () => {
    const wrapper = mountChart()
    const btn50y = wrapper.findAll('.chart-range')[2]

    await btn50y.trigger('click')

    expect(btn50y.classes()).toContain('chart-range--active')
    // Previous active should no longer be active
    const btn100y = wrapper.findAll('.chart-range')[1]
    expect(btn100y.classes()).not.toContain('chart-range--active')
  })

  it('range buttons have tablist/tab ARIA roles', () => {
    const wrapper = mountChart()
    const tablist = wrapper.find('[role="tablist"]')
    expect(tablist.exists()).toBe(true)
    expect(tablist.attributes('aria-label')).toBe('Time range')

    const tabs = wrapper.findAll('[role="tab"]')
    expect(tabs).toHaveLength(4)
  })

  it('active range button has aria-selected="true"', () => {
    const wrapper = mountChart()
    const activeTab = wrapper.find('.chart-range--active')
    expect(activeTab.attributes('aria-selected')).toBe('true')
  })

  it('renders an SVG chart with role="img"', () => {
    const wrapper = mountChart()
    const svg = wrapper.find('svg[role="img"]')
    expect(svg.exists()).toBe(true)
    expect(svg.attributes('aria-label')).toContain('Share of net personal wealth')
  })

  it('renders series paths inside the SVG', () => {
    const wrapper = mountChart()
    const paths = wrapper.findAll('svg path')
    // Should have at least 4 series paths (Top 10%, Top 1%, Middle 40%, Bottom 50%)
    expect(paths.length).toBeGreaterThanOrEqual(4)
  })

  it('renders the source citation in the footer', () => {
    const wrapper = mountChart()
    const footer = wrapper.find('.chart-footer')
    expect(footer.exists()).toBe(true)
    expect(footer.text()).toContain('WID.world')
  })

  it('renders download links (PNG, SVG, CSV)', () => {
    const wrapper = mountChart()
    const downloadLinks = wrapper.findAll('.chart-footer-download a')
    expect(downloadLinks).toHaveLength(3)
    const texts = downloadLinks.map((l) => l.text())
    expect(texts.some((t) => t.includes('PNG'))).toBe(true)
    expect(texts.some((t) => t.includes('SVG'))).toBe(true)
    expect(texts.some((t) => t.includes('CSV'))).toBe(true)
  })

  it('series legend shows Top 10% and Top 1%', () => {
    const wrapper = mountChart()
    const toolbar = wrapper.find('.chart-toolbar')
    expect(toolbar.text()).toContain('Top 10%')
    expect(toolbar.text()).toContain('Top 1%')
  })

  it('has correct aria-labelledby on section', () => {
    const wrapper = mountChart()
    const section = wrapper.find('section')
    expect(section.attributes('aria-labelledby')).toBe('featured-heading')
  })
})

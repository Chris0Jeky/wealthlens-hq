import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ChartToolbar from '@/components/ChartToolbar.vue'

const sampleSeries = [
  { label: 'Top 10%', color: 'var(--wl-red)', bold: true },
  { label: 'Top 1%', color: 'var(--wl-ink)' },
]

const sampleRanges = ['200y', '100y', '50y', '25y']

describe('ChartToolbar', () => {
  it('renders series legend items with coloured dots', () => {
    const wrapper = mount(ChartToolbar, {
      props: { series: sampleSeries },
    })
    const dots = wrapper.findAll('.chart-toolbar__dot')
    expect(dots).toHaveLength(2)
    expect(dots[0].attributes('style')).toContain('var(--wl-red)')
    expect(dots[1].attributes('style')).toContain('var(--wl-ink)')
  })

  it('renders series labels with bold styling when specified', () => {
    const wrapper = mount(ChartToolbar, {
      props: { series: sampleSeries },
    })
    const tags = wrapper.findAll('.chart-toolbar__tag')
    // First tag after title (no title prop given) is the first series
    const boldEl = tags[0].find('b')
    expect(boldEl.exists()).toBe(true)
    expect(boldEl.text()).toBe('Top 10%')
  })

  it('renders range buttons and marks the active one', () => {
    const wrapper = mount(ChartToolbar, {
      props: { ranges: sampleRanges, activeRange: '100y' },
    })
    const buttons = wrapper.findAll('button[role="tab"]')
    expect(buttons).toHaveLength(4)

    const activeBtn = buttons.find((b) => b.classes().includes('active'))
    expect(activeBtn).toBeDefined()
    expect(activeBtn!.text()).toBe('100y')
    expect(activeBtn!.attributes('aria-selected')).toBe('true')
  })

  it('emits "range-change" when a range button is clicked', async () => {
    const wrapper = mount(ChartToolbar, {
      props: { ranges: sampleRanges, activeRange: '200y' },
    })
    const buttons = wrapper.findAll('button[role="tab"]')
    await buttons[2].trigger('click')

    expect(wrapper.emitted('range-change')).toBeTruthy()
    expect(wrapper.emitted('range-change')![0]).toEqual(['50y'])
  })

  it('renders title and unit when provided', () => {
    const wrapper = mount(ChartToolbar, {
      props: { title: 'Share of wealth', unit: '%' },
    })
    expect(wrapper.text()).toContain('Share of wealth')
    expect(wrapper.text()).toContain('(%)')
  })

  it('does not render range tablist when ranges array is empty', () => {
    const wrapper = mount(ChartToolbar, {
      props: { ranges: [] },
    })
    expect(wrapper.find('[role="tablist"]').exists()).toBe(false)
  })

  it('navigates ranges with ArrowRight key', async () => {
    const wrapper = mount(ChartToolbar, {
      props: { ranges: sampleRanges, activeRange: '200y' },
    })
    const tablist = wrapper.find('[role="tablist"]')
    await tablist.trigger('keydown', { key: 'ArrowRight' })
    expect(wrapper.emitted('range-change')![0]).toEqual(['100y'])
  })

  it('sets tabindex=0 on active tab and -1 on inactive tabs', () => {
    const wrapper = mount(ChartToolbar, {
      props: { ranges: sampleRanges, activeRange: '100y' },
    })
    const buttons = wrapper.findAll('button[role="tab"]')
    const activeBtn = buttons.find((b) => b.text() === '100y')
    const inactiveBtn = buttons.find((b) => b.text() === '200y')
    expect(activeBtn!.attributes('tabindex')).toBe('0')
    expect(inactiveBtn!.attributes('tabindex')).toBe('-1')
  })
})

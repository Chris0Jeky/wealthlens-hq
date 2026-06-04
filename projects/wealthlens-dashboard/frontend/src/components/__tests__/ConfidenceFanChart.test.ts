import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ConfidenceFanChart from '@/components/ConfidenceFanChart.vue'
import type { Interval, IntervalMethod } from '@/types/simulator'

const band: Interval = { low: 1, central: 2.5, high: 3 }

/** Default props with the required `intervalMethod` filled in. */
function props(overrides: Record<string, unknown> = {}) {
  return {
    interval: band,
    label: 'Revenue',
    intervalMethod: 'alpha_sweep' as IntervalMethod,
    ...overrides,
  }
}

describe('ConfidenceFanChart', () => {
  it('renders the central value inside a role="img" figure', () => {
    const wrapper = mount(ConfidenceFanChart, {
      props: props({ label: 'Total revenue' }),
    })
    expect(wrapper.find('[role="img"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('£2.50bn')
    expect(wrapper.text()).toContain('Total revenue')
  })

  it('shows low and high bounds for a sourced, non-degenerate band', () => {
    const wrapper = mount(ConfidenceFanChart, { props: props() })
    expect(wrapper.text()).toContain('£1.00bn')
    expect(wrapper.text()).toContain('£3.00bn')
  })

  // Each method must appear in BOTH the aria-label and the visible "Band:" line,
  // so a swap of the two map entries would be caught.
  const methods: [IntervalMethod, string][] = [
    ['monte_carlo', 'Monte-Carlo credible interval'],
    ['alpha_sweep', 'Pareto-α range'],
  ]
  it.each(methods)(
    'labels the %s method in both the aria-label and the caption',
    (method, text) => {
      const wrapper = mount(ConfidenceFanChart, {
        props: props({ intervalMethod: method }),
      })
      const label = wrapper.find('[role="img"]').attributes('aria-label') ?? ''
      expect(label).toContain('central £2.50bn')
      expect(label).toContain(`${text} range from £1.00bn to £3.00bn`)
      expect(wrapper.text()).toContain(`Band: ${text}.`)
    },
  )

  it('renders caveats in a warning banner above the figure', () => {
    const wrapper = mount(ConfidenceFanChart, {
      props: props({ caveats: ['Provenance incomplete'] }),
    })
    expect(wrapper.find('[role="alert"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Provenance incomplete')
    // The banner is a sibling above the figure, so figcaption stays the figure's first child.
    expect(wrapper.find('figure').find('figcaption').exists()).toBe(true)
    expect(wrapper.find('figure [role="alert"]').exists()).toBe(false)
  })

  it('renders no banner when there are no caveats', () => {
    const wrapper = mount(ConfidenceFanChart, { props: props() })
    expect(wrapper.find('[role="alert"]').exists()).toBe(false)
  })

  it('treats a degenerate interval as a bare point estimate', () => {
    const wrapper = mount(ConfidenceFanChart, {
      props: props({ interval: { low: 5, central: 5, high: 5 } }),
    })
    expect(wrapper.text()).toContain('£5.00bn')
    expect(wrapper.text()).toContain('uncertainty unquantified')
    // No whisker, no low/high band, and only the (muted) central marker is drawn.
    const lines = wrapper.findAll('line')
    expect(lines).toHaveLength(1)
    expect(lines[0].classes()).toContain('stroke-gray-600')
    expect(wrapper.find('[role="img"]').attributes('aria-label')).toContain(
      'point estimate',
    )
  })

  it('hides the band when provenance is incomplete, even with a real spread', () => {
    // The whole point of the contract: an unsourced band must not be drawn while
    // the accessible name calls it a point estimate. Visual and aria must agree.
    const wrapper = mount(ConfidenceFanChart, {
      props: props({ provenanceComplete: false }),
    })
    expect(wrapper.text()).toContain('uncertainty unquantified')
    expect(wrapper.text()).not.toContain('£1.00bn') // low bound hidden
    expect(wrapper.text()).not.toContain('£3.00bn') // high bound hidden
    expect(wrapper.findAll('line')).toHaveLength(1) // only the central marker
    const label = wrapper.find('[role="img"]').attributes('aria-label') ?? ''
    expect(label).toContain('point estimate')
  })

  it('draws the whisker only for a sourced band', () => {
    const wrapper = mount(ConfidenceFanChart, { props: props() })
    // 3 whisker lines + 1 central marker.
    expect(wrapper.findAll('line')).toHaveLength(4)
    expect(wrapper.find('svg g').classes()).toContain('stroke-blue-600')
  })

  it('respects custom currency, unit and decimals', () => {
    const wrapper = mount(ConfidenceFanChart, {
      props: props({
        interval: { low: 1000, central: 2000, high: 3000 },
        label: 'Households',
        currency: '',
        unit: '',
        decimals: 0,
      }),
    })
    expect(wrapper.text()).toContain('2000')
    expect(wrapper.text()).not.toContain('£')
  })

  it('clamps and renders an interval with negative values without error', () => {
    const wrapper = mount(ConfidenceFanChart, {
      props: props({ interval: { low: -2, central: -1, high: 0.5 } }),
    })
    expect(wrapper.find('[role="img"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('£-1.00bn')
    expect(wrapper.text()).toContain('£-2.00bn')
  })
})

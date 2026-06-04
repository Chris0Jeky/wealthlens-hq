import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ConfidenceFanChart from '@/components/ConfidenceFanChart.vue'
import type { Interval } from '@/types/simulator'

const band: Interval = { low: 1, central: 2.5, high: 3 }

describe('ConfidenceFanChart', () => {
  it('renders the central value inside a role="img" figure', () => {
    const wrapper = mount(ConfidenceFanChart, {
      props: { interval: band, label: 'Total revenue' },
    })
    expect(wrapper.find('[role="img"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('£2.50bn')
    expect(wrapper.text()).toContain('Total revenue')
  })

  it('shows low and high bounds for a non-degenerate band', () => {
    const wrapper = mount(ConfidenceFanChart, {
      props: { interval: band, label: 'Revenue' },
    })
    expect(wrapper.text()).toContain('£1.00bn')
    expect(wrapper.text()).toContain('£3.00bn')
  })

  it('describes the full band in the aria-label', () => {
    const wrapper = mount(ConfidenceFanChart, {
      props: {
        interval: band,
        label: 'Total revenue',
        intervalMethod: 'monte_carlo',
      },
    })
    const label = wrapper.find('[role="img"]').attributes('aria-label') ?? ''
    expect(label).toContain('central £2.50bn')
    expect(label).toContain('Monte-Carlo credible interval')
    expect(label).toContain('range from £1.00bn to £3.00bn')
  })

  it('labels the interval method below the chart', () => {
    const wrapper = mount(ConfidenceFanChart, {
      props: {
        interval: band,
        label: 'Revenue',
        intervalMethod: 'alpha_sweep',
      },
    })
    expect(wrapper.text()).toContain('Pareto-α range')
  })

  it('renders caveats in a warning banner', () => {
    const wrapper = mount(ConfidenceFanChart, {
      props: {
        interval: band,
        label: 'Revenue',
        caveats: ['Provenance incomplete'],
      },
    })
    expect(wrapper.find('[role="alert"]').exists()).toBe(true)
    expect(wrapper.text()).toContain('Provenance incomplete')
  })

  it('renders no banner when there are no caveats', () => {
    const wrapper = mount(ConfidenceFanChart, {
      props: { interval: band, label: 'Revenue' },
    })
    expect(wrapper.find('[role="alert"]').exists()).toBe(false)
  })

  it('treats a degenerate interval as a point estimate', () => {
    const wrapper = mount(ConfidenceFanChart, {
      props: { interval: { low: 5, central: 5, high: 5 }, label: 'Revenue' },
    })
    expect(wrapper.text()).toContain('£5.00bn')
    expect(wrapper.text()).toContain('uncertainty unquantified')
    const label = wrapper.find('[role="img"]').attributes('aria-label') ?? ''
    expect(label).toContain('point estimate')
  })

  it('treats an unsourced (provenance-incomplete) band as a point estimate', () => {
    const wrapper = mount(ConfidenceFanChart, {
      props: { interval: band, label: 'Revenue', provenanceComplete: false },
    })
    expect(wrapper.text()).toContain('uncertainty unquantified')
  })

  it('respects custom currency, unit and decimals', () => {
    const wrapper = mount(ConfidenceFanChart, {
      props: {
        interval: { low: 1000, central: 2000, high: 3000 },
        label: 'Households',
        currency: '',
        unit: '',
        decimals: 0,
      },
    })
    expect(wrapper.text()).toContain('2000')
    expect(wrapper.text()).not.toContain('£')
  })
})

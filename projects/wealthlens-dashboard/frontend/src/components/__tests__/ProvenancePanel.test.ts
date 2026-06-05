import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ProvenancePanel from '@/components/ProvenancePanel.vue'
import type { ConsumedAssumption } from '@/types/simulator'

const ALPHA: ConsumedAssumption = {
  assumption_id: 'toptail.pareto_alpha.overall.v1',
  domain: 'top-tail',
  source: 'Vermeulen (2018); calibrated to UK WAS',
  source_urls: [
    'https://doi.org/10.1111/roiw.12279',
    'https://www.ons.gov.uk/file?uri=/x/totalwealthtables.xlsx',
  ],
}

const NO_URL: ConsumedAssumption = {
  assumption_id: 'behaviour.avoidance.cgt_lock_in.v1',
  domain: 'avoidance',
  source: 'Agersnap & Zidar (2021); HMRC internal estimates',
  source_urls: [],
}

describe('ProvenancePanel', () => {
  it('renders each consumed source with its citation links', () => {
    const wrapper = mount(ProvenancePanel, { props: { assumptions: [ALPHA] } })
    expect(wrapper.find('#provenance-heading').text()).toContain(
      'Sources',
    )
    expect(wrapper.text()).toContain('Vermeulen (2018)')
    const links = wrapper.findAll('a')
    expect(links).toHaveLength(2)
    // Citation links open safely in a new tab.
    expect(links[0].attributes('href')).toBe('https://doi.org/10.1111/roiw.12279')
    expect(links[0].attributes('target')).toBe('_blank')
    expect(links[0].attributes('rel')).toContain('noopener')
    // Concise host labels (no www.).
    expect(links[0].text()).toContain('doi.org')
    expect(links[1].text()).toContain('ons.gov.uk')
    expect(links[1].text()).not.toContain('www.')
  })

  it('notes when a source has no public link instead of an empty link list', () => {
    const wrapper = mount(ProvenancePanel, { props: { assumptions: [NO_URL] } })
    expect(wrapper.findAll('a')).toHaveLength(0)
    expect(wrapper.text()).toContain('No public link available')
  })

  it('renders nothing when no assumptions were consumed', () => {
    const wrapper = mount(ProvenancePanel, { props: { assumptions: [] } })
    expect(wrapper.find('section').exists()).toBe(false)
  })

  it('orders assumptions deterministically by id', () => {
    const wrapper = mount(ProvenancePanel, {
      props: { assumptions: [ALPHA, NO_URL] },
    })
    const items = wrapper.findAll('li')
    expect(items).toHaveLength(2)
    // behaviour.* sorts before toptail.*
    expect(items[0].text()).toContain('Agersnap')
    expect(items[1].text()).toContain('Vermeulen')
  })

  it('is robust to an undefined assumptions prop', () => {
    const wrapper = mount(ProvenancePanel, {
      props: { assumptions: undefined as unknown as ConsumedAssumption[] },
    })
    expect(wrapper.find('section').exists()).toBe(false)
  })
})

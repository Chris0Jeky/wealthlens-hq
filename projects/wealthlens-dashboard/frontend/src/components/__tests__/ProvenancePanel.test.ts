import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ProvenancePanel from '@/components/ProvenancePanel.vue'
import type {
  ConsumedAssumption,
  PopulationProvenanceEntry,
} from '@/types/simulator'

const POP_SOURCES: PopulationProvenanceEntry[] = [
  {
    id: 'ons-was-wealth',
    name: 'ONS Wealth and Assets Survey (WAS)',
    url: 'https://www.ons.gov.uk/file?uri=/x/totalwealthtables.xlsx',
    access_date: '2026-05-30',
    licence: 'OGL-3.0',
  },
  { id: 'synth.pareto_alpha' }, // id-only generation parameter — not a citable source
]

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
    const h2 = wrapper.find('h2')
    expect(h2.text()).toContain('Sources')
    // The region is named by its heading via a unique (useId) id.
    expect(wrapper.find('section').attributes('aria-labelledby')).toBe(
      h2.attributes('id'),
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
    // Top-level (assumption) list items only — not the nested citation-link items.
    const items = wrapper.findAll('section > ul > li')
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

  it('does not throw when an assumption omits source_urls entirely', () => {
    const missing = {
      assumption_id: 'a.b.v1',
      domain: 'd',
      source: 'A source with no urls key',
    } as ConsumedAssumption
    const wrapper = mount(ProvenancePanel, { props: { assumptions: [missing] } })
    expect(wrapper.findAll('a')).toHaveLength(0)
    expect(wrapper.text()).toContain('No public link available')
  })

  it('disambiguates two same-host citation links (WCAG 2.4.4)', () => {
    const sameHost: ConsumedAssumption = {
      assumption_id: 'x.y.v1',
      domain: 'migration',
      source: 'Two same-host citations',
      source_urls: [
        'https://doi.org/10.1257/pol.20200258',
        'https://doi.org/10.1257/app.20220615',
      ],
    }
    const wrapper = mount(ProvenancePanel, { props: { assumptions: [sameHost] } })
    const texts = wrapper.findAll('a').map((l) => l.text().trim())
    expect(texts).toHaveLength(2)
    // Same host -> distinct labels (host + last path segment), not two bare "doi.org".
    expect(new Set(texts).size).toBe(2)
    expect(texts.every((t) => t.startsWith('doi.org/'))).toBe(true)
  })

  it('renders citation links as a list for screen-reader item semantics', () => {
    const wrapper = mount(ProvenancePanel, { props: { assumptions: [ALPHA] } })
    // The links live in a nested <ul><li> (not a bare <p>) for list semantics.
    const linkItems = wrapper.findAll('section > ul > li > ul > li')
    expect(linkItems.length).toBe(2)
    expect(linkItems.every((li) => li.find('a').exists())).toBe(true)
  })

  it('lists population data sources with a URL (and skips id-only synth params)', () => {
    const wrapper = mount(ProvenancePanel, {
      props: { assumptions: [ALPHA], populationSources: POP_SOURCES },
    })
    expect(wrapper.text()).toContain('Population data sources')
    expect(wrapper.text()).toContain('ONS Wealth and Assets Survey')
    expect(wrapper.text()).toContain('accessed 2026-05-30')
    expect(wrapper.text()).toContain('OGL-3.0')
    // The id-only synth generation parameter is not a citable source.
    expect(wrapper.text()).not.toContain('synth.pareto_alpha')
    const onsLink = wrapper
      .findAll('a')
      .find((a) => a.attributes('href')?.includes('ons.gov.uk'))
    expect(onsLink).toBeTruthy()
  })

  it('renders the section for population sources even with no assumptions', () => {
    const wrapper = mount(ProvenancePanel, {
      props: { assumptions: [], populationSources: POP_SOURCES },
    })
    expect(wrapper.find('section').exists()).toBe(true)
    expect(wrapper.text()).toContain('Population data sources')
    // No assumptions -> the modelling-assumptions intro is absent.
    expect(wrapper.text()).not.toContain('modelling assumptions behind')
  })

  it('hides the population subsection when no source carries a URL', () => {
    const wrapper = mount(ProvenancePanel, {
      props: { assumptions: [ALPHA], populationSources: [{ id: 'synth.x' }] },
    })
    expect(wrapper.text()).not.toContain('Population data sources')
  })
})

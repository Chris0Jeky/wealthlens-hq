import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SourcesStrip from '@/components/SourcesStrip.vue'

describe('SourcesStrip', () => {
  it('renders 5 source cards', () => {
    const wrapper = mount(SourcesStrip)
    const cards = wrapper.findAll('.src-card')
    expect(cards).toHaveLength(5)
  })

  it('renders correct acronyms', () => {
    const wrapper = mount(SourcesStrip)
    const acros = wrapper.findAll('.src-card-acro').map((el) => el.text())
    expect(acros).toEqual(['ONS', 'HMRC', 'WID', 'LR', 'DWP'])
  })

  it('renders full names for each source', () => {
    const wrapper = mount(SourcesStrip)
    const fulls = wrapper.findAll('.src-card-full').map((el) => el.text())
    expect(fulls).toContain('Office for National Statistics')
    expect(fulls).toContain('HM Revenue & Customs')
    expect(fulls).toContain('World Inequality Database')
    expect(fulls).toContain('HM Land Registry')
    expect(fulls).toContain('Department for Work & Pensions')
  })

  it('uses role="list" and role="listitem" for accessibility', () => {
    const wrapper = mount(SourcesStrip)
    const list = wrapper.find('[role="list"]')
    expect(list.exists()).toBe(true)

    const items = wrapper.findAll('[role="listitem"]')
    expect(items).toHaveLength(5)
  })

  it('has correct aria-labelledby', () => {
    const wrapper = mount(SourcesStrip)
    const section = wrapper.find('section')
    expect(section.attributes('aria-labelledby')).toBe('sources-heading')
    expect(wrapper.find('#sources-heading').exists()).toBe(true)
  })

  it('renders the label text', () => {
    const wrapper = mount(SourcesStrip)
    const label = wrapper.find('.sources-label')
    expect(label.text()).toContain('Every number cites its source')
  })
})

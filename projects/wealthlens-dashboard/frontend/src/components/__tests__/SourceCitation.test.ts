import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SourceCitation from '../SourceCitation.vue'

describe('SourceCitation', () => {
  const props = {
    source: 'World Inequality Database (wid.world)',
    sourceUrl: 'https://wid.world',
    accessDate: '2026-05-14',
  }

  it('renders source name as a link', () => {
    const wrapper = mount(SourceCitation, { props })
    const link = wrapper.find('a')
    expect(link.text()).toContain('World Inequality Database (wid.world)')
    expect(link.attributes('href')).toBe('https://wid.world')
  })

  it('sets target="_blank" and rel="noopener noreferrer"', () => {
    const wrapper = mount(SourceCitation, { props })
    const link = wrapper.find('a')
    expect(link.attributes('target')).toBe('_blank')
    expect(link.attributes('rel')).toBe('noopener noreferrer')
  })

  it('includes screen-reader new tab warning', () => {
    const wrapper = mount(SourceCitation, { props })
    const srOnly = wrapper.find('.sr-only')
    expect(srOnly.text()).toBe('(opens in new tab)')
  })

  it('sanitizes non-http URLs to #', () => {
    const wrapper = mount(SourceCitation, {
      props: { ...props, sourceUrl: 'javascript:alert(1)' },
    })
    const link = wrapper.find('a')
    expect(link.attributes('href')).toBe('#')
  })

  it('displays the access date', () => {
    const wrapper = mount(SourceCitation, { props })
    expect(wrapper.text()).toContain('accessed 2026-05-14')
  })

  it('displays "Source:" label', () => {
    const wrapper = mount(SourceCitation, { props })
    expect(wrapper.text()).toContain('Source:')
  })
})

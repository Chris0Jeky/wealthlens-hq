import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SkipLink from '@/components/SkipLink.vue'

describe('SkipLink', () => {
  it('renders with default target', () => {
    const wrapper = mount(SkipLink)
    const link = wrapper.find('a')
    expect(link.attributes('href')).toBe('#main-content')
  })

  it('uses custom target when provided', () => {
    const wrapper = mount(SkipLink, { props: { target: '#charts' } })
    const link = wrapper.find('a')
    expect(link.attributes('href')).toBe('#charts')
  })

  it('has sr-only class for visual hiding', () => {
    const wrapper = mount(SkipLink)
    expect(wrapper.find('a').classes()).toContain('sr-only')
  })

  it('contains skip link text', () => {
    const wrapper = mount(SkipLink)
    expect(wrapper.text()).toContain('Skip to main content')
  })
})

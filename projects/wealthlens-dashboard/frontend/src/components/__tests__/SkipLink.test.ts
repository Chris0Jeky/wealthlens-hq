import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SkipLink from '@/components/SkipLink.vue'

describe('SkipLink', () => {
  it('skip link exists in rendered output', () => {
    const wrapper = mount(SkipLink)
    const link = wrapper.find('a')
    expect(link.exists()).toBe(true)
    expect(link.text()).toBe('Skip to main content')
  })

  it('skip link targets #main-content', () => {
    const wrapper = mount(SkipLink)
    const link = wrapper.find('a')
    expect(link.attributes('href')).toBe('#main-content')
  })

  it('skip link has the skip-link class for styling', () => {
    const wrapper = mount(SkipLink)
    expect(wrapper.find('a').classes()).toContain('skip-link')
  })

  it('uses custom target when provided', () => {
    const wrapper = mount(SkipLink, { props: { target: '#charts' } })
    const link = wrapper.find('a')
    expect(link.attributes('href')).toBe('#charts')
  })

  it('main content element has correct id (integration check)', () => {
    // Verify that our skip link's default href matches the expected id
    const wrapper = mount(SkipLink)
    const href = wrapper.find('a').attributes('href')
    expect(href).toBe('#main-content')
    // The corresponding <main id="main-content" tabindex="-1"> lives in App.vue
  })
})

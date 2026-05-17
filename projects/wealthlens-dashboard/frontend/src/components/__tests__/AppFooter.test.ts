import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent, h } from 'vue'
import AppFooter from '@/components/AppFooter.vue'

const RouterLinkStub = defineComponent({
  name: 'RouterLink',
  props: { to: { type: String, required: true } },
  setup(props, { slots }) {
    return () =>
      h(
        'a',
        { href: props.to },
        slots.default?.(),
      )
  },
})

function mountFooter() {
  return mount(AppFooter, {
    global: {
      stubs: { RouterLink: RouterLinkStub },
    },
  })
}

describe('AppFooter', () => {
  it('renders copyright with the current year', () => {
    const wrapper = mountFooter()
    const year = new Date().getFullYear().toString()
    expect(wrapper.text()).toContain(`© ${year} WealthLens UK`)
  })

  it('renders the MIT licence text', () => {
    const wrapper = mountFooter()
    expect(wrapper.text()).toContain('MIT licensed')
  })

  it('renders GitHub link with correct href', () => {
    const wrapper = mountFooter()
    const ghLink = wrapper.find('a[href="https://github.com/Chris0Jeky/wealthlens-hq"]')
    expect(ghLink.exists()).toBe(true)
    expect(ghLink.attributes('target')).toBe('_blank')
    expect(ghLink.attributes('rel')).toBe('noopener')
  })

  it('renders social links (Bluesky, Mastodon)', () => {
    const wrapper = mountFooter()
    expect(wrapper.text()).toContain('Bluesky')
    expect(wrapper.text()).toContain('Mastodon')
  })

  it('has role="contentinfo" on footer element', () => {
    const wrapper = mountFooter()
    const footer = wrapper.find('footer[role="contentinfo"]')
    expect(footer.exists()).toBe(true)
  })

  it('renders navigation sections (Explore, Project, Follow)', () => {
    const wrapper = mountFooter()
    expect(wrapper.text()).toContain('Explore')
    expect(wrapper.text()).toContain('Project')
    expect(wrapper.text()).toContain('Follow')
  })
})

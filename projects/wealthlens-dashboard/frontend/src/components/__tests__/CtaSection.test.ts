import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import CtaSection from '@/components/CtaSection.vue'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div />' } },
    { path: '/charts/:name', component: { template: '<div />' } },
  ],
})

function mountCta() {
  return mount(CtaSection, {
    global: {
      plugins: [router],
    },
  })
}

describe('CtaSection', () => {
  it('renders the heading', () => {
    const wrapper = mountCta()
    const h2 = wrapper.find('h2')
    expect(h2.exists()).toBe(true)
    expect(h2.text()).toContain("can't fix what you can't see")
  })

  it('renders three action buttons', () => {
    const wrapper = mountCta()
    const btns = wrapper.findAll('.wl-btn')
    expect(btns).toHaveLength(3)
  })

  it('has "Read the data" as primary action', () => {
    const wrapper = mountCta()
    const redBtn = wrapper.find('.wl-btn--red')
    expect(redBtn.exists()).toBe(true)
    expect(redBtn.text()).toContain('Read the data')
  })

  it('has GitHub and Bluesky external links', () => {
    const wrapper = mountCta()
    const ghLink = wrapper.find('a[href*="github.com"]')
    expect(ghLink.exists()).toBe(true)
    expect(ghLink.attributes('target')).toBe('_blank')
    expect(ghLink.attributes('rel')).toContain('noopener')

    const bskyLink = wrapper.find('a[href*="bsky.app"]')
    expect(bskyLink.exists()).toBe(true)
    expect(bskyLink.attributes('target')).toBe('_blank')
  })

  it('has correct aria-labelledby', () => {
    const wrapper = mountCta()
    const section = wrapper.find('section')
    expect(section.attributes('aria-labelledby')).toBe('cta-heading')
    expect(wrapper.find('#cta-heading').exists()).toBe(true)
  })

  it('renders the lead text paragraph', () => {
    const wrapper = mountCta()
    const lead = wrapper.find('.cta-lead')
    expect(lead.exists()).toBe(true)
    expect(lead.text()).toContain('Pull the figure')
  })
})

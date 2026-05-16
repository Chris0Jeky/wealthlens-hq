import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import HeroSection from '@/components/HeroSection.vue'

/**
 * HeroSection uses RouterLink and imports WealthFlowSankey.
 * We provide a real router and let the Sankey component render normally.
 */
const router = createRouter({
  history: createMemoryHistory(),
  routes: [
    { path: '/', component: { template: '<div />' } },
    { path: '/charts/:name', component: { template: '<div />' } },
  ],
})

function mountHero() {
  return mount(HeroSection, {
    global: {
      plugins: [router],
    },
  })
}

describe('HeroSection', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('renders a headline', () => {
    const wrapper = mountHero()
    const h1 = wrapper.find('h1')
    expect(h1.exists()).toBe(true)
    expect(h1.text().length).toBeGreaterThan(0)
  })

  it('renders the first headline on mount (Cascade)', () => {
    const wrapper = mountHero()
    const h1 = wrapper.find('h1')
    // First headline: "Everything in your life is ten years late."
    expect(h1.text()).toContain('ten years late')
  })

  it('renders CTA buttons', () => {
    const wrapper = mountHero()
    const actions = wrapper.find('.hero-actions')
    expect(actions.exists()).toBe(true)

    // Should have a RouterLink (red button) and an anchor (ghost button)
    const redBtn = wrapper.find('.wl-btn--red')
    expect(redBtn.exists()).toBe(true)
    expect(redBtn.text()).toContain('See where it went')

    const ghostBtn = wrapper.find('.wl-btn--ghost')
    expect(ghostBtn.exists()).toBe(true)
    expect(ghostBtn.text()).toContain('gut')
  })

  it('displays source citation', () => {
    const wrapper = mountHero()
    const meta = wrapper.find('.hero-meta')
    expect(meta.exists()).toBe(true)
    expect(meta.text()).toContain('Source:')
  })

  it('has correct aria-labelledby on the section', () => {
    const wrapper = mountHero()
    const section = wrapper.find('section')
    expect(section.attributes('aria-labelledby')).toBe('hero-heading')
    expect(wrapper.find('#hero-heading').exists()).toBe(true)
  })

  it('rotates headlines after 12 seconds', async () => {
    const wrapper = mountHero()
    const h1 = wrapper.find('h1')

    const firstText = h1.text()

    // Advance 12 seconds to trigger rotation
    vi.advanceTimersByTime(12_000)
    await wrapper.vm.$nextTick()

    const secondText = h1.text()
    expect(secondText).not.toBe(firstText)
    // Second headline should contain "three houses"
    expect(secondText).toContain('three houses')
  })

  it('renders the WealthFlowSankey component', () => {
    const wrapper = mountHero()
    // The Sankey renders a div with class "hero-lens-stage"
    expect(wrapper.find('.hero-lens-stage').exists()).toBe(true)
  })

  it('cleans up rotation timer on unmount (timer count decreases)', () => {
    const wrapper = mountHero()
    const timersBefore = vi.getTimerCount()
    expect(timersBefore).toBeGreaterThan(0)

    wrapper.unmount()
    const timersAfter = vi.getTimerCount()
    // Timer count should decrease — the hero's rotation interval is cleared.
    // Child components (WealthFlowSankey) may have their own pending
    // requestAnimationFrame callbacks that remain, so we check for decrease
    // rather than zero.
    expect(timersAfter).toBeLessThan(timersBefore)
  })

  it('headline has italic emphasis segments', () => {
    const wrapper = mountHero()
    const em = wrapper.find('h1 em')
    expect(em.exists()).toBe(true)
    expect(em.text()).toBe('ten years late')
  })
})

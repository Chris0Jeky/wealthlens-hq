import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent, h } from 'vue'
import NavBar from '@/components/NavBar.vue'

const mockRoute = { path: '/' }

const RouterLinkStub = defineComponent({
  name: 'RouterLink',
  props: { to: { type: String, required: true } },
  setup(props, { slots, attrs }) {
    return () =>
      h(
        'a',
        {
          href: props.to,
          'aria-current': attrs['aria-current'] ?? null,
          onClick: (e: Event) => {
            e.preventDefault()
          },
        },
        slots.default?.(),
      )
  },
})

vi.mock('vue-router', () => ({
  useRoute: () => mockRoute,
}))

function setRoute(path: string) {
  mockRoute.path = path
}

function mountNavBar() {
  return mount(NavBar, {
    global: {
      stubs: { RouterLink: RouterLinkStub },
    },
  })
}

function isMobileNavHidden(wrapper: ReturnType<typeof mount>) {
  const nav = wrapper.find('#mobile-nav')
  return nav.attributes('style')?.includes('display: none') ?? false
}

describe('NavBar', () => {
  it('renders the brand text', () => {
    setRoute('/')
    const wrapper = mountNavBar()
    expect(wrapper.text()).toContain('WealthLens')
    expect(wrapper.text()).toContain('UK')
  })

  it('renders navigation links', () => {
    setRoute('/')
    const wrapper = mountNavBar()
    expect(wrapper.text()).toContain('Dashboard')
    expect(wrapper.text()).toContain('Wealth Shares')
    expect(wrapper.text()).toContain('Housing')
    expect(wrapper.text()).toContain('CGT')
    expect(wrapper.text()).toContain('Simulator')
  })

  it('marks the current route with aria-current="page"', () => {
    setRoute('/charts/wealth-shares')
    const wrapper = mountNavBar()
    const links = wrapper.findAll('a[aria-current="page"]')
    const texts = links.map((l) => l.text())
    expect(texts).toContain('Wealth Shares')
    expect(texts).not.toContain('Dashboard')
  })

  it('marks home as current when on root path', () => {
    setRoute('/')
    const wrapper = mountNavBar()
    const links = wrapper.findAll('a[aria-current="page"]')
    const texts = links.map((l) => l.text())
    expect(texts).toContain('Dashboard')
  })

  it('does not mark a link as active on a prefix-only match', () => {
    setRoute('/charts/wealth-shares-extended')
    const wrapper = mountNavBar()
    const links = wrapper.findAll('a[aria-current="page"]')
    const texts = links.map((l) => l.text())
    expect(texts).not.toContain('Wealth Shares')
  })

  it('has GitHub external links with correct rel attributes', () => {
    setRoute('/')
    const wrapper = mountNavBar()
    const ghLinks = wrapper.findAll('a[href*="github.com"]')
    expect(ghLinks.length).toBeGreaterThanOrEqual(2)
    for (const link of ghLinks) {
      expect(link.attributes('target')).toBe('_blank')
      expect(link.attributes('rel')).toBe('noopener noreferrer')
    }
  })

  it('toggles mobile menu visibility on button click', async () => {
    setRoute('/')
    const wrapper = mountNavBar()
    const btn = wrapper.find('button[aria-label="Toggle navigation menu"]')
    expect(btn.attributes('aria-expanded')).toBe('false')
    expect(isMobileNavHidden(wrapper)).toBe(true)

    await btn.trigger('click')
    expect(btn.attributes('aria-expanded')).toBe('true')
    expect(isMobileNavHidden(wrapper)).toBe(false)
  })

  it('hides mobile menu when a mobile link is clicked', async () => {
    setRoute('/')
    const wrapper = mountNavBar()
    const btn = wrapper.find('button[aria-label="Toggle navigation menu"]')
    await btn.trigger('click')
    expect(isMobileNavHidden(wrapper)).toBe(false)

    const mobileLinks = wrapper.findAll('#mobile-nav a')
    expect(mobileLinks.length).toBeGreaterThan(0)
    await mobileLinks[0].trigger('click')
    expect(isMobileNavHidden(wrapper)).toBe(true)
  })

  it('mobile-nav always exists in DOM for aria-controls', () => {
    setRoute('/')
    const wrapper = mountNavBar()
    expect(wrapper.find('#mobile-nav').exists()).toBe(true)
    const btn = wrapper.find('button[aria-label="Toggle navigation menu"]')
    expect(btn.attributes('aria-controls')).toBe('mobile-nav')
  })

  it('renders desktop nav with hidden md:flex classes', () => {
    setRoute('/')
    const wrapper = mountNavBar()
    const desktopNav = wrapper.find('nav[aria-label="Main navigation"]')
    expect(desktopNav.classes()).toContain('hidden')
    expect(desktopNav.classes()).toContain('md:flex')
  })

  it('includes sr-only "opens in new tab" text for GitHub links', () => {
    setRoute('/')
    const wrapper = mountNavBar()
    const ghLinks = wrapper.findAll('a[href*="github.com"]')
    for (const link of ghLinks) {
      const srOnly = link.find('.sr-only')
      expect(srOnly.exists()).toBe(true)
      expect(srOnly.text()).toBe('(opens in new tab)')
    }
  })
})

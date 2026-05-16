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

  it('has a GitHub external link', () => {
    setRoute('/')
    const wrapper = mountNavBar()
    const ghLink = wrapper.find('a[href*="github.com"]')
    expect(ghLink.exists()).toBe(true)
    expect(ghLink.attributes('target')).toBe('_blank')
    expect(ghLink.attributes('rel')).toBe('noopener')
  })

  it('toggles mobile menu on button click', async () => {
    setRoute('/')
    const wrapper = mountNavBar()
    const btn = wrapper.find('button[aria-label="Toggle navigation menu"]')
    expect(btn.attributes('aria-expanded')).toBe('false')
    expect(wrapper.find('#mobile-nav').exists()).toBe(false)

    await btn.trigger('click')
    expect(btn.attributes('aria-expanded')).toBe('true')
    expect(wrapper.find('#mobile-nav').exists()).toBe(true)
  })

  it('closes mobile menu when a mobile link is clicked', async () => {
    setRoute('/')
    const wrapper = mountNavBar()
    const btn = wrapper.find('button[aria-label="Toggle navigation menu"]')
    await btn.trigger('click')
    expect(wrapper.find('#mobile-nav').exists()).toBe(true)

    const mobileLinks = wrapper.findAll('#mobile-nav a')
    expect(mobileLinks.length).toBeGreaterThan(0)
    await mobileLinks[0].trigger('click')
    expect(wrapper.find('#mobile-nav').exists()).toBe(false)
  })

  it('has correct aria-controls on the mobile toggle button', () => {
    setRoute('/')
    const wrapper = mountNavBar()
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
})

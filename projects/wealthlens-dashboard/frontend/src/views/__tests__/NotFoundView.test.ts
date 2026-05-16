import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createRouter, createMemoryHistory } from 'vue-router'
import NotFoundView from '../NotFoundView.vue'

function mountWithRouter() {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/', component: { template: '<div />' } }],
  })
  return mount(NotFoundView, {
    global: { plugins: [router] },
  })
}

describe('NotFoundView', () => {
  it('renders 404 heading', () => {
    const wrapper = mountWithRouter()
    expect(wrapper.find('h1').text()).toBe('Page not found')
  })

  it('renders decorative 404 text', () => {
    const wrapper = mountWithRouter()
    const decorative = wrapper.find('p[aria-hidden="true"]')
    expect(decorative.exists()).toBe(true)
    expect(decorative.text()).toBe('404')
  })

  it('renders explanation text', () => {
    const wrapper = mountWithRouter()
    expect(wrapper.text()).toContain("doesn't exist or has been moved")
  })

  it('has a link back to home', () => {
    const wrapper = mountWithRouter()
    const link = wrapper.find('a')
    expect(link.attributes('href')).toBe('/')
  })

  it('link text mentions dashboard', () => {
    const wrapper = mountWithRouter()
    const link = wrapper.find('a')
    expect(link.text()).toContain('Back to dashboard')
  })
})

import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import PageHeader from '@/components/PageHeader.vue'

describe('PageHeader', () => {
  it('renders title as h1', () => {
    const wrapper = mount(PageHeader, { props: { title: 'Dashboard' } })
    expect(wrapper.find('h1').text()).toBe('Dashboard')
  })

  it('renders description when provided', () => {
    const wrapper = mount(PageHeader, {
      props: { title: 'Charts', description: 'UK wealth data' },
    })
    expect(wrapper.find('p').text()).toBe('UK wealth data')
  })

  it('hides description when not provided', () => {
    const wrapper = mount(PageHeader, { props: { title: 'Home' } })
    expect(wrapper.find('p').exists()).toBe(false)
  })

  it('renders actions slot', () => {
    const wrapper = mount(PageHeader, {
      props: { title: 'Data' },
      slots: { actions: '<button class="action">Export</button>' },
    })
    expect(wrapper.find('.action').text()).toBe('Export')
  })

  it('hides actions container when no slot content', () => {
    const wrapper = mount(PageHeader, { props: { title: 'Data' } })
    expect(wrapper.findAll('.flex').length).toBe(0)
  })

  it('uses header element', () => {
    const wrapper = mount(PageHeader, { props: { title: 'Test' } })
    expect(wrapper.find('header').exists()).toBe(true)
  })
})

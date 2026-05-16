import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import Pagination from '@/components/Pagination.vue'

describe('Pagination', () => {
  it('does not render when totalPages is 1', () => {
    const wrapper = mount(Pagination, { props: { page: 1, totalPages: 1 } })
    expect(wrapper.find('nav').exists()).toBe(false)
  })

  it('renders nav when totalPages > 1', () => {
    const wrapper = mount(Pagination, { props: { page: 1, totalPages: 5 } })
    expect(wrapper.find('nav').exists()).toBe(true)
    expect(wrapper.find('nav').attributes('aria-label')).toBe('Pagination')
  })

  it('disables previous button on first page', () => {
    const wrapper = mount(Pagination, { props: { page: 1, totalPages: 5 } })
    const prev = wrapper.find('button[aria-label="Previous page"]')
    expect(prev.attributes('disabled')).toBeDefined()
  })

  it('disables next button on last page', () => {
    const wrapper = mount(Pagination, { props: { page: 5, totalPages: 5 } })
    const next = wrapper.find('button[aria-label="Next page"]')
    expect(next.attributes('disabled')).toBeDefined()
  })

  it('marks current page with aria-current', () => {
    const wrapper = mount(Pagination, { props: { page: 3, totalPages: 5 } })
    const current = wrapper.find('[aria-current="page"]')
    expect(current.exists()).toBe(true)
    expect(current.text()).toBe('3')
  })

  it('emits update:page on next click', async () => {
    const wrapper = mount(Pagination, { props: { page: 2, totalPages: 5 } })
    const next = wrapper.find('button[aria-label="Next page"]')
    await next.trigger('click')
    expect(wrapper.emitted('update:page')).toEqual([[3]])
  })

  it('emits update:page on previous click', async () => {
    const wrapper = mount(Pagination, { props: { page: 3, totalPages: 5 } })
    const prev = wrapper.find('button[aria-label="Previous page"]')
    await prev.trigger('click')
    expect(wrapper.emitted('update:page')).toEqual([[2]])
  })

  it('emits update:page on page number click', async () => {
    const wrapper = mount(Pagination, { props: { page: 1, totalPages: 5 } })
    const pageBtn = wrapper.find('[aria-label="Page 2"]')
    await pageBtn.trigger('click')
    expect(wrapper.emitted('update:page')).toEqual([[2]])
  })

  it('shows ellipsis for large page ranges', () => {
    const wrapper = mount(Pagination, { props: { page: 5, totalPages: 10 } })
    const ellipsis = wrapper.findAll('[aria-hidden="true"]')
    expect(ellipsis.length).toBeGreaterThanOrEqual(1)
    expect(ellipsis[0].text()).toBe('…')
  })

  it('does not emit when clicking current page', async () => {
    const wrapper = mount(Pagination, { props: { page: 3, totalPages: 5 } })
    const current = wrapper.find('[aria-current="page"]')
    await current.trigger('click')
    expect(wrapper.emitted('update:page')).toBeUndefined()
  })
})

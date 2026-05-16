import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SkeletonLoader from '@/components/SkeletonLoader.vue'

describe('SkeletonLoader', () => {
  it('renders a single block by default', () => {
    const wrapper = mount(SkeletonLoader)
    const el = wrapper.find('[role="status"]')
    expect(el.exists()).toBe(true)
    expect(el.attributes('aria-label')).toBe('Loading')
  })

  it('applies default width and height', () => {
    const wrapper = mount(SkeletonLoader)
    const el = wrapper.find('[role="status"]')
    expect(el.attributes('style')).toContain('width: 100%')
    expect(el.attributes('style')).toContain('height: 1rem')
  })

  it('accepts custom width and height', () => {
    const wrapper = mount(SkeletonLoader, {
      props: { width: '200px', height: '2rem' },
    })
    const el = wrapper.find('[role="status"]')
    expect(el.attributes('style')).toContain('width: 200px')
    expect(el.attributes('style')).toContain('height: 2rem')
  })

  it('applies rounded-full when rounded prop is true', () => {
    const wrapper = mount(SkeletonLoader, { props: { rounded: true } })
    const el = wrapper.find('[role="status"]')
    expect(el.classes()).toContain('rounded-full')
  })

  it('renders multiple lines when lines prop > 1', () => {
    const wrapper = mount(SkeletonLoader, { props: { lines: 3 } })
    const blocks = wrapper.findAll('.animate-pulse')
    expect(blocks.length).toBe(3)
  })

  it('makes the last line shorter (75%) for visual variety', () => {
    const wrapper = mount(SkeletonLoader, { props: { lines: 3 } })
    const blocks = wrapper.findAll('.animate-pulse')
    expect(blocks[2].attributes('style')).toContain('width: 75%')
    expect(blocks[0].attributes('style')).toContain('width: 100%')
  })

  it('has animate-pulse class for motion', () => {
    const wrapper = mount(SkeletonLoader)
    expect(wrapper.find('.animate-pulse').exists()).toBe(true)
  })
})

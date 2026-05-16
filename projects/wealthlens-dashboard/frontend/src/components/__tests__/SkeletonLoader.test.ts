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

  it('sets aria-busy="true"', () => {
    const wrapper = mount(SkeletonLoader)
    expect(wrapper.find('[role="status"]').attributes('aria-busy')).toBe('true')
  })

  it('accepts custom label prop', () => {
    const wrapper = mount(SkeletonLoader, { props: { label: 'Loading chart' } })
    expect(wrapper.find('[role="status"]').attributes('aria-label')).toBe('Loading chart')
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
    const blocks = wrapper.findAll('.motion-safe\\:animate-pulse')
    expect(blocks.length).toBe(3)
  })

  it('makes the last line shorter (75%) for visual variety', () => {
    const wrapper = mount(SkeletonLoader, { props: { lines: 3 } })
    const blocks = wrapper.findAll('.motion-safe\\:animate-pulse')
    expect(blocks[2].attributes('style')).toContain('width: 75%')
    expect(blocks[0].attributes('style')).toContain('width: 100%')
  })

  it('uses motion-safe:animate-pulse for reduced-motion support', () => {
    const wrapper = mount(SkeletonLoader)
    const el = wrapper.find('[role="status"]')
    expect(el.classes()).toContain('motion-safe:animate-pulse')
  })

  it('applies rounded-full in multi-line mode when rounded is true', () => {
    const wrapper = mount(SkeletonLoader, { props: { lines: 3, rounded: true } })
    const blocks = wrapper.findAll('.motion-safe\\:animate-pulse')
    expect(blocks[0].classes()).toContain('rounded-full')
    expect(blocks[2].classes()).toContain('rounded-full')
  })

  it('treats lines=0 as single block', () => {
    const wrapper = mount(SkeletonLoader, { props: { lines: 0 } })
    const el = wrapper.find('[role="status"]')
    expect(el.attributes('style')).toContain('width: 100%')
  })

  it('treats lines=1 as single block', () => {
    const wrapper = mount(SkeletonLoader, { props: { lines: 1 } })
    const el = wrapper.find('[role="status"]')
    expect(el.attributes('style')).toContain('height: 1rem')
  })
})

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import SearchInput from '@/components/SearchInput.vue'

describe('SearchInput', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  it('renders an input with placeholder', () => {
    const wrapper = mount(SearchInput, {
      props: { modelValue: '', placeholder: 'Filter datasets' },
    })
    const input = wrapper.find('input')
    expect(input.exists()).toBe(true)
    expect(input.attributes('placeholder')).toBe('Filter datasets')
  })

  it('has sr-only label for accessibility', () => {
    const wrapper = mount(SearchInput, {
      props: { modelValue: '', placeholder: 'Search data' },
    })
    const label = wrapper.find('label')
    expect(label.exists()).toBe(true)
    expect(label.classes()).toContain('sr-only')
    expect(label.text()).toBe('Search data')
  })

  it('emits update:modelValue after debounce', async () => {
    const wrapper = mount(SearchInput, {
      props: { modelValue: '', debounceMs: 200 },
    })
    const input = wrapper.find('input')
    await input.setValue('test')
    expect(wrapper.emitted('update:modelValue')).toBeUndefined()

    vi.advanceTimersByTime(200)
    expect(wrapper.emitted('update:modelValue')).toEqual([['test']])
  })

  it('shows clear button when value is non-empty', () => {
    const wrapper = mount(SearchInput, {
      props: { modelValue: 'hello' },
    })
    const clear = wrapper.find('button[aria-label="Clear search"]')
    expect(clear.exists()).toBe(true)
  })

  it('hides clear button when value is empty', () => {
    const wrapper = mount(SearchInput, {
      props: { modelValue: '' },
    })
    const clear = wrapper.find('button[aria-label="Clear search"]')
    expect(clear.exists()).toBe(false)
  })

  it('emits empty string immediately on clear', async () => {
    const wrapper = mount(SearchInput, {
      props: { modelValue: 'test' },
    })
    const clear = wrapper.find('button[aria-label="Clear search"]')
    await clear.trigger('click')
    expect(wrapper.emitted('update:modelValue')).toEqual([['']])
  })

  it('uses type="search" for native browser support', () => {
    const wrapper = mount(SearchInput, { props: { modelValue: '' } })
    expect(wrapper.find('input').attributes('type')).toBe('search')
  })

  it('has autocomplete off', () => {
    const wrapper = mount(SearchInput, { props: { modelValue: '' } })
    expect(wrapper.find('input').attributes('autocomplete')).toBe('off')
  })
})

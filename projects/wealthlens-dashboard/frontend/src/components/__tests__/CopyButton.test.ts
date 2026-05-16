import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import CopyButton from '@/components/CopyButton.vue'

describe('CopyButton', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    })
  })

  it('renders a button', () => {
    const wrapper = mount(CopyButton, { props: { text: 'hello' } })
    expect(wrapper.find('button').exists()).toBe(true)
  })

  it('has default aria-label', () => {
    const wrapper = mount(CopyButton, { props: { text: 'test' } })
    expect(wrapper.find('button').attributes('aria-label')).toBe('Copy to clipboard')
  })

  it('accepts custom label', () => {
    const wrapper = mount(CopyButton, {
      props: { text: 'x', label: 'Copy URL' },
    })
    expect(wrapper.find('button').attributes('aria-label')).toBe('Copy URL')
  })

  it('shows "Copy" text initially', () => {
    const wrapper = mount(CopyButton, { props: { text: 'data' } })
    expect(wrapper.text()).toContain('Copy')
  })

  it('shows "Copied!" after click', async () => {
    const wrapper = mount(CopyButton, { props: { text: 'data' } })
    await wrapper.find('button').trigger('click')
    await Promise.resolve()
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Copied!')
  })

  it('copies the text prop to clipboard', async () => {
    const wrapper = mount(CopyButton, { props: { text: 'copy me' } })
    await wrapper.find('button').trigger('click')
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('copy me')
  })

  it('resets after 2 seconds', async () => {
    const wrapper = mount(CopyButton, { props: { text: 'temp' } })
    await wrapper.find('button').trigger('click')
    await Promise.resolve()
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Copied!')
    vi.advanceTimersByTime(2000)
    await wrapper.vm.$nextTick()
    expect(wrapper.text()).toContain('Copy')
  })
})

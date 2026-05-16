import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { useKeyboardShortcut } from '@/composables/useKeyboardShortcut'

function withSetup(composable: () => void): { unmount: () => void } {
  const Wrapper = defineComponent({
    setup() {
      composable()
      return {}
    },
    template: '<div />',
  })
  const wrapper = mount(Wrapper, { attachTo: document.body })
  return { unmount: () => wrapper.unmount() }
}

function fireKeydown(key: string, mods: { ctrlKey?: boolean; shiftKey?: boolean; altKey?: boolean; metaKey?: boolean } = {}) {
  const event = new KeyboardEvent('keydown', { key, bubbles: true, ...mods })
  document.dispatchEvent(event)
  return event
}

describe('useKeyboardShortcut', () => {
  it('calls handler when matching key is pressed', () => {
    const handler = vi.fn()
    withSetup(() => useKeyboardShortcut('k', handler))
    fireKeydown('k')
    expect(handler).toHaveBeenCalledTimes(1)
  })

  it('does not call handler for non-matching key', () => {
    const handler = vi.fn()
    withSetup(() => useKeyboardShortcut('k', handler))
    fireKeydown('j')
    expect(handler).not.toHaveBeenCalled()
  })

  it('respects ctrl modifier', () => {
    const handler = vi.fn()
    withSetup(() => useKeyboardShortcut('s', handler, { ctrl: true }))
    fireKeydown('s')
    expect(handler).not.toHaveBeenCalled()
    fireKeydown('s', { ctrlKey: true })
    expect(handler).toHaveBeenCalledTimes(1)
  })

  it('respects shift modifier', () => {
    const handler = vi.fn()
    withSetup(() => useKeyboardShortcut('?', handler, { shift: true }))
    fireKeydown('?', { shiftKey: true })
    expect(handler).toHaveBeenCalledTimes(1)
    fireKeydown('?')
    expect(handler).toHaveBeenCalledTimes(1)
  })

  it('respects alt modifier', () => {
    const handler = vi.fn()
    withSetup(() => useKeyboardShortcut('n', handler, { alt: true }))
    fireKeydown('n', { altKey: true })
    expect(handler).toHaveBeenCalledTimes(1)
  })

  it('removes listener on unmount', () => {
    const handler = vi.fn()
    const { unmount } = withSetup(() => useKeyboardShortcut('k', handler))
    unmount()
    fireKeydown('k')
    expect(handler).not.toHaveBeenCalled()
  })

  it('supports metaKey as ctrl alternative', () => {
    const handler = vi.fn()
    withSetup(() => useKeyboardShortcut('k', handler, { ctrl: true }))
    fireKeydown('k', { metaKey: true })
    expect(handler).toHaveBeenCalledTimes(1)
  })
})

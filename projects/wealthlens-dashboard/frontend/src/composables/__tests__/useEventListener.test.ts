import { describe, it, expect, vi } from 'vitest'
import { ref, nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { useEventListener } from '@/composables/useEventListener'

function withSetup(composable: () => void): { unmount: () => void } {
  const Wrapper = defineComponent({
    setup() {
      composable()
      return {}
    },
    template: '<div />',
  })
  const wrapper = mount(Wrapper)
  return { unmount: () => wrapper.unmount() }
}

describe('useEventListener', () => {
  it('adds listener to static target on mount', () => {
    const handler = vi.fn()
    const target = new EventTarget()
    withSetup(() => useEventListener(target, 'click', handler))
    target.dispatchEvent(new Event('click'))
    expect(handler).toHaveBeenCalledTimes(1)
  })

  it('removes listener on unmount', () => {
    const handler = vi.fn()
    const target = new EventTarget()
    const { unmount } = withSetup(() => useEventListener(target, 'click', handler))
    unmount()
    target.dispatchEvent(new Event('click'))
    expect(handler).not.toHaveBeenCalled()
  })

  it('supports ref targets', async () => {
    const handler = vi.fn()
    const target = ref<EventTarget | null>(null)
    withSetup(() => useEventListener(target, 'click', handler))

    const el = new EventTarget()
    target.value = el
    await nextTick()
    el.dispatchEvent(new Event('click'))
    expect(handler).toHaveBeenCalledTimes(1)
  })

  it('removes listener when ref changes', async () => {
    const handler = vi.fn()
    const target = ref<EventTarget | null>(new EventTarget())
    withSetup(() => useEventListener(target, 'click', handler))

    const oldEl = target.value!
    target.value = new EventTarget()
    await nextTick()
    oldEl.dispatchEvent(new Event('click'))
    expect(handler).not.toHaveBeenCalled()
  })

  it('cleans up ref target on unmount', async () => {
    const handler = vi.fn()
    const el = new EventTarget()
    const target = ref<EventTarget | null>(el)
    const { unmount } = withSetup(() => useEventListener(target, 'click', handler))
    unmount()
    el.dispatchEvent(new Event('click'))
    expect(handler).not.toHaveBeenCalled()
  })

  it('handles null ref gracefully', () => {
    const handler = vi.fn()
    const target = ref<EventTarget | null>(null)
    expect(() => {
      withSetup(() => useEventListener(target, 'click', handler))
    }).not.toThrow()
  })
})

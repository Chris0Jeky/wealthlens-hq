import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref, nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { useIntersectionObserver } from '@/composables/useIntersectionObserver'

let observeCallback: (entries: Array<{ isIntersecting: boolean }>) => void
let mockObserve: ReturnType<typeof vi.fn>
let mockUnobserve: ReturnType<typeof vi.fn>
let mockDisconnect: ReturnType<typeof vi.fn>

describe('useIntersectionObserver', () => {
  beforeEach(() => {
    mockObserve = vi.fn()
    mockUnobserve = vi.fn()
    mockDisconnect = vi.fn()

    window.IntersectionObserver = class {
      constructor(cb: (entries: Array<{ isIntersecting: boolean }>) => void) {
        observeCallback = cb
      }
      observe = mockObserve
      unobserve = mockUnobserve
      disconnect = mockDisconnect
    } as unknown as typeof IntersectionObserver
  })

  function mountWithObserver(options = {}) {
    const Comp = defineComponent({
      setup() {
        const el = ref<HTMLElement | null>(document.createElement('div'))
        const { isVisible } = useIntersectionObserver(el, options)
        return { isVisible, el }
      },
      template: '<div ref="el" />',
    })
    return mount(Comp)
  }

  it('starts with isVisible false', () => {
    const wrapper = mountWithObserver()
    expect(wrapper.vm.isVisible).toBe(false)
  })

  it('sets isVisible true when element intersects', async () => {
    const wrapper = mountWithObserver()
    observeCallback([{ isIntersecting: true }])
    await nextTick()
    expect(wrapper.vm.isVisible).toBe(true)
  })

  it('unobserves after first intersection when once=true', async () => {
    mountWithObserver({ once: true })
    observeCallback([{ isIntersecting: true }])
    await nextTick()
    expect(mockUnobserve).toHaveBeenCalled()
  })

  it('does not unobserve when once=false', async () => {
    mountWithObserver({ once: false })
    observeCallback([{ isIntersecting: true }])
    await nextTick()
    expect(mockUnobserve).not.toHaveBeenCalled()
  })

  it('resets isVisible when element leaves viewport with once=false', async () => {
    const wrapper = mountWithObserver({ once: false })
    observeCallback([{ isIntersecting: true }])
    await nextTick()
    expect(wrapper.vm.isVisible).toBe(true)

    observeCallback([{ isIntersecting: false }])
    await nextTick()
    expect(wrapper.vm.isVisible).toBe(false)
  })

  it('disconnects observer on unmount', () => {
    const wrapper = mountWithObserver()
    wrapper.unmount()
    expect(mockDisconnect).toHaveBeenCalled()
  })

  it('calls observe on the target element', () => {
    mountWithObserver()
    expect(mockObserve).toHaveBeenCalled()
  })
})

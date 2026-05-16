import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref, nextTick } from 'vue'
import { mount } from '@vue/test-utils'
import { defineComponent, type Ref } from 'vue'
import { useChartDimensions } from '../useChartDimensions'

let resizeCallback: ResizeObserverCallback | null = null
let observedElements: Element[] = []

const mockDisconnect = vi.fn()

class MockResizeObserver {
  constructor(cb: ResizeObserverCallback) {
    resizeCallback = cb
  }
  observe(el: Element) {
    observedElements.push(el)
  }
  unobserve() {}
  disconnect() {
    mockDisconnect()
  }
}

vi.stubGlobal('ResizeObserver', MockResizeObserver)

function createTestComponent(width = 800) {
  return defineComponent({
    setup() {
      const containerRef = ref<HTMLElement | null>(null) as Ref<HTMLElement | null>
      const { dimensions } = useChartDimensions(containerRef)
      return { containerRef, dimensions }
    },
    template: '<div ref="containerRef" :style="{ width: width + \'px\' }"></div>',
    props: { width: { type: Number, default: width } },
  })
}

function simulateResize(width: number) {
  if (resizeCallback) {
    resizeCallback(
      [{ contentRect: { width } } as unknown as ResizeObserverEntry],
      {} as ResizeObserver,
    )
  }
}

describe('useChartDimensions', () => {
  beforeEach(() => {
    resizeCallback = null
    observedElements = []
    mockDisconnect.mockClear()
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('observes the container element on mount', () => {
    const wrapper = mount(createTestComponent())
    expect(observedElements.length).toBe(1)
    wrapper.unmount()
  })

  it('computes height from width using aspect ratio', () => {
    const wrapper = mount(createTestComponent())
    simulateResize(1000)
    const dims = wrapper.vm.dimensions
    // 1000 * 0.56 = 560, clamped to max 600 => 560
    expect(dims.height).toBe(560)
    expect(dims.width).toBe(1000)
    wrapper.unmount()
  })

  it('clamps height to minimum 300px for narrow containers', () => {
    const wrapper = mount(createTestComponent())
    simulateResize(400)
    const dims = wrapper.vm.dimensions
    // 400 * 0.56 = 224, clamped to min 300
    expect(dims.height).toBe(300)
    wrapper.unmount()
  })

  it('clamps height to maximum 600px for wide containers', () => {
    const wrapper = mount(createTestComponent())
    simulateResize(1200)
    const dims = wrapper.vm.dimensions
    // 1200 * 0.56 = 672, clamped to max 600
    expect(dims.height).toBe(600)
    wrapper.unmount()
  })

  it('disconnects observer on unmount', () => {
    const wrapper = mount(createTestComponent())
    wrapper.unmount()
    expect(mockDisconnect).toHaveBeenCalledOnce()
  })
})

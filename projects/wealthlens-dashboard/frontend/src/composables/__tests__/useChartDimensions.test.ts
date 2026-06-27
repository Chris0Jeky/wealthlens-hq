import { describe, it, expect, vi, beforeEach } from "vitest"
import { ref } from "vue"
import { mount } from "@vue/test-utils"
import { defineComponent, h } from "vue"
import { useChartDimensions } from "@/composables/useChartDimensions"

let observeCallback: ((entries: Array<{ contentRect: { width: number } }>) => void) | null = null

class MockResizeObserver {
  constructor(cb: (entries: Array<{ contentRect: { width: number } }>) => void) {
    observeCallback = cb
  }
  observe() {}
  disconnect() {}
  unobserve() {}
}

describe("useChartDimensions", () => {
  beforeEach(() => {
    observeCallback = null
    vi.stubGlobal("ResizeObserver", MockResizeObserver)
  })

  it("returns initial dimensions with zero width", () => {
    const containerRef = ref<HTMLElement | null>(null)
    const { dimensions } = useChartDimensions(containerRef)
    expect(dimensions.value.width).toBe(0)
    expect(dimensions.value.height).toBe(200)
  })

  it("updates dimensions from container element", () => {
    const TestComp = defineComponent({
      setup() {
        const containerRef = ref<HTMLElement | null>(null)
        const { dimensions } = useChartDimensions(containerRef)
        return { containerRef, dimensions }
      },
      render() {
        return h("div", {
          ref: "containerRef",
          style: { width: "800px" },
        })
      },
    })

    const wrapper = mount(TestComp, {
      attachTo: document.body,
    })

    if (observeCallback) {
      observeCallback([{ contentRect: { width: 800 } }])
    }

    expect(wrapper.vm.dimensions.width).toBe(800)
    expect(wrapper.vm.dimensions.height).toBe(400)
    wrapper.unmount()
  })

  it("clamps height to min/max bounds", () => {
    const containerRef = ref<HTMLElement | null>(null)
    const { dimensions } = useChartDimensions(containerRef)

    expect(dimensions.value.height).toBeGreaterThanOrEqual(200)
    expect(dimensions.value.height).toBeLessThanOrEqual(600)
  })
})

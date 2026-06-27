import { describe, it, expect, vi, afterEach } from "vitest"
import { mount } from "@vue/test-utils"
import { defineComponent } from "vue"
import { useReducedMotion } from "@/composables/useReducedMotion"

function createComponent() {
  return defineComponent({
    setup() {
      const { prefersReducedMotion } = useReducedMotion()
      return { prefersReducedMotion }
    },
    template: "<div>{{ prefersReducedMotion }}</div>",
  })
}

describe("useReducedMotion", () => {
  let listeners: Map<string, (e: MediaQueryListEvent) => void>
  let mockMatches: boolean

  function setupMatchMedia(matches: boolean) {
    mockMatches = matches
    listeners = new Map()

    vi.stubGlobal(
      "matchMedia",
      vi.fn().mockImplementation(() => ({
        matches: mockMatches,
        addEventListener: (event: string, fn: (e: MediaQueryListEvent) => void) => {
          listeners.set(event, fn)
        },
        removeEventListener: (event: string) => {
          listeners.delete(event)
        },
      })),
    )
  }

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("returns false when user has no motion preference", () => {
    setupMatchMedia(false)
    const wrapper = mount(createComponent())
    expect(wrapper.vm.prefersReducedMotion).toBe(false)
    wrapper.unmount()
  })

  it("returns true when user prefers reduced motion", () => {
    setupMatchMedia(true)
    const wrapper = mount(createComponent())
    expect(wrapper.vm.prefersReducedMotion).toBe(true)
    wrapper.unmount()
  })

  it("reacts to media query changes", () => {
    setupMatchMedia(false)
    const wrapper = mount(createComponent())
    expect(wrapper.vm.prefersReducedMotion).toBe(false)

    const handler = listeners.get("change")
    expect(handler).toBeDefined()
    handler!({ matches: true } as MediaQueryListEvent)
    expect(wrapper.vm.prefersReducedMotion).toBe(true)

    handler!({ matches: false } as MediaQueryListEvent)
    expect(wrapper.vm.prefersReducedMotion).toBe(false)
    wrapper.unmount()
  })

  it("cleans up listener on unmount", () => {
    setupMatchMedia(false)
    const wrapper = mount(createComponent())
    expect(listeners.has("change")).toBe(true)
    wrapper.unmount()
    expect(listeners.has("change")).toBe(false)
  })

  it("returns false when matchMedia is undefined", () => {
    vi.stubGlobal("matchMedia", undefined)
    const wrapper = mount(createComponent())
    expect(wrapper.vm.prefersReducedMotion).toBe(false)
    wrapper.unmount()
  })
})

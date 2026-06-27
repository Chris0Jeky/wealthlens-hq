import { describe, it, expect, vi } from "vitest"
import { ref, nextTick, defineComponent } from "vue"
import { mount } from "@vue/test-utils"
import { useMinLoadingTime } from "../useMinLoadingTime"

describe("useMinLoadingTime", () => {
  it("reflects loading=true immediately", () => {
    const loading = ref(true)
    const { showing } = useMinLoadingTime(loading, 300)
    expect(showing.value).toBe(true)
  })

  it("enforces minimum duration when loading starts true", async () => {
    vi.useFakeTimers()
    const loading = ref(true)
    const { showing } = useMinLoadingTime(loading, 300)

    loading.value = false
    await nextTick()
    expect(showing.value).toBe(true)

    vi.advanceTimersByTime(299)
    await nextTick()
    expect(showing.value).toBe(true)

    vi.advanceTimersByTime(1)
    await nextTick()
    expect(showing.value).toBe(false)

    vi.useRealTimers()
  })

  it("keeps showing=true for minimum duration even if loading goes false quickly", async () => {
    vi.useFakeTimers()
    const loading = ref(false)
    const { showing } = useMinLoadingTime(loading, 300)

    loading.value = true
    await nextTick()
    expect(showing.value).toBe(true)

    loading.value = false
    await nextTick()
    expect(showing.value).toBe(true)

    vi.advanceTimersByTime(300)
    await nextTick()
    expect(showing.value).toBe(false)

    vi.useRealTimers()
  })

  it("hides immediately after minMs if loading already false", async () => {
    vi.useFakeTimers()
    const loading = ref(false)
    const { showing } = useMinLoadingTime(loading, 200)

    loading.value = true
    await nextTick()

    loading.value = false
    await nextTick()

    vi.advanceTimersByTime(200)
    await nextTick()
    expect(showing.value).toBe(false)

    vi.useRealTimers()
  })

  it("stays showing while loading remains true past minMs", async () => {
    vi.useFakeTimers()
    const loading = ref(false)
    const { showing } = useMinLoadingTime(loading, 100)

    loading.value = true
    await nextTick()

    vi.advanceTimersByTime(200)
    await nextTick()
    expect(showing.value).toBe(true)

    loading.value = false
    await nextTick()
    expect(showing.value).toBe(false)

    vi.useRealTimers()
  })

  it("clears timer on unmount", async () => {
    vi.useFakeTimers()

    const loading = ref(false)
    let showing: { value: boolean } | undefined

    const Wrapper = defineComponent({
      setup() {
        const result = useMinLoadingTime(loading, 300)
        showing = result.showing
        return {}
      },
      template: "<div />",
    })

    const wrapper = mount(Wrapper)

    // Trigger loading to start the timer
    loading.value = true
    await nextTick()
    expect(showing!.value).toBe(true)

    // Turn off loading while timer is still pending
    loading.value = false
    await nextTick()
    // showing should still be true because timer hasn't fired yet
    expect(showing!.value).toBe(true)

    // Unmount while timer is pending
    wrapper.unmount()

    // Advance timers past the minMs — timer should have been cleared
    vi.advanceTimersByTime(500)
    await nextTick()

    // showing should still be true (timer was cleared, never set it to false)
    expect(showing!.value).toBe(true)

    vi.useRealTimers()
  })
})

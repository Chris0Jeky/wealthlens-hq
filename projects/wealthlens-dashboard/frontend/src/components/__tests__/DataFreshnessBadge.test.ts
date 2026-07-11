import { describe, it, expect, vi, beforeEach, afterEach } from "vitest"
import { mount, flushPromises } from "@vue/test-utils"
import DataFreshnessBadge from "@/components/DataFreshnessBadge.vue"
import { _resetCache } from "@/composables/useDataFreshness"

/** Helper: builds a freshness.json response with a given date for one slug. */
function mockFreshnessResponse(
  dateStr: string,
  source = "ONS Wealth and Assets Survey",
  slug = "wealth-shares",
) {
  return {
    [slug]: { last_updated: dateStr, source },
  }
}

/**
 * Returns a YYYY-MM-DD string for N days ago, formatted from LOCAL date components.
 *
 * The component computes "today" from local components (useDataFreshness daysAgo:
 * Date.UTC(now.getFullYear(), now.getMonth(), now.getDate())), so this helper must
 * also use local components — then the entry date and the component's "today" agree
 * in EVERY timezone. The original bug mixed local getDate() with toISOString() (UTC),
 * which is off by one in UTC+ zones just after local midnight. (Building from UTC
 * instead only papers over UTC-12..+11 and still fails UTC+12..+14.) The frozen clock
 * below then just removes the wall-clock dependency for a stable absolute date.
 */
function daysAgoDate(days: number): string {
  const d = new Date()
  d.setDate(d.getDate() - days)
  const pad = (n: number) => String(n).padStart(2, "0")
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
}

describe("DataFreshnessBadge", () => {
  beforeEach(() => {
    vi.restoreAllMocks()
    // Freeze the clock so the absolute "today" is stable across runs (no midnight-tick
    // race). Timezone-independence comes from daysAgoDate using LOCAL components to
    // match the component, NOT from the frozen instant — so any runner timezone works.
    // Only Date is faked, leaving promises/timers untouched (flushPromises still runs).
    vi.useFakeTimers({ toFake: ["Date"] })
    vi.setSystemTime(new Date("2026-06-15T12:00:00Z"))
    _resetCache()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it("renders date for known dataset", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse(daysAgoDate(2)),
    } as Response)

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    })
    await flushPromises()

    expect(wrapper.text()).toContain("Data:")
    expect(wrapper.text()).toContain("2 days ago")
  })

  it("shows green dot while the source's cadence says no newer release is due", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse(daysAgoDate(3)),
    } as Response)

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    })
    await flushPromises()

    const dot = wrapper.find(".freshness-badge__dot")
    expect(dot.classes()).toContain("freshness-badge__dot--green")
  })

  it("stays green for annual data months old (F3 — cadence-aware, no more 30-day red)", async () => {
    // wealth-shares is an annual series: 100-day-old data is fully current.
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse(daysAgoDate(100)),
    } as Response)

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    })
    await flushPromises()

    const dot = wrapper.find(".freshness-badge__dot")
    expect(dot.classes()).toContain("freshness-badge__dot--green")
  })

  it("shows amber when our copy may lag a due release — never red", async () => {
    // boe-rates is a monthly series: 60-day-old data means an update is due.
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse(daysAgoDate(60), "Bank of England", "boe-rates"),
    } as Response)

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "boe-rates" },
    })
    await flushPromises()

    const dot = wrapper.find(".freshness-badge__dot")
    expect(dot.classes()).toContain("freshness-badge__dot--amber")
    expect(dot.classes()).not.toContain("freshness-badge__dot--red")
  })

  it("shows grey for a suspended source regardless of age — the WAS case", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () =>
        mockFreshnessResponse(daysAgoDate(700), "ONS WAS Round 7", "wealth-by-decile"),
    } as Response)

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-by-decile" },
    })
    await flushPromises()

    const dot = wrapper.find(".freshness-badge__dot")
    expect(dot.classes()).toContain("freshness-badge__dot--grey")
  })

  it("gracefully handles missing dataset (renders nothing)", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse(daysAgoDate(1)),
    } as Response)

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "nonexistent-dataset" },
    })
    await flushPromises()

    expect(wrapper.find(".freshness-badge").exists()).toBe(false)
  })

  it("rejects invalid date-only freshness entries", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse("2026-13-01"),
    } as Response)

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    })
    await flushPromises()

    expect(wrapper.find(".freshness-badge").exists()).toBe(false)
  })

  it("rejects malformed freshness dates", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse("not-a-date"),
    } as Response)

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    })
    await flushPromises()

    expect(wrapper.find(".freshness-badge").exists()).toBe(false)
  })

  it("gracefully handles fetch failure (renders nothing)", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValueOnce(new Error("Network error"))

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    })
    await flushPromises()

    expect(wrapper.find(".freshness-badge").exists()).toBe(false)
  })

  it("shows relative time - today", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse(daysAgoDate(0)),
    } as Response)

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    })
    await flushPromises()

    expect(wrapper.text()).toContain("today")
  })

  it("shows relative time - weeks ago", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse(daysAgoDate(21)),
    } as Response)

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    })
    await flushPromises()

    expect(wrapper.text()).toContain("3 weeks ago")
  })

  it("has tooltip with full date and source", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse(daysAgoDate(5), "HMRC"),
    } as Response)

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    })
    await flushPromises()

    const badge = wrapper.find(".freshness-badge")
    const title = badge.attributes("title")
    expect(title).toContain("Last updated:")
    expect(title).toContain("Source: HMRC")
  })

  it("has accessible role and aria-label", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse(daysAgoDate(2)),
    } as Response)

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    })
    await flushPromises()

    const badge = wrapper.find('[role="status"]')
    expect(badge.exists()).toBe(true)
    expect(badge.attributes("aria-label")).toContain("Data updated")
  })
})

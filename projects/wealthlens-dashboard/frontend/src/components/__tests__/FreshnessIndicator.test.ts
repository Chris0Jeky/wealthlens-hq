import { describe, it, expect, beforeEach, afterEach, vi } from "vitest"
import { mount } from "@vue/test-utils"
import FreshnessIndicator from "@/components/FreshnessIndicator.vue"
import type { DatasetFreshnessEntry } from "@/types/api"

/**
 * The indicator is cadence-aware (docs/product/freshness-grammar.md): it
 * grades last_updated against the dataset's provenance cadence and ignores
 * the wall-clock `status` field (kept for API shape parity).
 */
const NOW = new Date("2026-07-11T00:00:00Z")

function daysBefore(days: number): string {
  return new Date(NOW.getTime() - days * 86_400_000).toISOString()
}

function factory(dataset: string, freshness: DatasetFreshnessEntry) {
  return mount(FreshnessIndicator, { props: { dataset, freshness } })
}

describe("FreshnessIndicator", () => {
  beforeEach(() => {
    vi.useFakeTimers()
    vi.setSystemTime(NOW)
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  describe("cadence-aware states (F3)", () => {
    it("annual data months old is Current with a green dot — never Expired", () => {
      const wrapper = factory("wealth-shares", {
        last_updated: daysBefore(100),
        age_hours: 100 * 24,
        status: "expired", // the vestigial wall-clock field must be ignored
      })
      expect(wrapper.find('[data-testid="freshness-dot"]').classes()).toContain("bg-green-500")
      expect(wrapper.find('[data-testid="freshness-label"]').text()).toBe("Current")
      expect(wrapper.text()).not.toContain("Expired")
    })

    it("data older than its cadence shows Update due with an amber dot", () => {
      const wrapper = factory("boe-rates", {
        last_updated: daysBefore(90),
        age_hours: 90 * 24,
        status: "expired",
      })
      expect(wrapper.find('[data-testid="freshness-dot"]').classes()).toContain("bg-yellow-500")
      expect(wrapper.find('[data-testid="freshness-label"]').text()).toBe("Update due")
    })

    it("a suspended source shows Source suspended with a grey dot — the WAS case", () => {
      const wrapper = factory("wealth-by-decile", {
        last_updated: daysBefore(800),
        age_hours: 800 * 24,
        status: "expired",
      })
      expect(wrapper.find('[data-testid="freshness-dot"]').classes()).toContain("bg-gray-400")
      expect(wrapper.find('[data-testid="freshness-label"]').text()).toBe("Source suspended")
    })

    it("shows Unknown for a missing date", () => {
      const wrapper = factory("wealth-shares", {
        last_updated: null,
        age_hours: null,
        status: "unknown",
      })
      expect(wrapper.find('[data-testid="freshness-dot"]').classes()).toContain("bg-gray-400")
      expect(wrapper.find('[data-testid="freshness-label"]').text()).toBe("Unknown")
    })
  })

  describe("tooltip text", () => {
    it("combines relative age with the cadence explanation", () => {
      const wrapper = factory("wealth-shares", {
        last_updated: daysBefore(2),
        age_hours: 48,
        status: "fresh",
      })
      const tooltip = wrapper.find('[data-testid="freshness-tooltip"]')
      expect(tooltip.text()).toContain("Last updated: 2 days ago")
      expect(tooltip.text()).toContain("no newer release is expected")
    })

    it("shows hours when age is under a day", () => {
      const wrapper = factory("boe-rates", {
        last_updated: daysBefore(0.2),
        age_hours: 5,
        status: "fresh",
      })
      expect(wrapper.find('[data-testid="freshness-tooltip"]').text()).toContain(
        "Last updated: 5 hours ago",
      )
    })

    it("explains a missing date without fabricating one", () => {
      const wrapper = factory("wealth-shares", {
        last_updated: null,
        age_hours: null,
        status: "unknown",
      })
      expect(wrapper.find('[data-testid="freshness-tooltip"]').text()).toContain(
        "No update date recorded",
      )
    })
  })

  describe("accessibility", () => {
    it("has an aria-label combining label and tooltip", () => {
      const wrapper = factory("wealth-shares", {
        last_updated: daysBefore(2),
        age_hours: 48,
        status: "fresh",
      })
      const aria = wrapper.find(".freshness-indicator").attributes("aria-label")
      expect(aria).toContain("Current:")
      expect(aria).toContain("Last updated: 2 days ago")
    })

    it("includes sr-only text for screen readers", () => {
      const wrapper = factory("wealth-shares", {
        last_updated: daysBefore(2),
        age_hours: 48,
        status: "fresh",
      })
      expect(wrapper.find(".sr-only").text()).toContain("Last updated: 2 days ago")
    })

    it("is focusable via tabindex and hides the dot from AT", () => {
      const wrapper = factory("wealth-shares", {
        last_updated: daysBefore(1),
        age_hours: 24,
        status: "fresh",
      })
      expect(wrapper.find(".freshness-indicator").attributes("tabindex")).toBe("0")
      expect(wrapper.find('[data-testid="freshness-dot"]').attributes("aria-hidden")).toBe("true")
    })
  })
})

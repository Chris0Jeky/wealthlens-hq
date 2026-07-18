import { describe, it, expect, beforeEach, afterEach, vi } from "vitest"
import { relativeTime } from "@/composables/useDataFreshness"

const NOW = new Date("2026-07-11T12:00:00Z")

function daysBefore(days: number): Date {
  return new Date(NOW.getTime() - days * 86_400_000)
}

describe("relativeTime", () => {
  beforeEach(() => {
    vi.useFakeTimers({ toFake: ["Date"] })
    vi.setSystemTime(NOW)
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it("handles days and weeks", () => {
    expect(relativeTime(daysBefore(0))).toBe("today")
    expect(relativeTime(daysBefore(1))).toBe("1 day ago")
    expect(relativeTime(daysBefore(5))).toBe("5 days ago")
    expect(relativeTime(daysBefore(10))).toBe("1 week ago")
    expect(relativeTime(daysBefore(21))).toBe("3 weeks ago")
  })

  it("rounds months to the nearest month (F10: a ~2-month age said '1 month ago')", () => {
    expect(relativeTime(daysBefore(35))).toBe("1 month ago")
    // The audit case: ~58 days (14 May → 11 Jul) must read as 2 months
    expect(relativeTime(daysBefore(58))).toBe("2 months ago")
    expect(relativeTime(daysBefore(150))).toBe("5 months ago")
  })

  it("says years past a year instead of pretending month precision", () => {
    expect(relativeTime(daysBefore(400))).toBe("1 year ago")
    expect(relativeTime(daysBefore(800))).toBe("2 years ago")
  })
})

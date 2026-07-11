import { describe, it, expect, vi, afterEach } from "vitest"
import { buildShareLinks, openShareIntent } from "../shareIntents"

describe("buildShareLinks", () => {
  const links = buildShareLinks(
    "https://example.com/charts/wealth-shares",
    "Who owns wealth in the UK?",
  )

  it("builds the three intent URLs with encoded url and title", () => {
    const url = encodeURIComponent("https://example.com/charts/wealth-shares")
    expect(links.twitter).toBe(
      `https://twitter.com/intent/tweet?url=${url}&text=${encodeURIComponent("Who owns wealth in the UK? — WealthLens UK")}`,
    )
    expect(links.linkedin).toBe(`https://www.linkedin.com/sharing/share-offsite/?url=${url}`)
    expect(links.bluesky).toContain("https://bsky.app/intent/compose?text=")
    expect(links.bluesky).toContain(url)
  })
})

describe("openShareIntent", () => {
  afterEach(() => vi.restoreAllMocks())

  it("opens a new window with noopener", () => {
    const openSpy = vi.spyOn(window, "open").mockReturnValue({} as Window)
    openShareIntent("https://example.com/intent")
    expect(openSpy).toHaveBeenCalledWith(
      "https://example.com/intent",
      "_blank",
      "noopener,noreferrer",
    )
  })
})

import { describe, it, expect } from "vitest"
import { buildEmbedSnippet, embedUrl, EMBED_MESSAGE_SOURCE } from "../embedSnippet"

const BASE = "https://chris0jeky.github.io/wealthlens-hq"

describe("embedSnippet", () => {
  it("targets the chrome-free /embed shell, not the article page", () => {
    expect(embedUrl(BASE, "wealth-shares")).toBe(`${BASE}/embed/wealth-shares`)
    expect(embedUrl(`${BASE}/`, "wealth-shares")).toBe(`${BASE}/embed/wealth-shares`)
  })

  it("builds an iframe with sandbox, lazy loading, and an accessible title", () => {
    const snippet = buildEmbedSnippet(BASE, "wealth-shares", "Who owns wealth in the UK?")
    expect(snippet).toContain(`src="${BASE}/embed/wealth-shares"`)
    expect(snippet).toContain('sandbox="allow-scripts allow-popups"')
    expect(snippet).not.toContain("allow-same-origin") // the no-cookies pledge
    expect(snippet).toContain('loading="lazy"')
    expect(snippet).toContain('title="Who owns wealth in the UK? — WealthLens UK"')
  })

  it("includes the height auto-resize listener scoped to this chart", () => {
    const snippet = buildEmbedSnippet(BASE, "boe-rates", "The cost of borrowing")
    expect(snippet).toContain("<script>")
    expect(snippet).toContain(EMBED_MESSAGE_SOURCE)
    expect(snippet).toContain('d.chart!=="boe-rates"')
    expect(snippet).toContain("</script>")
  })

  it("respects the width option", () => {
    expect(buildEmbedSnippet(BASE, "x", "T", "600")).toContain('width="600"')
    expect(buildEmbedSnippet(BASE, "x", "T")).toContain('width="100%"')
  })
})

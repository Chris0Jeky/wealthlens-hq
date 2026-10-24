import { afterEach, describe, expect, it } from "vitest"
import { containsPreviewOrigin, normalizePrerenderedAssetUrls } from "../prerender-assets"

describe("normalizePrerenderedAssetUrls", () => {
  afterEach(() => {
    document.head.innerHTML = ""
    document.body.innerHTML = ""
  })

  it("removes the preview origin from Vite's runtime preloads and lazy stylesheets", () => {
    document.head.innerHTML = `
      <script type="module" src="http://localhost:4180/wealthlens-hq/assets/index.js"></script>
      <link rel="modulepreload" href="http://localhost:4180/wealthlens-hq/assets/chart.js">
      <link rel="stylesheet" href="http://localhost:4180/wealthlens-hq/assets/chart.css">
    `

    normalizePrerenderedAssetUrls("http://localhost:4180")

    expect(document.querySelector("script")?.getAttribute("src")).toBe(
      "/wealthlens-hq/assets/index.js",
    )
    expect(document.querySelector('[rel="modulepreload"]')?.getAttribute("href")).toBe(
      "/wealthlens-hq/assets/chart.js",
    )
    expect(document.querySelector('[rel="stylesheet"]')?.getAttribute("href")).toBe(
      "/wealthlens-hq/assets/chart.css",
    )
    expect(document.documentElement.outerHTML).not.toContain("localhost:4180")
  })

  it.each(["http://127.0.0.1:4181", "http://[::1]:4182"])(
    "uses the actual preview origin %s and preserves URL query and fragment",
    (origin) => {
      document.head.innerHTML = `<link rel="stylesheet" href="${origin}/wealthlens-hq/assets/page.css?v=1#font">`

      normalizePrerenderedAssetUrls(origin)

      expect(document.querySelector("link")?.getAttribute("href")).toBe(
        "/wealthlens-hq/assets/page.css?v=1#font",
      )
    },
  )

  it("preserves canonical identity, external resources and existing root-relative assets", () => {
    document.head.innerHTML = `
      <link rel="canonical" href="https://chris0jeky.github.io/wealthlens-hq/charts/wealth-shares">
      <link rel="stylesheet" href="https://cdn.example.com/site.css">
      <link rel="stylesheet" href="http://localhost:41800/assets/other.css">
      <script type="module" src="/wealthlens-hq/assets/index.js"></script>
    `
    const before = document.head.innerHTML

    normalizePrerenderedAssetUrls("http://localhost:4180")

    expect(document.head.innerHTML).toBe(before)
  })

  it("also preserves root-hosted deployment paths rather than hard-coding the repository base", () => {
    document.head.innerHTML = '<link rel="stylesheet" href="http://localhost:4180/assets/page.css">'

    normalizePrerenderedAssetUrls("http://localhost:4180")

    expect(document.querySelector("link")?.getAttribute("href")).toBe("/assets/page.css")
  })
})

describe("containsPreviewOrigin", () => {
  it("does not mistake a different port or hostname for the preview origin", () => {
    expect(
      containsPreviewOrigin(
        '<link href="http://localhost:41800/assets/other.css">',
        "http://localhost:4180",
      ),
    ).toBe(false)
    expect(containsPreviewOrigin("https://example.com/assets/app.js", "https://example.co")).toBe(
      false,
    )
  })

  it.each(["/assets/app.js", "?v=1", "#fragment", ""])(
    "detects an exact remaining preview origin before %s",
    (suffix) => {
      expect(
        containsPreviewOrigin(`<img src="http://[::1]:4182${suffix}">`, "http://[::1]:4182"),
      ).toBe(true)
    },
  )
})

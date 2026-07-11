import { describe, it, expect } from "vitest"
import { readFileSync } from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"
import {
  buildPrerenderRoutes,
  routeToOutputFile,
  NOT_FOUND_PROBE_PATH,
} from "../prerender-manifest"
import { buildSitemapXml } from "../sitemap-xml"
import { VALID_CHART_NAMES } from "../../src/constants/charts"

const FRONTEND_ROOT = join(dirname(fileURLToPath(import.meta.url)), "..", "..")

/** The committed static data layer — the same file the prerender reads from dist. */
function committedDatasetSlugs(): string[] {
  const raw = readFileSync(join(FRONTEND_ROOT, "public", "data", "datasets.json"), "utf-8")
  return (JSON.parse(raw) as { datasets: string[] }).datasets
}

describe("buildPrerenderRoutes", () => {
  const routes = buildPrerenderRoutes(committedDatasetSlugs())
  const paths = routes.map((r) => r.path)

  it("covers every chart in VALID_CHART_NAMES (all 12)", () => {
    expect(VALID_CHART_NAMES.size).toBe(12)
    for (const name of VALID_CHART_NAMES) {
      expect(paths).toContain(`/charts/${name}`)
    }
  })

  it("covers the home page, every static page, and all four tools", () => {
    for (const p of [
      "/",
      "/about",
      "/methodology",
      "/data-sources",
      "/contribute",
      "/faq",
      "/simulator",
      "/tools/wealth-calculator",
      "/tools/wealth-scale",
      "/tools/wealth-tax-simulator",
      "/tools/tax-calculator",
    ]) {
      expect(paths).toContain(p)
    }
  })

  it("covers one dataset route per entry in the data layer", () => {
    for (const slug of committedDatasetSlugs()) {
      expect(paths).toContain(`/datasets/${slug}`)
    }
  })

  it("never includes the 404 probe and has no duplicates", () => {
    expect(paths).not.toContain(NOT_FOUND_PROBE_PATH)
    expect(new Set(paths).size).toBe(paths.length)
  })

  it("marks every route for the sitemap (the probe is handled separately)", () => {
    expect(routes.every((r) => r.sitemap)).toBe(true)
  })
})

describe("routeToOutputFile", () => {
  it("maps the root to index.html and the probe to 404.html", () => {
    expect(routeToOutputFile("/")).toBe("index.html")
    expect(routeToOutputFile(NOT_FOUND_PROBE_PATH)).toBe("404.html")
  })

  it("maps routes to flat .html files preserving the URL form (ADR 0001)", () => {
    expect(routeToOutputFile("/charts/wealth-shares")).toBe("charts/wealth-shares.html")
    expect(routeToOutputFile("/tools/wealth-scale")).toBe("tools/wealth-scale.html")
    expect(routeToOutputFile("/faq")).toBe("faq.html")
  })
})

describe("buildSitemapXml", () => {
  const routes = buildPrerenderRoutes(committedDatasetSlugs())
  const xml = buildSitemapXml(routes, "https://chris0jeky.github.io/wealthlens-hq")

  it("lists exactly the sitemap-flagged prerendered routes", () => {
    const locs = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1])
    expect(locs.length).toBe(routes.filter((r) => r.sitemap).length)
    expect(locs).toContain("https://chris0jeky.github.io/wealthlens-hq/")
    expect(locs).toContain("https://chris0jeky.github.io/wealthlens-hq/charts/wealth-shares")
    expect(locs).toContain("https://chris0jeky.github.io/wealthlens-hq/tools/wealth-scale")
    // Non-slash URL form everywhere except the root
    for (const loc of locs.slice(1)) {
      expect(loc.endsWith("/")).toBe(false)
    }
  })

  it("omits lastmod (no fabricated freshness) and is well-formed", () => {
    expect(xml).not.toContain("<lastmod>")
    expect(xml).toContain('<?xml version="1.0" encoding="UTF-8"?>')
    expect(xml).toContain('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    expect(xml.trim().endsWith("</urlset>")).toBe(true)
  })
})

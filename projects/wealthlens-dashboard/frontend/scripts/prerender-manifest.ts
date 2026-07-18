/**
 * Prerender route manifest — the single source for WHICH routes are baked
 * to static HTML (ADR 0001) and for the generated sitemap.xml.
 *
 * The prerender script and the sitemap are produced from the same list in
 * the same run, so "sitemap lists exactly the prerendered set" holds by
 * construction. Keep this file free of browser imports: it runs under Node
 * (tsx) and under vitest.
 */
import { VALID_CHART_NAMES } from "../src/constants/charts"

export interface PrerenderRoute {
  /** Route path as registered in src/router (no base, no trailing slash except "/"). */
  path: string
  /** Include in the generated sitemap.xml (the 404 probe never is). */
  sitemap: boolean
  /** Sitemap crawl hints. */
  changefreq: "monthly" | "yearly"
  priority: number
}

/**
 * Path probed to snapshot the NotFoundView into dist/404.html. It must never
 * match a real route; the router's catch-all renders the 404 page for it.
 */
export const NOT_FOUND_PROBE_PATH = "/__prerender-404-probe__"

const STATIC_ROUTES: PrerenderRoute[] = [
  { path: "/", sitemap: true, changefreq: "monthly", priority: 1.0 },
  { path: "/about", sitemap: true, changefreq: "yearly", priority: 0.6 },
  { path: "/methodology", sitemap: true, changefreq: "monthly", priority: 0.6 },
  { path: "/data-sources", sitemap: true, changefreq: "monthly", priority: 0.7 },
  { path: "/contribute", sitemap: true, changefreq: "yearly", priority: 0.5 },
  { path: "/faq", sitemap: true, changefreq: "monthly", priority: 0.6 },
  { path: "/simulator", sitemap: true, changefreq: "monthly", priority: 0.8 },
  { path: "/tools/wealth-calculator", sitemap: true, changefreq: "monthly", priority: 0.7 },
  { path: "/tools/wealth-scale", sitemap: true, changefreq: "monthly", priority: 0.7 },
  { path: "/tools/wealth-tax-simulator", sitemap: true, changefreq: "monthly", priority: 0.7 },
  { path: "/tools/tax-calculator", sitemap: true, changefreq: "monthly", priority: 0.7 },
]

/**
 * Build the full prerender route list.
 *
 * @param datasetSlugs slugs from the deployed data layer's datasets.json —
 *   passed in (not imported) so the prerender reads the post-build truth in
 *   dist/ and tests can pin fixtures.
 */
export function buildPrerenderRoutes(datasetSlugs: readonly string[]): PrerenderRoute[] {
  const chartRoutes: PrerenderRoute[] = [...VALID_CHART_NAMES].sort().map((name) => ({
    path: `/charts/${name}`,
    sitemap: true,
    changefreq: "monthly" as const,
    priority: 0.8,
  }))

  const datasetRoutes: PrerenderRoute[] = [...datasetSlugs].sort().map((slug) => ({
    path: `/datasets/${slug}`,
    sitemap: true,
    changefreq: "monthly" as const,
    priority: 0.5,
  }))

  // Chrome-free iframe shells (RFC-001f): prerendered so third-party embeds
  // get instant real HTML, but noindex + excluded from the sitemap — they
  // are satellites of the chart articles, not pages to rank.
  const embedRoutes: PrerenderRoute[] = [...VALID_CHART_NAMES].sort().map((name) => ({
    path: `/embed/${name}`,
    sitemap: false,
    changefreq: "monthly" as const,
    priority: 0.1,
  }))

  return [...STATIC_ROUTES, ...chartRoutes, ...datasetRoutes, ...embedRoutes]
}

/**
 * Map a route path to its output file inside dist/.
 *
 * Flat `.html` files (not `route/index.html`): GitHub Pages serves `/faq`
 * from `faq.html` with HTTP 200 and NO redirect, so every existing
 * non-trailing-slash URL keeps its exact form (ADR 0001).
 */
export function routeToOutputFile(path: string): string {
  if (path === "/") return "index.html"
  if (path === NOT_FOUND_PROBE_PATH) return "404.html"
  return `${path.replace(/^\//, "")}.html`
}

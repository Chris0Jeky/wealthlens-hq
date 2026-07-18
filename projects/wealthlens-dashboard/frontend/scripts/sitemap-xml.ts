/**
 * Sitemap XML builder — pure function so vitest can pin the output.
 *
 * Consumes the prerender manifest (ADR 0001): the sitemap always lists
 * exactly the routes that were baked to static HTML, nothing else.
 * No <lastmod>: we don't track per-page content dates, and stamping the
 * build date would fabricate freshness (the reality-check F4 lesson).
 */
import type { PrerenderRoute } from "./prerender-manifest"

function escapeXml(value: string): string {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&apos;")
}

/**
 * @param routes prerendered routes; only `sitemap: true` entries are listed
 * @param siteUrl absolute site origin + base, no trailing slash
 */
export function buildSitemapXml(routes: readonly PrerenderRoute[], siteUrl: string): string {
  const base = siteUrl.replace(/\/$/, "")
  const entries = routes
    .filter((r) => r.sitemap)
    .map((r) => {
      const loc = r.path === "/" ? `${base}/` : `${base}${r.path}`
      return [
        "  <url>",
        `    <loc>${escapeXml(loc)}</loc>`,
        `    <changefreq>${r.changefreq}</changefreq>`,
        `    <priority>${r.priority.toFixed(1)}</priority>`,
        "  </url>",
      ].join("\n")
    })

  return [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ...entries,
    "</urlset>",
    "",
  ].join("\n")
}

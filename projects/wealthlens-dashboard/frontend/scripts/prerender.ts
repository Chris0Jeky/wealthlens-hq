/**
 * Post-build route prerender (ADR 0001 — docs/adr/0001-dashboard-route-prerendering.md).
 *
 * Snapshots every enumerable route of the built app to a static HTML file:
 * starts Vite's preview server over dist/, drives each route in headless
 * chromium, waits for the usePageMeta marker + network idle, and writes the
 * serialised document to dist/<route>.html. Also writes dist/404.html (the
 * baked NotFoundView, used as the GitHub Pages fallback) and dist/sitemap.xml
 * from the same route list, so the sitemap and the prerendered set cannot
 * diverge.
 *
 * Run AFTER `vite build` (with VITE_STATIC_DATA=true so the baked pages carry
 * real data, as on deploy):  npm run build && npm run prerender
 *
 * Fails loudly: any route that doesn't produce meta + meaningful content
 * aborts the build rather than shipping a half-baked page.
 */
import { preview, type PreviewServer } from "vite"
import { chromium, type Browser, type Page } from "@playwright/test"
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs"
import { dirname, join, resolve } from "node:path"
import { fileURLToPath } from "node:url"
import {
  buildPrerenderRoutes,
  routeToOutputFile,
  NOT_FOUND_PROBE_PATH,
  type PrerenderRoute,
} from "./prerender-manifest"
import { buildSitemapXml } from "./sitemap-xml"
import { SITE_URL } from "../src/constants/site"
import { META_MARKER_ATTR } from "../src/composables/usePageMeta"

const FRONTEND_ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "..")
const DIST_DIR = join(FRONTEND_ROOT, "dist")

/** Minimum rendered text length for a page to count as "has content". */
const MIN_MAIN_TEXT_CHARS = 40

interface SnapshotResult {
  path: string
  outputFile: string
  bytes: number
  title: string
}

function readDatasetSlugs(): string[] {
  const datasetsJson = join(DIST_DIR, "data", "datasets.json")
  if (!existsSync(datasetsJson)) {
    throw new Error(
      `${datasetsJson} not found — run \`npm run build\` first (the prerender reads the built data layer).`,
    )
  }
  const parsed = JSON.parse(readFileSync(datasetsJson, "utf-8")) as { datasets?: unknown }
  if (!Array.isArray(parsed.datasets) || parsed.datasets.some((d) => typeof d !== "string")) {
    throw new Error(`${datasetsJson} has no string[] "datasets" key — refusing to guess routes.`)
  }
  return parsed.datasets as string[]
}

async function snapshotRoute(
  page: Page,
  origin: string,
  base: string,
  route: PrerenderRoute | { path: string },
): Promise<SnapshotResult> {
  const url = `${origin}${base.replace(/\/$/, "")}${route.path}`
  await page.goto(url, { waitUntil: "networkidle", timeout: 45_000 })

  // usePageMeta marker: every view sets og:url (directly or by default), so
  // its presence means the route's meta pass has run.
  await page.waitForSelector(`head meta[${META_MARKER_ATTR}][property="og:url"]`, {
    state: "attached",
    timeout: 15_000,
  })
  await page.waitForSelector("#app main", { state: "attached", timeout: 15_000 })

  const checks = await page.evaluate(() => {
    const mainText = document.querySelector("#app main")?.textContent?.trim() ?? ""
    return {
      mainTextLength: mainText.length,
      ogTitleCount: document.head.querySelectorAll('meta[property="og:title"]').length,
      htmlIsDark: document.documentElement.classList.contains("dark"),
      title: document.title,
    }
  })
  if (checks.mainTextLength < MIN_MAIN_TEXT_CHARS) {
    throw new Error(
      `${route.path}: rendered <main> has only ${checks.mainTextLength} chars of text — refusing to bake an empty page.`,
    )
  }
  if (checks.ogTitleCount !== 1) {
    throw new Error(
      `${route.path}: expected exactly 1 og:title after render, found ${checks.ogTitleCount} — meta ownership is broken.`,
    )
  }
  if (checks.htmlIsDark) {
    throw new Error(
      `${route.path}: snapshot browser rendered in dark mode — baked pages must be theme-neutral (the inline head script applies the visitor's theme).`,
    )
  }

  const html = await page.content()
  const outputFile = routeToOutputFile(route.path)
  const outputPath = join(DIST_DIR, outputFile)
  mkdirSync(dirname(outputPath), { recursive: true })
  writeFileSync(outputPath, html, "utf-8")
  return { path: route.path, outputFile, bytes: html.length, title: checks.title }
}

async function main(): Promise<void> {
  if (!existsSync(join(DIST_DIR, "index.html"))) {
    throw new Error(`${DIST_DIR} has no index.html — run \`npm run build\` first.`)
  }

  const routes = buildPrerenderRoutes(readDatasetSlugs())

  let server: PreviewServer | undefined
  let browser: Browser | undefined
  try {
    server = await preview({
      root: FRONTEND_ROOT,
      preview: { port: 4180, strictPort: false, open: false },
    })
    const localUrl = server.resolvedUrls?.local[0]
    if (!localUrl) throw new Error("Vite preview server reported no local URL.")
    const { origin, pathname: base } = new URL(localUrl)
    console.log(`[prerender] preview server at ${localUrl} — ${routes.length} routes + 404`)

    browser = await chromium.launch()
    const context = await browser.newContext({
      viewport: { width: 1280, height: 800 },
      serviceWorkers: "block",
      colorScheme: "light",
      reducedMotion: "reduce",
      locale: "en-GB",
      timezoneId: "Europe/London",
    })
    const page = await context.newPage()

    const results: SnapshotResult[] = []
    for (const route of routes) {
      const result = await snapshotRoute(page, origin, base, route)
      results.push(result)
      console.log(
        `[prerender] ${result.path} -> ${result.outputFile} (${result.bytes} bytes) "${result.title}"`,
      )
    }

    // The GitHub Pages fallback for genuinely unknown routes: the real,
    // noindex Page-not-found view — not a copy of the home shell.
    const notFound = await snapshotRoute(page, origin, base, { path: NOT_FOUND_PROBE_PATH })
    console.log(`[prerender] 404 probe -> ${notFound.outputFile} (${notFound.bytes} bytes)`)

    const sitemap = buildSitemapXml(routes, SITE_URL)
    writeFileSync(join(DIST_DIR, "sitemap.xml"), sitemap, "utf-8")
    console.log(
      `[prerender] sitemap.xml -> ${routes.filter((r) => r.sitemap).length} URLs (matches the prerendered set by construction)`,
    )
    console.log(`[prerender] done: ${results.length} routes + 404.html + sitemap.xml`)
  } finally {
    await browser?.close()
    await server?.close()
  }
}

main().catch((err: unknown) => {
  console.error("[prerender] FAILED:", err instanceof Error ? err.message : err)
  process.exitCode = 1
})

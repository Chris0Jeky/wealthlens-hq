import { watchEffect, onScopeDispose, type Ref, isRef, computed } from "vue"
import { SITE_URL, SITE_NAME } from "@/constants/site"

/**
 * Options for the usePageMeta composable.
 * All fields are optional and can be reactive (Ref) or plain strings.
 */
export interface PageMetaOptions {
  /** Page title — will be combined as "title — WealthLens UK" */
  title?: string | Ref<string | undefined>
  /** Meta description for SEO and social previews */
  description?: string | Ref<string | undefined>
  /** OpenGraph type (defaults to "website") */
  ogType?: string
  /** Canonical page URL — also emitted as <link rel="canonical"> */
  url?: string | Ref<string | undefined>
  /** Social share image URL (absolute URL required by scrapers) */
  image?: string | Ref<string | undefined>
  /** Alt text for the social share image */
  imageAlt?: string | Ref<string | undefined>
  /** Twitter card type: "summary" or "summary_large_image" */
  twitterCard?: "summary" | "summary_large_image"
  /** Robots directive, e.g. "noindex" for the 404 and embed pages */
  robots?: string
}

/**
 * Marker attribute on every element this composable creates.
 *
 * The build-time prerender (ADR 0001) snapshots pages with these elements
 * in place, so crawlers see them baked into the HTML; `main.ts` strips all
 * `[data-wl-meta]` elements before mounting so the mounting view recreates
 * them exactly once. This attribute is the contract between the three —
 * change it in all of usePageMeta, stripPrerenderedMeta, and
 * scripts/prerender.ts together.
 */
export const META_MARKER_ATTR = "data-wl-meta"

/** All 12 per-chart OG images and the fallbacks are rendered at 1200x630
 * by scripts/generate-og-images.ts; the dimension tags below assume it. */
const OG_IMAGE_WIDTH = "1200"
const OG_IMAGE_HEIGHT = "630"

/** Scrapers that find no og:image fall back to nothing — always ship one. */
const DEFAULT_OG_IMAGE = `${SITE_URL}/og/og-default.png`
const DEFAULT_OG_IMAGE_ALT =
  "WealthLens UK — open-source, source-backed data on UK wealth inequality"

/** Unwrap a value that may or may not be a Ref. */
function unwrap(value: string | Ref<string | undefined> | undefined): string | undefined {
  if (value === undefined) return undefined
  if (isRef(value)) return value.value
  return value
}

/**
 * Manages document <head> meta tags for OpenGraph and Twitter Card previews.
 *
 * Sets title, description, canonical link, og:*, and twitter:* tags
 * reactively. Cleans up all managed tags when the component scope is
 * disposed.
 *
 * This composable is the single source of per-route meta: the build-time
 * prerender bakes whatever it sets (ADR 0001), so baked and hydrated meta
 * cannot drift. Do not add per-page meta tags to index.html.
 *
 * Each instance creates and exclusively owns its own elements, preventing
 * cross-contamination during route transitions where two instances may be
 * mounted simultaneously.
 *
 * @example
 * ```ts
 * usePageMeta({
 *   title: 'Wealth Shares — Who owns wealth in the UK?',
 *   description: 'Two centuries of data on UK wealth concentration.',
 *   url: `${SITE_URL}/charts/wealth-shares`,
 *   image: `${SITE_URL}/og/wealth-shares.png`,
 * })
 * ```
 */
export function usePageMeta(options: PageMetaOptions): void {
  // SSR guard: bail out when document is not available (e.g. Node.js / SSR)
  if (typeof document === "undefined") return

  /**
   * Tracks all elements created by this instance for cleanup.
   * Each instance always creates its own elements — never queries for
   * existing ones — to avoid cross-contamination during route transitions.
   */
  const managedElements: (HTMLMetaElement | HTMLLinkElement)[] = []

  /**
   * Create a new <meta> element owned exclusively by this instance.
   * Never queries the DOM for existing elements to prevent multi-instance conflicts.
   */
  function createOwnedMeta(attr: "property" | "name", value: string): HTMLMetaElement {
    const el = document.createElement("meta")
    el.setAttribute(attr, value)
    el.setAttribute(META_MARKER_ATTR, "")
    document.head.appendChild(el)
    managedElements.push(el)
    return el
  }

  /**
   * Find a meta element that this instance previously created (by attribute key).
   * Only searches within managedElements, never the global DOM.
   */
  function findOwned(attr: "property" | "name", key: string): HTMLMetaElement | undefined {
    return managedElements.find(
      (el): el is HTMLMetaElement => el instanceof HTMLMetaElement && el.getAttribute(attr) === key,
    )
  }

  /**
   * Set content on a meta element owned by this instance.
   * If content is truthy, creates or updates the element.
   * If content is falsy, removes the element if it exists.
   * This ensures stale tags are always cleaned up (e.g. imageAlt going from truthy to falsy).
   */
  function setMeta(attr: "property" | "name", key: string, content: string | undefined): void {
    const existing = findOwned(attr, key)
    if (content) {
      if (existing) {
        existing.setAttribute("content", content)
      } else {
        const el = createOwnedMeta(attr, key)
        el.setAttribute("content", content)
      }
    } else {
      // Remove the element if we own it and content is now empty
      if (existing) {
        existing.remove()
        const idx = managedElements.indexOf(existing)
        if (idx !== -1) managedElements.splice(idx, 1)
      }
    }
  }

  /**
   * Set (or remove) the <link rel="canonical"> owned by this instance.
   * Same ownership rules as setMeta.
   */
  function setCanonical(href: string | undefined): void {
    const existing = managedElements.find(
      (el): el is HTMLLinkElement =>
        el instanceof HTMLLinkElement && el.getAttribute("rel") === "canonical",
    )
    if (href) {
      if (existing) {
        existing.setAttribute("href", href)
      } else {
        const el = document.createElement("link")
        el.setAttribute("rel", "canonical")
        el.setAttribute("href", href)
        el.setAttribute(META_MARKER_ATTR, "")
        document.head.appendChild(el)
        managedElements.push(el)
      }
    } else if (existing) {
      existing.remove()
      const idx = managedElements.indexOf(existing)
      if (idx !== -1) managedElements.splice(idx, 1)
    }
  }

  // Use a computed to make all options reactive in one pass
  const resolvedTitle = computed(() => unwrap(options.title))
  const resolvedDescription = computed(() => unwrap(options.description))
  const resolvedUrl = computed(() => unwrap(options.url))
  const resolvedImage = computed(() => unwrap(options.image))
  const resolvedImageAlt = computed(() => unwrap(options.imageAlt))

  watchEffect(() => {
    const title = resolvedTitle.value
    const description = resolvedDescription.value
    const url = resolvedUrl.value
    const image = resolvedImage.value ?? DEFAULT_OG_IMAGE
    const imageAlt =
      resolvedImageAlt.value ?? (resolvedImage.value ? undefined : DEFAULT_OG_IMAGE_ALT)
    const ogType = options.ogType ?? "website"
    const twitterCard = options.twitterCard ?? "summary_large_image"

    // Document title
    const fullTitle = title ? `${title} — ${SITE_NAME}` : SITE_NAME
    document.title = fullTitle

    // Standard meta description
    setMeta("name", "description", description)

    // Canonical link — only when the page declares its URL (the 404 page
    // deliberately doesn't).
    setCanonical(url)

    // OpenGraph tags
    setMeta("property", "og:title", title ?? SITE_NAME)
    setMeta("property", "og:description", description)
    setMeta("property", "og:type", ogType)
    setMeta("property", "og:url", url ?? SITE_URL)
    setMeta("property", "og:image", image)
    setMeta("property", "og:image:width", OG_IMAGE_WIDTH)
    setMeta("property", "og:image:height", OG_IMAGE_HEIGHT)
    setMeta("property", "og:site_name", SITE_NAME)
    setMeta("property", "og:locale", "en_GB")

    // Twitter Card tags
    setMeta("name", "twitter:card", twitterCard)
    setMeta("name", "twitter:title", title ?? SITE_NAME)
    setMeta("name", "twitter:description", description)
    setMeta("name", "twitter:image", image)

    // Image alt — always called unconditionally so stale alt tags are removed
    setMeta("name", "twitter:image:alt", imageAlt)
    setMeta("property", "og:image:alt", imageAlt)

    // Robots directive (e.g. noindex on the 404 page)
    setMeta("name", "robots", options.robots)
  })

  // Cleanup: remove only the elements this instance created
  onScopeDispose(() => {
    for (const el of managedElements) {
      el.remove()
    }
    managedElements.length = 0
    // Restore base title
    document.title = SITE_NAME
  })
}

import { watchEffect, onScopeDispose, type Ref, isRef, computed } from 'vue'

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
  /** Canonical page URL */
  url?: string | Ref<string | undefined>
  /** Social share image URL (absolute URL recommended) */
  image?: string | Ref<string | undefined>
  /** Alt text for the social share image */
  imageAlt?: string | Ref<string | undefined>
  /** Twitter card type: "summary" or "summary_large_image" */
  twitterCard?: 'summary' | 'summary_large_image'
}

const SITE_NAME = 'WealthLens UK'
const BASE_URL = 'https://chris0jeky.github.io/wealthlens-hq'

/** Unwrap a value that may or may not be a Ref. */
function unwrap(value: string | Ref<string | undefined> | undefined): string | undefined {
  if (value === undefined) return undefined
  if (isRef(value)) return value.value
  return value
}

/**
 * Manages document <head> meta tags for OpenGraph and Twitter Card previews.
 *
 * Sets title, description, og:*, and twitter:* meta tags reactively.
 * Cleans up all managed tags when the component scope is disposed.
 *
 * Each instance creates and exclusively owns its own meta elements,
 * preventing cross-contamination during route transitions where two
 * instances may be mounted simultaneously.
 *
 * @example
 * ```ts
 * usePageMeta({
 *   title: 'Wealth Shares — Who owns wealth in the UK?',
 *   description: 'Two centuries of data on UK wealth concentration.',
 *   image: 'https://chris0jeky.github.io/wealthlens-hq/og/wealth-shares.png',
 * })
 * ```
 */
export function usePageMeta(options: PageMetaOptions): void {
  // SSR guard: bail out when document is not available (e.g. Node.js / SSR)
  if (typeof document === 'undefined') return

  /**
   * Tracks all <meta> elements created by this instance for cleanup.
   * Each instance always creates its own elements — never queries for
   * existing ones — to avoid cross-contamination during route transitions.
   */
  const managedElements: HTMLMetaElement[] = []

  /**
   * Create a new <meta> element owned exclusively by this instance.
   * Never queries the DOM for existing elements to prevent multi-instance conflicts.
   */
  function createOwnedMeta(attr: 'property' | 'name', value: string): HTMLMetaElement {
    const el = document.createElement('meta')
    el.setAttribute(attr, value)
    document.head.appendChild(el)
    managedElements.push(el)
    return el
  }

  /**
   * Find a meta element that this instance previously created (by attribute key).
   * Only searches within managedElements, never the global DOM.
   */
  function findOwned(attr: 'property' | 'name', key: string): HTMLMetaElement | undefined {
    return managedElements.find(
      (el) => el.getAttribute(attr) === key,
    )
  }

  /**
   * Set content on a meta element owned by this instance.
   * If content is truthy, creates or updates the element.
   * If content is falsy, removes the element if it exists.
   * This ensures stale tags are always cleaned up (e.g. imageAlt going from truthy to falsy).
   */
  function setMeta(attr: 'property' | 'name', key: string, content: string | undefined): void {
    const existing = findOwned(attr, key)
    if (content) {
      if (existing) {
        existing.setAttribute('content', content)
      } else {
        const el = createOwnedMeta(attr, key)
        el.setAttribute('content', content)
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
    const image = resolvedImage.value
    const imageAlt = resolvedImageAlt.value
    const ogType = options.ogType ?? 'website'
    const twitterCard = options.twitterCard ?? 'summary_large_image'

    // Document title
    const fullTitle = title ? `${title} — ${SITE_NAME}` : SITE_NAME
    document.title = fullTitle

    // Standard meta description
    setMeta('name', 'description', description)

    // OpenGraph tags
    setMeta('property', 'og:title', title ?? SITE_NAME)
    setMeta('property', 'og:description', description)
    setMeta('property', 'og:type', ogType)
    setMeta('property', 'og:url', url ?? BASE_URL)
    setMeta('property', 'og:image', image)
    setMeta('property', 'og:site_name', SITE_NAME)

    // Twitter Card tags
    setMeta('name', 'twitter:card', twitterCard)
    setMeta('name', 'twitter:title', title ?? SITE_NAME)
    setMeta('name', 'twitter:description', description)
    setMeta('name', 'twitter:image', image)

    // Image alt — always called unconditionally so stale alt tags are removed
    setMeta('name', 'twitter:image:alt', imageAlt)
    setMeta('property', 'og:image:alt', imageAlt)
  })

  // Cleanup: remove only the meta elements this instance created
  onScopeDispose(() => {
    for (const el of managedElements) {
      el.remove()
    }
    managedElements.length = 0
    // Restore base title
    document.title = SITE_NAME
  })
}

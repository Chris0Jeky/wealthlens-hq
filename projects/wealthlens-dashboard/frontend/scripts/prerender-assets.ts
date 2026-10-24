/**
 * Runs in the snapshot browser via page.evaluate. Vite's runtime adds absolute
 * preload/stylesheet URLs; baking their preview origin would send visitors to
 * their own localhost. Keep the full deployment pathname, query and fragment.
 * This function must stay self-contained so Playwright can serialize it.
 */
export function normalizePrerenderedAssetUrls(previewOrigin: string): void {
  for (const element of document.querySelectorAll("script[src], link[href]")) {
    const attribute = element.tagName === "SCRIPT" ? "src" : "href"
    const value = element.getAttribute(attribute) ?? ""
    if (!/^(?:https?:)?\/\//.test(value)) continue
    const url = new URL(value, previewOrigin)
    if (url.origin === previewOrigin) {
      element.setAttribute(attribute, `${url.pathname}${url.search}${url.hash}`)
    }
  }
}

/** Reject leftover preview references without confusing another port for it. */
export function containsPreviewOrigin(html: string, previewOrigin: string): boolean {
  const escapedOrigin = previewOrigin.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")
  return new RegExp(`${escapedOrigin}(?=[/?#"'\\s<>]|$)`).test(html)
}

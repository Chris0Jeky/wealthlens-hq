/**
 * Share-intent URLs for a chart page — shared by SharePanel and ShareBar so
 * the two surfaces cannot drift.
 */
export interface ShareLinks {
  twitter: string
  linkedin: string
  bluesky: string
}

export function buildShareLinks(chartUrl: string, chartTitle: string): ShareLinks {
  const encodedUrl = encodeURIComponent(chartUrl)
  const encodedTitle = encodeURIComponent(`${chartTitle} — WealthLens UK`)
  return {
    twitter: `https://twitter.com/intent/tweet?url=${encodedUrl}&text=${encodedTitle}`,
    linkedin: `https://www.linkedin.com/sharing/share-offsite/?url=${encodedUrl}`,
    bluesky: `https://bsky.app/intent/compose?text=${encodedTitle}+${encodedUrl}`,
  }
}

/** Open a share intent in a new window, falling back to same-tab navigation. */
export function openShareIntent(url: string): void {
  const win = window.open(url, "_blank", "noopener,noreferrer")
  if (!win) {
    window.location.href = url
  }
}

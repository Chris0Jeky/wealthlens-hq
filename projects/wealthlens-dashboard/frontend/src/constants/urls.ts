/**
 * Runtime URL bases derived from the current origin + Vite base path.
 * (Absolute-canonical URLs for meta tags use SITE_URL in constants/site.ts;
 * these runtime forms exist so dev/preview links point at the running host.)
 */
export const SITE_BASE_URL = `${window.location.origin}${import.meta.env.BASE_URL.replace(/\/$/, "")}`

export const CHARTS_BASE_URL = `${SITE_BASE_URL}/charts`

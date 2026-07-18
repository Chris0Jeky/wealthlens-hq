/// <reference types="vite/client" />

/**
 * Newest dataset last_updated date ("16 May 2026"), injected at build time
 * by the `define` blocks in vite.config.ts / vitest.config.ts (see
 * scripts/data-vintage.ts). Empty string when no vintage is known.
 */
declare const __WL_DATA_VINTAGE__: string

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  /** Plausible Analytics domain — set to enable tracking (optional). */
  readonly VITE_PLAUSIBLE_DOMAIN?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

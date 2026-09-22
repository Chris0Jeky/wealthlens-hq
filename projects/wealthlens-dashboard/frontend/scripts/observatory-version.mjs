/**
 * Build-time version of the vendored Observatory adapter (public/observatory.js).
 *
 * The version is the first 16 hex chars of the SHA-256 of the adapter bytes,
 * CRLF-normalised to LF exactly as observatory/check.mjs hashes them, so it is a
 * prefix of the digest observatory.lock.json pins. vite.config.ts / vitest.config.ts
 * inject it as `__WL_OBSERVATORY_VERSION__`, and src/utils/observatory.ts requests
 * `observatory.js?v=<version>`: regenerating the adapter changes the URL, so the
 * service worker's cache-first script branch cannot keep serving the old bytes.
 *
 * Plain ESM JavaScript (typed by the sibling .d.mts) so that observatory/check.mjs
 * can import it under plain `node` and prove the version matches the lock.
 */
import { createHash } from "node:crypto"
import { readFileSync } from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

export const OBSERVATORY_VERSION_LENGTH = 16

// Not `new URL(rel, import.meta.url)`: Vite rewrites that pattern into an asset URL.
export const DEFAULT_OBSERVATORY_PATH = join(
  dirname(fileURLToPath(import.meta.url)),
  "..",
  "public",
  "observatory.js",
)

export function observatoryDigest(code) {
  return createHash("sha256").update(code.replaceAll("\r\n", "\n")).digest("hex")
}

export function observatoryVersion(code) {
  return observatoryDigest(code).slice(0, OBSERVATORY_VERSION_LENGTH)
}

/** Throws if the adapter is missing: a build must not ship an unversioned URL silently. */
export function readObservatoryVersion(path = DEFAULT_OBSERVATORY_PATH) {
  return observatoryVersion(readFileSync(path, "utf8"))
}

import { describe, expect, it } from "vitest"
import { readFileSync } from "node:fs"
import { resolve } from "node:path"
import {
  OBSERVATORY_VERSION_LENGTH,
  observatoryDigest,
  observatoryVersion,
  readObservatoryVersion,
} from "../observatory-version.mjs"

// scripts/__tests__ -> frontend -> wealthlens-dashboard -> projects -> repo root
const REPO_ROOT = resolve(__dirname, "../../../../..")
const LOCK_KEY = "projects/wealthlens-dashboard/frontend/public/observatory.js"

// Injected by vitest.config.ts; env.d.ts (which declares it for src/) is not in tsconfig.node.
declare const __WL_OBSERVATORY_VERSION__: string

interface Lock {
  installs: Record<string, { sha256: string }>
}

describe("observatory version", () => {
  it("is the prefix of the digest observatory.lock.json pins for the vendored adapter", () => {
    const lock = JSON.parse(
      readFileSync(resolve(REPO_ROOT, "observatory.lock.json"), "utf8"),
    ) as Lock
    const locked = lock.installs[LOCK_KEY]?.sha256
    expect(locked).toMatch(/^[0-9a-f]{64}$/)
    expect(readObservatoryVersion()).toBe(locked.slice(0, OBSERVATORY_VERSION_LENGTH))
  })

  it("is the value the build injects into the bundle", () => {
    expect(__WL_OBSERVATORY_VERSION__).toBe(readObservatoryVersion())
  })

  it("ignores CRLF vs LF checkouts, as the lock check does", () => {
    expect(observatoryDigest("a\r\nb\r\n")).toBe(observatoryDigest("a\nb\n"))
  })

  it("changes when the adapter bytes change, so a regenerated artifact gets a new URL", () => {
    const inert = 'const config = {"endpoint":""};'
    const active = 'const config = {"endpoint":"https://collector.example"};'
    expect(observatoryVersion(inert)).not.toBe(observatoryVersion(active))
    expect(observatoryVersion(inert)).toHaveLength(OBSERVATORY_VERSION_LENGTH)
  })
})

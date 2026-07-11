import { describe, it, expect } from "vitest"
import { mkdtempSync, writeFileSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { readDataVintage } from "../data-vintage"

function fixture(content: string): string {
  const dir = mkdtempSync(join(tmpdir(), "wl-vintage-"))
  const path = join(dir, "freshness.json")
  writeFileSync(path, content, "utf-8")
  return path
}

describe("readDataVintage", () => {
  it("returns the newest last_updated across datasets, formatted en-GB", () => {
    const path = fixture(
      JSON.stringify({
        a: { last_updated: "2026-05-16", source: "X" },
        b: { last_updated: "2026-03-01", source: "Y" },
        c: { last_updated: "2026-04-10", source: "Z" },
      }),
    )
    expect(readDataVintage(path)).toBe("16 May 2026")
  })

  it("skips missing or malformed dates instead of fabricating one", () => {
    const path = fixture(
      JSON.stringify({
        a: { source: "no date" },
        b: { last_updated: "not-a-date" },
        c: { last_updated: "2026-02-03" },
      }),
    )
    expect(readDataVintage(path)).toBe("3 Feb 2026")
  })

  it("returns empty string when no entry has a parsable date", () => {
    expect(readDataVintage(fixture(JSON.stringify({ a: { source: "X" } })))).toBe("")
  })

  it("returns empty string for a missing file", () => {
    expect(readDataVintage(join(tmpdir(), "does-not-exist", "freshness.json"))).toBe("")
  })

  it("returns empty string for invalid JSON", () => {
    expect(readDataVintage(fixture("not json"))).toBe("")
  })

  it("reads the real committed freshness file to a non-empty vintage", () => {
    expect(readDataVintage()).toMatch(/^\d{1,2} [A-Z][a-z]{2} \d{4}$/)
  })
})

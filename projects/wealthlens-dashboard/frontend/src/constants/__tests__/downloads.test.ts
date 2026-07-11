import { describe, it, expect } from "vitest"
import { csvDownloadUrl, hasCsvDownload, CSV_DOWNLOAD_EXCLUDED } from "../downloads"
import { VALID_CHART_NAMES } from "@/constants/charts"

describe("downloads", () => {
  it("builds base-path-aware CSV URLs", () => {
    expect(csvDownloadUrl("wealth-shares")).toBe("/data/wealth-shares.csv")
  })

  it("excludes only the NC-ND dataset until ACTION-REQUIRED #10 is decided", () => {
    expect([...CSV_DOWNLOAD_EXCLUDED]).toEqual(["generational-wealth"])
    expect(hasCsvDownload("generational-wealth")).toBe(false)
    for (const slug of VALID_CHART_NAMES) {
      if (slug !== "generational-wealth") {
        expect(hasCsvDownload(slug), slug).toBe(true)
      }
    }
  })
})

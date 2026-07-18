import { describe, it, expect, afterEach } from "vitest"
import { stripPrerenderedMeta } from "../prerenderedMeta"

function addHeadEl(tag: string, attrs: Record<string, string>): Element {
  const el = document.createElement(tag)
  for (const [k, v] of Object.entries(attrs)) el.setAttribute(k, v)
  document.head.appendChild(el)
  return el
}

describe("stripPrerenderedMeta", () => {
  afterEach(() => {
    document.head
      .querySelectorAll("[data-wl-meta], meta[property], link[rel='canonical'], meta[name]")
      .forEach((el) => el.remove())
  })

  it("removes exactly the marked elements and reports the count", () => {
    addHeadEl("meta", { property: "og:title", content: "Baked", "data-wl-meta": "" })
    addHeadEl("meta", { name: "description", content: "Baked desc", "data-wl-meta": "" })
    addHeadEl("link", { rel: "canonical", href: "https://example.com/x", "data-wl-meta": "" })
    const invariant = addHeadEl("meta", { name: "theme-color", content: "#C8161D" })

    const removed = stripPrerenderedMeta()

    expect(removed).toBe(3)
    expect(document.head.querySelectorAll("[data-wl-meta]").length).toBe(0)
    // Route-invariant tags without the marker survive
    expect(document.head.contains(invariant)).toBe(true)
  })

  it("is a no-op on a page with no baked meta (dev server)", () => {
    addHeadEl("meta", { name: "viewport", content: "width=device-width" })
    expect(stripPrerenderedMeta()).toBe(0)
    expect(document.head.querySelector('meta[name="viewport"]')).not.toBeNull()
  })
})

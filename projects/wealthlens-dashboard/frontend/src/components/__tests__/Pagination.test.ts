import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import Pagination from "@/components/Pagination.vue"

describe("Pagination", () => {
  it("does not render when totalPages is 1", () => {
    const wrapper = mount(Pagination, { props: { page: 1, totalPages: 1 } })
    expect(wrapper.find("nav").exists()).toBe(false)
  })

  it("renders nav when totalPages > 1", () => {
    const wrapper = mount(Pagination, { props: { page: 1, totalPages: 5 } })
    expect(wrapper.find("nav").exists()).toBe(true)
    expect(wrapper.find("nav").attributes("aria-label")).toBe("Pagination")
  })

  it("uses list semantics for page items", () => {
    const wrapper = mount(Pagination, { props: { page: 1, totalPages: 5 } })
    expect(wrapper.find('ul[role="list"]').exists()).toBe(true)
    expect(wrapper.findAll("li").length).toBeGreaterThan(0)
  })

  it("marks previous as aria-disabled on first page", () => {
    const wrapper = mount(Pagination, { props: { page: 1, totalPages: 5 } })
    const prev = wrapper.find('button[aria-label="Previous page"]')
    expect(prev.attributes("aria-disabled")).toBe("true")
  })

  it("marks next as aria-disabled on last page", () => {
    const wrapper = mount(Pagination, { props: { page: 5, totalPages: 5 } })
    const next = wrapper.find('button[aria-label="Next page"]')
    expect(next.attributes("aria-disabled")).toBe("true")
  })

  it("marks current page with aria-current", () => {
    const wrapper = mount(Pagination, { props: { page: 3, totalPages: 5 } })
    const current = wrapper.find('[aria-current="page"]')
    expect(current.exists()).toBe(true)
    expect(current.text()).toBe("3")
  })

  it("emits update:page on next click", async () => {
    const wrapper = mount(Pagination, { props: { page: 2, totalPages: 5 } })
    const next = wrapper.find('button[aria-label="Next page"]')
    await next.trigger("click")
    expect(wrapper.emitted("update:page")).toEqual([[3]])
  })

  it("emits update:page on previous click", async () => {
    const wrapper = mount(Pagination, { props: { page: 3, totalPages: 5 } })
    const prev = wrapper.find('button[aria-label="Previous page"]')
    await prev.trigger("click")
    expect(wrapper.emitted("update:page")).toEqual([[2]])
  })

  it("emits update:page on page number click", async () => {
    const wrapper = mount(Pagination, { props: { page: 1, totalPages: 5 } })
    const pageBtn = wrapper.find('[aria-label="Page 2"]')
    await pageBtn.trigger("click")
    expect(wrapper.emitted("update:page")).toEqual([[2]])
  })

  it("shows ellipsis for large page ranges", () => {
    const wrapper = mount(Pagination, { props: { page: 5, totalPages: 10 } })
    const ellipsis = wrapper.findAll('[aria-hidden="true"]')
    expect(ellipsis.length).toBeGreaterThanOrEqual(1)
    expect(ellipsis[0].text()).toBe("…")
  })

  it("does not emit when clicking current page", async () => {
    const wrapper = mount(Pagination, { props: { page: 3, totalPages: 5 } })
    const current = wrapper.find('[aria-current="page"]')
    await current.trigger("click")
    expect(wrapper.emitted("update:page")).toBeUndefined()
  })

  it("shows both pages when totalPages is 2", () => {
    const wrapper = mount(Pagination, { props: { page: 1, totalPages: 2 } })
    const buttons = wrapper.findAll('button[aria-label^="Page"]')
    expect(buttons).toHaveLength(2)
    expect(buttons[0].text()).toBe("1")
    expect(buttons[1].text()).toBe("2")
  })

  it("clamps page to totalPages for aria-current", () => {
    const wrapper = mount(Pagination, { props: { page: 99, totalPages: 5 } })
    const current = wrapper.find('[aria-current="page"]')
    expect(current.exists()).toBe(true)
    expect(current.text()).toBe("5")
  })

  it("does not emit on aria-disabled prev click", async () => {
    const wrapper = mount(Pagination, { props: { page: 1, totalPages: 5 } })
    const prev = wrapper.find('button[aria-label="Previous page"]')
    await prev.trigger("click")
    expect(wrapper.emitted("update:page")).toBeUndefined()
  })
})

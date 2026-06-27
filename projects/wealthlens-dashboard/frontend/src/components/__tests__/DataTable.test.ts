import { describe, it, expect } from "vitest"
import { mount } from "@vue/test-utils"
import DataTable from "@/components/DataTable.vue"

const columns = [
  { key: "year", label: "Year", align: "left" as const },
  { key: "value", label: "Value", align: "right" as const },
]

const rows = [
  { year: "2020", value: 1234 },
  { year: "2021", value: 5678 },
]

describe("DataTable", () => {
  it("renders column headers", () => {
    const wrapper = mount(DataTable, { props: { columns, rows } })
    const headers = wrapper.findAll("th")
    expect(headers).toHaveLength(2)
    expect(headers[0].text()).toBe("Year")
    expect(headers[1].text()).toBe("Value")
  })

  it("renders row data", () => {
    const wrapper = mount(DataTable, { props: { columns, rows } })
    const cells = wrapper.findAll("td")
    expect(cells).toHaveLength(4)
    expect(cells[0].text()).toBe("2020")
    expect(cells[1].text()).toBe("1234")
  })

  it("shows empty state when no rows", () => {
    const wrapper = mount(DataTable, { props: { columns, rows: [] } })
    const td = wrapper.find("td")
    expect(td.text()).toContain("No data available")
    expect(td.attributes("colspan")).toBe("2")
  })

  it("renders sr-only caption when provided", () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows, caption: "Wealth data table" },
    })
    const caption = wrapper.find("caption")
    expect(caption.exists()).toBe(true)
    expect(caption.text()).toBe("Wealth data table")
    expect(caption.classes()).toContain("sr-only")
  })

  it("applies right alignment class", () => {
    const wrapper = mount(DataTable, { props: { columns, rows } })
    const headers = wrapper.findAll("th")
    expect(headers[1].classes()).toContain("text-right")
  })

  it("displays dash for null values", () => {
    const wrapper = mount(DataTable, {
      props: { columns, rows: [{ year: "2022", value: null }] },
    })
    const cells = wrapper.findAll("td")
    expect(cells[1].text()).toBe("—")
  })

  it('uses scope="col" on header cells', () => {
    const wrapper = mount(DataTable, { props: { columns, rows } })
    const headers = wrapper.findAll("th")
    headers.forEach((h) => expect(h.attributes("scope")).toBe("col"))
  })

  it("is horizontally scrollable on overflow", () => {
    const wrapper = mount(DataTable, { props: { columns, rows } })
    expect(wrapper.find(".overflow-x-auto").exists()).toBe(true)
  })
})

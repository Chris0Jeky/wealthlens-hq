import { describe, it, expect, vi, beforeEach } from "vitest"
import { mount, flushPromises } from "@vue/test-utils"
import { createPinia, setActivePinia } from "pinia"
import { defineComponent, h } from "vue"
import type { DatasetMetadata } from "@/stores/data"

const mockMetadata: DatasetMetadata[] = [
  {
    name: "wealth-shares",
    description: "Top 1%/10% wealth shares in GB",
    source: "World Inequality Database",
    source_url: "https://wid.world/",
    access_date: "2026-05-14",
    row_count: 150,
    columns: ["year", "percentile", "value"],
  },
  {
    name: "housing-affordability",
    description: "House price to earnings ratio by region",
    source: "ONS",
    source_url: "https://www.ons.gov.uk/housing",
    access_date: "2026-05-14",
    row_count: 500,
    columns: ["year", "region", "ratio"],
  },
  {
    name: "cgt-concentration",
    description: "Capital gains by size of gain",
    source: "HMRC",
    source_url: "https://www.gov.uk/government/statistics/capital-gains-tax-statistics",
    access_date: "2026-05-14",
    row_count: 80,
    columns: ["year", "band", "amount"],
  },
  {
    name: "wealth-by-decile",
    description: "Total net wealth by decile",
    source: "ONS Wealth and Assets Survey",
    source_url: "https://www.ons.gov.uk/wealth",
    access_date: "2026-05-14",
    row_count: 100,
    columns: ["decile", "wealth"],
  },
  {
    name: "productivity-pay",
    description: "UK productivity vs. real pay, indexed to 100 at 1997",
    source: "ONS Labour Productivity & AWE",
    source_url: "https://www.ons.gov.uk/productivity",
    access_date: "2026-05-16",
    row_count: 27,
    columns: ["year", "productivity_index", "pay_index"],
  },
  {
    name: "gdhi-by-region",
    description: "Gross disposable household income per head by region",
    source: "ONS Regional GDHI",
    source_url: "https://www.ons.gov.uk/economy/gdhi",
    access_date: "2026-05-16",
    row_count: 200,
    columns: ["year", "region", "gdhi_per_head"],
  },
  {
    name: "tax-composition",
    description: "UK tax revenue composition: work taxes vs wealth taxes",
    source: "HMRC Tax and NIC Receipts",
    source_url: "https://www.gov.uk/government/statistics/hmrc-tax-receipts",
    access_date: "2026-05-16",
    row_count: 30,
    columns: ["year", "income_tax", "cgt", "iht"],
  },
  {
    name: "boe-rates",
    description: "Bank Rate and CPI annual inflation",
    source: "Bank of England Interactive Analytical Database",
    source_url: "https://www.bankofengland.co.uk/boeapps/database/",
    access_date: "2026-05-16",
    row_count: 300,
    columns: ["date", "bank_rate", "cpi"],
  },
  {
    name: "child-poverty",
    description: "Child poverty rates by UK region (after housing costs)",
    source: "DWP/HMRC Children in Low Income Families",
    source_url: "https://www.gov.uk/government/statistics/children-in-low-income-families",
    access_date: "2026-05-16",
    row_count: 120,
    columns: ["year", "region", "rate"],
  },
  {
    name: "generational-wealth",
    description: "Median household wealth by generation at equivalent ages",
    source: "Resolution Foundation / ONS Wealth and Assets Survey",
    source_url: "https://www.resolutionfoundation.org/publications/",
    access_date: "2026-05-16",
    row_count: 50,
    columns: ["generation", "age", "wealth"],
  },
  {
    // Static (committed-JSON) datasets appended to all-metadata by the generator.
    name: "wage-stagnation",
    description: "UK median real weekly earnings have barely recovered since 2008",
    source: "ONS ASHE",
    source_url:
      "https://www.ons.gov.uk/employmentandlabourmarket/peopleinwork/earningsandworkinghours/datasets/ashe1702",
    access_date: "2026-05-16",
    row_count: 25,
    columns: ["year", "real_weekly"],
  },
  {
    name: "inheritance-tax",
    description: "Share of estates liable for Inheritance Tax in the UK",
    source: "HMRC Inheritance Tax Statistics 2021-22",
    source_url: "https://www.gov.uk/government/statistics/inheritance-tax-statistics",
    access_date: "2026-05-16",
    row_count: 6,
    columns: ["year", "deaths", "liable", "rate_pct", "revenue_bn"],
  },
]

const mockFetchAllMetadata = vi.fn()

vi.mock("@/stores/data", () => ({
  useDataStore: () => ({
    fetchAllMetadata: mockFetchAllMetadata,
  }),
}))

// Stub RouterLink
const RouterLinkStub = defineComponent({
  name: "RouterLink",
  props: { to: { type: String, required: true } },
  setup(props, { slots }) {
    return () => h("a", { href: props.to }, slots.default?.())
  },
})

import DataSourcesView from "@/views/DataSourcesView.vue"

function mountView() {
  return mount(DataSourcesView, {
    global: {
      stubs: { RouterLink: RouterLinkStub },
      plugins: [createPinia()],
    },
  })
}

describe("DataSourcesView", () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    mockFetchAllMetadata.mockReset()
  })

  it("renders the page header", async () => {
    mockFetchAllMetadata.mockResolvedValue(mockMetadata)
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain("Data Sources")
  })

  it("shows loading state initially", () => {
    mockFetchAllMetadata.mockImplementation(() => new Promise(() => {}))
    const wrapper = mountView()
    expect(wrapper.text()).toContain("Loading data sources...")
  })

  it("shows error state when fetch fails", async () => {
    mockFetchAllMetadata.mockRejectedValue(new Error("Server unavailable"))
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain("Server unavailable")
  })

  it("renders all 12 datasets after loading", async () => {
    mockFetchAllMetadata.mockResolvedValue(mockMetadata)
    const wrapper = mountView()
    await flushPromises()
    // Should mention all 12 sources (10 CSV-pipeline + 2 static-JSON datasets)
    expect(wrapper.text()).toContain("Showing 12 of 12 data sources")
  })

  it("shows source links as external links with correct URLs", async () => {
    mockFetchAllMetadata.mockResolvedValue(mockMetadata)
    const wrapper = mountView()
    await flushPromises()
    // Check that source URLs are present as links
    const links = wrapper.findAll('a[target="_blank"]')
    const hrefs = links.map((l) => l.attributes("href"))
    expect(hrefs).toContain("https://wid.world/")
    expect(hrefs).toContain("https://www.gov.uk/government/statistics/capital-gains-tax-statistics")
  })

  it("shows source organisation names", async () => {
    mockFetchAllMetadata.mockResolvedValue(mockMetadata)
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain("World Inequality Database")
    expect(wrapper.text()).toContain("HMRC")
    expect(wrapper.text()).toContain("Bank of England")
  })

  it("shows access dates for datasets", async () => {
    mockFetchAllMetadata.mockResolvedValue(mockMetadata)
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain("2026-05-14")
    expect(wrapper.text()).toContain("2026-05-16")
  })

  it("filters datasets when searching", async () => {
    mockFetchAllMetadata.mockResolvedValue(mockMetadata)
    const wrapper = mountView()
    await flushPromises()

    const input = wrapper.find('input[type="search"]')
    await input.setValue("wealth")
    // Trigger debounce by directly setting the model
    await wrapper.find('input[type="search"]').trigger("input")
    // Wait for the debounce (200ms)
    await new Promise((r) => setTimeout(r, 250))
    await flushPromises()

    // "wealth" matches wealth-shares, wealth-by-decile, generational-wealth,
    // and tax-composition (description contains "wealth taxes") — 4 of 12 total.
    expect(wrapper.text()).toContain("Showing 4 of 12 data sources")
  })

  it("shows no results message when filter matches nothing", async () => {
    mockFetchAllMetadata.mockResolvedValue(mockMetadata)
    const wrapper = mountView()
    await flushPromises()

    const input = wrapper.find('input[type="search"]')
    await input.setValue("xyznonexistent")
    await wrapper.find('input[type="search"]').trigger("input")
    await new Promise((r) => setTimeout(r, 250))
    await flushPromises()

    expect(wrapper.text()).toContain("No data sources match your search")
  })

  it("includes transparency commitment text", async () => {
    mockFetchAllMetadata.mockResolvedValue(mockMetadata)
    const wrapper = mountView()
    await flushPromises()
    expect(wrapper.text()).toContain("committed to full data transparency")
  })

  it("renders table headers on desktop view", async () => {
    mockFetchAllMetadata.mockResolvedValue(mockMetadata)
    const wrapper = mountView()
    await flushPromises()
    const headers = wrapper.findAll("th")
    const headerTexts = headers.map((h) => h.text())
    expect(headerTexts).toContain("Dataset")
    expect(headerTexts).toContain("Source")
    expect(headerTexts).toContain("Licence")
    expect(headerTexts).toContain("Frequency")
    expect(headerTexts).toContain("Accessed")
  })
})

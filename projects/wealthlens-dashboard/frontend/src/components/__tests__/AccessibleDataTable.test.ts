import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import AccessibleDataTable from "@/components/AccessibleDataTable.vue";

describe("AccessibleDataTable", () => {
  const sampleRows = [
    { year: 2020, region: "London", value: 1234567.89 },
    { year: 2021, region: "Manchester", value: null },
    { year: 2022, region: "Edinburgh", value: 42000 },
  ];

  const defaultProps = {
    rows: sampleRows,
    columns: ["year", "region", "value"],
    caption: "Wealth distribution by region, 2020-2022",
    numericColumns: ["value"],
  };

  it("renders caption text", () => {
    const wrapper = mount(AccessibleDataTable, { props: defaultProps });
    const caption = wrapper.find("caption");
    expect(caption.exists()).toBe(true);
    expect(caption.text()).toBe(defaultProps.caption);
  });

  it("renders correct number of columns in header", () => {
    const wrapper = mount(AccessibleDataTable, { props: defaultProps });
    const headers = wrapper.findAll("th");
    expect(headers).toHaveLength(defaultProps.columns.length);
    expect(headers[0].text()).toBe("year");
    expect(headers[1].text()).toBe("region");
    expect(headers[2].text()).toBe("value");
  });

  it("renders correct number of data rows", () => {
    const wrapper = mount(AccessibleDataTable, { props: defaultProps });
    const rows = wrapper.findAll("tbody tr");
    expect(rows).toHaveLength(sampleRows.length);
  });

  it("null values display as em-dash", () => {
    const wrapper = mount(AccessibleDataTable, { props: defaultProps });
    const cells = wrapper.findAll("tbody td");
    // The null value is in row index 1, column index 2 (value column)
    // Row 1 cells start at index 3 (3 columns per row): cell index 5 is value
    const nullCell = cells[5];
    expect(nullCell.text()).toBe("—");
  });

  it("non-finite numbers (NaN/Infinity) display as em-dash, not the literal 'NaN'", () => {
    const wrapper = mount(AccessibleDataTable, {
      props: {
        rows: [{ year: 2020, region: "London", value: Number.NaN }],
        columns: ["year", "region", "value"],
        caption: "c",
        numericColumns: ["value"],
      },
    });
    const cells = wrapper.findAll("tbody td");
    expect(cells[2].text()).toBe("—");
    expect(wrapper.text()).not.toContain("NaN");
  });

  it("details element is collapsed by default (no open attribute)", () => {
    const wrapper = mount(AccessibleDataTable, { props: defaultProps });
    const details = wrapper.find("details");
    expect(details.exists()).toBe(true);
    expect(details.attributes("open")).toBeUndefined();
  });

  it("numbers are formatted with locale", () => {
    const wrapper = mount(AccessibleDataTable, { props: defaultProps });
    const cells = wrapper.findAll("tbody td");
    // First row, third column (value = 1234567.89) → cell index 2
    const numberCell = cells[2];
    // en-GB locale formats with commas: 1,234,567.89
    expect(numberCell.text()).toBe((1234567.89).toLocaleString("en-GB"));
  });

  it("uses th elements with scope=col for accessibility", () => {
    const wrapper = mount(AccessibleDataTable, { props: defaultProps });
    const headers = wrapper.findAll("th");
    for (const header of headers) {
      expect(header.attributes("scope")).toBe("col");
    }
  });

  it("table element uses native semantics without redundant role", () => {
    const wrapper = mount(AccessibleDataTable, { props: defaultProps });
    const table = wrapper.find("table");
    expect(table.exists()).toBe(true);
    expect(table.attributes("role")).toBeUndefined();
  });

  it("year column renders without locale formatting when not in numericColumns", () => {
    const wrapper = mount(AccessibleDataTable, { props: defaultProps });
    const cells = wrapper.findAll("tbody td");
    expect(cells[0].text()).toBe("2020");
  });
});

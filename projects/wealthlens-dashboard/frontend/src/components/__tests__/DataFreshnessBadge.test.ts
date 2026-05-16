import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount, flushPromises } from "@vue/test-utils";
import DataFreshnessBadge from "@/components/DataFreshnessBadge.vue";
import { _resetCache } from "@/composables/useDataFreshness";

/** Helper: builds a freshness.json response with a given date for "wealth-shares". */
function mockFreshnessResponse(dateStr: string, source = "ONS Wealth and Assets Survey") {
  return {
    "wealth-shares": { last_updated: dateStr, source },
  };
}

/** Returns an ISO date string for N days ago from today. */
function daysAgoDate(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() - days);
  return d.toISOString().split("T")[0];
}

describe("DataFreshnessBadge", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    _resetCache();
  });

  it("renders date for known dataset", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse(daysAgoDate(2)),
    } as Response);

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    });
    await flushPromises();

    expect(wrapper.text()).toContain("Data:");
    expect(wrapper.text()).toContain("2 days ago");
  });

  it("shows green dot when data is less than 7 days old", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse(daysAgoDate(3)),
    } as Response);

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    });
    await flushPromises();

    const dot = wrapper.find(".freshness-badge__dot");
    expect(dot.classes()).toContain("freshness-badge__dot--green");
  });

  it("shows amber dot when data is 7–30 days old", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse(daysAgoDate(14)),
    } as Response);

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    });
    await flushPromises();

    const dot = wrapper.find(".freshness-badge__dot");
    expect(dot.classes()).toContain("freshness-badge__dot--amber");
  });

  it("shows red dot when data is more than 30 days old", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse(daysAgoDate(45)),
    } as Response);

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    });
    await flushPromises();

    const dot = wrapper.find(".freshness-badge__dot");
    expect(dot.classes()).toContain("freshness-badge__dot--red");
  });

  it("gracefully handles missing dataset (renders nothing)", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse(daysAgoDate(1)),
    } as Response);

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "nonexistent-dataset" },
    });
    await flushPromises();

    expect(wrapper.find(".freshness-badge").exists()).toBe(false);
  });

  it("gracefully handles fetch failure (renders nothing)", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValueOnce(new Error("Network error"));

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    });
    await flushPromises();

    expect(wrapper.find(".freshness-badge").exists()).toBe(false);
  });

  it("shows relative time - today", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse(daysAgoDate(0)),
    } as Response);

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    });
    await flushPromises();

    expect(wrapper.text()).toContain("today");
  });

  it("shows relative time - weeks ago", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse(daysAgoDate(21)),
    } as Response);

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    });
    await flushPromises();

    expect(wrapper.text()).toContain("3 weeks ago");
  });

  it("has tooltip with full date and source", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse(daysAgoDate(5), "HMRC"),
    } as Response);

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    });
    await flushPromises();

    const badge = wrapper.find(".freshness-badge");
    const title = badge.attributes("title");
    expect(title).toContain("Last updated:");
    expect(title).toContain("Source: HMRC");
  });

  it("has accessible role and aria-label", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValueOnce({
      ok: true,
      json: async () => mockFreshnessResponse(daysAgoDate(2)),
    } as Response);

    const wrapper = mount(DataFreshnessBadge, {
      props: { dataset: "wealth-shares" },
    });
    await flushPromises();

    const badge = wrapper.find('[role="status"]');
    expect(badge.exists()).toBe(true);
    expect(badge.attributes("aria-label")).toContain("Data updated");
  });
});

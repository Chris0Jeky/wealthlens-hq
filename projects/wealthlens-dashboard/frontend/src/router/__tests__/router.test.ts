import { describe, it, expect } from "vitest";
import router from "@/router/index";

describe("Router configuration", () => {
  it('resolves / to the "home" route', () => {
    const resolved = router.resolve("/");
    expect(resolved.name).toBe("home");
  });

  it('resolves /charts/wealth-shares to the "chart" route with correct param', () => {
    const resolved = router.resolve("/charts/wealth-shares");
    expect(resolved.name).toBe("chart");
    expect(resolved.params.name).toBe("wealth-shares");
  });

  it('resolves /charts/housing-affordability to the "chart" route with correct param', () => {
    const resolved = router.resolve("/charts/housing-affordability");
    expect(resolved.name).toBe("chart");
    expect(resolved.params.name).toBe("housing-affordability");
  });

  it('resolves an unknown path to the "not-found" catch-all route', () => {
    const resolved = router.resolve("/nonexistent");
    expect(resolved.name).toBe("not-found");
  });

  it("has the expected number of route definitions", () => {
    // home, dataset-detail, chart, methodology, about (x2), contribute,
    // wealth-calculator, wealth-scale, not-found catch-all
    expect(router.getRoutes()).toHaveLength(9);
  });

  it('the "chart" route has a dynamic :name param', () => {
    const chartRoute = router.getRoutes().find((r) => r.name === "chart");
    expect(chartRoute).toBeDefined();
    expect(chartRoute!.path).toBe("/charts/:name");
  });
});

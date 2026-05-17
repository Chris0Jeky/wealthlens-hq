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
    // home, dataset-detail, chart, methodology, data-sources, about,
    // contribute, wealth-calculator, not-found catch-all
    expect(router.getRoutes()).toHaveLength(9);
  });

  it('resolves /data-sources to the "data-sources" route', () => {
    const resolved = router.resolve("/data-sources");
    expect(resolved.name).toBe("data-sources");
  });

  it('the "chart" route has a dynamic :name param', () => {
    const chartRoute = router.getRoutes().find((r) => r.name === "chart");
    expect(chartRoute).toBeDefined();
    expect(chartRoute!.path).toBe("/charts/:name");
  });
});

describe("Route-level code splitting", () => {
  it("all route components use lazy loading (function components)", () => {
    const routes = router.getRoutes();
    for (const route of routes) {
      const components = route.components ?? {};
      for (const [, comp] of Object.entries(components)) {
        expect(typeof comp).toBe("function");
      }
    }
  });
});

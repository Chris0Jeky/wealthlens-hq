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
    // contribute, wealth-calculator, faq, wealth-tax-simulator,
    // tax-calculator, not-found catch-all
    expect(router.getRoutes()).toHaveLength(12);
  });

  it('resolves /tools/wealth-tax-simulator to the "wealth-tax-simulator" route', () => {
    const resolved = router.resolve("/tools/wealth-tax-simulator");
    expect(resolved.name).toBe("wealth-tax-simulator");
  });

  it('resolves /data-sources to the "data-sources" route', () => {
    const resolved = router.resolve("/data-sources");
    expect(resolved.name).toBe("data-sources");
  });

  it('resolves /faq to the "faq" route', () => {
    const resolved = router.resolve("/faq");
    expect(resolved.name).toBe("faq");
  });

  it('resolves /tools/tax-calculator to the "tax-calculator" route', () => {
    const resolved = router.resolve("/tools/tax-calculator");
    expect(resolved.name).toBe("tax-calculator");
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

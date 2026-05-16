import { describe, it, expect } from "vitest";
import { readFileSync } from "fs";
import { resolve } from "path";
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
    // wealth-calculator, not-found catch-all
    expect(router.getRoutes()).toHaveLength(8);
  });

  it('the "chart" route has a dynamic :name param', () => {
    const chartRoute = router.getRoutes().find((r) => r.name === "chart");
    expect(chartRoute).toBeDefined();
    expect(chartRoute!.path).toBe("/charts/:name");
  });
});

describe("Route-level code splitting", () => {
  it("all route components use dynamic imports (lazy loading)", () => {
    // Read the router source to verify no static component imports are used.
    // Static imports would appear as: component: SomeView (an identifier),
    // whereas dynamic imports appear as: component: () => import(...)
    const routerSource = readFileSync(
      resolve(__dirname, "../index.ts"),
      "utf-8",
    );

    // Find all component: lines — they should all use arrow function + import()
    const componentLines = routerSource
      .split("\n")
      .filter((line) => line.trim().startsWith("component:"));

    expect(componentLines.length).toBeGreaterThan(0);

    for (const line of componentLines) {
      expect(line).toMatch(
        /component:\s*\(\)\s*=>\s*import\(/,
      );
    }
  });

  it("router source does not statically import any view components", () => {
    const routerSource = readFileSync(
      resolve(__dirname, "../index.ts"),
      "utf-8",
    );

    // Static view imports would look like: import XView from '../views/...'
    const staticViewImports = routerSource
      .split("\n")
      .filter((line) => /^import\s+\w+.*from\s+['"].*views\//.test(line.trim()));

    expect(staticViewImports).toHaveLength(0);
  });
});

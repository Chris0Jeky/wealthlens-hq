import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";

describe("prefetchRouteComponent", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.resetModules();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("calls the import function after timeout (setTimeout fallback)", async () => {
    const { prefetchRouteComponent } = await import("@/utils/prefetch");
    const importFn = vi.fn().mockResolvedValue({});

    prefetchRouteComponent(importFn);

    expect(importFn).not.toHaveBeenCalled();
    vi.advanceTimersByTime(4000);
    expect(importFn).toHaveBeenCalledTimes(1);
  });

  it("deduplicates — same function is only prefetched once", async () => {
    const { prefetchRouteComponent } = await import("@/utils/prefetch");
    const importFn = vi.fn().mockResolvedValue({});

    prefetchRouteComponent(importFn);
    prefetchRouteComponent(importFn);

    vi.advanceTimersByTime(4000);
    expect(importFn).toHaveBeenCalledTimes(1);
  });

  it("uses requestIdleCallback when available", async () => {
    const { prefetchRouteComponent } = await import("@/utils/prefetch");
    const importFn = vi.fn().mockResolvedValue({});
    const mockRIC = vi.fn((cb: () => void) => {
      cb();
      return 1;
    });

    Object.defineProperty(window, "requestIdleCallback", {
      value: mockRIC,
      writable: true,
      configurable: true,
    });

    prefetchRouteComponent(importFn);

    expect(mockRIC).toHaveBeenCalled();
    expect(importFn).toHaveBeenCalledTimes(1);

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    delete (window as any).requestIdleCallback;
  });

  it("does not throw if the import function rejects", async () => {
    const { prefetchRouteComponent } = await import("@/utils/prefetch");
    const importFn = vi.fn().mockRejectedValue(new Error("Network error"));

    prefetchRouteComponent(importFn);
    vi.advanceTimersByTime(4000);

    expect(importFn).toHaveBeenCalledTimes(1);
  });

  it("respects custom timeout", async () => {
    const { prefetchRouteComponent } = await import("@/utils/prefetch");
    const importFn = vi.fn().mockResolvedValue({});

    prefetchRouteComponent(importFn, 1000);

    vi.advanceTimersByTime(999);
    expect(importFn).not.toHaveBeenCalled();

    vi.advanceTimersByTime(1);
    expect(importFn).toHaveBeenCalledTimes(1);
  });
});

describe("prefetchRouteComponents", () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.resetModules();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("staggers prefetch timeouts for each component", async () => {
    const { prefetchRouteComponents } = await import("@/utils/prefetch");
    const fn1 = vi.fn().mockResolvedValue({});
    const fn2 = vi.fn().mockResolvedValue({});
    const fn3 = vi.fn().mockResolvedValue({});

    prefetchRouteComponents([fn1, fn2, fn3]);

    vi.advanceTimersByTime(4000);
    expect(fn1).toHaveBeenCalledTimes(1);
    expect(fn2).not.toHaveBeenCalled();
    expect(fn3).not.toHaveBeenCalled();

    vi.advanceTimersByTime(500);
    expect(fn2).toHaveBeenCalledTimes(1);
    expect(fn3).not.toHaveBeenCalled();

    vi.advanceTimersByTime(500);
    expect(fn3).toHaveBeenCalledTimes(1);
  });
});

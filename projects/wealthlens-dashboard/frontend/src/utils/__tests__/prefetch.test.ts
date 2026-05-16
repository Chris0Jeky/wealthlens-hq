import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { prefetchRouteComponent, prefetchRouteComponents } from "@/utils/prefetch";

describe("prefetchRouteComponent", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("calls the import function via requestIdleCallback", () => {
    const importFn = vi.fn().mockResolvedValue({});

    // jsdom does not have requestIdleCallback, so it will fall through to setTimeout
    prefetchRouteComponent(importFn);

    expect(importFn).not.toHaveBeenCalled();

    // Advance past the default timeout
    vi.advanceTimersByTime(4000);

    expect(importFn).toHaveBeenCalledTimes(1);
  });

  it("uses requestIdleCallback when available", () => {
    const importFn = vi.fn().mockResolvedValue({});
    const mockRIC = vi.fn((cb: () => void) => {
      cb();
      return 1;
    });

    // Temporarily add requestIdleCallback
    Object.defineProperty(window, "requestIdleCallback", {
      value: mockRIC,
      writable: true,
      configurable: true,
    });

    prefetchRouteComponent(importFn);

    expect(mockRIC).toHaveBeenCalled();
    expect(importFn).toHaveBeenCalledTimes(1);

    // Clean up
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    delete (window as any).requestIdleCallback;
  });

  it("does not throw if the import function rejects", () => {
    const importFn = vi.fn().mockRejectedValue(new Error("Network error"));

    prefetchRouteComponent(importFn);
    vi.advanceTimersByTime(4000);

    // Should not throw — errors are silently caught
    expect(importFn).toHaveBeenCalledTimes(1);
  });

  it("respects custom timeout", () => {
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
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it("prefetches multiple components", () => {
    const fn1 = vi.fn().mockResolvedValue({});
    const fn2 = vi.fn().mockResolvedValue({});
    const fn3 = vi.fn().mockResolvedValue({});

    prefetchRouteComponents([fn1, fn2, fn3]);

    vi.advanceTimersByTime(4000);

    expect(fn1).toHaveBeenCalledTimes(1);
    expect(fn2).toHaveBeenCalledTimes(1);
    expect(fn3).toHaveBeenCalledTimes(1);
  });
});

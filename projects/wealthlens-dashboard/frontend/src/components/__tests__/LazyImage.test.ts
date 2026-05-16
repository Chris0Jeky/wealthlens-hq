import { describe, it, expect, vi, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import LazyImage from "../LazyImage.vue";

const mockObserve = vi.fn();
const mockDisconnect = vi.fn();

beforeEach(() => {
  mockObserve.mockClear();
  mockDisconnect.mockClear();

  const MockIO = vi.fn(function (this: any, callback: any) {
    this.observe = mockObserve.mockImplementation(() => {
      callback([{ isIntersecting: true }]);
    });
    this.disconnect = mockDisconnect;
    this.unobserve = vi.fn();
  });
  global.IntersectionObserver = MockIO as unknown as typeof IntersectionObserver;
});

describe("LazyImage", () => {
  it("renders an img element", () => {
    const wrapper = mount(LazyImage, {
      props: { src: "/test.png", alt: "Test image" },
    });
    expect(wrapper.find("img").exists()).toBe(true);
  });

  it("sets alt text", () => {
    const wrapper = mount(LazyImage, {
      props: { src: "/test.png", alt: "A chart" },
    });
    expect(wrapper.find("img").attributes("alt")).toBe("A chart");
  });

  it("sets src when in view", async () => {
    const wrapper = mount(LazyImage, {
      props: { src: "/chart.png", alt: "Chart" },
    });
    await wrapper.vm.$nextTick();
    expect(wrapper.find("img").attributes("src")).toBe("/chart.png");
  });

  it("applies loaded class after load event", async () => {
    const wrapper = mount(LazyImage, {
      props: { src: "/img.png", alt: "Image" },
    });
    await wrapper.find("img").trigger("load");
    expect(wrapper.find("img").classes()).toContain("lazy-img--loaded");
  });

  it("passes width and height attributes", () => {
    const wrapper = mount(LazyImage, {
      props: { src: "/img.png", alt: "Img", width: 600, height: 400 },
    });
    expect(wrapper.find("img").attributes("width")).toBe("600");
    expect(wrapper.find("img").attributes("height")).toBe("400");
  });

  it("disconnects observer on unmount", () => {
    const wrapper = mount(LazyImage, {
      props: { src: "/img.png", alt: "Img" },
    });
    wrapper.unmount();
    expect(mockDisconnect).toHaveBeenCalled();
  });
});

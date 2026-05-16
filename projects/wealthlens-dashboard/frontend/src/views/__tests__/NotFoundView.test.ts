import { describe, it, expect } from "vitest";
import { mount, RouterLinkStub } from "@vue/test-utils";
import NotFoundView from "@/views/NotFoundView.vue";

describe("NotFoundView", () => {
  function mountView() {
    return mount(NotFoundView, {
      global: { stubs: { RouterLink: RouterLinkStub } },
    });
  }

  it("renders a 404 heading", () => {
    const wrapper = mountView();
    expect(wrapper.find("h1").text()).toBe("404");
  });

  it("renders a descriptive subheading", () => {
    const wrapper = mountView();
    expect(wrapper.find("h2").text()).toBe("Page not found");
  });

  it("has a link back to the dashboard", () => {
    const wrapper = mountView();
    const link = wrapper.findComponent(RouterLinkStub);
    expect(link.exists()).toBe(true);
    expect(link.props("to")).toBe("/");
  });
});

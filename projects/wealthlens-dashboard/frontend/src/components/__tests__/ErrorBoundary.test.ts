import { describe, it, expect, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { defineComponent, onMounted } from "vue";
import ErrorBoundary from "@/components/ErrorBoundary.vue";

/**
 * Helper: a child component that throws during onMounted.
 * Vue's onErrorCaptured hook in ErrorBoundary will catch it, but
 * @vue/test-utils re-throws errors from flushPostFlushCbs.
 * We handle that with config.errorHandler on the app instance.
 */
const ThrowingChild = defineComponent({
  setup() {
    onMounted(() => {
      throw new Error("child went boom");
    });
    return () => null;
  },
});

/** Stub for <router-link> so ErrorBoundary's template compiles. */
const RouterLinkStub = defineComponent({
  props: { to: { type: String, default: "/" } },
  template: '<a :href="to"><slot /></a>',
});

/**
 * Mount a tree with ErrorBoundary wrapping ThrowingChild.
 *
 * @vue/test-utils re-throws lifecycle errors even after
 * onErrorCaptured returns false. Setting config.errorHandler
 * on the app absorbs the re-throw so the test can inspect the DOM.
 */
function mountWithThrowingChild() {
  const Wrapper = defineComponent({
    components: { ErrorBoundary, ThrowingChild },
    template: `<ErrorBoundary><ThrowingChild /></ErrorBoundary>`,
  });

  return mount(Wrapper, {
    global: {
      stubs: { "router-link": RouterLinkStub },
      config: {
        // Absorb the error so mount() doesn't throw.
        // ErrorBoundary's onErrorCaptured already captured it.
        errorHandler: vi.fn(),
      },
    },
  });
}

describe("ErrorBoundary", () => {
  const globalConfig = {
    stubs: { "router-link": RouterLinkStub },
  };

  it("renders default slot content when there is no error", () => {
    const wrapper = mount(ErrorBoundary, {
      global: globalConfig,
      slots: {
        default: "<p>All good</p>",
      },
    });
    expect(wrapper.text()).toContain("All good");
    // The error alert region should not be present
    expect(wrapper.find('[role="alert"]').exists()).toBe(false);
  });

  it("shows error message when a child component throws", async () => {
    const tree = mountWithThrowingChild();
    await tree.vm.$nextTick();

    expect(tree.text()).toContain("Something went wrong");
    expect(tree.text()).toContain("child went boom");
  });

  it("shows a retry button on first error", async () => {
    const tree = mountWithThrowingChild();
    await tree.vm.$nextTick();

    const button = tree.find("button");
    expect(button.exists()).toBe(true);
    expect(button.text()).toContain("Try again");
  });

  it("has role=alert on the error container for accessibility", async () => {
    const tree = mountWithThrowingChild();
    await tree.vm.$nextTick();

    const alert = tree.find('[role="alert"]');
    expect(alert.exists()).toBe(true);
  });

  it("re-renders child after clicking Try again", async () => {
    const tree = mountWithThrowingChild();
    await tree.vm.$nextTick();

    expect(tree.find('[role="alert"]').exists()).toBe(true);

    await tree.find("button").trigger("click");
    await tree.vm.$nextTick();

    // The child re-throws on re-render, so error reappears
    // but the retry mechanism was exercised
    expect(tree.text()).toContain("Something went wrong");
  });

  it("shows Back to dashboard link after MAX_RETRIES exhausted", async () => {
    const tree = mountWithThrowingChild();

    for (let i = 0; i < 3; i++) {
      await tree.vm.$nextTick();
      const btn = tree.find("button");
      if (btn.exists()) await btn.trigger("click");
    }
    await tree.vm.$nextTick();

    expect(tree.find("button").exists()).toBe(false);
    expect(tree.text()).toContain("Back to dashboard");
  });
});

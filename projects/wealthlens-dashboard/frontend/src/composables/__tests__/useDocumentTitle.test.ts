import { describe, it, expect, beforeEach } from "vitest"
import { ref, nextTick } from "vue"
import { useDocumentTitle } from "../useDocumentTitle"
import { mount } from "@vue/test-utils"
import { defineComponent } from "vue"

function createComponent(initial?: string) {
  return defineComponent({
    setup() {
      const title = ref<string | undefined>(initial)
      useDocumentTitle(title)
      return { title }
    },
    template: "<div />",
  })
}

describe("useDocumentTitle", () => {
  beforeEach(() => {
    document.title = ""
  })

  it("sets base title when title ref is undefined", () => {
    mount(createComponent())
    expect(document.title).toBe("WealthLens UK")
  })

  it("sets combined title when title ref has a value", () => {
    mount(createComponent("Charts"))
    expect(document.title).toBe("Charts — WealthLens UK")
  })

  it("updates document title reactively", async () => {
    const wrapper = mount(createComponent("Page 1"))
    expect(document.title).toBe("Page 1 — WealthLens UK")
    wrapper.vm.title = "Page 2"
    await nextTick()
    expect(document.title).toBe("Page 2 — WealthLens UK")
  })

  it("reverts to base when title becomes undefined", async () => {
    const wrapper = mount(createComponent("Something"))
    wrapper.vm.title = undefined
    await nextTick()
    expect(document.title).toBe("WealthLens UK")
  })
})

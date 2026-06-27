import { mount } from "@vue/test-utils"
import { afterEach, describe, expect, it, vi } from "vitest"
import i18n from "@/i18n"
import LanguageSwitcher from "../LanguageSwitcher.vue"

const localStorageDescriptor = Object.getOwnPropertyDescriptor(window, "localStorage")

function mockUnavailableLocalStorage() {
  const storage = {
    getItem: vi.fn(() => null),
    setItem: vi.fn(() => {
      throw new DOMException("Storage blocked", "SecurityError")
    }),
    removeItem: vi.fn(),
    clear: vi.fn(),
  }

  Object.defineProperty(window, "localStorage", {
    configurable: true,
    value: storage,
  })

  return storage
}

describe("LanguageSwitcher", () => {
  afterEach(() => {
    if (localStorageDescriptor) {
      Object.defineProperty(window, "localStorage", localStorageDescriptor)
    }
    i18n.global.locale.value = "en"
  })

  it("updates locale without throwing when storage writes fail", async () => {
    const storage = mockUnavailableLocalStorage()
    const wrapper = mount(LanguageSwitcher, {
      global: {
        plugins: [i18n],
      },
    })

    await expect(wrapper.find("select").setValue("en")).resolves.toBeUndefined()
    expect(storage.setItem).toHaveBeenCalledWith("wl-locale", "en")
    expect(i18n.global.locale.value).toBe("en")
  })
})

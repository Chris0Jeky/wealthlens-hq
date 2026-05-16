import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent, ref, nextTick } from 'vue'
import { useClickOutside } from '@/composables/useClickOutside'

function createTestComponent(handler: () => void) {
  return defineComponent({
    setup() {
      const targetRef = ref<HTMLElement | null>(null)
      useClickOutside(targetRef, handler)
      return { targetRef }
    },
    template: `
      <div>
        <div ref="targetRef" data-testid="target">Inside</div>
        <div data-testid="outside">Outside</div>
      </div>
    `,
  })
}

describe('useClickOutside', () => {
  it('calls handler when clicking outside the target', async () => {
    const handler = vi.fn()
    const wrapper = mount(createTestComponent(handler), {
      attachTo: document.body,
    })
    await nextTick()

    const outside = wrapper.find('[data-testid="outside"]')
    await outside.trigger('pointerdown')
    expect(handler).toHaveBeenCalledOnce()
    wrapper.unmount()
  })

  it('does not call handler when clicking inside the target', async () => {
    const handler = vi.fn()
    const wrapper = mount(createTestComponent(handler), {
      attachTo: document.body,
    })
    await nextTick()

    const target = wrapper.find('[data-testid="target"]')
    await target.trigger('pointerdown')
    expect(handler).not.toHaveBeenCalled()
    wrapper.unmount()
  })

  it('does not call handler when clicking the target element itself', async () => {
    const handler = vi.fn()
    const wrapper = mount(createTestComponent(handler), {
      attachTo: document.body,
    })
    await nextTick()

    const target = wrapper.find('[data-testid="target"]')
    await target.trigger('pointerdown')
    expect(handler).not.toHaveBeenCalled()
    wrapper.unmount()
  })

  it('cleans up the listener on unmount', async () => {
    const handler = vi.fn()
    const wrapper = mount(createTestComponent(handler), {
      attachTo: document.body,
    })
    await nextTick()
    wrapper.unmount()

    document.body.dispatchEvent(new Event('pointerdown', { bubbles: true }))
    expect(handler).not.toHaveBeenCalled()
  })

  it('exposes start and stop for manual control', async () => {
    const handler = vi.fn()
    const targetRef = ref<HTMLElement | null>(null)

    const TestComp = defineComponent({
      setup() {
        const { start, stop } = useClickOutside(targetRef, handler)
        return { targetRef, start, stop }
      },
      template: `
        <div>
          <div ref="targetRef" data-testid="target">Inside</div>
          <button data-testid="outside">Outside</button>
        </div>
      `,
    })

    const wrapper = mount(TestComp, { attachTo: document.body })
    await nextTick()

    wrapper.vm.stop()
    const outside = wrapper.find('[data-testid="outside"]')
    await outside.trigger('pointerdown')
    expect(handler).not.toHaveBeenCalled()

    wrapper.vm.start()
    await outside.trigger('pointerdown')
    expect(handler).toHaveBeenCalledOnce()

    wrapper.unmount()
  })

  it('handles null ref gracefully', async () => {
    const handler = vi.fn()
    const targetRef = ref<HTMLElement | null>(null)

    const TestComp = defineComponent({
      setup() {
        useClickOutside(targetRef, handler)
        return {}
      },
      template: '<div>No ref</div>',
    })

    const wrapper = mount(TestComp, { attachTo: document.body })
    await nextTick()

    document.body.dispatchEvent(new Event('pointerdown', { bubbles: true }))
    expect(handler).not.toHaveBeenCalled()
    wrapper.unmount()
  })
})

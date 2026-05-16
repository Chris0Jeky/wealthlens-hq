import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ConfirmDialog from '@/components/ConfirmDialog.vue'

function mountDialog(props: Record<string, unknown> = {}, slotContent = '') {
  return mount(ConfirmDialog, {
    props: { open: false, title: 'Confirm action', ...props },
    slots: { default: slotContent || 'Are you sure?' },
    attachTo: document.body,
  })
}

describe('ConfirmDialog', () => {
  it('renders a dialog element', () => {
    const wrapper = mountDialog()
    expect(wrapper.find('dialog').exists()).toBe(true)
  })

  it('displays the title', () => {
    const wrapper = mountDialog({ open: true, title: 'Delete item?' })
    expect(wrapper.text()).toContain('Delete item?')
  })

  it('displays slot content as the body', () => {
    const wrapper = mountDialog({ open: true }, 'This cannot be undone.')
    expect(wrapper.text()).toContain('This cannot be undone.')
  })

  it('uses custom confirm and cancel labels', () => {
    const wrapper = mountDialog({
      open: true,
      confirmLabel: 'Yes, delete',
      cancelLabel: 'Keep it',
    })
    expect(wrapper.text()).toContain('Yes, delete')
    expect(wrapper.text()).toContain('Keep it')
  })

  it('uses default Confirm and Cancel labels', () => {
    const wrapper = mountDialog({ open: true })
    expect(wrapper.text()).toContain('Confirm')
    expect(wrapper.text()).toContain('Cancel')
  })

  it('emits confirm when confirm button is clicked', async () => {
    const wrapper = mountDialog({ open: true })
    const buttons = wrapper.findAll('button')
    const confirmBtn = buttons.find((b) => b.text() === 'Confirm')!
    await confirmBtn.trigger('click')
    expect(wrapper.emitted('confirm')).toHaveLength(1)
  })

  it('emits cancel when cancel button is clicked', async () => {
    const wrapper = mountDialog({ open: true })
    const buttons = wrapper.findAll('button')
    const cancelBtn = buttons.find((b) => b.text() === 'Cancel')!
    await cancelBtn.trigger('click')
    expect(wrapper.emitted('cancel')).toHaveLength(1)
  })

  it('applies destructive styling when destructive prop is true', () => {
    const wrapper = mountDialog({ open: true, destructive: true })
    const buttons = wrapper.findAll('button')
    const confirmBtn = buttons.find((b) => b.text() === 'Confirm')!
    expect(confirmBtn.classes()).toContain('bg-red-600')
  })

  it('applies default blue styling when not destructive', () => {
    const wrapper = mountDialog({ open: true, destructive: false })
    const buttons = wrapper.findAll('button')
    const confirmBtn = buttons.find((b) => b.text() === 'Confirm')!
    expect(confirmBtn.classes()).toContain('bg-blue-600')
  })

  it('has an h2 heading for the title', () => {
    const wrapper = mountDialog({ open: true, title: 'Test title' })
    const h2 = wrapper.find('h2')
    expect(h2.exists()).toBe(true)
    expect(h2.text()).toBe('Test title')
  })
})

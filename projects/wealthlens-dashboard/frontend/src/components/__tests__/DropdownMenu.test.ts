import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DropdownMenu from '@/components/DropdownMenu.vue'

const items = [
  { id: 'a', label: 'Option A' },
  { id: 'b', label: 'Option B' },
  { id: 'c', label: 'Option C', disabled: true },
  { id: 'd', label: 'Option D' },
]

describe('DropdownMenu', () => {
  it('renders trigger button with label', () => {
    const wrapper = mount(DropdownMenu, { props: { items, label: 'Select' } })
    expect(wrapper.find('button').text()).toContain('Select')
  })

  it('menu is closed by default', () => {
    const wrapper = mount(DropdownMenu, { props: { items, label: 'Pick' } })
    expect(wrapper.find('[role="menu"]').exists()).toBe(false)
  })

  it('opens menu on button click', async () => {
    const wrapper = mount(DropdownMenu, { props: { items, label: 'Pick' } })
    await wrapper.find('button').trigger('click')
    expect(wrapper.find('[role="menu"]').exists()).toBe(true)
  })

  it('sets aria-expanded on trigger', async () => {
    const wrapper = mount(DropdownMenu, { props: { items, label: 'Pick' } })
    expect(wrapper.find('button').attributes('aria-expanded')).toBe('false')
    await wrapper.find('button').trigger('click')
    expect(wrapper.find('button').attributes('aria-expanded')).toBe('true')
  })

  it('uses aria-haspopup="menu"', () => {
    const wrapper = mount(DropdownMenu, { props: { items, label: 'Pick' } })
    expect(wrapper.find('button').attributes('aria-haspopup')).toBe('menu')
  })

  it('menu has aria-labelledby pointing to trigger', async () => {
    const wrapper = mount(DropdownMenu, { props: { items, label: 'Pick' } })
    await wrapper.find('button').trigger('click')
    const triggerId = wrapper.find('button').attributes('id')
    expect(wrapper.find('[role="menu"]').attributes('aria-labelledby')).toBe(triggerId)
  })

  it('renders all items as menuitems', async () => {
    const wrapper = mount(DropdownMenu, { props: { items, label: 'Pick' } })
    await wrapper.find('button').trigger('click')
    const menuItems = wrapper.findAll('[role="menuitem"]')
    expect(menuItems.length).toBe(4)
    expect(menuItems[0].text()).toBe('Option A')
  })

  it('emits select with item id on click', async () => {
    const wrapper = mount(DropdownMenu, { props: { items, label: 'Pick' } })
    await wrapper.find('button').trigger('click')
    await wrapper.findAll('[role="menuitem"]')[1].trigger('click')
    expect(wrapper.emitted('select')).toEqual([['b']])
  })

  it('closes menu after selection', async () => {
    const wrapper = mount(DropdownMenu, { props: { items, label: 'Pick' } })
    await wrapper.find('button').trigger('click')
    await wrapper.findAll('[role="menuitem"]')[0].trigger('click')
    expect(wrapper.find('[role="menu"]').exists()).toBe(false)
  })

  it('does not emit select for disabled items', async () => {
    const wrapper = mount(DropdownMenu, { props: { items, label: 'Pick' } })
    await wrapper.find('button').trigger('click')
    await wrapper.findAll('[role="menuitem"]')[2].trigger('click')
    expect(wrapper.emitted('select')).toBeUndefined()
  })

  it('marks disabled items with aria-disabled', async () => {
    const wrapper = mount(DropdownMenu, { props: { items, label: 'Pick' } })
    await wrapper.find('button').trigger('click')
    const disabledItem = wrapper.findAll('[role="menuitem"]')[2]
    expect(disabledItem.attributes('aria-disabled')).toBe('true')
  })

  it('closes on Escape key', async () => {
    const wrapper = mount(DropdownMenu, {
      props: { items, label: 'Pick' },
      attachTo: document.body,
    })
    await wrapper.find('button').trigger('click')
    expect(wrapper.find('[role="menu"]').exists()).toBe(true)
    await wrapper.trigger('keydown', { key: 'Escape' })
    expect(wrapper.find('[role="menu"]').exists()).toBe(false)
    wrapper.unmount()
  })

  it('focuses first enabled item on open', async () => {
    const wrapper = mount(DropdownMenu, {
      props: { items, label: 'Pick' },
      attachTo: document.body,
    })
    await wrapper.find('button').trigger('click')
    const firstItem = wrapper.findAll('[role="menuitem"]')[0]
    expect(firstItem.element).toBe(document.activeElement)
    wrapper.unmount()
  })

  it('ArrowDown moves focus to next enabled item', async () => {
    const wrapper = mount(DropdownMenu, {
      props: { items, label: 'Pick' },
      attachTo: document.body,
    })
    await wrapper.find('button').trigger('click')
    await wrapper.trigger('keydown', { key: 'ArrowDown' })
    const secondItem = wrapper.findAll('[role="menuitem"]')[1]
    expect(secondItem.element).toBe(document.activeElement)
    wrapper.unmount()
  })

  it('ArrowDown skips disabled items', async () => {
    const wrapper = mount(DropdownMenu, {
      props: { items, label: 'Pick' },
      attachTo: document.body,
    })
    await wrapper.find('button').trigger('click')
    await wrapper.trigger('keydown', { key: 'ArrowDown' })
    await wrapper.trigger('keydown', { key: 'ArrowDown' })
    const fourthItem = wrapper.findAll('[role="menuitem"]')[3]
    expect(fourthItem.element).toBe(document.activeElement)
    wrapper.unmount()
  })

  it('ArrowUp moves focus to previous item', async () => {
    const wrapper = mount(DropdownMenu, {
      props: { items, label: 'Pick' },
      attachTo: document.body,
    })
    await wrapper.find('button').trigger('click')
    await wrapper.trigger('keydown', { key: 'ArrowDown' })
    await wrapper.trigger('keydown', { key: 'ArrowUp' })
    const firstItem = wrapper.findAll('[role="menuitem"]')[0]
    expect(firstItem.element).toBe(document.activeElement)
    wrapper.unmount()
  })

  it('Home moves focus to first enabled item', async () => {
    const wrapper = mount(DropdownMenu, {
      props: { items, label: 'Pick' },
      attachTo: document.body,
    })
    await wrapper.find('button').trigger('click')
    await wrapper.trigger('keydown', { key: 'ArrowDown' })
    await wrapper.trigger('keydown', { key: 'Home' })
    const firstItem = wrapper.findAll('[role="menuitem"]')[0]
    expect(firstItem.element).toBe(document.activeElement)
    wrapper.unmount()
  })

  it('End moves focus to last enabled item', async () => {
    const wrapper = mount(DropdownMenu, {
      props: { items, label: 'Pick' },
      attachTo: document.body,
    })
    await wrapper.find('button').trigger('click')
    await wrapper.trigger('keydown', { key: 'End' })
    const lastItem = wrapper.findAll('[role="menuitem"]')[3]
    expect(lastItem.element).toBe(document.activeElement)
    wrapper.unmount()
  })
})

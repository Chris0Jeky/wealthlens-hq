import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import DropdownMenu from '@/components/DropdownMenu.vue'

const items = [
  { id: 'a', label: 'Option A' },
  { id: 'b', label: 'Option B' },
  { id: 'c', label: 'Option C', disabled: true },
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

  it('renders all items as menuitems', async () => {
    const wrapper = mount(DropdownMenu, { props: { items, label: 'Pick' } })
    await wrapper.find('button').trigger('click')
    const menuItems = wrapper.findAll('[role="menuitem"]')
    expect(menuItems.length).toBe(3)
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
})

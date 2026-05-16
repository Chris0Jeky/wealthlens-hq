import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import FilterChips from '@/components/FilterChips.vue'

const options = [
  { id: 'london', label: 'London' },
  { id: 'wales', label: 'Wales' },
  { id: 'scotland', label: 'Scotland' },
]

describe('FilterChips', () => {
  it('renders all options as buttons', () => {
    const wrapper = mount(FilterChips, {
      props: { options, selected: [], label: 'Regions' },
    })
    const buttons = wrapper.findAll('button')
    expect(buttons.length).toBe(3)
    expect(buttons[0].text()).toBe('London')
  })

  it('renders legend with label', () => {
    const wrapper = mount(FilterChips, {
      props: { options, selected: [], label: 'Regions' },
    })
    expect(wrapper.find('legend').text()).toBe('Regions')
  })

  it('marks selected chips with aria-pressed=true', () => {
    const wrapper = mount(FilterChips, {
      props: { options, selected: ['wales'], label: 'Regions' },
    })
    const buttons = wrapper.findAll('button')
    expect(buttons[0].attributes('aria-pressed')).toBe('false')
    expect(buttons[1].attributes('aria-pressed')).toBe('true')
  })

  it('applies active styling to selected chips', () => {
    const wrapper = mount(FilterChips, {
      props: { options, selected: ['london'], label: 'Regions' },
    })
    expect(wrapper.findAll('button')[0].classes()).toContain('bg-blue-600')
  })

  it('emits update:selected with added id on click', async () => {
    const wrapper = mount(FilterChips, {
      props: { options, selected: ['london'], label: 'Regions' },
    })
    await wrapper.findAll('button')[2].trigger('click')
    expect(wrapper.emitted('update:selected')![0][0]).toContain('london')
    expect(wrapper.emitted('update:selected')![0][0]).toContain('scotland')
  })

  it('emits update:selected with removed id on deselect', async () => {
    const wrapper = mount(FilterChips, {
      props: { options, selected: ['london', 'wales'], label: 'Regions' },
    })
    await wrapper.findAll('button')[0].trigger('click')
    const emitted = wrapper.emitted('update:selected')![0][0] as string[]
    expect(emitted).not.toContain('london')
    expect(emitted).toContain('wales')
  })

  it('supports empty selection', async () => {
    const wrapper = mount(FilterChips, {
      props: { options, selected: ['london'], label: 'Regions' },
    })
    await wrapper.findAll('button')[0].trigger('click')
    const emitted = wrapper.emitted('update:selected')![0][0] as string[]
    expect(emitted).toEqual([])
  })

  it('has role=group with aria-label', () => {
    const wrapper = mount(FilterChips, {
      props: { options, selected: [], label: 'Regions' },
    })
    const group = wrapper.find('[role="group"]')
    expect(group.attributes('aria-label')).toBe('Regions')
  })
})

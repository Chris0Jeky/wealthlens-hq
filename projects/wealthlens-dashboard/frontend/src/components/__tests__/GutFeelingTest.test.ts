import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import GutFeelingTest from '@/components/GutFeelingTest.vue'

describe('GutFeelingTest', () => {
  it('renders all 8 cards', () => {
    const wrapper = mount(GutFeelingTest)
    const cards = wrapper.findAll('.gut-card')
    expect(cards).toHaveLength(8)
  })

  it('renders card numbers 01 through 08', () => {
    const wrapper = mount(GutFeelingTest)
    const nums = wrapper.findAll('.gut-card-num')
    const numTexts = nums.map((n) => n.text())
    expect(numTexts).toEqual(['01', '02', '03', '04', '05', '06', '07', '08'])
  })

  it('renders question text on each card', () => {
    const wrapper = mount(GutFeelingTest)
    const questions = wrapper.findAll('.gut-card-q')
    expect(questions).toHaveLength(8)
    // Spot-check first and last
    expect(questions[0].text()).toContain('renting at thirty')
    expect(questions[7].text()).toContain('kids will live with us')
  })

  it('cards start unrevealed (no "revealed" class)', () => {
    const wrapper = mount(GutFeelingTest)
    const cards = wrapper.findAll('.gut-card')
    cards.forEach((card) => {
      expect(card.classes()).not.toContain('revealed')
    })
  })

  it('clicking a card toggles the "revealed" class', async () => {
    const wrapper = mount(GutFeelingTest)
    const firstCard = wrapper.findAll('.gut-card')[0]

    // Click to reveal
    await firstCard.trigger('click')
    expect(firstCard.classes()).toContain('revealed')

    // Click again to un-reveal
    await firstCard.trigger('click')
    expect(firstCard.classes()).not.toContain('revealed')
  })

  it('Enter key triggers reveal', async () => {
    const wrapper = mount(GutFeelingTest)
    const firstCard = wrapper.findAll('.gut-card')[0]

    await firstCard.trigger('keydown', { key: 'Enter' })
    expect(firstCard.classes()).toContain('revealed')
  })

  it('Space key triggers reveal', async () => {
    const wrapper = mount(GutFeelingTest)
    const firstCard = wrapper.findAll('.gut-card')[0]

    await firstCard.trigger('keydown', { key: ' ' })
    expect(firstCard.classes()).toContain('revealed')
  })

  it('other keys do not trigger reveal', async () => {
    const wrapper = mount(GutFeelingTest)
    const firstCard = wrapper.findAll('.gut-card')[0]

    await firstCard.trigger('keydown', { key: 'Tab' })
    expect(firstCard.classes()).not.toContain('revealed')
  })

  it('cards have correct ARIA attributes', () => {
    const wrapper = mount(GutFeelingTest)
    const cards = wrapper.findAll('.gut-card')

    cards.forEach((card) => {
      expect(card.attributes('role')).toBe('button')
      expect(card.attributes('tabindex')).toBe('0')
      expect(card.attributes('aria-expanded')).toBe('false')
      expect(card.attributes('aria-label')).toMatch(/^Question \d{2}:/)
    })
  })

  it('aria-expanded updates to "true" on reveal', async () => {
    const wrapper = mount(GutFeelingTest)
    const firstCard = wrapper.findAll('.gut-card')[0]

    await firstCard.trigger('click')
    expect(firstCard.attributes('aria-expanded')).toBe('true')
  })

  it('revealed card shows source citation', async () => {
    const wrapper = mount(GutFeelingTest)
    const firstCard = wrapper.findAll('.gut-card')[0]

    await firstCard.trigger('click')
    const src = firstCard.find('.gut-answer-src')
    expect(src.exists()).toBe(true)
    expect(src.text()).toContain('Source:')
  })

  it('each card has a stat section in the answer', () => {
    const wrapper = mount(GutFeelingTest)
    const answers = wrapper.findAll('.gut-answer')
    expect(answers).toHaveLength(8)

    answers.forEach((answer) => {
      expect(answer.find('.gut-answer-stat').exists()).toBe(true)
      expect(answer.find('.gut-answer-body').exists()).toBe(true)
    })
  })

  it('section has correct aria-labelledby', () => {
    const wrapper = mount(GutFeelingTest)
    const section = wrapper.find('section')
    expect(section.attributes('aria-labelledby')).toBe('gut-heading')
    expect(wrapper.find('#gut-heading').exists()).toBe(true)
  })
})

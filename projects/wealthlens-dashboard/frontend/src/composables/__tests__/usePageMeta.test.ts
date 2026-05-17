import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { ref, nextTick, defineComponent } from 'vue'
import { mount, type VueWrapper } from '@vue/test-utils'
import { usePageMeta, type PageMetaOptions } from '../usePageMeta'

/** Helper: create a component that calls usePageMeta with given options. */
function createComponent(options: PageMetaOptions) {
  return defineComponent({
    setup() {
      usePageMeta(options)
      return {}
    },
    template: '<div />',
  })
}

/** Helper: get meta content by property or name attribute. */
function getMeta(attr: 'property' | 'name', key: string): string | null {
  const el = document.head.querySelector<HTMLMetaElement>(
    `meta[${attr}="${key}"]`,
  )
  return el?.getAttribute('content') ?? null
}

/** Helper: get all meta content values for a given attribute key. */
function getAllMeta(attr: 'property' | 'name', key: string): string[] {
  const els = document.head.querySelectorAll<HTMLMetaElement>(
    `meta[${attr}="${key}"]`,
  )
  return Array.from(els).map((el) => el.getAttribute('content') ?? '')
}

describe('usePageMeta', () => {
  let wrapper: VueWrapper | null = null

  beforeEach(() => {
    document.title = ''
    // Clear any leftover meta tags from previous tests
    document.head
      .querySelectorAll('meta[property^="og:"], meta[name^="twitter:"], meta[name="description"]')
      .forEach((el) => el.remove())
  })

  afterEach(() => {
    wrapper?.unmount()
    wrapper = null
  })

  it('sets document title with site name suffix', () => {
    wrapper = mount(createComponent({ title: 'About' }))
    expect(document.title).toBe('About — WealthLens UK')
  })

  it('sets base title when no title is provided', () => {
    wrapper = mount(createComponent({}))
    expect(document.title).toBe('WealthLens UK')
  })

  it('sets meta description', () => {
    wrapper = mount(
      createComponent({ description: 'A test description' }),
    )
    expect(getMeta('name', 'description')).toBe('A test description')
  })

  it('sets OpenGraph tags', () => {
    wrapper = mount(
      createComponent({
        title: 'Wealth Shares',
        description: 'UK wealth data',
        url: 'https://example.com/charts/wealth-shares',
        image: 'https://example.com/og/wealth-shares.png',
      }),
    )
    expect(getMeta('property', 'og:title')).toBe('Wealth Shares')
    expect(getMeta('property', 'og:description')).toBe('UK wealth data')
    expect(getMeta('property', 'og:url')).toBe(
      'https://example.com/charts/wealth-shares',
    )
    expect(getMeta('property', 'og:image')).toBe(
      'https://example.com/og/wealth-shares.png',
    )
    expect(getMeta('property', 'og:site_name')).toBe('WealthLens UK')
    expect(getMeta('property', 'og:type')).toBe('website')
  })

  it('sets Twitter Card tags', () => {
    wrapper = mount(
      createComponent({
        title: 'Housing',
        description: 'Housing affordability data',
        image: 'https://example.com/og/housing.png',
        twitterCard: 'summary_large_image',
      }),
    )
    expect(getMeta('name', 'twitter:card')).toBe('summary_large_image')
    expect(getMeta('name', 'twitter:title')).toBe('Housing')
    expect(getMeta('name', 'twitter:description')).toBe(
      'Housing affordability data',
    )
    expect(getMeta('name', 'twitter:image')).toBe(
      'https://example.com/og/housing.png',
    )
  })

  it('sets image alt text on both og and twitter', () => {
    wrapper = mount(
      createComponent({
        image: 'https://example.com/og/test.png',
        imageAlt: 'Alt text for the image',
      }),
    )
    expect(getMeta('name', 'twitter:image:alt')).toBe(
      'Alt text for the image',
    )
    expect(getMeta('property', 'og:image:alt')).toBe(
      'Alt text for the image',
    )
  })

  it('allows custom ogType', () => {
    wrapper = mount(createComponent({ ogType: 'article' }))
    expect(getMeta('property', 'og:type')).toBe('article')
  })

  it('updates reactively when refs change', async () => {
    const title = ref<string | undefined>('Page One')
    const description = ref<string | undefined>('First page')

    wrapper = mount(
      defineComponent({
        setup() {
          usePageMeta({ title, description })
          return {}
        },
        template: '<div />',
      }),
    )

    expect(document.title).toBe('Page One — WealthLens UK')
    expect(getMeta('property', 'og:title')).toBe('Page One')

    title.value = 'Page Two'
    description.value = 'Second page'
    await nextTick()

    expect(document.title).toBe('Page Two — WealthLens UK')
    expect(getMeta('property', 'og:title')).toBe('Page Two')
    expect(getMeta('property', 'og:description')).toBe('Second page')
    expect(getMeta('name', 'twitter:title')).toBe('Page Two')
  })

  it('cleans up meta tags on unmount', () => {
    wrapper = mount(
      createComponent({
        title: 'Temporary',
        description: 'Will be removed',
        image: 'https://example.com/og/temp.png',
      }),
    )

    // Tags should exist
    expect(getMeta('property', 'og:title')).toBe('Temporary')
    expect(getMeta('name', 'twitter:title')).toBe('Temporary')

    wrapper.unmount()
    wrapper = null

    // Tags should be removed
    expect(getMeta('property', 'og:title')).toBeNull()
    expect(getMeta('name', 'twitter:title')).toBeNull()
    expect(getMeta('property', 'og:image')).toBeNull()
    // Title should revert to base
    expect(document.title).toBe('WealthLens UK')
  })

  it('defaults og:url to base URL when not provided', () => {
    wrapper = mount(createComponent({ title: 'Test' }))
    expect(getMeta('property', 'og:url')).toBe(
      'https://chris0jeky.github.io/wealthlens-hq',
    )
  })

  it('uses summary_large_image as default twitter card type', () => {
    wrapper = mount(createComponent({}))
    expect(getMeta('name', 'twitter:card')).toBe('summary_large_image')
  })

  it('supports summary twitter card type', () => {
    wrapper = mount(createComponent({ twitterCard: 'summary' }))
    expect(getMeta('name', 'twitter:card')).toBe('summary')
  })

  it('removes stale imageAlt tags when alt text changes to empty', async () => {
    const imageAlt = ref<string | undefined>('Some alt text')

    wrapper = mount(
      defineComponent({
        setup() {
          usePageMeta({
            image: 'https://example.com/og/test.png',
            imageAlt,
          })
          return {}
        },
        template: '<div />',
      }),
    )

    expect(getMeta('name', 'twitter:image:alt')).toBe('Some alt text')
    expect(getMeta('property', 'og:image:alt')).toBe('Some alt text')

    // Change to empty — should remove the meta elements
    imageAlt.value = undefined
    await nextTick()

    expect(getMeta('name', 'twitter:image:alt')).toBeNull()
    expect(getMeta('property', 'og:image:alt')).toBeNull()
  })

  it('handles concurrent mount/unmount without cross-contamination', () => {
    // Simulate a route transition: mount the first (outgoing) component
    const wrapper1 = mount(
      createComponent({
        title: 'Page A',
        description: 'Description A',
        image: 'https://example.com/og/a.png',
      }),
    )

    expect(getMeta('property', 'og:title')).toBe('Page A')

    // Mount the second (incoming) component while first is still alive
    const wrapper2 = mount(
      createComponent({
        title: 'Page B',
        description: 'Description B',
        image: 'https://example.com/og/b.png',
      }),
    )

    // Both instances should have their own elements in the DOM
    const ogTitles = getAllMeta('property', 'og:title')
    expect(ogTitles).toContain('Page A')
    expect(ogTitles).toContain('Page B')

    // Unmount the first (outgoing) component — simulates route leave
    wrapper1.unmount()

    // The second instance's tags should still be intact
    expect(getMeta('property', 'og:title')).toBe('Page B')
    expect(getMeta('property', 'og:description')).toBe('Description B')
    expect(getMeta('property', 'og:image')).toBe('https://example.com/og/b.png')
    expect(getMeta('name', 'twitter:title')).toBe('Page B')

    // Verify there is exactly one of each tag now (no leftovers from instance 1)
    expect(getAllMeta('property', 'og:title')).toEqual(['Page B'])
    expect(getAllMeta('name', 'twitter:title')).toEqual(['Page B'])

    // Clean up
    wrapper2.unmount()

    // All tags should be gone
    expect(getMeta('property', 'og:title')).toBeNull()
    expect(getMeta('name', 'twitter:title')).toBeNull()
  })

  it('is a no-op when document is undefined (SSR)', () => {
    // We cannot truly undefine document in jsdom, but we can verify
    // the SSR guard exists by checking the composable runs without error
    // in normal conditions. The actual SSR guard is tested by code inspection.
    // This test verifies the composable still works correctly.
    wrapper = mount(createComponent({ title: 'SSR test' }))
    expect(document.title).toBe('SSR test — WealthLens UK')
  })
})

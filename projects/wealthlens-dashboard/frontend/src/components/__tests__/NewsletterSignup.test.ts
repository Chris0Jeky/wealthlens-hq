import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import NewsletterSignup from '@/components/NewsletterSignup.vue'

describe('NewsletterSignup', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('renders form with email input and submit button', () => {
    const wrapper = mount(NewsletterSignup)
    expect(wrapper.find('input[type="email"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').exists()).toBe(true)
    expect(wrapper.find('button[type="submit"]').text()).toBe('Subscribe')
  })

  it('renders heading and subtitle', () => {
    const wrapper = mount(NewsletterSignup)
    expect(wrapper.find('h3').text()).toBe('Stay informed')
    expect(wrapper.find('.newsletter__subtitle').text()).toContain('Monthly updates')
  })

  it('disables submit button for invalid email', async () => {
    const wrapper = mount(NewsletterSignup)
    const input = wrapper.find('input[type="email"]')
    const button = wrapper.find('button[type="submit"]')

    await input.setValue('not-an-email')
    expect((button.element as HTMLButtonElement).disabled).toBe(true)
  })

  it('enables submit button for valid email', async () => {
    const wrapper = mount(NewsletterSignup)
    const input = wrapper.find('input[type="email"]')
    const button = wrapper.find('button[type="submit"]')

    await input.setValue('test@example.com')
    expect((button.element as HTMLButtonElement).disabled).toBe(false)
  })

  it('shows success message after successful submit', async () => {
    const mockFetch = vi.fn().mockResolvedValue({ ok: true })
    vi.stubGlobal('fetch', mockFetch)

    const wrapper = mount(NewsletterSignup)
    await wrapper.find('input[type="email"]').setValue('test@example.com')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.find('.newsletter__success').text()).toBe("You're subscribed!")
    expect(mockFetch).toHaveBeenCalledOnce()
  })

  it('shows error message on network failure', async () => {
    const mockFetch = vi.fn().mockRejectedValue(new Error('Network error'))
    vi.stubGlobal('fetch', mockFetch)

    const wrapper = mount(NewsletterSignup)
    await wrapper.find('input[type="email"]').setValue('test@example.com')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.find('.newsletter__error').text()).toBe('Network error')
  })

  it('shows error message on non-ok response', async () => {
    const mockFetch = vi.fn().mockResolvedValue({ ok: false, status: 400 })
    vi.stubGlobal('fetch', mockFetch)

    const wrapper = mount(NewsletterSignup)
    await wrapper.find('input[type="email"]').setValue('test@example.com')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.find('.newsletter__error').text()).toContain('Subscription failed')
  })

  it('disables submit button during submission', async () => {
    let resolvePromise: (value: unknown) => void
    const mockFetch = vi.fn().mockImplementation(
      () => new Promise((resolve) => { resolvePromise = resolve }),
    )
    vi.stubGlobal('fetch', mockFetch)

    const wrapper = mount(NewsletterSignup)
    await wrapper.find('input[type="email"]').setValue('test@example.com')
    await wrapper.find('form').trigger('submit')

    const button = wrapper.find('button[type="submit"]')
    expect((button.element as HTMLButtonElement).disabled).toBe(true)
    expect(button.text()).toContain('Subscribing...')

    resolvePromise!({ ok: true })
    await flushPromises()

    expect(wrapper.find('.newsletter__success').exists()).toBe(true)
  })

  it('has aria-live region for status messages', () => {
    const wrapper = mount(NewsletterSignup)
    const status = wrapper.find('[aria-live="polite"]')
    expect(status.exists()).toBe(true)
  })

  it('sends email in form data to API', async () => {
    const mockFetch = vi.fn().mockResolvedValue({ ok: true })
    vi.stubGlobal('fetch', mockFetch)

    const wrapper = mount(NewsletterSignup)
    await wrapper.find('input[type="email"]').setValue('user@domain.co.uk')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(mockFetch).toHaveBeenCalledWith(
      expect.stringContaining('buttondown.email'),
      expect.objectContaining({ method: 'POST' }),
    )
    const body = mockFetch.mock.calls[0][1].body as FormData
    expect(body.get('email')).toBe('user@domain.co.uk')
  })
})

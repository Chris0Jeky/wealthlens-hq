import { describe, expect, it, vi, afterEach } from 'vitest'
import { fetchWithRetry } from '../fetchWithRetry'

/**
 * Uses real timers with a tiny backoff (1ms) to avoid fake-timer
 * pitfalls with Promise-based delays.
 */
describe('fetchWithRetry', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('returns on first success', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ status: 200, ok: true }),
    )
    const res = await fetchWithRetry('/api/test', undefined, 3, 1)
    expect(res.status).toBe(200)
    expect(fetch).toHaveBeenCalledTimes(1)
  })

  it('retries on 500 then succeeds', async () => {
    const mock = vi
      .fn()
      .mockResolvedValueOnce({ status: 500, ok: false })
      .mockResolvedValueOnce({ status: 200, ok: true })
    vi.stubGlobal('fetch', mock)

    const res = await fetchWithRetry('/api/test', undefined, 3, 1)
    expect(res.status).toBe(200)
    expect(mock).toHaveBeenCalledTimes(2)
  })

  it('retries on network error then succeeds', async () => {
    const mock = vi
      .fn()
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValueOnce({ status: 200, ok: true })
    vi.stubGlobal('fetch', mock)

    const res = await fetchWithRetry('/api/test', undefined, 3, 1)
    expect(res.status).toBe(200)
    expect(mock).toHaveBeenCalledTimes(2)
  })

  it('does not retry on 404', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ status: 404, ok: false }),
    )
    const res = await fetchWithRetry('/api/test', undefined, 3, 1)
    expect(res.status).toBe(404)
    expect(fetch).toHaveBeenCalledTimes(1)
  })

  it('throws after 5xx retries exhausted', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockResolvedValue({ status: 500, ok: false }),
    )

    await expect(
      fetchWithRetry('/api/test', undefined, 2, 1),
    ).rejects.toThrow('HTTP 500')
    // 1 initial + 2 retries = 3 total attempts
    expect(fetch).toHaveBeenCalledTimes(3)
  })

  it('throws after max retries exhausted', async () => {
    vi.stubGlobal(
      'fetch',
      vi.fn().mockRejectedValue(new Error('timeout')),
    )

    await expect(
      fetchWithRetry('/api/test', undefined, 2, 1),
    ).rejects.toThrow('timeout')
    // 1 initial + 2 retries = 3 total attempts
    expect(fetch).toHaveBeenCalledTimes(3)
  })
})

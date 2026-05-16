import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { api } from '@/api/client'

describe('api client', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })

  afterEach(() => {
    vi.unstubAllGlobals()
  })

  function mockResponse(body: unknown, status = 200) {
    ;(fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
      ok: status >= 200 && status < 300,
      status,
      statusText: status === 200 ? 'OK' : 'Not Found',
      json: () => Promise.resolve(body),
    })
  }

  it('listDatasets calls correct URL', async () => {
    mockResponse({ datasets: ['a', 'b'] })
    const result = await api.listDatasets()
    expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/data/')
    expect(result.datasets).toEqual(['a', 'b'])
  })

  it('getMetadata calls correct URL', async () => {
    mockResponse({ datasets: [] })
    await api.getMetadata()
    expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/data/metadata')
  })

  it('getDatasetMetadata encodes name', async () => {
    mockResponse({ name: 'wealth-shares' })
    await api.getDatasetMetadata('wealth-shares')
    expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/data/wealth-shares/metadata')
  })

  it('getDatasetColumns calls correct URL', async () => {
    mockResponse({ dataset: 'x', row_count: 5, columns: [] })
    await api.getDatasetColumns('wealth-by-decile')
    expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/data/wealth-by-decile/columns')
  })

  it('getDataset includes page and limit params', async () => {
    mockResponse({ data: [], page: 2, limit: 50, total: 100, total_pages: 2 })
    await api.getDataset('housing-affordability', 2, 50)
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/data/housing-affordability?page=2&limit=50',
    )
  })

  it('health calls correct URL', async () => {
    mockResponse({ status: 'ok' })
    const result = await api.health()
    expect(result.status).toBe('ok')
  })

  it('throws on non-2xx response', async () => {
    mockResponse(null, 404)
    await expect(api.listDatasets()).rejects.toThrow('API 404: Not Found')
  })

  it('uses default page and limit', async () => {
    mockResponse({ data: [], page: 1, limit: 100, total: 0, total_pages: 1 })
    await api.getDataset('cgt-concentration')
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/data/cgt-concentration?page=1&limit=100',
    )
  })
})

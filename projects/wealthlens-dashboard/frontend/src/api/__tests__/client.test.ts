import { describe, it, expect, vi, beforeEach } from 'vitest'
import { api, ApiError } from '../client'

const mockFetch = vi.fn()
vi.stubGlobal('fetch', mockFetch)

function jsonResponse(body: unknown, status = 200) {
  return {
    ok: status >= 200 && status < 300,
    status,
    statusText: status === 200 ? 'OK' : 'Not Found',
    json: () => Promise.resolve(body),
  }
}

describe('api client', () => {
  beforeEach(() => {
    mockFetch.mockReset()
  })

  describe('listDatasets', () => {
    it('fetches /api/data/ and returns datasets', async () => {
      mockFetch.mockResolvedValue(jsonResponse({ datasets: ['a', 'b'] }))
      const result = await api.listDatasets()
      expect(mockFetch).toHaveBeenCalledWith('/api/data/')
      expect(result.datasets).toEqual(['a', 'b'])
    })
  })

  describe('getDataset', () => {
    it('fetches paginated data with encoded name', async () => {
      mockFetch.mockResolvedValue(
        jsonResponse({ data: [], page: 1, limit: 100, total: 0, total_pages: 1 }),
      )
      await api.getDataset('wealth-shares', 2, 50)
      expect(mockFetch).toHaveBeenCalledWith('/api/data/wealth-shares?page=2&limit=50')
    })
  })

  describe('getMetadata', () => {
    it('fetches single dataset metadata', async () => {
      const meta = { name: 'x', source: 's', source_url: 'u', access_date: 'd', row_count: 1, columns: ['a'], description: 'desc' }
      mockFetch.mockResolvedValue(jsonResponse(meta))
      const result = await api.getMetadata('x')
      expect(result.name).toBe('x')
    })
  })

  describe('error handling', () => {
    it('throws ApiError on non-ok response', async () => {
      mockFetch.mockResolvedValue(jsonResponse(null, 404))
      await expect(api.listDatasets()).rejects.toThrow(ApiError)
    })

    it('ApiError includes status code', async () => {
      mockFetch.mockResolvedValue(jsonResponse(null, 500))
      await expect(api.listDatasets()).rejects.toMatchObject({ status: 500 })
    })

    it('throws ApiError with status 0 on network failure', async () => {
      mockFetch.mockRejectedValue(new TypeError('Failed to fetch'))
      const err = await api.listDatasets().catch((e) => e)
      expect(err).toBeInstanceOf(ApiError)
      expect(err.status).toBe(0)
      expect(err.message).toBe('Could not reach the server')
    })

    it('throws ApiError when response is not valid JSON', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        status: 200,
        statusText: 'OK',
        json: () => Promise.reject(new SyntaxError('Unexpected token')),
      })
      const err = await api.listDatasets().catch((e) => e)
      expect(err).toBeInstanceOf(ApiError)
      expect(err.message).toBe('Response was not valid JSON')
    })
  })
})

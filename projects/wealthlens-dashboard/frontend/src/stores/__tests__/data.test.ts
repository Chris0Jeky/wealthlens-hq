import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useDataStore } from '@/stores/data'

describe('useDataStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it('has empty datasets initially', () => {
    const store = useDataStore()
    expect(store.datasets).toEqual([])
  })

  it('is not loading initially', () => {
    const store = useDataStore()
    expect(store.loading).toBe(false)
  })

  it('has no error initially', () => {
    const store = useDataStore()
    expect(store.error).toBeNull()
  })

  describe('fetchDatasets', () => {
    it('populates the datasets list on success', async () => {
      const mockDatasets = ['wealth-shares', 'housing-affordability']
      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: async () => ({ datasets: mockDatasets }),
      } as Response)

      const store = useDataStore()
      await store.fetchDatasets()

      expect(store.datasets).toEqual(mockDatasets)
      expect(store.loading).toBe(false)
      expect(store.error).toBeNull()
    })

    it('sets loading to true while fetching', async () => {
      let resolveFetch!: (value: Response) => void
      vi.spyOn(globalThis, 'fetch').mockReturnValueOnce(
        new Promise((resolve) => {
          resolveFetch = resolve
        }),
      )

      const store = useDataStore()
      const fetchPromise = store.fetchDatasets()
      expect(store.loading).toBe(true)

      resolveFetch({
        ok: true,
        json: async () => ({ datasets: [] }),
      } as Response)
      await fetchPromise

      expect(store.loading).toBe(false)
    })

    it('sets error on non-ok HTTP response', async () => {
      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
        ok: false,
        status: 500,
      } as Response)

      const store = useDataStore()
      await store.fetchDatasets()

      expect(store.error).toBe('HTTP 500')
      expect(store.loading).toBe(false)
      expect(store.datasets).toEqual([])
    })

    it('sets error on network failure', async () => {
      vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(
        new TypeError('Failed to fetch'),
      )

      const store = useDataStore()
      await store.fetchDatasets()

      expect(store.error).toBe('Could not reach the server')
      expect(store.loading).toBe(false)
    })

    it('clears previous error on successful retry', async () => {
      const fetchSpy = vi.spyOn(globalThis, 'fetch')
      fetchSpy.mockRejectedValueOnce(new Error('Network error'))

      const store = useDataStore()
      await store.fetchDatasets()
      expect(store.error).toBe('Could not reach the server')

      fetchSpy.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ datasets: ['recovered'] }),
      } as Response)

      await store.fetchDatasets()
      expect(store.error).toBeNull()
      expect(store.datasets).toEqual(['recovered'])
    })

    it('handles non-Error thrown values', async () => {
      vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce('string error')

      const store = useDataStore()
      await store.fetchDatasets()

      expect(store.error).toBe('Could not reach the server')
      expect(store.loading).toBe(false)
    })
  })

  describe('fetchDataset', () => {
    it('returns paginated data on success', async () => {
      const mockResponse = {
        data: [{ decile: 1, wealth: 15000 }],
        page: 1,
        limit: 100,
        total: 1,
        total_pages: 1,
      }
      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse,
      } as Response)

      const store = useDataStore()
      const result = await store.fetchDataset('wealth-shares')

      expect(result).toEqual(mockResponse)
      expect(globalThis.fetch).toHaveBeenCalledWith(
        '/api/data/wealth-shares?page=1&limit=100',
      )
    })

    it('passes pagination params', async () => {
      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: async () => ({ data: [], page: 2, limit: 50, total: 0, total_pages: 0 }),
      } as Response)

      const store = useDataStore()
      await store.fetchDataset('wealth-shares', 2, 50)

      expect(globalThis.fetch).toHaveBeenCalledWith(
        '/api/data/wealth-shares?page=2&limit=50',
      )
    })

    it('throws on non-ok response', async () => {
      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
        ok: false,
        status: 404,
      } as Response)

      const store = useDataStore()
      await expect(store.fetchDataset('missing')).rejects.toThrow('HTTP 404')
    })
  })

  describe('fetchMetadata', () => {
    it('fetches and caches metadata', async () => {
      const mockMeta = {
        name: 'wealth-shares',
        description: 'Top 1%/10% wealth shares',
        source: 'World Inequality Database',
        source_url: 'https://wid.world/',
        access_date: '2026-05-14',
        row_count: 100,
        columns: ['year', 'percentile', 'share'],
      }
      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: async () => mockMeta,
      } as Response)

      const store = useDataStore()
      const result = await store.fetchMetadata('wealth-shares')

      expect(result).toEqual(mockMeta)
      expect(store.metadata.get('wealth-shares')).toEqual(mockMeta)
    })

    it('returns cached metadata without refetching', async () => {
      const mockMeta = {
        name: 'wealth-shares',
        description: 'Top 1%/10% wealth shares',
        source: 'WID',
        source_url: 'https://wid.world/',
        access_date: '2026-05-14',
        row_count: 50,
        columns: ['year'],
      }
      const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: async () => mockMeta,
      } as Response)

      const store = useDataStore()
      await store.fetchMetadata('wealth-shares')
      const second = await store.fetchMetadata('wealth-shares')

      expect(second).toEqual(mockMeta)
      expect(fetchSpy).toHaveBeenCalledTimes(1)
    })
  })

  describe('fetchAllMetadata', () => {
    it('fetches all metadata and populates cache', async () => {
      const mockDatasets = [
        { name: 'a', description: 'A', source: 'S', source_url: 'http://x', access_date: '2026-01-01', row_count: 10, columns: ['x'] },
        { name: 'b', description: 'B', source: 'S', source_url: 'http://y', access_date: '2026-01-01', row_count: 20, columns: ['y'] },
      ]
      vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
        ok: true,
        json: async () => ({ datasets: mockDatasets }),
      } as Response)

      const store = useDataStore()
      const result = await store.fetchAllMetadata()

      expect(result).toEqual(mockDatasets)
      expect(store.metadata.get('a')).toEqual(mockDatasets[0])
      expect(store.metadata.get('b')).toEqual(mockDatasets[1])
    })
  })
})

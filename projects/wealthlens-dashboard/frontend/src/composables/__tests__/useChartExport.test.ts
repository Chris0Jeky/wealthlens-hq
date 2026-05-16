import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref } from 'vue'
import { useChartExport } from '@/composables/useChartExport'

describe('useChartExport', () => {
  let mockChart: {
    getOption: ReturnType<typeof vi.fn>
    setOption: ReturnType<typeof vi.fn>
    getDataURL: ReturnType<typeof vi.fn>
    getConnectedDataURL: ReturnType<typeof vi.fn>
    renderToSVGString?: ReturnType<typeof vi.fn>
  }

  let linkClicked: boolean
  let linkDownload: string

  beforeEach(() => {
    mockChart = {
      getOption: vi.fn(() => ({ graphic: [] })),
      setOption: vi.fn(),
      getDataURL: vi.fn(() => 'data:image/png;base64,fakedata'),
      getConnectedDataURL: vi.fn(() => 'data:image/svg+xml;charset=UTF-8,%3Csvg%3E%3C/svg%3E'),
    }

    linkClicked = false
    linkDownload = ''

    vi.spyOn(document, 'createElement').mockImplementation((tag: string) => {
      if (tag === 'a') {
        const el = {
          href: '',
          download: '',
          style: { display: '' },
          click: () => {
            linkClicked = true
            linkDownload = el.download
          },
        }
        return el as unknown as HTMLElement
      }
      return document.createElement(tag)
    })

    vi.spyOn(document.body, 'appendChild').mockImplementation(<T extends Node>(node: T) => node)
    vi.spyOn(document.body, 'removeChild').mockImplementation(<T extends Node>(node: T) => node)

    vi.stubGlobal('URL', {
      ...URL,
      createObjectURL: vi.fn(() => 'blob:http://localhost/fake-blob'),
      revokeObjectURL: vi.fn(),
    })
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
  })

  describe('exportPNG', () => {
    it('returns true and triggers download on success', () => {
      const chartRef = ref({ chart: mockChart })
      const { exportPNG } = useChartExport(chartRef)

      const result = exportPNG({ filename: 'test-chart' })

      expect(result).toBe(true)
      expect(linkClicked).toBe(true)
      expect(linkDownload).toBe('test-chart.png')
      expect(mockChart.getDataURL).toHaveBeenCalledWith({
        type: 'png',
        pixelRatio: 2,
        backgroundColor: '#fff',
      })
    })

    it('uses custom pixelRatio and backgroundColor', () => {
      const chartRef = ref({ chart: mockChart })
      const { exportPNG } = useChartExport(chartRef)

      exportPNG({ filename: 'test', pixelRatio: 3, backgroundColor: '#000' })

      expect(mockChart.getDataURL).toHaveBeenCalledWith({
        type: 'png',
        pixelRatio: 3,
        backgroundColor: '#000',
      })
    })

    it('clamps pixelRatio to minimum of 1', () => {
      const chartRef = ref({ chart: mockChart })
      const { exportPNG } = useChartExport(chartRef)

      exportPNG({ filename: 'test', pixelRatio: -1 })

      expect(mockChart.getDataURL).toHaveBeenCalledWith(
        expect.objectContaining({ pixelRatio: 1 }),
      )
    })

    it('adds and removes watermark during export', () => {
      const chartRef = ref({ chart: mockChart })
      const { exportPNG } = useChartExport(chartRef)

      exportPNG({ filename: 'test', source: 'WID.world' })

      expect(mockChart.setOption).toHaveBeenCalledTimes(2)
      const addCall = mockChart.setOption.mock.calls[0][0]
      expect(addCall.graphic[0].style.text).toContain('WealthLens UK')
      expect(addCall.graphic[0].style.text).toContain('WID.world')
    })

    it('removes watermark even when getDataURL throws', () => {
      mockChart.getDataURL.mockImplementation(() => { throw new Error('Canvas tainted') })
      const chartRef = ref({ chart: mockChart })
      const { exportPNG } = useChartExport(chartRef)

      const result = exportPNG({ filename: 'test' })

      expect(result).toBe(false)
      // Watermark removal still attempted (second setOption call)
      const removeCalls = mockChart.setOption.mock.calls.filter((call) => {
        const option = call[0] as { graphic?: Array<{ $action?: string }> }
        return option.graphic?.[0]?.$action === 'remove'
      })
      expect(removeCalls.length).toBe(1)
    })

    it('restores previous graphic elements after export', () => {
      const existingGraphic = [{ id: 'existing-annotation', type: 'text' }]
      mockChart.getOption.mockReturnValue({ graphic: existingGraphic })
      const chartRef = ref({ chart: mockChart })
      const { exportPNG } = useChartExport(chartRef)

      exportPNG({ filename: 'test' })

      // Should call setOption 3 times: add watermark, remove watermark, restore previous
      expect(mockChart.setOption).toHaveBeenCalledTimes(3)
      const restoreCall = mockChart.setOption.mock.calls[2][0]
      expect(restoreCall.graphic).toEqual(existingGraphic)
    })

    it('returns false when chart ref is null', () => {
      const chartRef = ref(null)
      const { exportPNG } = useChartExport(chartRef)

      expect(exportPNG({ filename: 'test' })).toBe(false)
    })

    it('returns false when chart instance is null', () => {
      const chartRef = ref({ chart: null })
      const { exportPNG } = useChartExport(chartRef)

      expect(exportPNG({ filename: 'test' })).toBe(false)
    })

    it('returns false for empty filename', () => {
      const chartRef = ref({ chart: mockChart })
      const { exportPNG } = useChartExport(chartRef)

      expect(exportPNG({ filename: '' })).toBe(false)
    })

    it('returns false when getDataURL returns invalid data', () => {
      mockChart.getDataURL.mockReturnValue('')
      const chartRef = ref({ chart: mockChart })
      const { exportPNG } = useChartExport(chartRef)

      expect(exportPNG({ filename: 'test' })).toBe(false)
    })

    it('sanitizes filename by stripping special characters', () => {
      const chartRef = ref({ chart: mockChart })
      const { exportPNG } = useChartExport(chartRef)

      exportPNG({ filename: 'wealth../../etc/passwd' })

      expect(linkDownload).toBe('wealthetcpasswd.png')
    })
  })

  describe('exportSVG', () => {
    it('returns true and triggers download on success', () => {
      const chartRef = ref({ chart: mockChart })
      const { exportSVG } = useChartExport(chartRef)

      const result = exportSVG({ filename: 'test-chart' })

      expect(result).toBe(true)
      expect(linkClicked).toBe(true)
      expect(linkDownload).toBe('test-chart.svg')
      expect(mockChart.getConnectedDataURL).toHaveBeenCalledWith({ type: 'svg' })
    })

    it('creates and revokes a blob URL', () => {
      const chartRef = ref({ chart: mockChart })
      const { exportSVG } = useChartExport(chartRef)

      exportSVG({ filename: 'test' })

      expect(URL.createObjectURL).toHaveBeenCalled()
      expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:http://localhost/fake-blob')
    })

    it('handles base64-encoded SVG data URLs', () => {
      const svgContent = '<svg><text>hello</text></svg>'
      const base64 = btoa(svgContent)
      mockChart.getConnectedDataURL.mockReturnValue(`data:image/svg+xml;base64,${base64}`)
      const chartRef = ref({ chart: mockChart })
      const { exportSVG } = useChartExport(chartRef)

      const result = exportSVG({ filename: 'test' })

      expect(result).toBe(true)
    })

    it('uses renderToSVGString when getConnectedDataURL is unavailable', () => {
      const chart = {
        ...mockChart,
        getConnectedDataURL: undefined,
        renderToSVGString: vi.fn(() => '<svg></svg>'),
      }
      const chartRef = ref({ chart })
      const { exportSVG } = useChartExport(chartRef)

      const result = exportSVG({ filename: 'test' })

      expect(result).toBe(true)
      expect(chart.renderToSVGString).toHaveBeenCalled()
    })

    it('returns false when neither SVG method is available', () => {
      const chart = {
        ...mockChart,
        getConnectedDataURL: undefined,
        renderToSVGString: undefined,
      }
      const chartRef = ref({ chart })
      const { exportSVG } = useChartExport(chartRef)

      const result = exportSVG({ filename: 'test' })

      expect(result).toBe(false)
    })

    it('removes watermark even when getConnectedDataURL throws', () => {
      mockChart.getConnectedDataURL.mockImplementation(() => { throw new Error('fail') })
      const chartRef = ref({ chart: mockChart })
      const { exportSVG } = useChartExport(chartRef)

      const result = exportSVG({ filename: 'test' })

      expect(result).toBe(false)
      const removeCalls = mockChart.setOption.mock.calls.filter((call) => {
        const option = call[0] as { graphic?: Array<{ $action?: string }> }
        return option.graphic?.[0]?.$action === 'remove'
      })
      expect(removeCalls.length).toBe(1)
    })

    it('returns false when getConnectedDataURL returns invalid format', () => {
      mockChart.getConnectedDataURL.mockReturnValue('invalid-no-comma')
      const chartRef = ref({ chart: mockChart })
      const { exportSVG } = useChartExport(chartRef)

      expect(exportSVG({ filename: 'test' })).toBe(false)
    })

    it('returns false when chart ref is null', () => {
      const chartRef = ref(null)
      const { exportSVG } = useChartExport(chartRef)

      expect(exportSVG({ filename: 'test' })).toBe(false)
    })

    it('adds watermark with source citation', () => {
      const chartRef = ref({ chart: mockChart })
      const { exportSVG } = useChartExport(chartRef)

      exportSVG({ filename: 'test', source: 'ONS' })

      const addCall = mockChart.setOption.mock.calls[0][0]
      expect(addCall.graphic[0].style.text).toContain('Source: ONS')
    })
  })
})

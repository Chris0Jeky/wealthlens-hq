import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref } from 'vue'
import { useChartExport } from '@/composables/useChartExport'

describe('useChartExport', () => {
  let mockChart: {
    getOption: ReturnType<typeof vi.fn>
    setOption: ReturnType<typeof vi.fn>
    getDataURL: ReturnType<typeof vi.fn>
    getConnectedDataURL: ReturnType<typeof vi.fn>
  }

  let linkClicked: boolean
  let linkHref: string
  let linkDownload: string

  beforeEach(() => {
    mockChart = {
      getOption: vi.fn(() => ({ graphic: [] })),
      setOption: vi.fn(),
      getDataURL: vi.fn(() => 'data:image/png;base64,fakedata'),
      getConnectedDataURL: vi.fn(() => 'data:image/svg+xml;charset=UTF-8,<svg></svg>'),
    }

    linkClicked = false
    linkHref = ''
    linkDownload = ''

    // Mock document.createElement for the <a> download trick
    vi.spyOn(document, 'createElement').mockImplementation((tag: string) => {
      if (tag === 'a') {
        const el = {
          href: '',
          download: '',
          style: { display: '' },
          click: () => {
            linkClicked = true
            linkHref = el.href
            linkDownload = el.download
          },
        }
        return el as unknown as HTMLElement
      }
      return document.createElement(tag)
    })

    vi.spyOn(document.body, 'appendChild').mockImplementation(() => null as any)
    vi.spyOn(document.body, 'removeChild').mockImplementation(() => null as any)

    // Mock URL.createObjectURL and revokeObjectURL
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
    it('calls getDataURL on the chart instance with correct options', () => {
      const chartRef = ref({ chart: mockChart })
      const { exportPNG } = useChartExport(chartRef)

      exportPNG({ filename: 'test-chart' })

      expect(mockChart.getDataURL).toHaveBeenCalledWith({
        type: 'png',
        pixelRatio: 2,
        backgroundColor: '#fff',
      })
    })

    it('triggers a download with the correct filename', () => {
      const chartRef = ref({ chart: mockChart })
      const { exportPNG } = useChartExport(chartRef)

      exportPNG({ filename: 'wealth-shares' })

      expect(linkClicked).toBe(true)
      expect(linkDownload).toBe('wealth-shares.png')
    })

    it('uses custom pixelRatio and backgroundColor when provided', () => {
      const chartRef = ref({ chart: mockChart })
      const { exportPNG } = useChartExport(chartRef)

      exportPNG({
        filename: 'test',
        pixelRatio: 3,
        backgroundColor: '#000',
      })

      expect(mockChart.getDataURL).toHaveBeenCalledWith({
        type: 'png',
        pixelRatio: 3,
        backgroundColor: '#000',
      })
    })

    it('adds and removes watermark during export', () => {
      const chartRef = ref({ chart: mockChart })
      const { exportPNG } = useChartExport(chartRef)

      exportPNG({ filename: 'test', source: 'WID.world' })

      // setOption called at least twice: once to add watermark, once to remove
      expect(mockChart.setOption).toHaveBeenCalledTimes(2)

      // First call adds the watermark graphic
      const addCall = mockChart.setOption.mock.calls[0][0]
      expect(addCall.graphic).toBeDefined()
      expect(addCall.graphic[0].style.text).toContain('WealthLens UK')
      expect(addCall.graphic[0].style.text).toContain('WID.world')
    })

    it('does not throw when chart ref is null', () => {
      const chartRef = ref(null)
      const { exportPNG } = useChartExport(chartRef)

      expect(() => exportPNG({ filename: 'test' })).not.toThrow()
    })

    it('does not throw when chart instance is null', () => {
      const chartRef = ref({ chart: null })
      const { exportPNG } = useChartExport(chartRef)

      expect(() => exportPNG({ filename: 'test' })).not.toThrow()
    })
  })

  describe('exportSVG', () => {
    it('calls getConnectedDataURL on the chart instance', () => {
      const chartRef = ref({ chart: mockChart })
      const { exportSVG } = useChartExport(chartRef)

      exportSVG({ filename: 'test-chart' })

      expect(mockChart.getConnectedDataURL).toHaveBeenCalledWith({ type: 'svg' })
    })

    it('triggers a download with .svg extension', () => {
      const chartRef = ref({ chart: mockChart })
      const { exportSVG } = useChartExport(chartRef)

      exportSVG({ filename: 'wealth-shares' })

      expect(linkClicked).toBe(true)
      expect(linkDownload).toBe('wealth-shares.svg')
    })

    it('creates a blob for download', () => {
      const chartRef = ref({ chart: mockChart })
      const { exportSVG } = useChartExport(chartRef)

      exportSVG({ filename: 'test' })

      expect(URL.createObjectURL).toHaveBeenCalled()
      expect(URL.revokeObjectURL).toHaveBeenCalledWith('blob:http://localhost/fake-blob')
    })

    it('does not throw when chart ref is null', () => {
      const chartRef = ref(null)
      const { exportSVG } = useChartExport(chartRef)

      expect(() => exportSVG({ filename: 'test' })).not.toThrow()
    })

    it('does not throw when chart instance is null', () => {
      const chartRef = ref({ chart: null })
      const { exportSVG } = useChartExport(chartRef)

      expect(() => exportSVG({ filename: 'test' })).not.toThrow()
    })

    it('adds watermark with source citation during SVG export', () => {
      const chartRef = ref({ chart: mockChart })
      const { exportSVG } = useChartExport(chartRef)

      exportSVG({ filename: 'test', source: 'ONS' })

      const addCall = mockChart.setOption.mock.calls[0][0]
      expect(addCall.graphic[0].style.text).toContain('Source: ONS')
    })
  })
})

import { type Ref } from 'vue'

export type ExportFormat = 'png' | 'svg'

export interface EChartsExportable {
  getOption(): { graphic?: unknown[] }
  setOption(option: Record<string, unknown>): void
  getDataURL(opts: { type: string; pixelRatio: number; backgroundColor: string }): string
  getConnectedDataURL?(opts: { type: string }): string
  renderToSVGString?(): string
}

export type ChartComponentRef = { chart: EChartsExportable | null } | null

export interface ExportOptions {
  filename: string
  backgroundColor?: string
  pixelRatio?: number
  source?: string
}

export function useChartExport(chartRef: Ref<ChartComponentRef>) {
  function buildWatermark(source?: string): string {
    let text = 'WealthLens UK · wealthlens.uk'
    if (source) {
      text += ` · Source: ${source}`
    }
    return text
  }

  function addWatermark(chart: EChartsExportable, source?: string): unknown[] {
    const currentOption = chart.getOption()
    if (!currentOption) return []
    const previousGraphic = (currentOption.graphic as unknown[]) || []

    chart.setOption({
      graphic: [{
        type: 'text',
        id: 'wl-export-watermark',
        left: 'center',
        bottom: 8,
        style: {
          text: buildWatermark(source),
          fontSize: 11,
          fontFamily: 'monospace',
          fill: '#999',
          textAlign: 'center',
        },
        z: 100,
      }],
    })

    return previousGraphic
  }

  function removeWatermark(chart: EChartsExportable, previousGraphic: unknown[] | null): void {
    try {
      chart.setOption({
        graphic: [{
          id: 'wl-export-watermark',
          $action: 'remove',
        }],
      })

      if (previousGraphic && previousGraphic.length > 0) {
        chart.setOption({ graphic: previousGraphic })
      }
    } catch {
      // Best-effort cleanup — chart may be disposed
    }
  }

  function triggerDownload(url: string, filename: string): void {
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  function sanitizeFilename(name: string): string {
    return name.replace(/[^a-zA-Z0-9_-]/g, '') || 'chart'
  }

  function exportPNG(options: ExportOptions): boolean {
    const instance = chartRef.value
    if (!instance?.chart) {
      console.warn('[useChartExport] exportPNG: chart instance unavailable')
      return false
    }
    if (!options.filename) return false

    const chart = instance.chart
    const { filename, backgroundColor = '#fff', pixelRatio = 2, source } = options
    const safeName = sanitizeFilename(filename)

    let previousGraphic: unknown[] | null = null
    try {
      previousGraphic = addWatermark(chart, source)
      const dataUrl = chart.getDataURL({
        type: 'png',
        pixelRatio: Math.max(1, pixelRatio),
        backgroundColor,
      })
      if (!dataUrl || !dataUrl.startsWith('data:')) {
        console.error('[useChartExport] getDataURL returned invalid result')
        return false
      }
      triggerDownload(dataUrl, `${safeName}.png`)
      return true
    } catch (err) {
      console.error('[useChartExport] PNG export failed:', err)
      return false
    } finally {
      removeWatermark(chart, previousGraphic)
    }
  }

  function exportSVG(options: ExportOptions): boolean {
    const instance = chartRef.value
    if (!instance?.chart) {
      console.warn('[useChartExport] exportSVG: chart instance unavailable')
      return false
    }
    if (!options.filename) return false

    const chart = instance.chart
    const { filename, source } = options
    const safeName = sanitizeFilename(filename)

    let previousGraphic: unknown[] | null = null
    try {
      previousGraphic = addWatermark(chart, source)
      let svgContent: string

      if (typeof chart.getConnectedDataURL === 'function') {
        const dataUrl = chart.getConnectedDataURL({ type: 'svg' })
        if (!dataUrl || !dataUrl.includes(',')) {
          console.error('[useChartExport] getConnectedDataURL returned invalid result')
          return false
        }
        const [header, payload] = dataUrl.split(',')
        if (header.includes(';base64')) {
          svgContent = atob(payload)
        } else {
          svgContent = decodeURIComponent(payload)
        }
      } else if (typeof chart.renderToSVGString === 'function') {
        svgContent = chart.renderToSVGString()
      } else {
        console.warn('[useChartExport] SVG export unavailable — chart may use canvas renderer')
        return false
      }

      const blob = new Blob([svgContent], { type: 'image/svg+xml;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      try {
        triggerDownload(url, `${safeName}.svg`)
      } finally {
        URL.revokeObjectURL(url)
      }
      return true
    } catch (err) {
      console.error('[useChartExport] SVG export failed:', err)
      return false
    } finally {
      removeWatermark(chart, previousGraphic)
    }
  }

  return { exportPNG, exportSVG }
}

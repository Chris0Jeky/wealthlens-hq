import { type Ref } from 'vue'

/**
 * Options for chart image export.
 */
export interface ExportOptions {
  /** Filename without extension (extension is appended automatically). */
  filename: string
  /** Background color for PNG export. Defaults to '#fff'. */
  backgroundColor?: string
  /** Pixel ratio for PNG export. Defaults to 2 for retina. */
  pixelRatio?: number
  /** Source citation to include in the watermark. */
  source?: string
}

/**
 * Composable for exporting ECharts instances as PNG or SVG images.
 *
 * Accepts a ref to a vue-echarts component (which exposes a `.chart` property
 * giving access to the underlying ECharts instance).
 *
 * @example
 * ```ts
 * const chartRef = ref<InstanceType<typeof VChart> | null>(null)
 * const { exportPNG, exportSVG } = useChartExport(chartRef)
 *
 * exportPNG({ filename: 'wealth-shares', source: 'WID.world' })
 * ```
 */
export function useChartExport(chartRef: Ref<{ chart: any } | null>) {
  /**
   * Build watermark text for the exported image.
   */
  function buildWatermark(source?: string): string {
    let text = 'WealthLens UK · wealthlens.uk'
    if (source) {
      text += ` · Source: ${source}`
    }
    return text
  }

  /**
   * Add a text watermark graphic element to the chart instance.
   * Returns the previous graphic option so it can be restored after export.
   */
  function addWatermark(chart: any, source?: string): any {
    const currentOption = chart.getOption()
    const previousGraphic = currentOption.graphic || []

    const watermarkGraphic = {
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
    }

    chart.setOption({
      graphic: [watermarkGraphic],
    })

    return previousGraphic
  }

  /**
   * Remove the export watermark and restore previous graphic state.
   */
  function removeWatermark(chart: any, previousGraphic: any): void {
    // Remove the watermark by setting it invisible, then restore previous
    chart.setOption({
      graphic: [{
        id: 'wl-export-watermark',
        $action: 'remove',
      }],
    })

    // Restore any previous graphic elements
    if (previousGraphic && previousGraphic.length > 0) {
      chart.setOption({ graphic: previousGraphic })
    }
  }

  /**
   * Trigger a file download in the browser using a temporary anchor element.
   */
  function triggerDownload(url: string, filename: string): void {
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  /**
   * Export the chart as a PNG image.
   *
   * Adds a watermark, captures the chart as a data URL, triggers a download,
   * then removes the watermark.
   */
  function exportPNG(options: ExportOptions): void {
    const instance = chartRef.value
    if (!instance?.chart) return

    const chart = instance.chart
    const { filename, backgroundColor = '#fff', pixelRatio = 2, source } = options

    const previousGraphic = addWatermark(chart, source)

    try {
      const dataUrl = chart.getDataURL({
        type: 'png',
        pixelRatio,
        backgroundColor,
      })
      triggerDownload(dataUrl, `${filename}.png`)
    } finally {
      removeWatermark(chart, previousGraphic)
    }
  }

  /**
   * Export the chart as an SVG file.
   *
   * Uses getConnectedDataURL for SVG output, falling back to renderToSVGString
   * if available. Triggers a blob download.
   */
  function exportSVG(options: ExportOptions): void {
    const instance = chartRef.value
    if (!instance?.chart) return

    const chart = instance.chart
    const { filename, source } = options

    const previousGraphic = addWatermark(chart, source)

    try {
      let svgContent: string

      // Try getConnectedDataURL first (works with both canvas and svg renderers)
      if (typeof chart.getConnectedDataURL === 'function') {
        const dataUrl = chart.getConnectedDataURL({ type: 'svg' })
        // Data URL format: data:image/svg+xml;charset=UTF-8,...
        // Decode it to get the raw SVG
        const encoded = dataUrl.split(',')[1]
        svgContent = decodeURIComponent(encoded)
      } else if (typeof chart.renderToSVGString === 'function') {
        svgContent = chart.renderToSVGString()
      } else {
        // Fallback: use PNG export if SVG is not available
        exportPNG({ ...options, filename })
        return
      }

      const blob = new Blob([svgContent], { type: 'image/svg+xml;charset=utf-8' })
      const url = URL.createObjectURL(blob)
      triggerDownload(url, `${filename}.svg`)
      URL.revokeObjectURL(url)
    } finally {
      removeWatermark(chart, previousGraphic)
    }
  }

  return { exportPNG, exportSVG }
}

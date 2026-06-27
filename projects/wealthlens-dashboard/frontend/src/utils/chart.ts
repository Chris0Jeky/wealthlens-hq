/** Escape HTML special characters to prevent XSS in tooltip content. */
export function escapeHtml(str: string): string {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
}

/**
 * Coerce a raw dataset cell to a finite number, or NaN if it is missing/blank.
 *
 * Plain `Number()` is unsafe for chart data: `Number(null)`, `Number("")` and
 * `Number("   ")` all return `0`, which silently fabricates a real data point
 * (a £0 wage, a "year 0", a 0% share) from a missing or suppressed source cell.
 * Mapping those to `NaN` lets the standard `!isNaN(...)` filter drop the row, so
 * a missing cell is never plotted or shown in the accessible table as a
 * fabricated 0. A genuine numeric `0` passes through unchanged.
 *
 * Use this in every chart's parse step instead of bare `Number(...)`.
 *
 * Strictly accepts only `number` and non-blank numeric `string`. Everything else
 * (null/undefined, blank/whitespace strings, booleans, arrays, objects, symbols)
 * maps to NaN rather than relying on `Number()`'s quirks (`Number([])===0`,
 * `Number(true)===1`, `Number(Symbol())` throws). Non-finite results (`Infinity`
 * from `"1e309"`/`"Infinity"`) also map to NaN so the contract — a finite number
 * or NaN — always holds and `!isNaN(...)` filters drop them.
 */
export function toNumberOrNaN(value: unknown): number {
  let n: number
  if (typeof value === "number") {
    n = value
  } else if (typeof value === "string") {
    const trimmed = value.trim()
    n = trimmed === "" ? NaN : Number(trimmed)
  } else {
    return NaN // null/undefined/boolean/array/object/symbol
  }
  return Number.isFinite(n) ? n : NaN // reject Infinity/-Infinity/NaN
}

/** Safely compute min/max from a number array without spreading (stack-safe). */
export function safeMinMax(arr: number[]): { min: number; max: number } {
  if (arr.length === 0) return { min: 0, max: 0 }
  let min = arr[0]
  let max = arr[0]
  for (let i = 1; i < arr.length; i++) {
    if (arr[i] < min) min = arr[i]
    if (arr[i] > max) max = arr[i]
  }
  return { min, max }
}

/**
 * Warn in the console when a significant proportion of rows are dropped
 * during NaN filtering. Helps surface data quality issues during development
 * without breaking the UI.
 *
 * @param datasetName - Human-readable name of the dataset (e.g. "productivity-pay")
 * @param totalRows - Number of rows before filtering
 * @param validRows - Number of rows after filtering
 * @param threshold - Fraction of dropped rows that triggers the warning (default 0.2 = 20%)
 */
export function warnIfSignificantDataLoss(
  datasetName: string,
  totalRows: number,
  validRows: number,
  threshold = 0.2,
): void {
  if (totalRows === 0) return
  const dropped = totalRows - validRows
  const dropRate = dropped / totalRows
  if (dropRate > threshold) {
    console.warn(
      `[WealthLens] Dataset "${datasetName}": ${dropped}/${totalRows} rows (${(dropRate * 100).toFixed(1)}%) were filtered out due to invalid/NaN values. ` +
        `This may indicate changed column names or malformed data.`,
    )
  }
}

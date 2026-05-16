export function formatCurrency(value: number, decimals = 0): string {
  if (Math.abs(value) >= 1_000_000_000) {
    return `£${(value / 1_000_000_000).toFixed(decimals)}bn`
  }
  if (Math.abs(value) >= 1_000_000) {
    return `£${(value / 1_000_000).toFixed(decimals)}m`
  }
  if (Math.abs(value) >= 1_000) {
    return `£${(value / 1_000).toFixed(decimals)}k`
  }
  return `£${value.toFixed(decimals)}`
}

export function formatPercent(value: number, decimals = 1): string {
  return `${value.toFixed(decimals)}%`
}

export function formatCompact(value: number): string {
  if (Math.abs(value) >= 1_000_000_000) {
    return `${(value / 1_000_000_000).toFixed(1)}B`
  }
  if (Math.abs(value) >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(1)}M`
  }
  if (Math.abs(value) >= 1_000) {
    return `${(value / 1_000).toFixed(1)}K`
  }
  return String(value)
}

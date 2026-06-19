import { describe, expect, it } from 'vitest'
import { escapeHtml, safeMinMax, toNumberOrNaN } from '../chart'

describe('toNumberOrNaN', () => {
  it('maps null / undefined / blank strings to NaN (not a fabricated 0)', () => {
    // The whole point: plain Number(null) === 0, Number('') === 0, Number('  ') === 0,
    // which would silently fabricate a real data point from a missing cell.
    expect(toNumberOrNaN(null)).toBeNaN()
    expect(toNumberOrNaN(undefined)).toBeNaN()
    expect(toNumberOrNaN('')).toBeNaN()
    expect(toNumberOrNaN('   ')).toBeNaN()
  })

  it('maps non-numeric strings to NaN', () => {
    expect(toNumberOrNaN('n/a')).toBeNaN()
    expect(toNumberOrNaN('abc')).toBeNaN()
  })

  it('preserves a genuine numeric 0 (so a real zero is NOT dropped)', () => {
    expect(toNumberOrNaN(0)).toBe(0)
    expect(toNumberOrNaN('0')).toBe(0)
  })

  it('parses real numbers and numeric strings', () => {
    expect(toNumberOrNaN(42)).toBe(42)
    expect(toNumberOrNaN('42.5')).toBe(42.5)
    expect(toNumberOrNaN(-3.7)).toBe(-3.7)
  })
})

describe('escapeHtml', () => {
  it('escapes ampersands', () => {
    expect(escapeHtml('a&b')).toBe('a&amp;b')
  })

  it('escapes angle brackets', () => {
    expect(escapeHtml('<script>')).toBe('&lt;script&gt;')
  })

  it('escapes double quotes', () => {
    expect(escapeHtml('a"b')).toBe('a&quot;b')
  })

  it('returns plain text unchanged', () => {
    expect(escapeHtml('hello world')).toBe('hello world')
  })

  it('handles empty string', () => {
    expect(escapeHtml('')).toBe('')
  })
})

describe('safeMinMax', () => {
  it('returns min and max from array', () => {
    expect(safeMinMax([3, 1, 4, 1, 5])).toEqual({ min: 1, max: 5 })
  })

  it('handles single element', () => {
    expect(safeMinMax([42])).toEqual({ min: 42, max: 42 })
  })

  it('returns zeros for empty array', () => {
    expect(safeMinMax([])).toEqual({ min: 0, max: 0 })
  })

  it('handles negative numbers', () => {
    expect(safeMinMax([-5, -1, -3])).toEqual({ min: -5, max: -1 })
  })
})

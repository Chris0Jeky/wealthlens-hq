import { describe, expect, it } from 'vitest'
import { escapeHtml, safeMinMax } from '../chart'

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

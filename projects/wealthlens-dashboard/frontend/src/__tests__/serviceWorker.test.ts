import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

const serviceWorkerSource = readFileSync(
  resolve(__dirname, '../../public/sw.js'),
  'utf-8',
)

describe('service worker', () => {
  it('keeps API handling within the registered GitHub Pages scope', () => {
    expect(serviceWorkerSource).toContain(
      "url.pathname.startsWith('/wealthlens-hq/api/')",
    )
    expect(serviceWorkerSource).not.toContain(
      "url.pathname.startsWith('/api/')",
    )
  })

  it('returns a JSON API fallback instead of the offline HTML page', () => {
    expect(serviceWorkerSource).toContain('new Response(API_OFFLINE_BODY')
    expect(serviceWorkerSource).toContain('status: 503')
    expect(serviceWorkerSource).toContain(
      "'Content-Type': 'application/json; charset=utf-8'",
    )
    expect(serviceWorkerSource).toContain("'Cache-Control': 'no-store'")
  })
})

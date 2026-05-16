import { describe, it, expect, vi, beforeEach } from 'vitest'
import { useClipboard } from '@/composables/useClipboard'

describe('useClipboard', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    })
  })

  it('starts with copied=false', () => {
    const { copied } = useClipboard()
    expect(copied.value).toBe(false)
  })

  it('sets copied=true after successful copy', async () => {
    const { copied, copy } = useClipboard()
    const result = await copy('hello')
    expect(result).toBe(true)
    expect(copied.value).toBe(true)
  })

  it('resets copied after 2 seconds', async () => {
    const { copied, copy } = useClipboard()
    await copy('test')
    expect(copied.value).toBe(true)
    vi.advanceTimersByTime(2000)
    expect(copied.value).toBe(false)
  })

  it('passes text to clipboard API', async () => {
    const { copy } = useClipboard()
    await copy('data to copy')
    expect(navigator.clipboard.writeText).toHaveBeenCalledWith('data to copy')
  })

  it('returns false when clipboard write fails', async () => {
    ;(navigator.clipboard.writeText as ReturnType<typeof vi.fn>).mockRejectedValueOnce(
      new Error('denied'),
    )
    const { copied, copy } = useClipboard()
    const result = await copy('fail')
    expect(result).toBe(false)
    expect(copied.value).toBe(false)
  })

  it('returns false when clipboard API unavailable', async () => {
    Object.assign(navigator, { clipboard: undefined })
    const { copy } = useClipboard()
    const result = await copy('no api')
    expect(result).toBe(false)
  })
})

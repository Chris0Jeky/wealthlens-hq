import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { ref, nextTick } from 'vue'
import { mount, config } from '@vue/test-utils'
import { defineComponent } from 'vue'
import { useDebounce } from '@/composables/useDebounce'

function withSetup<T>(composable: () => T): { result: T; unmount: () => void } {
  let result!: T
  const Wrapper = defineComponent({
    setup() {
      result = composable()
      return {}
    },
    template: '<div />',
  })
  const wrapper = mount(Wrapper)
  return { result, unmount: () => wrapper.unmount() }
}

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it('returns initial value immediately', () => {
    const source = ref('hello')
    const { result } = withSetup(() => useDebounce(source, 300))
    expect(result.value).toBe('hello')
  })

  it('does not update debounced value before delay', async () => {
    const source = ref('a')
    const { result } = withSetup(() => useDebounce(source, 300))
    source.value = 'b'
    await nextTick()
    vi.advanceTimersByTime(100)
    expect(result.value).toBe('a')
  })

  it('updates debounced value after delay', async () => {
    const source = ref('a')
    const { result } = withSetup(() => useDebounce(source, 300))
    source.value = 'b'
    await nextTick()
    vi.advanceTimersByTime(300)
    expect(result.value).toBe('b')
  })

  it('resets timer on rapid changes', async () => {
    const source = ref(0)
    const { result } = withSetup(() => useDebounce(source, 200))
    source.value = 1
    await nextTick()
    vi.advanceTimersByTime(100)
    source.value = 2
    await nextTick()
    vi.advanceTimersByTime(100)
    expect(result.value).toBe(0)
    vi.advanceTimersByTime(100)
    expect(result.value).toBe(2)
  })

  it('uses default 300ms delay', async () => {
    const source = ref('x')
    const { result } = withSetup(() => useDebounce(source))
    source.value = 'y'
    await nextTick()
    vi.advanceTimersByTime(299)
    expect(result.value).toBe('x')
    vi.advanceTimersByTime(1)
    expect(result.value).toBe('y')
  })

  it('clears timer on unmount', async () => {
    const source = ref('a')
    const { result, unmount } = withSetup(() => useDebounce(source, 300))
    source.value = 'b'
    await nextTick()
    unmount()
    vi.advanceTimersByTime(300)
    expect(result.value).toBe('a')
  })

  it('works with numeric values', async () => {
    const source = ref(10)
    const { result } = withSetup(() => useDebounce(source, 100))
    source.value = 42
    await nextTick()
    vi.advanceTimersByTime(100)
    expect(result.value).toBe(42)
  })
})

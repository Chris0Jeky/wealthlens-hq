import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { defineComponent, nextTick, ref } from 'vue'
import { mount } from '@vue/test-utils'
import {
  useSimulatorDashboard,
  useSimulatorScenarios,
} from '@/composables/useSimulatorDashboard'

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

function mockJson(body: unknown, ok = true, status = 200) {
  ;(fetch as ReturnType<typeof vi.fn>).mockResolvedValue({
    ok,
    status,
    statusText: 'OK',
    json: async () => body,
  })
}

describe('useSimulatorDashboard composables', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn())
  })
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('fetches the scenario list from /api/simulator/', async () => {
    mockJson({ scenarios: [{ id: 'a', name: 'A', description: 'd' }] })
    const { result } = withSetup(() => useSimulatorScenarios())
    await nextTick()
    await nextTick()
    expect(fetch).toHaveBeenCalledWith('/api/simulator/', expect.anything())
    expect(result.data.value?.scenarios[0].id).toBe('a')
  })

  it('fetches a scenario dashboard and re-fetches when the id changes', async () => {
    mockJson({
      schema_version: '1.3',
      total_revenue_gbp_bn: { low: 1, central: 2, high: 3 },
    })
    const id = ref('one-percent-wealth-tax')
    const { result } = withSetup(() => useSimulatorDashboard(id))
    await nextTick()
    await nextTick()
    expect(fetch).toHaveBeenCalledWith(
      '/api/simulator/scenarios/one-percent-wealth-tax',
      expect.anything(),
    )
    expect(result.data.value?.schema_version).toBe('1.3')

    id.value = 'two-percent-wealth-tax'
    await nextTick()
    await nextTick()
    expect(fetch).toHaveBeenCalledWith(
      '/api/simulator/scenarios/two-percent-wealth-tax',
      expect.anything(),
    )
  })

  it('does not fetch while the scenario id is empty', async () => {
    const id = ref('')
    withSetup(() => useSimulatorDashboard(id))
    await nextTick()
    expect(fetch).not.toHaveBeenCalled()
  })

  it('surfaces an HTTP error', async () => {
    mockJson(null, false, 503)
    const { result } = withSetup(() => useSimulatorDashboard(ref('x')))
    await nextTick()
    await nextTick()
    expect(result.error.value).toContain('503')
    expect(result.data.value).toBeNull()
  })
})

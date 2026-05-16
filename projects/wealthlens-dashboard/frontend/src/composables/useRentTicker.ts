/**
 * useRentTicker — reactive composable that tracks rent paid to private
 * landlords in real time since the composable was created.
 *
 * UK private rental sector revenue ≈ £85bn/year ≈ £2,695/second.
 * Source: ONS Private Rental Market Statistics, 2024.
 *
 * Returns:
 *   rentPaid  — formatted string, e.g. "£14,832"
 *   elapsed   — formatted MM:SS string, e.g. "02:15"
 *
 * Uses setInterval at 100ms for a live-feeling counter. The interval
 * is cleared automatically on unmount.
 */
import { ref, onMounted, onUnmounted } from 'vue'

/** £85bn per year in milliseconds */
const RATE_PER_MS = 85_000_000_000 / (365.25 * 24 * 60 * 60 * 1000)

export function useRentTicker() {
  const rentPaid = ref('£0')
  const elapsed = ref('00:00')

  let startTime = 0
  let timer: ReturnType<typeof setInterval> | null = null

  function tick() {
    const ms = Date.now() - startTime
    const paid = Math.floor(ms * RATE_PER_MS)
    rentPaid.value = '£' + paid.toLocaleString('en-GB')

    const totalSeconds = Math.floor(ms / 1000)
    const mm = String(Math.floor(totalSeconds / 60)).padStart(2, '0')
    const ss = String(totalSeconds % 60).padStart(2, '0')
    elapsed.value = `${mm}:${ss}`
  }

  onMounted(() => {
    startTime = Date.now()
    tick()
    timer = setInterval(tick, 100)
  })

  onUnmounted(() => {
    if (timer) clearInterval(timer)
  })

  return { rentPaid, elapsed }
}

/**
 * useRentTicker — reactive composable that tracks rent paid to private
 * landlords in real time since the composable was created.
 *
 * UK private rental sector revenue ≈ £85bn/year ≈ £2,695/second.
 *
 * Source: ONS Private Rental Market Statistics, Table 2.7, 2024.
 * URL: https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/
 *      privaterentalmarketsummarystatisticsinengland
 * The £85bn figure is an estimate derived from: mean monthly private rent
 * (£1,326 in 2024) x ~5.4 million private rented households (English
 * Housing Survey 2022-23) x 12 months, rounded. Scotland, Wales, and NI
 * add a further ~10%, giving a UK-wide ballpark of ~£85bn.
 *
 * Returns:
 *   rentPaid  — formatted string, e.g. "£14,832"
 *   elapsed   — formatted MM:SS string, e.g. "02:15"
 *
 * Uses setInterval at 100ms for a live-feeling counter. The interval
 * is paused when the browser tab is hidden (to avoid wasting CPU) and
 * resumed when the tab becomes visible again. Cleaned up on unmount.
 */
import { ref, onMounted, onUnmounted } from 'vue'

/** £85bn per year in milliseconds */
const RATE_PER_MS = 85_000_000_000 / (365.25 * 24 * 60 * 60 * 1000)

export function useRentTicker() {
  const rentPaid = ref('£0')
  const elapsed = ref('00:00')

  let startTime = 0
  /** Accumulated elapsed time before the most recent pause (ms). */
  let accumulatedMs = 0
  /** Timestamp when the timer was last resumed (or first started). */
  let resumeTime = 0
  let timer: ReturnType<typeof setInterval> | null = null

  function tick() {
    const ms = accumulatedMs + (Date.now() - resumeTime)
    const paid = Math.floor(ms * RATE_PER_MS)
    rentPaid.value = '£' + paid.toLocaleString('en-GB')

    const totalSeconds = Math.floor(ms / 1000)
    const mm = String(Math.floor(totalSeconds / 60)).padStart(2, '0')
    const ss = String(totalSeconds % 60).padStart(2, '0')
    elapsed.value = `${mm}:${ss}`
  }

  function startTimer() {
    if (timer) return // already running
    resumeTime = Date.now()
    tick()
    timer = setInterval(tick, 100)
  }

  function stopTimer() {
    if (!timer) return
    accumulatedMs += Date.now() - resumeTime
    clearInterval(timer)
    timer = null
  }

  function onVisibilityChange() {
    if (document.hidden) {
      stopTimer()
    } else {
      startTimer()
    }
  }

  onMounted(() => {
    startTime = Date.now()
    resumeTime = startTime
    accumulatedMs = 0
    startTimer()
    document.addEventListener('visibilitychange', onVisibilityChange)
  })

  onUnmounted(() => {
    stopTimer()
    document.removeEventListener('visibilitychange', onVisibilityChange)
  })

  return { rentPaid, elapsed }
}

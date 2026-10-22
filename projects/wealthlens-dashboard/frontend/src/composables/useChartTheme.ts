import { computed, shallowRef, watch } from "vue"
import { useTheme } from "@/composables/useTheme"

/** Resolve CSS tokens to canvas colours after the document theme has updated. */
export function useChartTheme() {
  const { theme } = useTheme()
  function readColors() {
    const dark = theme.value === "dark"
    const style =
      typeof document === "undefined" ? null : getComputedStyle(document.documentElement)
    const token = (name: string, fallback: string) =>
      style?.getPropertyValue(name).trim() || fallback
    return {
      heading: token("--wl-ink", dark ? "#e8e8e8" : "#111111"),
      text: token("--wl-ink-body", dark ? "#cccccc" : "#1a1a1a"),
      muted: token("--wl-ink-muted", dark ? "#999999" : "#5a5550"),
      card: token("--wl-card", dark ? "#242424" : "#fbf8f1"),
    }
  }
  const colors = shallowRef(readColors())
  watch(
    theme,
    () => {
      colors.value = readColors()
    },
    { flush: "post" },
  )

  const axisStyle = computed(() => ({
    nameTextStyle: { color: colors.value.text },
    axisLine: { lineStyle: { color: colors.value.muted } },
    axisTick: { lineStyle: { color: colors.value.muted } },
  }))

  // Existing series palettes use six-digit hex colours. Lighten the same hues
  // on dark cards so bars, lines and reference marks retain at least 3:1 contrast.
  function markColor(hex: string): string {
    if (theme.value !== "dark") return hex
    const channels = hex.slice(1).match(/../g)!
    return (
      "#" +
      channels
        .map((channel) =>
          Math.round(parseInt(channel, 16) * 0.45 + 255 * 0.55)
            .toString(16)
            .padStart(2, "0"),
        )
        .join("")
    )
  }

  const onMark = computed(() => (theme.value === "dark" ? "#111111" : "#ffffff"))
  return { colors, axisStyle, markColor, onMark }
}

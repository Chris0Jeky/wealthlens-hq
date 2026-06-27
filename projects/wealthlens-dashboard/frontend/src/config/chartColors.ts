/**
 * Shared chart series colours — single source of truth.
 *
 * The wealth-shares chart (WealthSharesChart.vue) plots exactly two WID series,
 * and the broadsheet toolbar legend above it (chartArticles.ts) must use the
 * SAME colours, or the legend dots stop matching the lines. Keeping the two
 * literals here (rather than copied into each file) means a colour change in one
 * place propagates to the chart, the legend, and the guard test together —
 * preventing the "phantom series / wrong colours" drift this module was added
 * to fix.
 *
 * Contrast (against the light-theme white card background):
 *   - #1a56db (blue, top 10%) ~7.2:1
 *   - #dc2626 (red,  top 1%)  ~4.6:1
 * NOTE: dark-theme non-text contrast for these dots/lines is tracked separately
 * as a known deferred item (see ORCHESTRATION dark-theme AA), not here.
 */

/** Top 10% (WID p90p100) series colour. */
export const COLOR_TOP_10 = "#1a56db"

/** Top 1% (WID p99p100) series colour. */
export const COLOR_TOP_1 = "#dc2626"

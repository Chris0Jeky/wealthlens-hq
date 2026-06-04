/**
 * Types mirroring the WealthLens-Sim dashboard JSON contract
 * (`wealthlens_sim.outputs.to_dashboard_json`, schema 1.3).
 *
 * These are hand-written to match the Python contract; keep them in sync when the
 * simulator's `DASHBOARD_SCHEMA_VERSION` changes. Only the fields the frontend
 * consumes today are modelled — extend as components start reading more of the
 * contract.
 */

/** A credible interval: `low <= central <= high`, all in the figure's own unit. */
export interface Interval {
  low: number
  central: number
  high: number
}

/**
 * How a published low/high band was derived.
 * - `alpha_sweep`: the single multiplicative top-tail-Pareto-alpha range.
 * - `monte_carlo`: a Monte-Carlo credible interval over sampled parameters.
 */
export type IntervalMethod = 'alpha_sweep' | 'monte_carlo'

/** Props for {@link ConfidenceFanChart}. Prop-driven so it needs no backend. */
export interface ConfidenceFanChartProps {
  /** The interval to render (e.g. a revenue figure in GBP billions). */
  interval: Interval
  /** Human label for the metric, e.g. "Total revenue". */
  label: string
  /** Currency symbol prefixed to each value. Default "£". */
  currency?: string
  /** Unit suffix appended to each value, e.g. "bn" -> "£9.36bn". Default "bn". */
  unit?: string
  /** Decimal places for the displayed values. Default 2. */
  decimals?: number
  /**
   * Data-integrity caveats the consumer MUST render (the dashboard JSON
   * `caveats[]`). Shown as a warning banner above the chart.
   */
  caveats?: string[]
  /** How the band was derived; rendered as a small, muted method label. */
  intervalMethod?: IntervalMethod
  /**
   * Whether the simulator declared its provenance complete. When `false` the
   * band is unsourced/degenerate and is labelled and styled as such.
   */
  provenanceComplete?: boolean
}

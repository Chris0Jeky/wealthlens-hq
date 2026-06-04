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

/**
 * The dashboard JSON schema version these types were written against (mirror of
 * the Python `DASHBOARD_SCHEMA_VERSION`). The future `/api/simulator/dashboard`
 * bridge should assert `payload.schema_version === DASHBOARD_SCHEMA_VERSION` and
 * surface a loud mismatch rather than silently rendering stale-shaped data.
 */
export const DASHBOARD_SCHEMA_VERSION = '1.3'

/** Props for {@link ConfidenceFanChart}. Prop-driven so it needs no backend. */
export interface ConfidenceFanChartProps {
  /** The interval to render (e.g. a revenue figure in GBP billions). */
  interval: Interval
  /** Human label for the metric, e.g. "Total revenue". */
  label: string
  /**
   * How the band was derived; rendered as a small method label. **Required** — the
   * contract always emits a single root-level `interval_method` (one per payload,
   * NOT per `Interval`); the consumer threads that value down to each chart.
   */
  intervalMethod: IntervalMethod
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
  /**
   * Whether the simulator declared its provenance complete. When `false` the
   * band is unsourced/degenerate and is labelled and styled as such.
   */
  provenanceComplete?: boolean
}

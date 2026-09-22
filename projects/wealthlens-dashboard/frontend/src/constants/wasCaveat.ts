/**
 * Shared wording for the June-2025 Wealth and Assets Survey accreditation-loss
 * caveat on the interactive /tools/* surfaces.
 *
 * Mandated by research/methodology/was-caveats.md ("Any chart sourced from WAS
 * must carry a visible caveat") and the dashboard region CLAUDE.md, which also
 * requires the caveat to be wired to the figure via aria-describedby. The OSR
 * withdrew accredited official statistics status in June 2025 (Assessment
 * Report 396) after the survey's response rate fell.
 *
 * The clause is a predicate so each tool can compose it into its own sentence
 * ("the Wealth and Assets Survey lost ..." / "..., which lost ...") while the
 * disclosed fact stays worded identically everywhere.
 */
export const WAS_ACCREDITATION_LOSS =
  "lost accredited official statistics status in June 2025 (declining response rates)"

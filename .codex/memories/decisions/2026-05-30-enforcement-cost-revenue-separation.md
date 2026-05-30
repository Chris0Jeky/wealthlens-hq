# Decision: Enforcement Cost Is Not Revenue

Date: 2026-05-30
Status: Accepted

## Context

PR #336 replaced the v0.1 Family-F enforcement overstatement placeholder with a
baseline-vs-theoretical compliance model. Adversarial review found that folding
`enforcement_cost_bn` into `enforcement_uplift_bn` could make a revenue headline
negative and could break interval-bound attribution invariants when net fiscal
impact was negative.

## Decision

Treat Family-F enforcement revenue as gross compliance uplift. Keep additional
HMRC enforcement cost out of `total_revenue_gbp_bn`; surface it separately as
`enforcement_cost_bn` and expose `enforcement_net_fiscal_impact_bn` for uplift
minus cost. Dashboard schema version is bumped to `1.2`.

## Consequences

- Revenue totals cannot go negative because of a spending assumption.
- Decile and nation attribution invariants remain revenue-only:
  `sum(split) ~= total_revenue_gbp_bn - enforcement_uplift_bn`.
- Consumers that want fiscal impact must use
  `enforcement_net_fiscal_impact_bn`, not the revenue headline.
- Enforcement compliance assumptions and sources must appear in provenance when
  enforcement affects complete outputs.

## Sources

- HMRC, "Measuring tax gaps 2025 edition: tax gaps summary"; accessed
  2026-05-30:
  https://www.gov.uk/government/statistics/measuring-tax-gaps/1-tax-gaps-summary
- NAO, "Collecting the right tax from wealthy individuals"; accessed
  2026-05-30:
  https://www.nao.org.uk/reports/collecting-the-right-tax-from-wealthy-individuals/

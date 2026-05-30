# Decision: Default Synth Calibration Uses Great Britain Scope

Date: 2026-05-30
Status: Accepted

## Context

PR #335 calibrated the default synthetic household generator to public ONS/WAS
aggregate marginals and added source IDs to population provenance. The latest ONS
Wealth and Assets Survey release and dataset are Great Britain scoped, while the
prior default generator used a UK household total and included Northern Ireland
in the default nation shares.

## Decision

Use Great Britain as the default calibration scope for the synthetic population
until a Northern Ireland-compatible wealth marginal is wired in. Default
household counts and nation shares are anchored to ONS Great Britain household
counts for England, Wales, and Scotland, and Northern Ireland is excluded from
the default synth calibration scope.

## Consequences

- Default synthetic wealth totals now align with the public WAS scope used for
  wealth marginals.
- Published dashboard/example outputs must continue to label these figures as
  synthetic and GB-scoped when they depend on the default synth population.
- Adding a UK-wide default later requires a cited Northern Ireland-compatible
  wealth marginal or an explicit imputation decision.

## Sources

- ONS, "Total wealth in Great Britain: April 2018 to March 2020"; accessed
  2026-05-30:
  https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/latest
- ONS, "Total wealth: wealth in Great Britain"; accessed 2026-05-30:
  https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/datasets/totalwealthwealthingreatbritain
- ONS, "Families and households in the UK: 2022", household counts by regions
  and GB constituent countries; accessed 2026-05-30:
  https://www.ons.gov.uk/peoplepopulationandcommunity/birthsdeathsandmarriages/families/datasets/householdsbytypeofhouseholdandfamilyregionsofenglandandgbconstituentcountries/2022

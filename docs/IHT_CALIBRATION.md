# IHT Calibration: stock-to-flow and the synth overshoot

Status: Tier A IMPLEMENTED (stock-to-flow mortality conversion); Tier B/C pending.
IHT scenarios remain EXCLUDED. Last updated: 2026-06-05.
Owner area: `packages/wealthlens-sim` (Family D, inheritance tax).
Related: `tasks/inbox.md` (IHT calibration item), Blueprint v5 section 3.3
("credible IHT modelling requires mortality and age structure").

## Why IHT scenarios are not served

The synthetic IHT headline is a ~100x+ overshoot: roughly **£1,009bn** versus
**~£7-8bn** real annual UK IHT receipts (HMRC). IHT scenarios are therefore
deliberately excluded from the served set (see the comments in
`automation/data-pipelines/generate_simulator_dashboards.py` and
`projects/wealthlens-dashboard/backend/app/routers/simulator.py`). This note
records the precise cause and a tiered plan so a fix can be reviewed against a
clear target, and so we never serve an IHT number that cannot be sanity-checked
against published statistics.

## Root cause (precise)

The per-household IHT calculation is sound. `_compute_person_iht`
(`reforms/d_iht_reform.py`) correctly applies the nil-rate band (£325k), the
residence nil-rate band and its taper on the pre-relief estate (HMRC IHTM46023),
APR/BPR reliefs, spousal exemption, the 40% rate, and the 36% charitable rate. The
bug is in **aggregation**, `compute_aggregate_iht_revenue`:

```python
for hh in households:
    result = compute_household_iht(hh, config, person_flags)
    total_revenue += result.total_iht_liability * hh.weight
```

This sums every household's at-death liability across the whole grossed-up
population, i.e. it models the tax **as if every household died this year**. That
is a *stock* of latent estate liability, not the *annual flow* of estates that
actually pass at death. There is no mortality factor anywhere in the call chain;
`Person.age` exists on the schema but is never read by the IHT path, and synth
ages are drawn uniformly on [18, 90) and are uncorrelated with wealth.

## Two compounding errors

1. **Stock vs flow (~40x).** Only the estates of people who die in a year are
   subject to IHT. UK deaths are ~660k/year against ~27.5m households, an annual
   household crystallisation rate of roughly **0.024**. Multiplying the stock by
   this rate is the missing conversion.
2. **Synth top-tail over-concentration (~3x residual).** Even after the mortality
   conversion the headline is ~£21bn, still ~3x the ~£7-8bn real figure. The synth
   population over-states top wealth (lognormal body + Pareto tail, currently not
   calibrated tightly enough at the very top, and ages uncorrelated with wealth),
   so the taxable estate mass above the NRB is too large. This is a *separate*
   defect from the mortality bug and must not be hidden inside the mortality
   scalar.

Implied check: real annual flow / death rate = £7.5bn / 0.024 ~= £312bn implied
"real" stock, versus the synth's £1,009bn stock, i.e. the synth stock is ~3.2x too
high. That 3.2x is error (2), confirming the two are distinct.

## Calibration anchors (sources)

- HMRC IHT receipts ~£7-8bn/year (HMRC Tax and NIC Receipts; `hmrc-tax-receipts`
  already in `registries/sources.yml`).
- UK deaths registered ~660k/year (ONS Deaths registered, OGL; **to be added** to
  `registries/sources.yml` as e.g. `ons-deaths-registered`).
- ~4% of estates pay IHT (HMRC IHT Statistics; cited in
  `research/data-sources/data-source-registry.md`). Note this 4% is already
  captured implicitly: only ~4% of households have estates above the NRB after
  reliefs, so they are the only ones with a non-zero liability.

## Tiered plan

### Tier A - annual mortality conversion. DONE (2026-06-05).
Applied an ONS-sourced annual mortality/crystallisation rate to the aggregate AND
the decile/nation attribution (so the engine's decile-sum == total invariant and the
enforcement baseline stay consistent): `annual_iht = mortality_rate *
sum(at_death_liability * weight)`. Added `IHTConfig.annual_mortality_rate` (default
`ANNUAL_MORTALITY_RATE_2026 = 581_363 / 27_500_000 ~= 0.0211`), the
`registries/sources.yml` `ons-deaths-registered` entry, and the
`registries/assumptions.yml` `model.iht.annual_mortality_rate.v1` assumption. The
per-household at-death calculation is unchanged. **Measured result on the real synth
(n=2000, seed=20): stock £1009.0bn -> flow £21.3bn** (a sanity-bound test pins this).
Still ~3x the ~£7-8bn real, so IHT stays excluded.

Tier A limitations to document in code: uniform mortality (does not yet use
age-specific q_x), a deaths-per-household approximation (IHT crystallises per
estate, often on the second spouse death; not modelled in v0.1), and it does NOT
fix error (2). **IHT scenarios stay excluded after Tier A** because ~£21bn is
still not sanity-checkable against ~£7-8bn.

### Tier B - age-specific mortality + age-wealth correlation. Medium.
Use ONS National Life Tables q_x per the head's age, and make the synth draw ages
correlated with wealth (IHT estates skew old and wealthy). Refines *which* estates
crystallise and shrinks error (2). Requires 2-3 new data sources and synth
generator changes. This is the realistic path to a serveable IHT headline.

### Tier C - real WAS/FRS microdata. Large, multi-sprint.
Licensed microdata with genuine age-wealth correlation plus ONS period life
tables. Blocks on the UKDS licence (see `tasks/inbox.md` real-provider item).

## Re-enablement bar

Do not re-enable any served IHT scenario until the headline is sanity-checkable
against ~£7-8bn real (within a defensible band, with caveats). On current analysis
that requires at least Tier B (plus a tighter synth top-tail). Tier A is a strict
improvement (1,009bn -> ~21bn) and removes the most egregious (stock-vs-flow)
error, but is not sufficient on its own to serve.

## Open question for Chris (deferred)

How far should IHT go for v0.1? Options: (a) ship Tier A as a correctness fix and
keep IHT excluded (lowest effort, honest); (b) invest in Tier B to make a caveated
IHT scenario serveable; (c) wait for the real WAS/FRS provider (Tier C). The
recommendation is (a) now, (b) when the real-provider work is scheduled.

## Related minor item (separate)

Gate-3 note (`tasks/inbox.md`): the 10% charitable reduced-rate test uses the gross
estate rather than UK law's post-relief "baseline amount". Documented v0.1
simplification in `PersonIHTFlags`; refine alongside Tier B.

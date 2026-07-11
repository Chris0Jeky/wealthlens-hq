# Freshness grammar — what "fresh" honestly means here

Date: 2026-07-11
Status: ADOPTED (implemented with reality-check F3; supersedes the fixed
30-day fresh/stale/expired ladder in the frontend)
Companion: `docs/product/REALITY_CHECK_2026-07-11.md` finding F3.

## The problem with the old ladder

The public site graded every dataset on one wall-clock ladder: fresh under
7 days, stale under 30, **"Expired"** after that — thresholds designed for a
live API feed. But WealthLens republishes *official statistics*: WID updates
roughly annually, the Wealth and Assets Survey every two years (currently
suspended), HMRC receipts monthly. Fully current annual data was branded
red "Expired" after a month, and once the weekly refresh cron was disabled
(#495) the home page became a permanent wall of red — on a site whose first
value is data honesty. A freshness claim that ignores how often the source
publishes is a fabricated claim.

## What a freshness badge can honestly say

Two different questions hide inside "is this fresh?":

1. **Is our copy up to date with the source?** — Has the upstream published
   a release we haven't ingested?
2. **How old is the underlying data?** — An honest answer is a *date*, not
   a traffic light; the reader judges it against their own needs.

The badge answers question 1, **relative to each source's own cadence**.
Question 2 is answered by always showing the "data as of" date (the badge
tooltip, the masthead vintage, and every chart's source line already do).

## The four states

Let `age` = days since the dataset's curated `last_updated`, and `interval`
= the source's declared release cadence, with a **grace factor of 1.25**
(official releases slip; an annual series published 13 months ago is not
late).

| State | Condition | Badge | What it honestly means |
|---|---|---|---|
| **Current** | `age ≤ interval × 1.25` | green · "Current" | No newer upstream release is expected to exist yet. Fully-current annual data stays green all year. |
| **Update due** | `age > interval × 1.25` | amber · "Update due" | The source has likely published since we last ingested — *our copy* may lag. It does not mean the figures are wrong; they remain the newest we hold. |
| **Source suspended** | cadence declares `(suspended)` | grey · "Source suspended" | The source itself has stopped publishing (e.g. the Wealth and Assets Survey lost accreditation in June 2025 and is suspended). Age arithmetic is meaningless: there is nothing newer to be behind. The last published round remains the best available official data. |
| **Unknown** | no parsable date, or a cadence we can't map | grey · "Unknown" | We won't guess. The date line (if any) still shows. |

There is deliberately **no red state**. Red screamed "don't trust this",
which was almost always a false claim about correct, current data. The
worst honest situation — our ingest lags a known release — is amber,
because the remedy is ours (re-run the pipeline), not the reader's.

## Cadence source of truth

The interval comes from `frontend/src/constants/datasetProvenance.ts`
(`updateFrequency`), which is itself reconciled against
`registries/sources.yml` `update_pattern` and guarded by a keyset test —
we parse that one label rather than adding a second cadence copy:

| Label (provenance) | Interval |
|---|---|
| Monthly | 31 days |
| Quarterly | 92 days |
| Annual / Annual (irregular) | 366 days |
| Biennial | 731 days |
| …contains "(suspended)" | — (Suspended state) |
| anything unmapped | — (Unknown state; a unit test pins all 12 current labels so this can only happen to a future label) |

## The suspended-WAS case, spelled out

`wealth-by-decile` (and the WAS-derived generational series) sit on a
survey that is **suspended**. Under the old ladder they showed "Expired"
forever — implying the site was neglecting an available update. Under this
grammar they show "Source suspended", the tooltip names the situation, and
the WAS accreditation caveat (already enforced on every WAS chart) carries
the detail. That is the true state of the world: the data is as current as
UK official statistics allow.

## Relative-time copy

The "updated X ago" copy rounds honestly: month counts round to the nearest
month (the old copy said "1 month ago" for anything under 60 days — a
~2-month-old date read as half its age, reality-check F10), and ages
beyond a year say "N years ago" rather than "18 months ago" pretending
precision.

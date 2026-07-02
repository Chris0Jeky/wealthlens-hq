# RFC-007 — The data-health layer: honesty as UX

Last updated: 2026-07-02
Status: PROPOSED (product-frontier review 2026-07).
Index: [`../PRODUCT_FRONTIER_2026-07.md`](../PRODUCT_FRONTIER_2026-07.md)

## Problem and who it serves

WealthLens's genuine differentiator — the audit culture, the provenance
registry, the refusal to publish a miscalibrated IHT number, the WAS
caveat discipline — is almost entirely invisible machinery. Meanwhile the
single most replicated finding of the audience council (12 of 12
personas) is that **methodology candour was the only thing that reliably
converted sceptics in-session**: the retired sceptic, the economist, the
think-tanker, the journalist, and the FOI blogger all moved on the WAS
accreditation caveat specifically. At the same time, the UK's wealth
evidence base is in a live, newsworthy quality crisis (accreditation
suspended June 2025; a three-year publication lag; a series break; no
official time series) that no one is explaining to lay audiences.

Who it serves: every audience at once — it is the trust substrate the
other RFCs draw on — but most directly experts deciding whether to
recommend the site, and readers deciding whether it's "just some lobby
site".

## Value hypothesis

- **Evidence (council):** candour converting sceptics is observed
  behaviour, not stated preference — the demand sceptic's own conclusion:
  "protect it above every feature request". The economist's decisive page
  ("the page that decides whether he ever recommends the site to another
  economist") is a top-tail methodology explainer.
- **Evidence (landscape):** PolicyEngine publishes divergence-from-
  official-forecast tables and won HM Treasury's trust; data.police.uk's
  documented limitations are cited as why it's safe to cite; OSR's public
  suspension of WAS makes the explainer timely journalism, not evergreen
  filler.
- **Hypothesis (marked):** a "data health" badge changes reader behaviour.
  Unproven; but its cost is near-zero because every input already exists
  in `datasetProvenance.ts` + `was-caveats.md`.

## MVP slice (≤1 week) vs full vision

**MVP:**
1. **Publish the explainer**: "Why Britain lost track of its wealth" —
   the ~£800bn top-tail undercount, the £2.3tn pension-methodology break,
   the accreditation suspension, what can and cannot be said now. The
   research, references, and caveat language are already written in
   `research/methodology/was-caveats.md`; this is an editing job with a
   2-lens factual review. It is simultaneously the site's first
   methodology writeup and its most natural outreach artefact.
2. **Data-health badge v1** on every chart page: source, fieldwork period
   vs publication date, accreditation status, known breaks — rendered
   from the existing provenance single-source-of-truth (replacing the
   misleading 30-day freshness dot, which RFC-001c removes).

**Full vision:**
- **The trust dossier**: one public page assembling what already exists —
  the model charter ("no naked point estimates"), the IHT refusal story
  (`docs/IHT_CALIBRATION.md`: declining to publish a 3x-overshoot number
  is the single most credible thing a data project can show), the ADRs,
  the AI/LLM disclosure policy, the audit-arc summary (real bugs found
  and fixed before readers saw them). Title it plainly: "How we keep the
  numbers honest".
- **Update ledger** (Fed-DFA pattern): per dataset — source release date,
  WealthLens rebuild date, next expected release; "timeliness relative to
  the source" becomes the credibility signal the freshness badge failed
  to be.
- **Corrections & revisions log** (Full Fact pattern): a /corrections
  page; dated "what changed" notes when upstream revises or WealthLens
  fixes an error. The audit arc already generates the raw material.
- **A "what this number can't tell you" standard section** on chart
  pages, upgraded from collapsed accordion to skimmable bullets (the
  council showed collapsed caveats don't travel).
- **Top-tail methodology page**: how survey-based top shares compare to
  Rich-List-augmented and capitalised-income approaches, with the honest
  quantified gap — an *explainer of the literature*, explicitly NOT a
  novel WealthLens-adjusted series (anti-portfolio; the critics were
  right that a solo novel series invites specialist attack).

## Architecture sketch

Static content + one Vue component (the badge) reading
`datasetProvenance.ts`. The ledger extends RFC-002's changelog. No new
data, no backend, no LLM.

## Data sources

All internal docs already in-repo (`research/methodology/was-caveats.md`,
`docs/IHT_CALIBRATION.md`, `docs/MODEL_CHARTER.md`, ADRs, data-licences),
plus OSR's public statements on WAS (osr.statisticsauthority.gov.uk, open)
for the explainer's citations. Feasibility: highest-confidence RFC in the
set — it is assembly and editing of verified existing material.

## Cost envelope

£0. Editorial time only.

## Honesty / misreading / abuse risks and mitigations

- **Candour weaponised** ("even they admit the data is broken"): the
  explainer must pair every limitation with what CAN still be said and
  why the direction of known biases is understood (undercount ⇒ published
  concentration figures are floors, not ceilings — a point the existing
  caveat doc already makes with citations).
- **Self-congratulation risk** in the trust dossier: keep it descriptive
  (what we do, verifiable in the repo) not promotional; every claim links
  to the artefact (test, ADR, PR).
- **Badge fatigue**: one badge, consistent grammar, no stacking of five
  warning labels per chart — severity tiers instead.

## Open challenges, with candidate solutions

1. **Making candour skimmable without dilution**: candidate — the
   two-layer pattern: one-line badge + expandable detail, with the
   one-liner written to survive screenshots (artefact-carries-honesty
   law).
2. **Keeping the ledger honest when automation gaps exist** (3 pipelines
   are hardcoded transcriptions): the ledger states "manually
   transcribed" for those — the ledger's own honesty is the product.

## Definition of shipped (visible artifact)

The explainer is live and linked from every WAS-sourced chart; the
data-health badge replaces the freshness dot on all 12 pages; the trust
dossier page exists and is linked from the footer. (Outreach use — e.g.
sending the explainer to Tax Justice UK / Equality Trust — belongs to the
launch bundle, not this RFC.)

## Seeded tasks (half-day granularity)

- [ ] RFC-007a: edit was-caveats.md into the public explainer; 2-lens
  factual review; publish + cross-link from WAS charts (@agent)
- [ ] RFC-007b: data-health badge component from datasetProvenance
  (replaces freshness dot; pairs with RFC-001c) (@agent)
- [ ] RFC-007c: trust dossier page assembling charter/ADRs/IHT-refusal/
  disclosure with repo links (@agent)
- [ ] RFC-007d: update ledger + /corrections page riding RFC-002c's
  changelog (@agent)
- [ ] RFC-007e: top-tail methodology explainer (literature survey framing,
  no novel series), 2-lens reviewed (@agent)

## Dependencies and what it must NOT break

- Pairs with RFC-001c (badge swap) and RFC-002c (changelog). No blockers.
- Must not break: the mandated WAS caveat enforcement, the existing
  provenance guard tests.
- Must not: publish a novel adjusted series, or let any trust claim
  outrun a verifiable artefact.

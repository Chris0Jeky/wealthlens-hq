# RFC-002 — WealthLens Datasets: citable, versioned data packages

Last updated: 2026-07-02
Status: PROPOSED (product-frontier review 2026-07).
Index: [`../PRODUCT_FRONTIER_2026-07.md`](../PRODUCT_FRONTIER_2026-07.md)
Annex: problem C (citation permanence) governs the versioning design.

## Problem and who it serves

A de-facto public data API is already deployed and CORS-open: 12 datasets
as rows + citation metadata + a combined catalogue at stable URLs under
`chris0jeky.github.io/wealthlens-hq/data/` (verified live 2026-07-02). It
is documented nowhere, linked from nowhere, carries no licence field in the
machine metadata, has no versioning or changelog (files overwritten every
deploy; only 3 of 12 tracked in git), and provenance truth is fragmented
across ~6 unreconciled copies in the repo. Meanwhile ONS publishes wealth
statistics only as spreadsheet workbooks — the Wealth and Assets Survey is
entirely absent from the ONS API.

Who it serves: data journalists and think-tank researchers (pre-reconciled,
cited series faster than excavating ONS workbooks), academics (R-ready
series with vintages), open-data builders (the council's FOI enthusiast
converted on exactly this: "documentation IS the product"), students, and
partner organisations who could build surfaces on the endpoints (the
Carbon Intensity API pattern: WWF built the widget, the API team built the
API).

## Value hypothesis

- **Evidence (council):** the strongest cross-persona signal in the whole
  exercise — seven personas from seven professions converged on "publish
  the data layer honestly" (the honesty-hawk critic's phrase), and it maps
  to an *existing daily behaviour* (the think-tanker downloads data from a
  dozen sites weekly) rather than an aspirational one.
- **Evidence (landscape):** the vacuum is real and verified: WAS absent
  from the ONS API; IFS TaxLab items expose no per-chart data; RF's
  dashboard CSVs date to 2019 and 404; OWID proves metadata + citation +
  licence clarity is what converts a chart into the default citation.
- **Deflations to hold (critics):** most professionals will strip-mine and
  still cite ONS — acceptable; the mission is data visibility, not brand
  citations. Amplification via the open-data community reaches dozens, not
  millions — acceptable; those dozens include the gatekeepers (Commons
  Library researchers, Wikipedia editors) who confer reference status.
- **Hypothesis (marked):** named, versioned measures with permalinks will
  be cited by name in journalism the way OpenPrescribing measures are.
  Plausible via the adjacent-field precedent; unproven for wealth data.

## MVP slice (≤1 week) vs full vision

**MVP:**
1. A `/data` page on the site: every dataset listed with description,
   licence, source + access date, endpoint URLs (JSON + CSV), and column
   dictionary. This is documentation of what already exists.
2. `licence` + `attribution` fields added to every `{slug}-metadata.json`,
   read from `registries/sources.yml` (collapses one provenance copy;
   sources.yml becomes the single machine truth the generator consumes).
3. `changelog.json` + human `CHANGELOG-data.md` appended by the weekly
   pipeline when any dataset's content hash changes.
4. An honest stability line: "best-effort stable; changes announced in the
   changelog" — explicitly NOT a permanence contract (critic-corrected from
   the council's "URLs are a contract" wish; a solo founder must not
   promise what a job change could break).

**Full vision:**
- Dated snapshots: `/data/{slug}/2026-07/…` immutable paths per release,
  live path keeps updating ("the live URL is for readers; the dated URL is
  for citers" — Annex C).
- Git-tagged data releases riding the existing weekly-update PR flow;
  data/processed un-gitignored (or a dedicated data branch) so vintages
  have history.
- `datapackage.json` (Frictionless) or schema.org `Dataset` JSON-LD per
  dataset — machine-discoverable by aggregators and AI assistants.
- Published table schemas exported from `validate.py`'s CHECKS list (the
  internal QA contract becomes consumer-facing trust).
- **Named measures** (OpenPrescribing pattern): ~6 documented headline
  series — e.g. top-10%/top-1% wealth share (WID), wealth Gini, median
  wealth by decile (WAS R8), house-price-to-earnings ratio, CGT
  concentration by band, IHT-paying estate share — each with a permalink
  page, methodology note, and its own endpoint. Journalists cite named
  measures, not spreadsheets.
- Zenodo DOI per release: deferred until the release cadence has run for a
  few months (a DOI is an irreversible promise; see Annex C).

## Architecture sketch

- `scripts/generate_static_api.py` is the single seam: add licence fields,
  CSV emission, content-hash computation, changelog append, snapshot dirs.
  It already runs on every deploy.
- `registries/sources.yml` becomes the canonical machine registry; the
  frontend's `datasetProvenance.ts` gains a build-time drift-lock test
  against it (extending the existing keyset guard pattern) rather than
  being hand-maintained in parallel.
- The weekly workflow (`.github/workflows/weekly-data-update.yml`) already
  opens review PRs on change — tagging a data release per merged weekly PR
  gives versioning almost for free. Note current gap: it git-adds
  `data/processed/` which is gitignored; fix as part of the versioning
  task.
- No backend. Everything is files at stable paths on GH Pages.

## Data sources

The existing 12 pipelines' sources (all recorded with URL, access date,
licence in `registries/sources.yml` and `docs/data-licences.md`):
predominantly OGL v3 (ONS, HMRC, DWP, Land Registry), CC-BY (WID),
CC BY-NC-ND 4.0 (Resolution Foundation generational-wealth — must be
flagged NoDerivatives in its machine metadata; ACTION-REQUIRED #10 governs
its output licence). Honest feasibility note: three pipelines are hardcoded
transcriptions, not live fetches (child poverty, wage stagnation,
generational wealth) — their metadata must say `static_published`, and the
/data page must not claim "fetched weekly" for them.

## Cost envelope

£0 marginal hosting. Snapshot dirs grow the repo by ~a few hundred KB per
month at current dataset sizes (12 datasets, largest a few hundred rows) —
years of headroom before it matters.

## Honesty / misreading / abuse risks and mitigations

- **Blanket licence overclaim** (council wish): cannot honestly write
  "everything OGL, redistribute freely" — per-dataset licence fields are
  the fix, with the ND dataset explicitly marked.
- **Vintage confusion:** a researcher must never unknowingly mix the live
  series with a snapshot — snapshot files carry `vintage` inside the JSON
  and in the path, and the /data page explains the two-URL rule.
- **Republishing amplifies upstream errors:** the changelog + weekly
  validation gate is the mitigation; when upstream revises, the change is
  visible, not silent (Full Fact corrections pattern applied to data).
- **"WealthLens data" mislabelling:** metadata `attribution` field states
  "Source: ONS/HMRC/... ; processed by WealthLens" so downstream credit
  flows to the statistics producers — both honest and strategically right.

## Open challenges, with candidate solutions

1. **Where do vintages live?** Options: (a) commit snapshots to main
   (repo growth, simplest); (b) orphan `data-releases` branch; (c) GitHub
   Releases assets (free, clean, but URLs less pretty). Recommend (a) now
   at current sizes, revisit at 50MB. Documented so the decision doesn't
   re-litigate.
2. **Provenance-copy collapse without breakage:** datasetProvenance.ts is
   consumed by two public pages with a guard test; wire it to sources.yml
   at BUILD time (codegen) rather than runtime import, so the frontend
   stays static and the test suite still locks the keyset.
3. **CSV dialect for Excel-first users:** UTF-8 BOM + CRLF or not; decide
   once, document on /data (journalists paste into Excel; the FOI persona
   parses JSON — serve both from one generator).

## Definition of shipped (visible artifact)

An outsider with no repo access builds a working chart from documented
endpoints without asking a question — concretely: the /data page is live,
every endpoint on it returns data with licence + attribution in-band, the
changelog shows at least one real entry, and one external person (the
open-data blogger persona exists in real life) has been pointed at it.

## Seeded tasks (half-day granularity)

- [ ] RFC-002a: /data documentation page (all 12 datasets, endpoints,
  licences, column dictionaries from existing sidecars) (@agent)
- [ ] RFC-002b: licence + attribution fields in {slug}-metadata.json wired
  from sources.yml; ND dataset flagged (@agent)
- [ ] RFC-002c: content-hash changelog (json + md) appended by weekly
  pipeline; fix the gitignored data/processed add in the workflow (@agent)
- [ ] RFC-002d: dated snapshot emission /data/{slug}/YYYY-MM/ + two-URL
  rule documented (@agent)
- [ ] RFC-002e: build-time codegen of datasetProvenance.ts from sources.yml
  with drift-lock test retained (@agent)
- [ ] RFC-002f: named-measures v1 — pick 6, write methodology notes,
  permalink pages + endpoints (@agent, content 2-lens reviewed)
- [ ] RFC-002g: schema.org Dataset JSON-LD emitted into chart-page OG
  shells (pairs with RFC-001e) (@agent)

## Dependencies and what it must NOT break

- Pairs with RFC-001 (the human-facing buttons consume these endpoints);
  neither blocks the other.
- Must not break: the frontend's static data store contract
  (stores/data.ts), the analyst ingest's sources.yml consumption, the
  weekly workflow's PR review gate, the existing guard tests.
- Must not: promise URL permanence, add a licence claim sources.yml cannot
  back, or mint DOIs before the release cadence is proven.

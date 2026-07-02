# Hard-Problems Annex — Product Frontier 2026-07

Last updated: 2026-07-02
Status: thinking captured for future implementers. Companion to
[`../PRODUCT_FRONTIER_2026-07.md`](../PRODUCT_FRONTIER_2026-07.md) and the
RFC briefs in this directory. Nothing here is implementation work; everything
here is the reasoning a future session should NOT have to re-derive.

Each problem: first-principles analysis → prior art → recommended approach →
fallback path → which RFCs it binds.

---

## Problem A — Sub-national wealth statistics without ecological fallacy

Binds: RFC-006 (Wealth, where you live). Also constrains RFC-003 (comparator
regional context) and any future locality feature.

### The problem, from first principles

"What is wealth like in Bradford?" is the single most-demanded question the
audience council produced (the councillor, the renter, the campaigner all
asked it) and the single most dangerous one to answer. Household wealth in
Great Britain is measured by one instrument: the ONS Wealth and Assets Survey,
a sample survey reliable at GB and region (ITL1) level only, currently
running ~3 years late, with a suspended accreditation and known top-tail
undercoverage. **There is no measured wealth figure for any local authority,
constituency, or town in the UK.** Anyone who shows one is doing one of three
things: (a) model-based small-area estimation, (b) proxy substitution, or
(c) fabrication.

Two distinct statistical sins to avoid:

1. **Ecological fallacy** — attributing an area aggregate to individuals
   ("people in Kensington have £X"; Kensington's mean is driven by a thin
   tail; most residents are nowhere near it). The inference direction
   area→person is invalid exactly where inequality is the subject, because
   inequality WITHIN areas is usually larger than inequality between them.
2. **False granularity** — publishing a regional estimate re-labelled as
   local ("Yorkshire's median, shown on a Bradford page without saying so"),
   or disaggregating a survey below its design resolution. This is
   fabrication wearing a map.

The trap is that the *demand* is local but the *data* is regional — and the
temptation is to close that gap with modelling WealthLens does not have the
institutional standing to defend. The council's honesty-hawk critic was
right: a solo project publishing a novel derived local-wealth series invites
precisely the specialist attack it cannot survive.

### What IS honestly known below region (the decisive observation)

Wealth is a sum of components, and the components have wildly different
geographic resolution:

| Component | Best local resolution | Source (URL, licence) |
|---|---|---|
| Property values | Local authority, monthly | UK House Price Index (gov.uk/government/statistical-data-sets/uk-house-price-index, OGL v3); Land Registry Price Paid (gov.uk/government/statistical-data-sets/price-paid-data-downloads, OGL v3) |
| Housing affordability | LA, annual | ONS housing affordability in England and Wales (ons.gov.uk, OGL v3) — already a WealthLens pipeline |
| Tenure (own outright / mortgage / rent) | Output Area (~150 households), Census 2021 | ONS Census 2021 (ons.gov.uk/census, OGL v3) — tenure is the strongest census-grade wealth *signal* that exists |
| Income | MSOA (modelled, with CIs); ITL3 (measured) | ONS small-area income estimates (model-based, published WITH confidence intervals); Regional GDHI — already a WealthLens pipeline |
| Pay | LA, annual | ASHE (ons.gov.uk, OGL v3) |
| Deprivation | LSOA | English Indices of Deprivation (gov.uk, OGL) |
| Child poverty | LA/ward | DWP/HMRC Children in Low Income Families — already a WealthLens pipeline |
| Pension wealth | **Region. Full stop.** | WAS only |
| Financial wealth | **Region. Full stop.** | WAS only |

So the honest local product is not "wealth in your area" — it is **"what
Britain measures about wealth in your area, and what it cannot see."** The
measurement gap is not an embarrassment to hide; it is the most shareable
fact on the page. No official or civil-society product says plainly: *nobody
knows the pension wealth of your town, and here is why.*

### Prior art

- **ONS model-based small-area income estimates**: the canonical honest
  pattern — modelled MSOA estimates published *with confidence intervals*
  and an explicit "modelled" label. Consume, never imitate: cite their
  estimates as "ONS modelled"; do not build WealthLens's own model.
- **OpenPrescribing**: per-entity pages that are honest about what varies at
  that level and what does not; the product's authority came from refusing
  to over-resolve.
- **PolicyEngine's Nuffield-funded constituency microdata**: the
  research-grade route (survey fusion + reweighting). Months of contestable
  methodology with institutional backing — the road WealthLens should
  explicitly NOT take solo (recorded in the anti-portfolio).
- **Commons Library constituency dashboards / mySociety Local Intelligence
  Hub**: prove the per-area-page format works for councillors and local
  journalists — and prove the space WealthLens must NOT drift into (generic
  local-deprivation stats, already occupied). The differentiator must stay
  wealth-composition-adjacent.

### Recommended approach: the granularity ladder

Every figure on a local page carries one of three machine-readable badges,
enforced by the same provenance registry that drives the rest of the site:

- **Tier 1 — measured here**: census tenure mix, LA house prices, LA
  affordability ratio, LA pay, LA child poverty. Shown as local facts.
- **Tier 2 — modelled here, by an accredited producer**: ONS small-area
  income (with their CIs, drawn). Label: "modelled estimate (ONS)".
- **Tier 3 — not measured below region**: total wealth, pension wealth,
  financial wealth. Shown as the REGIONAL figure with its interval, visually
  distinct (e.g. a hatched band spanning the region), with the sentence:
  "This is the [Yorkshire] figure. No source measures this for [Bradford].
  See why →". The "why" link is a permanent methodology page.

Design rules that fall out of first principles:

1. Never render a Tier-3 number inside local-page chrome without the
   region-not-local marker adjacent (not in a collapsed accordion — the
   council showed collapsed caveats do not travel with screenshots; the
   screenshot IS the product).
2. The page title is "Wealth around you", not "Wealth in Bradford" —
   framing that the lens is honest about its focal length.
3. Individual-inference guard: any sentence template about an area speaks
   about the area's *distribution*, never its residents ("half of homes in X
   are owned outright", never "people in X are wealthy").
4. The measurement-gap section is a first-class feature with its own anchor
   URL, so journalists can cite the *absence* — absence-of-data as citable
   content is the cheapest genuinely novel artefact in this whole space.

### Fallback path

If even the ladder is too heavy for a first release: ship the national
explainer alone — "Why nobody can tell you your town's wealth" (content
already 80% written in `research/methodology/was-caveats.md`), with the
component-resolution table above rendered as the visual. Zero fabrication
risk, real editorial value, and it establishes the honesty franchise the
full feature later inherits.

---

## Problem B — Communicating uncertainty honestly to lay readers

Binds: RFC-004 (scenario library), RFC-003 (comparator), RFC-007
(data-health layer). The simulator already computes intervals; the question
is whether regular people can receive them without either bouncing or
misquoting.

### The problem, from first principles

A published range does two jobs at once: it transmits information (the
number could reasonably be here-to-here) and it transmits a stance (we will
not pretend to know more than we do). The failure modes are symmetric:

- **Point-estimate failure**: publish "£10bn" naked and you have fabricated
  certainty; when a rival model says £6bn you have no defence, and the
  correction costs more credibility than the range ever would.
- **Range failure**: publish "£6-13bn" and (1) intermediaries truncate it —
  the journalist's headline will say one number regardless; (2) lay readers
  may read the width as incompetence; (3) the range itself can lie — an
  interval implies you know the distribution of your ignorance, and a
  one-parameter sensitivity sweep does NOT license the same reading as a
  full Monte-Carlo band.

That third point is currently live in the product: the published simulator
scenarios carry an `alpha_sweep` interval (one assumption varied) while the
engine supports Monte-Carlo sampling over parameter distributions. These are
epistemically different objects and the UI labels them identically. Fixing
the *vocabulary* is as important as widening the machinery.

### Prior art (what the evidence actually says)

- The Winton Centre research programme (van der Bles et al., Royal Society
  Open Science 2019; PNAS 2020) found communicating uncertainty as a
  **numeric range** produced little or no loss of trust in either the number
  or the source, while vague verbal hedges performed worse. (Verify exact
  effect sizes before quoting publicly; the direction is well replicated.)
  This is the empirical licence for range-first design.
- **Bank of England fan charts**: 30 years of evidence that a lay-facing
  institution can lead with a distribution. Lesson: the fan communicates
  "wide = honest" preattentively; the failure was that experts, not lay
  readers, kept quoting the mode.
- **IPCC calibrated language**: fixed verbal likelihood scale, known to be
  systematically misread (readers compress "very likely" toward 50-70%).
  Lesson: words alone miscalibrate; numbers must anchor the words.
- **Election needles/probabilities (FiveThirtyEight, 2016)**: probability
  read as verdict. Lesson: a single salient pointer defeats the surrounding
  nuance; never give the point estimate more visual weight than its band.
- **The Wealth Tax Commission itself**: published revenue estimates with
  behavioural-attrition scenarios and survived hostile scrutiny — the
  strategy works in exactly this domain.

### Recommended approach: a house grammar for uncertainty

1. **Range-first sentence templates**, machine-generated from the same JSON
   the chart draws (so text and chart cannot drift): "A 1% annual tax above
   £2m would raise **between £A and £B a year** (central estimate £C) on the
   assumptions below." The range is the quotable object; the point is the
   parenthesis. If an intermediary truncates, the most likely quoted number
   is the range itself, because it comes first.
2. **Name the driver of the width, mechanically.** The engine's Sobol layer
   exists precisely to attribute variance to assumptions. One sentence:
   "Most of this range comes from how much top-tail wealth the survey
   misses." Uncertainty with a named cause reads as knowledge; uncertainty
   without one reads as hedging. This converts the engine's most
   research-grade capability into lay-legible honesty — a differentiator no
   UK incumbent has.
3. **A fixed interval-type vocabulary**, rendered as a small badge and
   carried in the JSON (`interval_method` already exists in the dashboard
   contract v1.3): "sensitivity range (one assumption varied)" vs
   "simulation band (assumptions sampled together)" vs "survey confidence
   interval (ONS)". Three types, three labels, never mixed.
4. **The exported artefact carries the band.** Council evidence says users
   harvest-and-leave (screenshot, PNG). Therefore honesty must be baked into
   the artefact: the PNG export draws the band and prints the range in the
   title line. A WealthLens number should be *unable to travel naked*.
5. **"What would change this number"** as a standard collapsible: the 2-3
   assumptions that dominate (from Sobol), each with its citation. This is
   the lay version of a robustness section, and it pre-answers the hostile
   reader.

Cheap validation: before styling work, show 5 lay readers (Chris's widening-
participation network is a real asset here) two versions of one scenario
sentence and ask one comprehension + one trust question each. That is an
afternoon, not a research programme, and it converts "we believe range-first
works" from hypothesis to tested-on-someone.

### Fallback path

If range-first demonstrably kills comprehension for the mass audience:
layered disclosure (headline range in the subhead, band drawn but muted,
detail behind one tap) — but two invariants are non-negotiable regardless:
the machine-readable data always carries the full interval + method, and no
export/share artefact ever renders a point without its range. Honesty
degrades gracefully in the prose; it never degrades in the data.

---

## Problem C — Citations that stay resolvable as the corpus and data grow

Binds: RFC-005 (Analyst as infrastructure), RFC-002 (data packages), and
H1-19's future (noted as post-v1 hardening, NOT a change to the locked v1
plan).

### The problem, from first principles

A citation is a promise: a future reader can retrieve the evidence I saw.
Every part of the current stack quietly breaks that promise over time:

1. **Chunk identity churn.** Analyst citations are chunk_ids — database
   serials. The ingest path (`write_chunks` + `refresh_documents`) prunes
   and rewrites rows on re-ingest, so ids are not stable across corpus
   refreshes. Any answer cached, quoted, or published today ("[chunk:9140]")
   dangles after the next ingest. At v1 scale (23 chunks, frozen corpus)
   this is invisible; the moment the corpus unfreezes post-v1, every
   previously-issued citation becomes a lottery ticket.
2. **Dataset overwrite.** The static JSON layer is regenerated and
   overwritten on every deploy; only 3 of 12 data files are git-tracked. A
   chart cited in a September essay may silently show different numbers in
   November with no way to see what changed.
3. **Upstream rot.** ONS reorganises URLs notoriously; the registry's
   source URLs will decay. A citation whose final hop 404s is a citation
   that fails its promise even if WealthLens's own layer is perfect.
4. **Retrieval drift.** Same question, grown corpus → different retrieved
   set → different answer. Not a bug — but unversioned, it means "the
   Analyst said X" is unfalsifiable later, which is fatal for a tool whose
   entire positioning is verifiability.

### Prior art

- **OWID archived embeds** (2025): live URL keeps updating; citation
  instructions point to a timestamped archive URL by default. The precise
  insight: *serve the update-seeker and the citer from two different URLs.*
- **Wikipedia citation norms**: access dates + Wayback links as standard
  armour against rot; "text-source integrity" (the citation supports the
  exact sentence it is attached to).
- **Content addressing (git, IPFS, Software Heritage)**: identity from
  content hash, not location — drift becomes *detectable* rather than
  silent.
- **FRED/DFA vintages and ALFRED**: economic-data precedent that "the
  series as known at time T" is a first-class object economists need.
- **Zenodo DOIs**: free, solo-feasible permanence — but a DOI is an
  irreversible promise; the mission-guardian critique (do not promise
  stability you might break) says: later, once release cadence is proven.

### Recommended approach

**1. Separate citation identity from storage identity.** The stable name of
a piece of evidence is its provenance tuple — `(source_id, document_id,
section, span)` — which survives re-ingest because it describes the source,
not the row. Add a content hash of the normalised chunk text. A public
citation is then `{provenance tuple, content_hash, corpus_vintage}`; a
resolver maps it to the current chunk row. Three outcomes, all honest:
- tuple resolves + hash matches → "verified, unchanged";
- tuple resolves + hash differs → "source revised since this answer" (shown,
  not hidden — revision transparency is a feature, per Full Fact's
  corrections pattern);
- tuple gone → "no longer in corpus", with the vintage pointer below.
This is post-v1 work; v1's chunk_id citations are fine for a frozen corpus
and a live demo, which is exactly what the locked plan promises.

**2. Corpus and dataset vintages.** Tag each ingest with a vintage stamp
(date + git SHA of the registry state). `query_log` already records enough
per-request state that an answer becomes a reproducible object: (question,
corpus_vintage, model, params). For datasets: dated snapshot paths
(`/data/{slug}/2026-07/…`) generated at deploy alongside the live path —
static hosting makes immutable dated paths nearly free — plus a changelog
the weekly pipeline appends to. The OWID rule, restated for WealthLens:
**the live URL is for readers; the dated URL is for citers.**

**3. Archive the upstream at ingest.** One call to the Internet Archive's
save API per registered source URL at fetch time, storing the wayback URL
in the registry row. Costs nothing, runs in the pipeline that already
records access dates, and means every WealthLens citation has a rot-proof
final hop.

**4. Trust UX that shows its work.** The Analyst already computes more
honesty than it displays: fabricated-citation detection, per-request cost,
component retrieval ranks. Surface them: "show the evidence" panel (the
debug retrieval view, productised), a removed-citation notice ("1 citation
was stripped: it did not match retrieved evidence"), the metrics page, and
the abstention card as a designed object rather than an apology. No
consumer AI product shows any of this; for the audience that matters
(the sceptical professional cluster in the council — who currently would
NOT trust an AI-mediated number), visible machinery is the only argument
that works. Their scepticism at v1-corpus scale is rational; the honest
positioning is "provably cited over a narrow corpus, growing", never
"ask me anything about UK wealth".

### Fallback path

If tuple-resolution proves too heavy: quote-anchored citations — every
answer embeds the verbatim sentence(s) it relied on plus source URL + access
date. A human can always re-verify by reading, even if machine resolution
lapses. This degrades gracefully because the quote travels inside the
answer; it costs answer length, not truth. (The compose layer's evidence
blocks already make this nearly free to implement.)

---

## Cross-cutting principle the three problems share

All three reduce to the same design law, which the council discovered
empirically (harvest-and-leave) and the landscape scan confirmed
(incumbent artefacts rot): **the artefact that leaves the site is the
product, and it must carry its own honesty.** A screenshot carries the
caveat or the caveat does not exist; an exported PNG carries the band or
the range was never communicated; a citation carries its vintage or it was
never verifiable. Design every surface as if the site itself will not be
there when the artefact is read — because for most readers, it won't be.

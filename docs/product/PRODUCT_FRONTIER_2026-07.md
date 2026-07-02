# Product Frontier — July 2026

Last updated: 2026-07-02

> The product-thinking companion to the July 2026 strategy pair
> (`strategy/state-of-the-project-2026-07.md`, `strategy/course-correction-2026-07.md`).
> Those docs cover *whether and when* to build; this one covers *what is worth
> building* — a deep review of every product surface, an audience-and-landscape
> evidence base, a scored extension portfolio with RFC briefs, and an
> anti-portfolio so future sessions don't re-litigate rejected ideas.
> **Nothing here overrides the July priority rule: Analyst URL + launch bundle
> first. Every RFC is post-launch-bundle work.**
>
> Method (2026-07-02, one ultracode session): 6 deep surface reviews of the
> repo + 9 web landscape scans + a 12-persona audience council attacked by 3
> adversarial critics + 6-lens idea generation (57 raw → 40 consolidated
> candidates, `frontier-candidates-2026-07.md`). A 3-judge scoring panel was
> cut short by session budget; portfolio scores below are synthesised from the
> council/critic evidence and marked as such. Single-source repo claims were
> spot-verified against the code before being written down.

## 1. Product philosophy (what the evidence taught us)

**Design for the exit.** The single most replicated audience finding: every
persona — renter to economist — harvests one artefact (a screenshot, a PNG, a
sentence, a citation, a CSV) and leaves. Retention wishes were consistently
fantasy; extraction behaviour was consistently real. Therefore: **the artefact
that leaves the site is the product, and it must carry its own honesty** —
watermarked exports, ranges baked into images, citations with vintages,
caveats that survive screenshotting. (This law closes the annex too: a
citation carries its vintage or it was never verifiable.)

**Candour converts sceptics; nothing else reliably does.** The WAS
accreditation caveat changed the mind of five hostile personas *in session* —
the only intervention that did. Methodology candour is the moat. It is
protected above every feature request, including popular ones that would
erode it (grievance framings, fake local precision, invented behavioural
estimates).

**Wiring beats building.** Read honestly, the council cast 12 votes for
finishing and wiring what exists before building anything new. The repo's
pattern (verified across all six surface reviews): assets built to a high
evidential standard that stop one seam short of anyone seeing them — an
853-test engine behind a two-item dropdown, a live-but-undocumented data API,
four orphaned tools, twelve unseen OG images, dead share buttons on flagship
pages.

**Reference status is the durable form of "impossible to ignore".** The
landscape scan's mechanism, confirmed across OWID, OpenPrescribing,
TheyWorkForYou, Carbon Intensity: stable per-thing URLs + machine-readable
route + predictable cadence + documented limitations = infrastructure; media
reuse follows from that, not from marketing. Virality decays (the canonical
1-pixel-wealth repo now 404s, its mirrors frozen on 2019 data); reference
compounds. WealthLens should be the thing people *reach for*, which mostly
means being the thing people can *take from*.

**Abstention is a feature, and absence is content.** "Cannot answer from this
corpus" (Analyst), "no source measures this for your town" (local pages),
"we declined to publish this number" (IHT calibration) — each is a designed
product object, not an apology. In a landscape of confident wrongness, the
tool that visibly refuses is the one professionals can afford to recommend.

## 2. Surface verdicts (deep reviews, 2026-07-02)

| Surface | Verdict |
|---|---|
| 12 chart pages | 7 genuinely good broadsheet articles + 5 bare orphans. The reuse layer is broken everywhere: no CSV/data download (the one link 404s), dead placeholder ShareBar on flagship pages, "embed" iframes the whole page, social previews never show the chart (12 OG images exist, crawlers can't see them), no cite affordance, freshness badge reds-out current annual data, 2 pages + no index unreachable by nav. |
| 3 calculators + scroller | The strongest regular-person hook in the product ("where do I fit in UK wealth" — which no UK tool offers, ONS's died in 2022) is built, cited, tested — and orphaned: zero nav links reach /tools/*. Runs on WAS Round 7 (2018-20) though Round 8 exists. No shareable result, no URL state. |
| Simulator | An 853-test engine (7 policy families, Monte-Carlo machinery one argument away, Sobol + behavioural layers built-but-unwired) surfaced as a 2-item dropdown that cannot answer the canonical question (1% over £2m). What IS rendered (fan chart, caveats, provenance) is exemplary. Engine README still says "pre-alpha skeleton". |
| Analyst (locked v1) | Past the hard part: hybrid retrieval + cited compose live locally at ~£0.002/answer, citations provably ⊆ retrieved set, spend metered fail-closed. Corpus 23 chunks from 2 tabular sources until the PDFs land; golden set 20/20 DRAFT awaiting Chris; plain /ask 501 until H1-19/20/21. v1 = API with no UI; honest v1 positioning is "provably cited over a narrow slice". |
| Data layer | A de-facto public data API is already live at stable URLs (12 datasets + citation metadata, CORS-open) — documented nowhere, no licence field, no versioning, provenance truth fragmented across ~6 copies. The weekly pipeline + validation gate are release infrastructure waiting to be pointed at the public. |
| Hidden assets | chart_to_social.py (16 launch PNGs, never used), was-caveats.md (a publishable explainer), trust-dossier raw material (ADRs, model charter, the IHT refusal), 10 standalone chart HTMLs (ready embed targets), ~58 catalogued unused sources, PWA/a11y story unclaimed. |

## 3. What the audiences said (12 personas, 3 adversarial critics)

Load-bearing signals that SURVIVED adversarial attack:
1. Fix/remove every dead control; activate OG previews (12/12 personas; zero
   behaviour change required — immune to attention-economics doubt).
2. Publish the existing data layer with licence + changelog (7 professions
   converged; maps to already-daily professional behaviour).
3. The canonical simulator scenario (1%/£2m) — six personas independently
   named the identical gap; when sceptics and campaigners want the same
   neutral arithmetic, it's a reference feature, not advocacy.
4. Surface the comparator on Round 8 with ranges-not-points and a share card
   — expectations set at "once + one share", which for this segment IS the
   loop.
5. Local pages at honest granularity only (housing/tenure/pay local; wealth
   stops at region, explicitly).
6. Methodology candour as the moat (see §1); a top-tail explainer is the
   page that decides expert word-of-mouth.

Key deflations (held throughout the RFCs): professionals will strip-mine and
still cite ONS (fine — mission is data visibility, not brand citations);
quiz-virality claims are survivorship bias; discovery, not features, is the
binding constraint at ~5 views/fortnight — which the launch bundle, not this
portfolio, addresses. Known council blind spot: no persona represented the
actual gatekeepers of reference status (Commons Library, Wikipedia editors,
press graphics desks) — the RFCs design for them anyway (licence clarity,
stable URLs, citations).

## 4. The landscape gap WealthLens can own

**Nobody owns the citable reference layer for UK wealth statistics.** OWID
ceded UK wealth (2 charts, annual refresh) while proving the chart-as-API
playbook; ONS's own comparator has been dead since March 2022, WAS lost
accreditation with no coherent official series and no API presence; IFS/RF
offer no embeds or APIs and their interactive artefacts demonstrably rot
(2019 CSVs that 404, an expired-cert simulator); the US Fed's DFA proves the
destination exists and has "no UK equivalent"; Full Fact writes prose without
charts or living evidence pages; nobody serves lesson-ready UK wealth data.
The gap is not a chart gap — it is an *infrastructure and honesty* gap, and
the incumbents' failure mode (rot) is precisely what WealthLens's pipeline
discipline already solves.

## 5. The portfolio (8 RFCs, scored)

Scores 1-5, synthesised from the council/critic evidence (judge panel
incomplete — see method note). Slots required by the review brief: regular
people ✓ (003, 006, 008), experts ✓ (001, 004, 007), infrastructure ✓ (002,
005), 12-month bet ✓ (004, 005). Every RFC has a ≤1-week first slice.

| RFC | Idea | Serves | Mission | Audience | Data | Solo | Honesty | Diff | Note |
|---|---|---|---|---|---|---|---|---|---|
| [001](rfc/RFC-001-reference-grade-chart-pages.md) | Reference-grade chart pages (download/cite/embed/previews/wiring) | everyone | 5 | 5 | 5 | 5 | 5 | 3 | Do first; every other RFC compounds on it |
| [002](rfc/RFC-002-citable-data-packages.md) | Citable, versioned data packages + documented static API | experts, builders | 5 | 4 | 5 | 5 | 5 | 4 | Strongest cross-persona demand; near-zero build |
| [003](rfc/RFC-003-wealth-comparator-v2.md) | "Where do you fit?" v2 (Round 8, ranges, twin pension positions, share card) | regular people | 4 | 5 | 4 | 4 | 4 | 5 | No UK competitor exists; usage = once + one share, by design |
| [004](rfc/RFC-004-scenario-library.md) | Scenario library: sim as the public reference for wealth-tax arithmetic | experts + curious public | 5 | 4 | 4 | 4 | 4 | 5 | 12-month bet #1; frozen until launch bundle ships; Budget 2026 is the peg |
| [005](rfc/RFC-005-analyst-as-infrastructure.md) | Analyst as infrastructure (post-v1): ask-this-chart, API docs, MCP, claim pages | researchers, builders | 5 | 3 | 4 | 4 | 4 | 5 | 12-month bet #2; strictly post-v1; evidence-navigation framing, not oracle |
| [006](rfc/RFC-006-wealth-where-you-live.md) | Honest local pages (granularity ladder; the measurement gap as content) | regular people, councillors, local press | 4 | 4 | 4 | 3 | 4 | 4 | Annex problem A governs; no sub-regional wealth, ever |
| [007](rfc/RFC-007-data-health-layer.md) | Data-health layer: WAS-crisis explainer, health badges, trust dossier | everyone (trust substrate) | 5 | 3 | 5 | 5 | 5 | 4 | Cheapest RFC; converts the moat from invisible to visible |
| [008](rfc/RFC-008-teach-this-chart.md) | Teach this chart (3-chart experiment: projector, worksheet, teachers page) | teachers, students | 4 | 3 | 5 | 4 | 4 | 4 | Deflated scope; WP network is the honest test channel |

**Recommended order** (when capacity exists, after the launch bundle):
001 → 002 + 007 (parallel, cheap) → 003 → 004 (once the sim freeze lifts)
→ 006 → 008; 005 waits for the Analyst URL by definition.

**Held one step short of the portfolio** (promising, needs a decision or a
proof first — full pool in
[`frontier-candidates-2026-07.md`](frontier-candidates-2026-07.md)):
- **"Off By How Much?" daily perception game** — the only candidate with real
  repeat-visit physics (Wordle genre; share artefact = your miss distance,
  which sidesteps the wealth-valence trap; teaches the perception gap that IS
  the mission). Honest, static, bank-of-statements buildable. Held because it
  is a new *surface* with a content-bank commitment, and the critics' rule —
  no new surfaces before the launch bundle proves discovery — applies
  double to a daily product with zero current audience. Revisit when
  analytics exist; a genuine RFC-009 candidate then.
- Scenario request board ("file a scenario, CI regenerates it") — fold into
  RFC-004 full vision once the grid exists.
- Hansard-linked claim pages and the citation lie-detector — fold into
  RFC-005e post-v1.
- Soundbite registry (broadcast-safe phrasings with vintages) — fold into
  RFC-002f named measures.

## 6. Anti-portfolio (rejected, with reasons — do not re-litigate)

1. **Sub-regional wealth estimates** (LA/constituency "wealth of Bradford") —
   no measured data below region; ecological fallacy or fabrication. The
   honest alternative IS the product (RFC-006 + Annex A).
2. **DB-pension "rough multiplier" in the comparator** — 2-3x valuation
   swings by scheme/age; false precision under the site's own name. Solved
   structurally by twin incl./excl.-pension positions (RFC-003).
3. **Behavioural-response central estimates** for wealth-tax revenue —
   elasticities are a research frontier; the module stays gated on cited
   base-share data (standing Chris question). "Upper bound, not a costing"
   until then.
4. **A WealthLens-adjusted top-tail wealth series** (Rich-List-augmented,
   discontinuity-stitched) — months of contestable research-grade
   methodology that invites the specialist attack it pretends to pre-empt.
   Explain the literature (RFC-007e); never publish a novel series solo.
5. **TikTok/vertical-video channel** — a per-platform content treadmill
   (second full-time job); payoff accrues to the feed, not the site; the
   persona demanding it conceded she'd rarely click through.
6. **Deposit-years / generational "it would take you 14 years" calculator** —
   stacks unsourced assumptions into one fake-precise viral sentence; a
   Full-Fact-style debunk waiting to happen.
7. **International comparison chart (UK vs FR/DE/US top shares)** mixing WID
   capitalised-income and WAS survey methods — apples-to-oranges by
   construction; needs the methodological essay nobody will read.
8. **Grievance/payslip cards and second-person-accusatory framings** ("you
   pay more than a landlord") — editorialising by design; breaks the
   neutrality that gets the site into classrooms and past editors.
9. **Newsletter as strategy** (vs as an experiment later) — single-digit
   subscribers for a permanent editorial commitment; a lapsed newsletter
   signals abandonment louder than none. Revisit only with real traffic.
10. **URL-permanence "contract" promises / DOIs now** — irreversible
    commitments a solo founder shouldn't mint yet; best-effort + changelog +
    git tags now, Zenodo DOIs when the release cadence is proven.
11. **Welsh i18n now** — the persona who asked conceded she'd use it
    "approximately never"; the i18n shell stays dormant until a real driver.
12. **Full TES-style worksheet publishing arm** — hoarding-trap economics +
    per-exam-cycle maintenance; the 3-chart experiment (RFC-008) is the
    honest version.
13. **Live-compute simulator backend** — breaks static economics for zero
    honesty gain; the precomputed grid serves the same questions.
14. **A real-time "wealth clock" / interpolated billionaire tracker** —
    fabricated interpolation dressed as liveness; the exact staleness-vs-
    sourcing failure that killed the viral pieces, inverted.
15. **Generic local-deprivation dashboard** — occupied territory (LG Inform,
    Commons Library, End Child Poverty); mission dilution (RFC-006 boundary).
16. **"What should I do about it" / agency content** — crosses from
    presenting data to prescribing policy; the honest move is to visibly not
    answer it and say why.

## 7. Hard-thinking annex

[`rfc/ANNEX-hard-problems.md`](rfc/ANNEX-hard-problems.md): (A) sub-national
statistics without ecological fallacy — the granularity ladder; (B) a house
grammar for communicating uncertainty to lay readers — range-first templates,
named drivers via Sobol, interval-type vocabulary, artefacts that can't
travel naked; (C) citations that stay resolvable as corpus and data grow —
provenance-tuple identity, corpus vintages, the two-URL rule, upstream
archiving, and the LLM trust UX that shows its work.

## 8. Seeds and status

Task seeds: each RFC carries its own half-day tasks; pointers live in
`tasks/inbox.md` § "2026-07-02 product frontier seeds". Candidate pool:
`frontier-candidates-2026-07.md` (40 ideas, unjudged). This review changes no
sprint priority: the July spear (Analyst URL + launch bundle,
course-correction S3) stands, and RFC-001's MVP is deliberately the same
work the launch bundle already needs (working downloads, previews, wiring)
so the first post links to a site whose buttons work.

# RFC-005 — The Analyst as infrastructure (post-v1): evidence API, MCP tool, ask-this-chart, claim pages

Last updated: 2026-07-02
Status: PROPOSED, **strictly post-v1**. Nothing here modifies
`docs/plan/HERO1_PLAN.md`, the M0-M6 sequence, the frozen corpus, or
`tasks/hero1-backlog.md` ordering. This is the answer to "what is the
Analyst FOR, once v1's live URL exists" — written now so v1 decisions
aren't accidentally hostile to it (they aren't; the locked architecture is
exactly right for this). Twelve-month-bet candidate #2.
Index: [`../PRODUCT_FRONTIER_2026-07.md`](../PRODUCT_FRONTIER_2026-07.md)
Annex: problem C (citation permanence + LLM trust UX) is the core design
input.

## Problem and who it serves

At v1 the Analyst is a JSON API with no UI, a 23-chunk corpus until the
IFS/RF PDFs land, and no link between it and the dashboard. The council's
sceptical professionals were blunt: the think-tanker "would not put an
AI-mediated figure anywhere near a hostile-journalist-facing note", and at
v1 corpus scale that scepticism is *rational*. The naive product framing —
"chatbot that answers wealth questions" — is both untrustworthy to experts
and dishonest at current corpus breadth.

The reframe this RFC proposes: the Analyst is not an oracle, it is
**evidence navigation infrastructure** — a citations-guaranteed retrieval
and composition layer that other surfaces (the dashboard, partner sites,
researchers' agents, eventually journalists' tools) query. Its buildable
assets already generalise: provenance-carrying chunks are a citations
database; the metered client seam is org-wide LLM cost governance;
fabricated-citation detection and structured abstention are trust features
no consumer AI product surfaces; the golden-set + deterministic-checks
harness is a publishable methodology.

Who it serves: researchers and their increasingly-agentic tooling (MCP),
curious readers on chart pages (grounded "ask about this chart"),
journalists checking recurring claims (living evidence pages), and other
builders (the API tier).

## Value hypothesis

- **Evidence:** PolicyEngine's "Explain with AI" exists but is *uncited* —
  their AI narrates model internals without sources (landscape scan
  verified); grounded citation is exactly the seam they left open. OWID
  has no question-answering layer at all. Full Fact's own 2026 report
  concedes prose rebuttals lose to repetition because they produce no
  reusable artefacts. Nobody offers a cited UK-statistics tool over MCP.
- **Evidence (in-house):** cited compose works today at ~£0.002/answer
  with citations provably ⊆ retrieved set; abstention and spend caps are
  designed-in, not bolted on. The hard parts of trustworthy-AI product are
  the parts already built.
- **Deflations to hold:** experts will not *quote* Analyst output for
  years, if ever — the adoption path is *tools and self-verification*
  (they read the citation, then cite ONS; that is mission success, not
  failure). Regular-person chat demand is unproven; "ask this chart" is
  deliberately scoped as an experiment on existing traffic, not a
  destination product.
- **Hypothesis (marked):** an MCP tool that returns cited, abstention-
  capable answers becomes disproportionately visible as researchers adopt
  agentic workflows through 2026-27; being first-and-honest in a small
  niche beats being late in a big one. This is the 12-month bet.

## MVP slice (≤1 week, first post-v1 week) vs full vision

**MVP:**
1. **"Ask about this chart"** on ONE chart page (the wealth-shares
   flagship): a button opening a panel that queries the live /ask with the
   chart's context pre-seeded (source ids constrained to that chart's
   dataset), rendering answer + resolved citations + the abstention card
   when refused. Static frontend calling the Hetzner API; feature-flagged;
   rate-limited by the existing budget middleware.
2. **API docs page**: the H1-20 published JSON schema + three curl
   examples + the honest positioning line ("provably cited over a narrow,
   growing corpus of official UK wealth statistics; refuses rather than
   guesses") + the metrics page link.

**Full vision:**
- **MCP server** exposing two tools: `search_evidence` (the debug
  retrieval surface, productised: query → provenance-carrying chunks with
  scores) and `ask` (cited answer | structured refusal). Same API
  underneath, same caps, same accounting. A researcher's Claude/agent can
  then ground UK-wealth claims through it natively.
- **Claim evidence pages** (the Full Fact steal, non-partisan by
  construction): ~15-20 recurring UK wealth claims ("the top 1% already
  pay most income tax", "a wealth tax has never worked anywhere", "half of
  households have no savings") each get a LIVING page: the claim, what the
  cited data shows (verdict-shaped but descriptive), the relevant chart,
  table-level citations, a revision log, ClaimReview/Dataset JSON-LD.
  Crucially the intake signal is `query_log` — the claims people actually
  ask the Analyst become the pages worth writing (Full Fact's
  claim-detection loop at zero marginal cost). Pages are static content
  reviewed by the 2-lens factual gate; the Analyst links to them as
  canonical answers for their claims.
- **Trust UX surfacing** (Annex C): "show the evidence" panel, visible
  stripped-citation notices ("1 citation removed: not in retrieved
  evidence"), the public metrics page framed as a feature, the abstention
  card designed as a product object.
- **Citation permanence hardening**: provenance-tuple + content-hash
  citations and corpus vintage stamps (Annex C §recommended approach) —
  required before any third party is encouraged to store Analyst answers.
- **Corpus growth governance**: post-v1 unfreeze protocol — a source
  enters only via the registry with licence + provenance gate, and each
  source lands WITH Chris-reviewed golden questions covering it
  (eval-first growth), so "what can it answer" and "what do we test"
  never diverge. The no-fabrication line holds forever.

## Architecture sketch

- No new services for MVP: the Hetzner CAX21 (ADR 0003) already carries
  app + Postgres + Langfuse; "ask this chart" is a frontend feature over
  the deployed API; the docs page is static.
- MCP server: thin adapter over the same FastAPI routes (stdio or SSE
  transport), deployed on the same box; every call still transits
  `llm/client.py` and the budget middleware — the ADR 0002 spend-cap
  architecture is precisely what makes a public-ish tool affordable.
- Claim pages: static site content; each page's citations resolve through
  the same registry the Analyst uses, so chart pages, claim pages, and
  answers cite identically (one citation grammar everywhere).
- CORS + a modest per-IP rate limit for the public /ask tier; the
  fail-closed 429 refusal body already specified in the locked plan
  (H1-27) is the abuse backstop.

## Data sources

The v1 frozen corpus (ONS WAS, HMRC CGT + receipts, 3-5 IFS/RF reports —
all registered in `registries/sources.yml` with URL/licence/access date).
Post-v1 growth candidates, already catalogued with licences in
`research/data-sources/data-source-registry.md`: ONS ETB (OGL v3), HBAI
(OGL v3), Wealth Tax Commission evidence papers (free), WID UK series
(CC-BY). Feasibility note: IFS/RF report PDFs are licence-permissive to
quote with attribution but check each report's terms at registration; the
registry row records the check.

## Cost envelope

Hosting: the already-decided ~£7/mo box. Marginal: ~£0.002/answer,
hard-capped by the budgets table (fail-closed, tested). A public tier at,
say, £5/month cap ≈ 2,500 answers/month ceiling — enforced by the
in-product mechanism, not hope. MCP adds no model spend beyond the same
metered calls.

## Honesty / misreading / abuse risks and mitigations

- **Overclaiming breadth** is the #1 reputational risk: the positioning
  line ships in the API docs, the UI panel, and the MCP tool description.
  Abstention coverage is the enforcement: out-of-corpus questions refuse,
  and that behaviour is CI-tested (v1's M4 gate) — the marketing claim and
  the test suite are the same artefact.
- **Hallucinated numbers**: already structurally mitigated (citations ⊆
  retrieved set, fabricated-id stripping + logging); the post-v1 move is
  making the mitigation VISIBLE (stripped-citation notice), converting a
  safety mechanism into a trust signal.
- **Prompt injection via corpus documents**: evidence is fenced as
  source-material-not-instructions since PR #476; PDF ingestion (H1-08)
  inherits the same hygiene; the MCP tool returns data, never executes.
- **Claim-page partisanship drift**: claims are selected by query_log
  frequency + editorial neutrality review, phrased descriptively, and
  every verdict-shaped sentence carries its citation; the 2-lens factual
  gate applies (the same bar as charts; course-correction E3 extends it to
  posts already).
- **Abuse/cost**: fail-closed caps + 429 refusal (locked plan); per-IP
  limits; no unauthenticated bulk endpoints.

## Open challenges, with candidate solutions

1. **Citation permanence before third parties store answers** — Annex C's
   provenance-tuple + vintage design; sequenced as the first hardening
   task after any external consumer exists.
2. **Latency for chart-page UX** (retrieval + compose ≈ seconds):
   candidate — optimistic UI showing retrieved evidence immediately,
   answer streaming after; abstention decisions are near-instant (gate
   precedes generation, by design).
3. **MCP discoverability** (a niche standard, fast-moving): candidate —
   publish to the community registries, write it up (writeup #2/#3 slots
   exist in `docs/plan/WRITEUPS.md`), and treat researcher word-of-mouth
   as the channel; cost of being early is near-zero since it's an adapter.
4. **Corpus-growth vs eval-capacity** (Chris's review time is the scarce
   input): eval-first growth rule above; growth rate is explicitly bounded
   by golden-set review capacity — a feature, not a bug, for a
   never-be-wrong product.

## Definition of shipped (visible artifact)

First slice: on the live wealth-shares chart page, a visitor clicks "Ask
about this chart", asks "which decile holds the most property wealth?",
and gets a cited answer (or an honest refusal) from the public URL — and
the API docs page exists with the schema, examples, and positioning line.
Full-vision markers: the MCP tool is installable and returns cited
evidence in a third-party agent; three claim pages are live with revision
logs.

## Seeded tasks (half-day granularity, all post-v1)

- [ ] RFC-005a: API docs page (schema, curl examples, positioning line,
  metrics link) (@agent)
- [ ] RFC-005b: "Ask about this chart" panel on wealth-shares, flagged,
  source-constrained, abstention card rendered (@agent)
- [ ] RFC-005c: MCP adapter exposing search_evidence + ask over the same
  routes/caps; publish + register (@agent)
- [ ] RFC-005d: citation permanence hardening per Annex C (provenance
  tuple + content hash + corpus vintage in responses) (@agent)
- [ ] RFC-005e: claim-pages v1 — pick 3 from query_log + editorial
  neutrality review; static pages with revision logs + ClaimReview JSON-LD
  (@agent, 2-lens reviewed)
- [ ] RFC-005f: stripped-citation notice + show-evidence panel in the
  answer UI (@agent)
- [ ] RFC-005g: corpus-unfreeze governance note in the analyst CLAUDE.md
  (eval-first growth rule) — one paragraph, post-v1 (@agent)

## Dependencies and what it must NOT break

- Hard-blocked on v1 shipping (live URL, H1-30/31/32) — by design.
  ACTION-REQUIRED #5 (golden answers) and #6 (Hetzner) gate v1 itself.
- Must not break: the locked plan while v1 is in flight (this document is
  inert until then); the spend-cap path (every new surface transits the
  same middleware); the abstention contract; the no-fabrication line.
- Must not: describe the Analyst as a general UK-statistics oracle, expose
  uncapped endpoints, or let any surface bypass `llm/client.py`.

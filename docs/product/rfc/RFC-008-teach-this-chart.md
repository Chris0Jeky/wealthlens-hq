# RFC-008 — Teach this chart: the classroom layer (deflated scope)

Last updated: 2026-07-02
Status: PROPOSED (product-frontier review 2026-07). Deliberately scoped as
an experiment, not a product line, per the adversarial critics.
Index: [`../PRODUCT_FRONTIER_2026-07.md`](../PRODUCT_FRONTIER_2026-07.md)

## Problem and who it serves

Nobody serves "UK wealth inequality, lesson-ready" (landscape scan,
verified): Gapminder and OWID have the pedagogy but no UK wealth data and
admit their teaching packs go stale; Oak National Academy has the
gold-standard lesson-kit format but no wealth-distribution content; BBC
Bitesize doesn't list GCSE Economics; tutor2u has exam-spec alignment but
static charts behind a partly-paid model; the Equality Trust's schools
resources are dated 2019 and chart-free. The demand is real but the
council's teacher persona and all three critics agree on its true shape:
teachers harvest artefacts (a projectable image, a printable worksheet)
at 9pm on Sunday; download-to-teach conversion is low; per-exam-cycle
spec maintenance is a hidden liability a solo founder must not take on.

WealthLens's unfair advantages here: pipeline-regenerated charts attack
the staleness that kills everyone else's packs; the citation discipline
is exactly the neutrality armour a teacher needs against parent
complaints; and Chris's widening-participation work is genuine domain
expertise and a genuine distribution channel (real teachers, real
classrooms, real feedback loop).

Who it serves: secondary teachers (GCSE Citizenship, GCSE/A-level
Economics), sixth-formers (EPQ/coursework), and indirectly the U3A/adult-
education audience the pensioner persona represents.

## Value hypothesis

- **Evidence (council):** the teacher persona's return trigger was a
  print-safe worksheet pack ("fits her Sunday-evening workflow, survives
  dead wifi and device-free classrooms, gets filed into her scheme of
  work"); her verdict named the exact distance: "roughly ten printable
  PDFs and a one-page teachers' note".
- **Critic deflation (held):** worksheet hoarding is real; a TES-style
  publishing arm is anti-portfolio. The experiment is 3 charts, not a
  catalogue; spec TAGS (metadata lines teachers can Google) not spec
  MAINTENANCE (a promise to track syllabus changes).
- **Hypothesis (marked):** "teach this chart" assets regenerated from the
  live pipeline stay current where every competitor's PDFs rot — the
  freshness edge converts to repeat classroom use year over year. Testable
  with 3 charts and Chris's WP network before any expansion.

## MVP slice (≤1 week) vs full vision

**MVP — the three-chart experiment:**
1. **Projector mode** on chart pages: one-click fullscreen — large fonts,
   high contrast, minimal chrome, arrow-key step-through of 2-3
   annotation reveals. (A CSS class + keypress handler on the existing
   chart components; genuinely a weekend-scale feature no UK inequality
   site has.)
2. **Printable worksheet (PDF-able print stylesheet)** for THREE charts
   (wealth shares, generational wealth, housing affordability): the chart
   mono-printer-safe, its data table, the source line with access date,
   3 tiered neutral questions (describe / calculate / evaluate), and one
   "what this data can't tell us" caveat — the last doubling as
   source-evaluation teaching material, which the teacher persona
   independently identified as a rare asset.
3. **A "For teachers" one-pager**: neutrality/editorial policy she can
   forward to a head of department or parent, licence line ("free to
   copy and adapt for your classroom", CC BY), and a static list of
   relevant spec references (AQA GCSE Economics 8136 distribution of
   income and wealth; Edexcel A-level 4.2.2; AQA A-level 7.1; KS4
   Citizenship) as *tags*, with the honest note that syllabi change and
   teachers should verify — tags without a maintenance promise.

**Full vision (only if the experiment shows real classroom use):**
worksheets for all 12 charts regenerated at deploy; starter/exit quiz
JSON per chart; a "UK wealth ladder" decile card activity (Dollar Street
mechanic on WAS decile profiles — guess-then-reveal); classroom demo mode
for the comparator (RFC-003f presets); a lightweight quality-mark
conversation (ACT/EBEA) and co-badging offer to the Equality Trust —
their schools materials are dated and chart-free, making this the
value-offering outreach hook the outreach rules require.

## Architecture sketch

Print CSS + a projector-mode class on existing components; worksheets are
the chart page itself with a `?print=worksheet` view (build nothing new
server-side); question text lives in `chartArticles.ts`-style config so
the 2-lens neutrality review has one diffable home. Regeneration is free:
the chart and table are already pipeline-fed.

## Data sources

No new data. The three charts' existing registry-reconciled sources (WID
CC-BY; ONS OGL v3). Worksheet licence: CC BY on WealthLens's layout/
questions, upstream data licences stated per chart (the NC-ND chart is
excluded from the worksheet set — generational-wealth is unfortunately
one of the three most teachable charts, so substitute wealth-by-decile
unless/until ACTION-REQUIRED #10 resolves the derivative question).

## Cost envelope

£0 marginal. Editorial + review time for 9 questions and one policy page.

## Honesty / misreading / abuse risks and mitigations

- **Neutrality under classroom scrutiny**: every question descriptive or
  analytical, never leading ("evaluate whether the data supports claim X"
  not "why is this unfair"); 2-lens review with one lens explicitly
  hostile ("could a parent complain?").
- **Pupil-disparity exposure**: no activity asks students for their own
  household data (RFC-003's demo mode exists for exactly this).
- **Spec-tag rot**: tags dated ("checked 2026-07") and framed as
  pointers, not promises.

## Open challenges, with candidate solutions

1. **Measuring classroom use with no analytics** (AR #4 pending):
   candidate — the WP-network feedback loop: 3-5 real teachers, a
   one-question follow-up after a term. Qualitative but honest; the
   expansion gate is their answer, not a download count.
2. **Print fidelity across school printers**: mono-safe palette variant
   for print CSS (the charts' colour semantics must survive greyscale) —
   half-day design task, reusable for all exports.

## Definition of shipped (visible artifact)

Three chart pages each offer "Project this chart" and "Print worksheet";
the For-teachers page is live; three real teachers (via the WP network)
have been handed the links and asked to use one in a lesson. Expansion
decision explicitly gated on their feedback.

## Seeded tasks (half-day granularity)

- [ ] RFC-008a: projector mode (fullscreen class + step-through reveals)
  on the chart components (@agent)
- [ ] RFC-008b: print stylesheet + worksheet view for 3 charts (mono-safe
  palette variant) (@agent)
- [ ] RFC-008c: 9 tiered questions + caveat lines, 2-lens neutrality
  review (@agent)
- [ ] RFC-008d: For-teachers page (policy, licence, dated spec tags)
  (@agent)
- [ ] RFC-008e: hand to 3 WP-network teachers; capture feedback; write
  the expand/stop note (@Chris intro, @agent materials)

## Dependencies and what it must NOT break

- Benefits from RFC-001 (cite/download) but independent.
- Must not break: WCAG AA (projector mode is an a11y win if done right —
  reuse reduced-motion handling), the non-partisan bar, chart-page
  performance.
- Must not: promise spec maintenance, build a worksheet CMS, include the
  NC-ND chart while AR #10 is open, or expand past 3 charts before the
  teacher feedback gate.

# WealthLens UK: Unified Research Blueprint v5

**Version date:** 21 May 2026
**Working title:** *WealthLens UK: An Open, Uncertainty-Aware Simulator for Wealth Policy, Top-Tail Inequality and Tax Reform*
**Status:** Fifth-pass unification. Synthesises two fourth-pass v4 blueprints (one operationally rich, one editorially tighter) into a single document that is meant to be the working blueprint, not another draft.

---

## Preamble: what this fifth pass does, and why

Two parallel fourth-pass blueprints existed: a long operational synthesis and a tighter editorial unification. Both were directionally correct but each was missing things the other had, and both were missing things neither had thought to address.

**From the operational v4** this version keeps: the explicit theory of change, the AI/LLM disclosure protocol, the glossary, the computational-cost analysis, the OBR-positioning question, the comparator-simulators table, the independent-reproduction gate, the £0.4bn↔£80bn revenue-range anchor, the devolved-expertise disclaimer, the symmetric "wildly-optimistic-answer" discipline, the 30-item risk register and the decision-point structure in the roadmap.

**From the editorial v4** this version keeps: the baseline-status matrix (every policy lever tagged for legal status), the explicit repository layout, the v0.1 must-include / must-not-include lists, the model-charter and dashboard-safety gates, the Bayesian second-pass top-tail specification, the machine-readable assumption-registry schema, the "announced baseline / consultation-sensitive" distinction, and the tighter prose discipline throughout.

**New in this pass** — material neither prior blueprint contained:

1. *§24 What success looks like at 24 months.* Concrete, falsifiable success metrics rather than aspirational language.
2. *§25 Year-1 project killers.* A separate, named list of specific things that would end the project in year one, distinct from the generic risk register.
3. *§26 Policy levers no one is modelling.* A map of the policy space neither WealthLens nor its UK comparators currently model: accessions tax, mark-to-market on large public holdings, deemed disposal at retirement, exit charges, gift-tax overhaul.
4. *§27 The post-HVCTS identity problem.* What WealthLens *is* once the May 2026 consultation closes and HVCTS is either implemented, modified or dropped. A project whose identity depends on one live consultation has a 14-month shelf life.
5. *§11.6 The behavioural validation-set problem.* Explicit acknowledgement that behavioural modules cannot be validated in the strict sense because there is no in-force UK comparator policy. The honest claim is robustness, not accuracy.
6. *§17.5 License, IP and backwards-compatibility commitment.* Neither prior document specified a license or a maintenance commitment for published baselines.
7. *§21.5 Pre-mortem as standing methodology.* Risk register made adversarial rather than descriptive.
8. Tightened cross-references between sections; some redundancy in the operational v4 has been cut.

This version is intended to be the working document. The next pass should be cuts, not additions.

---

## Executive thesis

The strongest version of WealthLens UK is **not** a campaign to prove the UK should adopt an annual wealth tax. It is an **open, uncertainty-aware UK wealth-policy lab** that compares wealth-focused reform packages under a common evidence standard, with the live UK policy environment as its operational anchor.

**Core research question.** Under imperfect UK wealth data, which wealth-focused policy packages most robustly raise revenue, reduce wealth concentration, protect low-liquidity households, limit avoidance and migration risk, and remain administratively credible?

**Core deliverable.** *WealthLens-Sim v0.1:* a reproducible, top-tail-corrected UK wealth-policy microsimulation platform with uncertainty bands, built on a PolicyEngine-UK-style rules-as-code layer and benchmarked against UKMOD, Wealth Tax Commission modelling, HMRC aggregates and ONS wealth aggregates.

**First publishable output.** Methodological, not polemical:

> *Reconstructing the Top Tail of UK Household Wealth under Survey Decline: An Open Microsimulation Baseline for Wealth-Policy Reform.*

The binding credibility problem is not whether a proposed tax sounds attractive. It is whether the model can reconstruct the wealth distribution — especially the top tail — without hiding uncertainty.

**Sequencing.**

1. **Measurement first.** Reconstruct GB/UK wealth with transparent uncertainty, especially the top tail.
2. **Static mechanical simulation second.** Implement current-law baselines and candidate policy families without behavioural assumptions hidden in the core.
3. **Behavioural uncertainty third.** Add migration, avoidance, timing, valuation, liquidity and reclassification modules as explicit sensitivity wrappers.
4. **Dynamic accumulation fourth.** Model multi-year accumulation, inheritances, pensions, CGT realisations and property-price capitalisation.
5. **ABM/RL last.** Use agent-based or reinforcement-learning models only after the simulator is already trusted by tax-policy audiences.

The first credibility test is not whether the project is technically impressive. It is whether it can reproduce known results, reconcile to official aggregates, expose uncertainty honestly and survive review by people who do not share the project's politics.

---

## Theory of change

This section exists because neither earlier blueprint stated it. Without an explicit theory of change, a project of this scope drifts into either advocacy or engineering vanity within 18 months.

**Premise.** UK wealth-policy debate is data-poor and method-opaque at exactly the moment policy demand is highest. Headline revenue figures from competing instruments span two orders of magnitude (the OBR's HVCTS forecast at ~£0.4bn/year and the Wealth Tax Commission's one-off levy at ~£80bn-£260bn). That spread is not noise; it reflects genuine modelling differences that are mostly invisible to non-specialists.

**Mechanism.** WealthLens does not change what policies are possible. It changes what kinds of *arguments about policies* are admissible by making the assumptions, data, uncertainty and trade-offs visible enough that policy disagreement becomes productive instead of rhetorical.

**Outcome (24-month horizon).** A small but consequential audience — Treasury analysts, OBR/IFS/CenTax researchers, tax committees, serious journalists — uses WealthLens to ground claims they would otherwise hand-wave. That audience does not need to be large. It needs to be the audience whose claims get cited.

**Outcome (5-year horizon).** Other UK wealth-policy modelling raises its evidentiary standards under quiet competitive pressure, the way PolicyEngine-UK has done for tax-benefit modelling.

**What would confirm the theory.**

- WealthLens outputs cited in OBR, IFS, CenTax or Treasury working papers.
- Tax committees ask oral-evidence questions in WealthLens terms (uncertainty ranges, package comparisons, transferability scores).
- Press coverage of wealth-tax proposals consistently includes uncertainty intervals.
- A competing modeller publishes a critique grounded in WealthLens's own published methods.

**What would falsify it.**

- WealthLens becomes a campaign citation: used by Tax Justice / IPPR / IFS-adjacent campaigners and ignored by Treasury / OBR / CenTax.
- Or, the inverse: WealthLens becomes a technocratic tool used only inside government and disappears from public debate.
- Or: the open-source build attracts no external contributors after 18 months.
- Or: another organisation (PolicyEngine-UK + CenTax, most plausibly) builds an equivalent and WealthLens fails to differentiate.

A theory of change has a falsification condition. If none of the above happens by month 30, the project's design assumptions were wrong and the project should be re-scoped or wound down, not extended.

---

## Critical editorial synthesis

### What this version keeps from both fourth-pass blueprints

- **Open-lab framing.** WealthLens answers "which packages are robust under uncertainty?", not "how do we justify a preferred tax?".
- **Package comparison.** Annual wealth tax is one family among seven: one-off levies, CGT reform, IHT/lifetime-transfer reform, property-tax reform, enforcement/information reform, devolution-asymmetric reform.
- **Top-tail uncertainty as a first-order result.** No silent favourite top-share estimate.
- **PolicyEngine-UK-compatible rules-as-code core, benchmarked against UKMOD, WTC and published HMRC/ONS aggregates.**
- **Static-first MVP.** No behavioural cleverness until the mechanical engine reproduces known results.
- **Uncertainty intervals by default.** No headline revenue figure without its assumptions and range.
- **Institutional layer is first-class.** Funding, governance, communications, ethics, partners and sustainability are designed in, not added later.
- **Devolution is first-class.** HVCTS is England-only; UK headlines without nation tags are simply wrong.

### What this version cuts or weakens

- **The implicit "wealth tax first" tone.** WealthLens compares annual wealth taxes against alternatives, not the other way around.
- **Single-number revenue claims.** Results are conditional ranges: baseline × top-tail model × valuation model × behavioural prior × compliance regime × legal design.
- **Strong novelty claims.** WealthLens's niche is the *intersection* of open code, top-tail reconstruction, wealth-policy packages, uncertainty discipline and public dashboarding. CenTax, IFS, PolicyEngine-UK, UKMOD, Resolution Foundation, WID.world and Oxford/DINA-related work all occupy adjacent space. The contribution is the join, not the elements.
- **Behavioural modules in v0.1.** They are explicit sensitivity wrappers in Phase 3.
- **RL/AI-first framing.** RL is a Phase 6 research extension, not the credibility foundation. Leading with RL is a documented failure mode.
- **Named-person inference.** Public outputs never infer or publish named individuals' wealth beyond already-public facts.

### What this fifth pass adds

- An explicit theory of change with falsification conditions (above).
- An AI/LLM disclosure protocol (§19). LLMs are everywhere in 2026 academic and policy workflows; pretending otherwise is the new HARKing.
- A comparator-simulators table that names what already exists (§16.2).
- An OBR-positioning answer — "why doesn't OBR just do this?" (§16.3).
- A new validation gate for independent reproduction by an external team (§14, Gate 6).
- The symmetric "wildly-optimistic-answer" discipline as a mirror of the "depressing-answer" discipline (§18.5).
- A computational-cost section sized honestly (§13.5).
- A glossary (§30).
- An explicit devolved-expertise disclaimer for Family G (§4.4).
- The £0.4bn↔£80bn revenue anchor as the public credibility argument for the whole project (§5.5).
- A baseline-status matrix tagging every policy lever as current-law / enacted-future / announced / consultation-stage / hypothetical (§3.1).
- A concrete repository layout and v0.1 build specification (§22).
- A 24-month success-metric section (§24).
- A year-1 project-killers list (§25).
- A "policy levers no one is modelling" gap map (§26).
- A post-HVCTS identity section (§27).
- The behavioural validation-set problem explicitly acknowledged (§11.6).
- License/IP and backwards-compatibility commitment (§17.5).
- Pre-mortem as standing risk methodology (§21.5).

---

## 1. Strategic framing and scope discipline

### 1.1 What WealthLens UK is and is not

| WealthLens UK *should be* | WealthLens UK *should not be* |
|---|---|
| An open simulation engine and public visualiser | An advocacy site for one preferred tax |
| A platform for comparing reform packages | A claim that one instrument is obviously optimal |
| Explicitly uncertainty-aware | A point-estimate revenue calculator |
| Focused on wealth stocks and stock-flow interactions | A general living-standards model |
| Honest about behavioural unknowns | A model that pretends elasticities are settled |
| Built on rules-as-code and reproducible pipelines | A PDF-only research project |
| Public-facing and research-grade off the same backend | A campaign calculator with academic language |
| Microsimulation first, behavioural and dynamic second | An AI-Economist-style RL demo looking for a policy use case |

The main political failure mode is being correctly identified as advocacy disguised as analysis. The solution is **structural neutrality**, not rhetorical neutrality: public assumptions, open code where legally possible, uncertainty intervals, published replication gates, visible engagement with counterarguments and a scoreboard that supports multiple objective functions. A project that hides its assumptions has no defence when its conclusions become politically inconvenient.

### 1.2 The actual policy question

The wrong question:

> Should the UK have a wealth tax?

The better question:

> Compared with reforming capital gains, inheritances, property taxation and enforcement, when does an annual wealth tax or one-off wealth levy perform better under plausible assumptions about valuation, avoidance, liquidity, migration and administrative cost?

That question is more useful, more publishable and harder to dismiss.

### 1.3 The political-economy window (May 2026)

The launch environment is not neutral. Three live conditions shape what is publishable:

1. **HVCTS consultation open.** GOV.UK published the High Value Council Tax Surcharge consultation on 19 May 2026 with a 14 July 2026 deadline. There is a concrete window for technical contributions.
2. **APR/BPR £2.5m cap in force from 6 April 2026.** Farm and business succession is a live political topic, not a historical one.
3. **Pension-IHT inclusion from 6 April 2027.** A major structural change to wealth-transfer taxation arrives during WealthLens's first development year.

WealthLens should design for this window without becoming captive to it (see §27 for the post-HVCTS identity problem).

---

## 2. UK wealth and inequality baseline

### 2.1 Household wealth distribution

The latest ONS Wealth and Assets Survey covers **April 2020 to March 2022** for Great Britain. WealthLens should treat this as the most important public survey anchor while also treating it as insufficient for the top tail.[^ons-wealth]

Key modelling implications:

- A UK wealth model that excludes **property** and **pensions** is not modelling UK wealth. It is modelling an administratively convenient subset.
- Regional incidence is not optional. Wealth levels and asset composition differ sharply between London/South East and poorer regions.
- WealthLens should report at minimum: median wealth, top-10% threshold, top-1% threshold/share, asset composition, regional/national incidence, liquidity, age/cohort and tenure.

### 2.2 Macro balance-sheet baseline (revised 2025 release)

The final ONS National Balance Sheet 2025 release reports household net worth of **£10.8 trillion in 2024**, revised down from earlier preliminary estimates.[^ons-nbs] Every WealthLens output must therefore carry a `macro_baseline_version` tag.

This matters because macro totals are not background context. They affect:

- survey-to-macro reconciliation;
- top-tail correction;
- denominator-sensitive top-share estimates;
- asset-class totals used in wealth-tax, property-tax and IHT scenarios;
- historical comparability.

### 2.3 The top-tail problem

The top-1% wealth share is not a settled number. It is a measurement problem. A credible WealthLens baseline should expose at least five variants:

| Variant | Meaning | Use |
|---|---|---|
| **Survey-only WAS** | Official survey weights with limited top correction | Lower-bound public-statistics baseline |
| **Pareto-corrected WAS** | Survey reweighted/imputed in upper tail | Primary research baseline |
| **Rich-list-augmented Pareto** | Pareto correction with public rich-list anchor/sensitivity | Upper-tail stress test |
| **Macro-reconciled / DINA-style** | Household distribution reconciled to national accounts | Long-run comparability baseline |
| **Hidden-wealth sensitivity** | Offshore, trusts and private-business wealth sensitivity | Compliance/observability stress test |

The model should not silently pick one favourite. It should show ranges and make the top-tail method visible in every chart. Top-tail uncertainty is not a footnote; it is one of the central findings.

### 2.4 Official wealth statistics are deteriorating

The Office for Statistics Regulation suspended the accredited official-statistics status of the Wealth and Assets Survey in June 2025 on quality grounds.[^osr-was] The right framing is not "WealthLens uses WAS" but:

> WealthLens treats WAS as indispensable but insufficient, and builds a data-fusion pipeline around it.

This is a major reason the project is worth building. The data environment is getting worse exactly when policy demand is rising.

### 2.5 Bottom-end fragility

WealthLens must not become only a "top 1% tool". The Family Resources Survey for 2024–25 reports that **18% of families had no savings** and **46% had less than £1,500 in savings**.[^frs] A household can be high wealth but low liquidity, or low wealth and extremely exposed to shocks.

WealthLens should report: liquid savings, secured/unsecured debts, tenure, age/cohort, pension wealth vs liquid wealth, business/farm illiquidity, deferral eligibility and take-up.

### 2.6 Income redistribution vs wealth redistribution

The UK tax-benefit system already substantially redistributes annual income flows. In FYE 2024, ONS reports that the richest fifth's mean equivalised household income before taxes and benefits was **12.2 times** that of the poorest fifth, falling to **3.3 times** after all taxes and benefits.[^ons-tax-benefits]

WealthLens should therefore distinguish:

- **income incidence:** who pays/receives in a given year;
- **wealth incidence:** whose stock of net worth changes;
- **lifecycle incidence:** how effects differ by age, pension status, homeownership and business ownership;
- **intergenerational incidence:** how reforms affect inheritance, gifts and dynastic accumulation.

The research niche is the *stock* of accumulated wealth, not a duplicate of living-standards distributional analysis.

---

## 3. Current UK wealth-related tax baseline as of 21 May 2026

The UK does not levy a comprehensive annual net wealth tax. It taxes wealth through a patchwork: capital gains, inheritance, property transactions, council tax, reliefs, residence rules, pensions and enforcement. WealthLens must compare reforms against this patchwork, not against "nothing".

### 3.1 Baseline status matrix

Every policy lever should be tagged by legal status. This avoids a subtle error of treating every announced measure as equally settled.

| Area | Status on 21 May 2026 | WealthLens treatment |
|---|---|---|
| CGT rates and annual exempt amount (2026–27) | Current law | Current-law baseline |
| Business Asset Disposal Relief / Investors' Relief at 18% from 6 April 2026 | Current law | Current-law baseline |
| IHT nil-rate band and residence nil-rate band freezes | Current law / scheduled | Current-law baseline with version tag |
| APR/BPR £2.5m 100% allowance from 6 April 2026 | Current law / enacted | Current-law baseline |
| IHT treatment of unused pension funds from 6 April 2027 | Enacted future law | Future-law baseline scenario |
| Death-in-service exclusion from pension-IHT changes | Confirmed in technical note | Future-law baseline scenario |
| HVCTS from April 2028 | Announced and under consultation | Announced-policy / consultation-sensitive baseline |
| Four-year FIG regime replacing non-dom remittance basis from 6 April 2025 | Current law | Residence/mobility baseline |
| Enforcement and observability | Current HMRC practice + reform scenarios | Separate policy family (Family F) |
| Annual net wealth tax | Hypothetical | Counterfactual scenario family (Family A) |
| One-off wealth levy | Hypothetical | Counterfactual scenario family (Family B) |

### 3.2 Capital Gains Tax

From 6 April 2026, GOV.UK lists CGT rates of **18% and 24% for individuals**, **24% for trustees and personal representatives**, and **18% for gains qualifying for Business Asset Disposal Relief or Investors' Relief**.[^cgt]

WealthLens should model CGT not just as a tax on realised gains, but as a behavioural margin: timing of realisations, emigration before disposal, income-to-gains reclassification, lock-in, business-exit timing, death uplift, main-residence relief, exit charges, carried-interest treatment. CGT reform is central because gains are highly concentrated and because private-business wealth is both hard to value and politically sensitive.

### 3.3 Inheritance Tax, APR/BPR and pensions

The 2026 baseline must include the post-Budget reforms to Agricultural Property Relief and Business Property Relief. The government states that a new **£2.5 million allowance** applies to the combined value of property qualifying for 100% APR/BPR, with 50% relief above that level, taking effect from **6 April 2026**.[^aprbpr]

The pension-IHT baseline should also include the Finance Act 2026 changes bringing IHT on pensions into effect for deaths on or after **6 April 2027**, with death-in-service benefits treated separately under the technical note.[^pensions-iht]

WealthLens should not treat IHT as a simple estate-rate calculator. Credible IHT modelling requires: estates and spouses/civil partners, nil-rate and residence nil-rate bands, tapering, pensions, lifetime gifts, trusts, farm/business relief, liquidity and instalment options, mortality and age structure, long-run intergenerational effects. A simplified estate-level model is acceptable for v0.1, but the assumptions must be explicit.

### 3.4 Property taxation and HVCTS

Property is unavoidable: land and housing dominate much of UK household wealth, and recurrent property taxation is one of the most practical wealth-adjacent policy levers.

The High Value Council Tax Surcharge is the most important live policy addition. The GOV.UK consultation, published **19 May 2026**, applies to England only and seeks views on a new charge on owners of residential properties worth **£2 million and above**.[^hvcts-gov] The consultation runs from **19 May to 14 July 2026** and is administered by MHCLG, HMT and HMRC Valuation Office.[^hvcts-gov]

Proposed charging structure:

| Property value band | Annual surcharge |
|---|---:|
| £2m to £2.5m | £2,500 |
| £2.5m to £3.5m | £3,500 |
| £3.5m to £5m | £5,000 |
| Over £5m | £7,500 |

The OBR's November 2025 EFO described the measure as applying from **April 2028** and estimated it would raise about **£0.4 billion in 2029–30**, flowing to central rather than local government.[^hvcts-obr]

WealthLens should treat HVCTS as:

- a named scenario in the current policy atlas;
- an *announced baseline / consultation-sensitive* lever for future-law comparisons (these two designations are deliberately distinct — the policy is announced; the design parameters are still moving);
- an urgent rapid-response use case because the consultation is live;
- an England-only policy unless Scottish, Welsh or NI equivalents are explicitly modelled;
- a property-valuation and liquidity-stress test case.

### 3.5 Non-dom replacement and residence-based taxation

The UK's residence/mobility baseline is no longer the pre-2025 non-dom world. From 6 April 2025, the remittance basis was replaced by a residence-based foreign income and gains regime. WealthLens should use the new residence environment when calibrating mobility, offshore and emigration scenarios.

The non-dom evidence is useful, but it is not direct evidence on an annual net wealth tax. It should calibrate a residence/migration module, not settle the entire behavioural model.

### 3.6 Enforcement and observability

Enforcement should be a policy family, not a caveat.

HMRC's 2025 tax-gap publication estimates the 2023–24 UK tax gap at **5.3% of theoretical liabilities, or £46.8 billion**.[^tax-gap] The NAO reports that HMRC defines wealthy individuals as those earning more than **£200,000** a year or with assets over **£2 million** in any of the last three years, and that HMRC identified approximately **850,000** wealthy individuals in 2023–24, with the wealthy compliance yield around **£5.2 billion** and the wealthy tax gap estimated at **£1.9 billion**.[^nao-wealthy]

WealthLens should model information regimes: beneficial-ownership visibility, trust reporting, offshore information exchange, Companies House PSC linkage, property-ownership linkage, valuation-audit intensity, rich-list reconciliation (as statistical sensitivity, not named inference), HMRC wealthy-taxpayer compliance staffing, penalties and compliance yield.

The question "what if HMRC had better wealth visibility?" may be one of the highest-value scenarios in the whole project — it raises revenue by increasing observability rather than rates, and may dominate rate changes on the robust frontier.

---

## 4. Devolution: make it first-class

A UK-wide WealthLens cannot treat all four nations as identical. Property taxation and some income-tax interactions are materially devolved.

### 4.1 Devolution map

| Domain | England | Scotland | Wales | Northern Ireland |
|---|---|---|---|---|
| Non-savings, non-dividend income tax | UK rates | Scottish rates and bands | Welsh rates mechanism | UK rates |
| Property transaction tax | SDLT | LBTT | LTT | SDLT |
| Recurrent property tax | Council Tax + proposed HVCTS | Council Tax | Council Tax | Domestic rates |
| CGT | Reserved | Reserved | Reserved | Reserved |
| IHT | Reserved | Reserved | Reserved | Reserved |
| Hypothetical annual wealth tax | Likely reserved / UK legislation | UK-wide unless devolved | UK-wide unless devolved | UK-wide unless devolved |

### 4.2 Modelling implications

- **HVCTS is England-only.** A "UK HVCTS revenue" headline is wrong unless the model explicitly adds equivalent policies elsewhere.
- **Property-tax reform needs a nation switch.** England, Scotland, Wales and Northern Ireland start from different recurrent-property-tax baselines.
- **Scottish income tax matters indirectly.** It interacts with CGT timing, income/capital reclassification, carried interest and residence decisions.
- **WAS covers Great Britain, not Northern Ireland.** NI wealth outputs require imputation and should be flagged.
- **Devolution-asymmetric reform is a real policy family.** Examples: England-only HVCTS; HVCTS replicated in Wales; Scottish property-tax revaluation; NI domestic-rates adjustment; UK-wide wealth tax with nation-specific offsets.

### 4.3 Recommended treatment

- Report all property-tax outputs by **nation** and **region**.
- Default to UK-wide baselines where taxes are reserved and nation-specific baselines where taxes are devolved.
- Add **Family G: Devolution-asymmetric reform** to the policy atlas.
- Flag every NI wealth output as imputed until a stronger NI-specific wealth source is available.
- Treat `nation` as a first-class field in the simulation schema, not a derived attribute.

### 4.4 The devolved-expertise disclaimer

WealthLens v0.1 will be built primarily by people without deep operational expertise in Scottish income tax administration, Welsh property tax mechanics or Northern Ireland's domestic rates system. The project should:

- name advisory contributors with devolved-tax expertise on the project page (and recruit them in the first 90 days if not present at launch);
- flag any devolved-tax modelling as "modelled by analogy" until reviewed by a practitioner from that nation;
- not publish Scotland-, Wales- or NI-specific revenue or incidence headlines without nation-specific review.

This disclaimer exists because the credibility cost of a single avoidable devolved error is high. Treasury, OBR and the devolved finance bodies will read carefully.

---

## 5. Where the evidence base is weakest

### 5.1 Wealth statistics are deteriorating

See §2.4. The OSR suspension of WAS accreditation is the central data-environment fact of the project.

### 5.2 The top end is structurally opaque

WAS undercoverage at the top is well-documented. Public rich-list data (Sunday Times, Forbes) is selection-biased and not a statistical sample. Offshore holdings, trust structures and private business valuations are partially observable at best. Top-tail estimates are sensitive to method choice in ways that headline numbers conceal.

### 5.3 Behavioural elasticities are wildly uncertain

The UK has limited direct evidence on annual wealth-tax responses because the UK has not had an annual wealth tax in living memory. Available evidence is:

- **UK non-dom reforms.** Direct UK evidence on a residence-based tax change. Useful for mobility calibration; not direct evidence on a broad annual wealth tax.
- **Scandinavian wealth taxes (Norway, Sweden historically, Switzerland ongoing).** Useful for cross-country priors. Transferability to a UK comprehensive wealth tax is limited by base differences, valuation regimes and enforcement design.
- **CGT realisation responses.** Better-evidenced than wealth-tax migration responses; relevant to CGT reform but not directly to wealth-tax behaviour.
- **Inheritance and gift responses.** Evidenced but heterogeneous; sensitive to how lifetime gifts and trusts are treated.

The honest position is that behavioural priors are **wide and weakly identified**. WealthLens should never present a single behavioural number as definitive (see §11.6 on the validation problem).

### 5.4 The Saez–Zucman / Summers–Sarin debate

The international debate over annual-wealth-tax revenue (Saez-Zucman bullish, Summers-Sarin sceptical) is structurally relevant: it shows that two careful teams looking at the same evidence can disagree by an order of magnitude on revenue. WealthLens should not pretend this is resolved. It should show why the disagreement persists.

### 5.5 The £0.4bn ↔ £80bn revenue range (public credibility anchor)

This is the single most important communication-grade fact about UK wealth policy:

- OBR's November 2025 forecast for HVCTS: **~£0.4bn in 2029–30**.[^hvcts-obr]
- Wealth Tax Commission's central one-off-levy estimate (2020): around **£80bn** at conservative thresholds, up to several hundred billion at aggressive designs.[^wtc]

These two numbers differ by a factor of 200. They are not estimates of the same thing — one is an announced recurrent property surcharge, the other a hypothetical one-off net wealth levy — but they are routinely presented to the public as comparable "wealth-policy revenue" figures.

WealthLens exists because this kind of comparison should not be left to press release alone. The standing public framing should be: *we cannot say which policy is right, but we can say what each estimate is doing differently, and why the gap is two hundred times rather than two times.* If WealthLens cannot explain the £0.4bn↔£80bn gap clearly to a non-specialist by month 6, the project has not yet earned a public dashboard.

---

## 6. Five core research questions and pass/fail criteria

| # | Research question | Primary deliverable | Pass/fail criterion |
|---:|---|---|---|
| Q1 | **Measurement.** How large is UK wealth concentration after survey undercoverage, top-tail missingness, offshore wealth, trusts and macro reconciliation are considered? | Top-tail-corrected baseline dataset + methods note | Reproduce official ONS/WAS tables and reconcile component totals to ONS balance-sheet aggregates within documented tolerances |
| Q2 | **Mechanical policy simulation.** What are the static revenue, incidence, liquidity and distributional effects of current-law and candidate reform packages? | WealthLens-Sim v0.1 | Reproduce Wealth Tax Commission / Advani–Hughson–Tarrant benchmark scenarios within ±5%, or publish why not |
| Q3 | **Behavioural uncertainty.** How sensitive are results to migration, avoidance, valuation, timing and reclassification assumptions? | Behavioural wrapper + sensitivity atlas | Every behavioural result reports prior source, transferability score, interval and static comparator |
| Q4 | **Dynamic effects.** How do reforms affect multi-year wealth accumulation, inheritances, CGT realisations, pension decumulation and property values? | Dynamic microsimulation v0.2/v0.3 | Model reproduces baseline multi-year wealth/tax trends before counterfactuals |
| Q5 | **Frontier.** Which packages remain attractive across plausible value judgements and uncertainty ranges? | Robust Pareto frontier report + dashboard | No single "winner" unless it dominates under explicitly stated objective weights |

Pass/fail criteria are not aspirational. A research question without one is a vibe.

---

## 7. Data architecture

The data architecture should be a **reconciliation pipeline**, not a simple ETL. The defensible contribution is showing how survey, macro, administrative and top-tail information are reconciled — and how disagreements between them are exposed rather than hidden.

### 7.1 Core sources

| Source | Role | Limitation |
|---|---|---|
| Wealth and Assets Survey | Core wealth distribution and asset composition | GB only; top-tail undercoverage; accreditation suspended |
| Family Resources Survey | Tax-benefit scaffold; UK-wide including NI | Weak on wealth and high-end assets |
| ONS National Balance Sheet | Macro asset totals and reconciliation | Sector-level, not distributional |
| HMRC CGT / IHT / SPI / Self Assessment statistics | Tax aggregates and distributional checks | Public tables limited; Datalab needed for microdata |
| UKMOD | Tax-benefit benchmark | Not a comprehensive wealth-policy simulator |
| PolicyEngine-UK | Open-source rules-as-code base | FRS-based; needs wealth extensions |
| Land Registry / property data | Property value and HVCTS modelling | England/Wales focus; matching and valuation limits |
| Companies House PSC / accounts data | Private-business ownership proxy | Control not value; incomplete and noisy |
| Sunday Times Rich List / public rich lists | Top-tail anchor and stress test | Visibility bias; not a statistical sample |
| Offshore / trust literature | Hidden-wealth sensitivity | Hard to allocate to households |
| UKHLS / Understanding Society | Dynamics and panels | Limited top-tail power |
| VOA HVCTS valuation process | £2m+ property identification for England | Access to aggregated outputs unclear |

### 7.2 Data principles

1. **Provenance first.** Every derived variable needs source, imputation method, version and uncertainty tag.
2. **Multiple baselines.** Ship survey-only, top-tail-corrected, macro-reconciled and stress-test variants in the same release.
3. **Observed vs imputed vs synthetic is always visible.** Public outputs distinguish these three.
4. **Macro reconciliation is explicit.** If survey totals disagree with national accounts, show the gap.
5. **No overfitting to rich lists.** Public rich lists are anchors and stress tests, not a complete truth set.
6. **Northern Ireland is explicit.** First release may be GB-only or UK-imputed, but the choice must be labelled.
7. **NBS figures are versioned.** Never silently update old analyses.
8. **No named-person wealth inference in public outputs.**

### 7.3 Top-tail reconstruction method

**First-pass (v0.1):**

1. Start with WAS asset-component distribution.
2. Harmonise to an FRS-compatible person/household schema.
3. Fit upper-tail Pareto / generalised-Pareto variants above multiple thresholds.
4. Add rich-list anchors as sensitivity, not ground truth.
5. Reconcile asset components to ONS National Balance Sheet totals.
6. Add hidden-wealth sensitivity for offshore assets, trusts and private-business holdings.
7. Produce top-share and threshold *intervals*, not single estimates.
8. Validate against published UK wealth-distribution studies and official tables.

**Second-pass (v0.2 onward):** the method should be **Bayesian** — specify priors for tail shape, hidden-wealth fraction, asset-class composition and macro reconciliation, then propagate posterior uncertainty through the simulator. This is the difference between "here are five estimates" and "here is a joint posterior over the wealth distribution conditional on stated priors". The first-pass approach is acceptable for v0.1; the Bayesian approach is required for any claim to method credibility beyond v0.1.

### 7.4 Synthetic wealth-augmented FRS

Because secure-data access typically takes 3–12 months (UKDS faster, ONS SRS slower, HMRC Datalab slowest), the public build should begin with a synthetic or semi-synthetic path:

1. Use FRS as the tax-benefit household spine.
2. Impute WAS-style wealth components onto FRS households using age, region, tenure, household type, income, employment, pension status and housing variables.
3. Calibrate component totals to the current ONS National Balance Sheet version.
4. Add synthetic top-tail records drawn from fitted distributions and public anchors.
5. Reweight to known demographic and fiscal aggregates.
6. Publish only synthetic/public outputs unless secure-data agreements permit more.

The early prototype must be honest: a **synthetic baseline for methods development**, not "official estimate".

### 7.5 Northern Ireland strategy

WAS does not cover Northern Ireland. WealthLens has three options, in order of credibility:

1. **Best:** find or build an NI wealth supplement from FRS-NI, NISRA household surveys, NI Land & Property Services data and HMRC NI aggregates. Hard, but defensible.
2. **Acceptable:** impute NI wealth distributions from GB analogues with explicit re-weighting based on observable income, tenure and demographic differences, flagged as imputation.
3. **Honest but limited:** publish v0.1 as GB-only, label it as such, and add NI in v0.2.

The wrong option is silently treating UK figures as if they covered NI when they cover only GB.

### 7.6 Assumption registry

Every assumption should be machine-readable. Schema:

| Field | Example |
|---|---|
| `assumption_id` | `behaviour.migration.non_dom_stock_elasticity.v1` |
| `domain` | migration, valuation, top-tail, compliance, liquidity |
| `value_or_distribution` | point, range or distribution |
| `source` | paper, official statistic, expert prior, calibration result |
| `transferability_score` | high / medium / low / stress-test only |
| `valid_range` | parameter range where model is defensible |
| `applies_to` | policy family and population |
| `last_reviewed` | date |
| `notes` | caveats and known disputes |

This prevents behavioural assumptions from becoming invisible ideology. Every report cites the assumption-IDs it depends on.

---

## 8. Simulation architecture

### 8.1 Layered architecture

```text
[1]  Source register and provenance layer
        ↓
[2]  Household / person / asset / tax schema  (nation is first-class)
        ↓
[3]  Wealth reconstruction and top-tail correction
        ↓
[4]  Current-law and announced-policy rules-as-code baseline
        ↓
[5]  Policy-family modules (A–G)
        ↓
[6]  Static mechanical simulator
        ↓
[7]  Uncertainty propagation (Monte Carlo / Bayesian)
        ↓
[8]  Behavioural response wrappers (Phase 3)
        ↓
[9]  Dynamic accumulation layer (Phase 5)
        ↓
[10] Robust-frontier search
        ↓
[11] Research outputs, JSON API and public dashboard
        ↓
[12] Provenance manifest emitted with every published number
```

### 8.2 Design principles

- **Rules-as-code, not rules-as-prose.** Tax law assumptions are executable, testable and version-controlled.
- **Static first.** Mechanical incidence must be correct before behavioural uncertainty is layered on top.
- **Every output is a distribution.** No public chart renders a naked point estimate when uncertainty exists.
- **ML around the edges, not at the legal core.** ML is for imputation, calibration, entity resolution and surrogate modelling; it never infers tax law.
- **Reconciliation, not just ETL.** The bridge between survey, administrative, macro and top-tail data *is* the research contribution.
- **Same backend for dashboard and research API.** No public toy model that produces different numbers from the research system.
- **Nation as first-class field.** Every household and every policy carries an explicit nation tag; "UK" outputs are always built from explicit nation components, not assumed.

### 8.3 Why static-first matters more than v2 conceded

The reason to insist on static-first is not technical conservatism. It is that behavioural models are unfalsifiable in the strict sense (see §11.6). If the mechanical layer is wrong, no behavioural overlay can save it; if it is right, behavioural ranges sit on top of a defensible substrate. Skipping straight to behavioural simulation produces a model with no falsifiable mechanical core, which is precisely the model whose conclusions look most modern and is least defensible under hostile review.

---

## 9. Policy scenario universe

Seven policy families, each with explicit design variables. The most useful public results will be packages, not single instruments.

### Family A: Annual net wealth taxes

Variables: threshold (£500k / £1m / £2m / £5m / £10m / £50m); rate (0.25% / 0.5% / 1% / 2%); tax unit (individual / household); base (comprehensive or excluding pensions / main residence / business assets); debt deductibility; trust/offshore treatment; deferral rules; valuation frequency; anti-avoidance design; residence test and exit charges.

**Caution:** high-threshold annual wealth taxes are extremely sensitive to top-tail measurement and behavioural assumptions. A wealth tax modelled at a £10m threshold is essentially a top-tail measurement exercise with a tax rate attached.

### Family B: One-off wealth levy

Variables: assessment date; rate and payment period; threshold; included assets; debt and liquidity treatment; anti-forestalling assumptions; recent-arrival and emigrant rules; estate interaction.

**Caution:** one-off levies and annual wealth taxes are not interchangeable. A one-off levy is efficient only if it is credibly unexpected and credibly one-off — two properties that erode the moment WealthLens itself starts modelling future levies.

### Family C: Capital gains reform

Variables: rate alignment with income tax; annual exempt amount; death uplift removal; main-residence relief options; business asset reliefs; carried interest; exit charge for emigrants; accrual taxation for selected assets; anti-forestalling and lock-in response.

CGT is central because gains are concentrated and the timing margin is large.

### Family D: Inheritance and lifetime-transfer reform

Variables: nil-rate bands; residence nil-rate band and taper; APR/BPR allowance and relief rate; pensions inclusion; lifetime gifts; recipient-based accessions tax; trusts; spousal transfers; instalment and liquidity rules.

IHT is not a substitute for an annual wealth tax, but well-designed transfer taxation can dominate poorly designed annual taxation on some objectives.

### Family E: Property-tax reform

Variables: HVCTS as proposed; HVCTS variants by threshold/rates/bands; council-tax revaluation; proportional property tax; land-value proxies; SDLT/LBTT/LTT replacement or offsets; owner vs occupier liability; low-income/high-property deferral; second-home and overseas-owner premiums.

Property-tax reform is unavoidable because property is visible, geographically concentrated and politically salient.

### Family F: Enforcement and information reform

Variables: beneficial-ownership reporting; trust/offshore reporting; wealthy-taxpayer segmentation; property-ownership linkage; valuation-audit resources; CGT compliance intensity; penalties/interest; data-sharing and anomaly detection.

This family may be the most cost-effective: raising revenue by increasing observability rather than rates. The £1.9bn wealthy tax gap is direct evidence that enforcement is not at its production-possibility frontier.

### Family G: Devolution-asymmetric reform

Variables: England-only HVCTS vs GB/UK equivalents; Scottish council-tax revaluation; Welsh property-tax reforms; NI domestic-rates adjustment; nation-specific property-tax offsets; internal UK mobility and residence effects.

This family exists because HVCTS is England-only and the UK property-tax baseline is not uniform.

### Combined package scenarios

The headline public output is package comparison:

1. **Reform-first package.** CGT + IHT + property-tax reform + enforcement, no annual wealth tax.
2. **High-threshold annual wealth-tax package.** £10m+ or £50m+ wealth tax + enforcement + deferral.
3. **One-off levy package.** Time-limited levy with strong legal design and no annual wealth tax.
4. **Property-heavy package.** HVCTS / proportional property tax + stamp-duty reform.
5. **Anti-avoidance package.** Enforcement and information improvements without major rate changes.
6. **Current trajectory plus.** HVCTS + APR/BPR reform + pension-IHT inclusion + CGT exit charge.
7. **Revenue-equivalent comparison set.** Packages designed to target the same revenue band (e.g. £5bn, £10bn, £20bn).
8. **Devolution comparison set.** England-only versus GB/UK-wide analogues.

Revenue-equivalent comparisons are essential because they separate "how much money is raised?" from "who pays, through which mechanism, with what side effects?".

---

## 10. Multi-objective scoreboard and robust frontier

### 10.1 Minimum scoreboard

Every scenario is scored, with uncertainty intervals, on:

- expected revenue and credible interval at year 1 / 5 / 10;
- gross and net of administrative / compliance costs;
- top-10%, top-1%, top-0.1% and top-0.01% wealth shares;
- wealth Gini and income Gini;
- regional and nation incidence;
- age/cohort and tenure incidence;
- liquidity stress by household type;
- low-end fragility effects;
- migration risk;
- avoidance / reclassification risk;
- valuation-dispute risk;
- investment / business-ownership distortion;
- housing-price capitalisation;
- legal complexity;
- implementation time;
- robustness across top-tail, valuation and behavioural scenarios;
- effect on observability and the measured tax gap.

### 10.2 Objective function

```text
Score(policy P, weights w, scenario s) =
        + w_rev   * revenue_gain(P, s)
        + w_top1  * reduction_in_top_1_share(P, s)
        + w_gini  * reduction_in_wealth_gini(P, s)
        + w_pov   * reduction_in_low_wealth_fragility(P, s)
        + w_prog  * improvement_in_tax_progressivity(P, s)
        - w_liq   * liquidity_stress(P, s)
        - w_adm   * admin_and_compliance_cost(P, s)
        - w_mig   * migration_and_avoidance_loss(P, s)
        - w_inv   * investment_or_housing_distortion(P, s)
        - w_legal * legal_and_delivery_complexity(P, s)
```

Outputs:

- the **robust Pareto frontier**;
- the **fragile frontier**: policies that appear good only under narrow assumptions;
- the **dominated set**;
- the **objective-sensitive set**: policies whose ranking depends heavily on whether the user weights revenue, inequality, liquidity or administrative simplicity.

### 10.3 Default objective profiles

To avoid the "user has to set ten weights to see anything" failure mode, ship six default profiles. They are not endorsements; they are illustrative weightings used in published debate.

| Profile | Headline emphasis | Approximate weighting |
|---|---|---|
| Revenue-first | Maximise revenue subject to liquidity floor | `w_rev` high; `w_liq` floor |
| Equality-first | Maximise top-tail share reduction | `w_top1` and `w_gini` high |
| Liquidity-protective | Minimise forced sales and arrears | `w_liq` and `w_pov` high |
| Administrative-realist | Minimise complexity and compliance cost | `w_adm`, `w_legal`, `w_mig` high |
| Investment-protective | Minimise business and housing distortion | `w_inv` high |
| Balanced default | Equal weighting across dimensions | Equal |

Users can build custom profiles. Defaults exist because most users do not.

### 10.4 What "robust" means

A policy is robust if it remains competitive across:

- survey-only and top-tail-corrected baselines;
- conservative and aggressive hidden-wealth assumptions;
- low, medium and high behavioural-response priors;
- low and high enforcement assumptions;
- reasonable variation in valuation error;
- GB-only versus UK-imputed datasets;
- England-only versus nation-adjusted property-tax baselines.

Policies that depend on one convenient assumption are **conditionally attractive**, not robust. The published frontier visualisations should label conditional attractiveness as such — colour-coded if needed — rather than averaging it away.

---

## 11. Behavioural modelling strategy (Phase 3)

### 11.1 Wrappers, not microfoundations

The behavioural layer is a wrapper around the validated static model. Each wrapper specifies:

- parameter definition;
- source (paper, official statistic, expert prior, calibration);
- valid range;
- default prior;
- transferability score to UK context;
- policy-family applicability;
- uncertainty propagation;
- side-by-side static and behaviour-adjusted output.

The point of wrapping is to make removing any behavioural assumption trivial. A modeller, reviewer or journalist should be able to ask "what does this look like with no behavioural response?" and get an answer from the same UI.

### 11.2 Transferability scoring

Behavioural parameters carry a transferability score for transferring evidence into the UK 2026 wealth-tax context:

| Tier | Meaning | Example |
|---|---|---|
| **High** | Direct UK evidence, same policy, recent | UK non-dom 2017/25 reform mobility |
| **Medium** | UK evidence, related policy | UK CGT realisation elasticities applied to wealth-tax realisation |
| **Low** | Foreign evidence, similar policy | Norwegian wealth-tax migration applied to UK design |
| **Stress-test only** | Foreign evidence, weak comparator, or contested | Saez–Zucman / Summers–Sarin US debate priors |

Stress-test-only priors are not used as defaults. They are used to ask "if this prior were correct, what would the policy look like?" — never to set a headline.

### 11.3 Eight modules

1. **Migration / residence.** UK non-dom evidence useful but not decisive for a broad annual wealth tax.
2. **Avoidance / reclassification.** Likely more important than physical emigration for many taxpayers.
3. **Timing.** CGT realisations, pre-announcement effects, delayed disposals.
4. **Valuation.** Dispute rates, appraisal costs, discounts for illiquid assets, property-valuation error.
5. **Liquidity.** Forced sales, borrowing, deferral take-up, arrears.
6. **Saving / labour / investment.** Effects can run in unintuitive directions.
7. **Inheritance / gifting.** Lifetime transfers, trusts, pension treatment, estate planning.
8. **Housing capitalisation.** Property values under recurrent property taxes and HVCTS.

### 11.4 Liquidity household typology

At minimum, distinguish:

- asset-rich / income-poor homeowners;
- pension-heavy households;
- illiquid business owners;
- farmers and land-rich households;
- high-income liquid-asset households;
- leveraged property owners;
- low-wealth / low-savings households.

HVCTS makes this especially important because some affected households may own high-value homes but have limited cash income — a politically salient typology that the simulator must be able to identify.

### 11.5 Scenario calibration

Report each major behavioural result across:

- **mechanical static** (no response);
- **low-response** (conservative priors);
- **UK non-dom anchored** (best UK-direct evidence);
- **Scandinavian middle** (mid-range cross-country priors);
- **Swiss / Norwegian high-response** (upper range);
- **adversarial avoidance** (aggressive avoidance assumption);
- **enhanced-enforcement** (Family F-style observability scenario).

No behavioural result is presented as settled fact.

### 11.6 The validation-set problem for behavioural modules

This section exists because neither prior blueprint addressed it directly.

**Standard validation requires a held-out test set.** For a UK behavioural model of an annual wealth tax, there is none: the UK has not had an annual wealth tax in living memory. Comparable evidence from Norway, Switzerland, Sweden, France and Spain is informative but not held-out: those base/design/enforcement environments differ from a hypothetical UK design.

This means **behavioural modules cannot be validated in the strict statistical sense**. They can only be:

1. *internally consistent* (priors stated, ranges propagated);
2. *historically plausible* (consistent with international evidence after transferability adjustment);
3. *robust* (results that survive across a wide prior space);
4. *transparent* (every assumption traceable to a source).

The honest claim is **robustness, not accuracy**. WealthLens should never describe its behavioural results as "validated"; it should describe them as "robust over a stated prior space" or "fragile to a stated assumption". This distinction is what separates an honest microsimulation from a model that performs precision it does not possess.

The published phrase should be something like:

> WealthLens behavioural results are robust across the stated prior space. They are not validated against a UK wealth-tax outcome because none exists. A result reported as robust here would still be defeated by a UK reform whose actual response fell outside the prior space.

If the project cannot stand behind that sentence, the behavioural layer is overclaiming.

---

## 12. AI / ML / ABM / RL: where they fit

### 12.1 Main recommendation

Use transparent microsimulation first. Use ML where it improves measurement, speed or uncertainty handling. Use ABM/RL later only where interactions genuinely matter.

### 12.2 Where ML is useful immediately

- top-tail reconstruction (Pareto fitting, generative tail models);
- missing asset imputation;
- entity resolution and ownership-network inference (Companies House PSC linkage);
- anomaly detection for impossible records;
- surrogate models for expensive scenario grids;
- clustering household liquidity/behaviour types;
- uncertainty propagation (variational inference, normalising flows).

### 12.3 Where ABM is useful (Phase 5+)

ABM becomes useful when interaction effects matter:

- housing-market feedback and price capitalisation;
- tax-adviser diffusion and avoidance networks;
- local migration clusters;
- private-business investment dynamics;
- intergenerational transfer networks.

This is Phase 5+, not MVP.

### 12.4 Where RL is useful — with sharp caveats

RL may be useful for robust policy-search experiments after the core simulator exists. It should never lead the project. Documented risks:

- stylised environments produce policies that do not survive legal/political constraints;
- economists may dismiss the project if RL appears before measurement and replication;
- policy recommendations from RL can be brittle under distributional shift;
- explainability is weaker than in rules-as-code microsimulation.

The Salesforce AI-Economist (Zheng et al.) is the explicit cautionary case: a technically elegant RL tax-policy design that received limited uptake in tax-policy circles because measurement, institutional realism and behavioural transferability were treated as out-of-scope. WealthLens explicitly inverts that ordering — institutional realism first, RL last — and that ordering choice should be visible in any methodology comparison.

Best use of RL: a separate methods paper on robust frontier search or adversarial policy design after the core simulator is established. Not v0.1. Not the main WealthLens output.

### 12.5 Where HANK / DSGE fits

HANK and DSGE models are macroeconomic substrates, not microsimulation substrates. They might inform long-run scenario priors (interest-rate feedback, wage dynamics, investment crowding) but should not be the core engine. WealthLens is a wealth-stock microsimulation, not a macroeconomic forecaster.

### 12.6 LLMs as research and development tooling

LLMs are pervasive in 2026 research workflows. WealthLens treats them as **tooling for the development process, never as authority on the model's outputs**. This means:

- LLMs may be used for code drafting, literature search, citation discovery, schema design, test generation, documentation drafting, naming.
- LLMs are **not** used to generate model outputs, set behavioural priors, draft policy interpretations, write quoted policy positions or settle methodological disputes.
- All LLM use in the development pipeline is disclosed (see §19).
- LLM-suggested code is reviewed and tested before merge under the same standard as human code.

This is the honest 2026 disclosure standard. The dishonest standard is to use LLMs heavily and not mention it.

---

## 13. Technical stack, the MVD chart, and computational cost

### 13.1 MVP stack

| Component | Recommendation | Reason |
|---|---|---|
| Core language | Python | Best ecosystem for PolicyEngine, data, statistics and visualisation |
| Rules engine | PolicyEngine-UK fork/module | Transparent tax-benefit formulas |
| Benchmark | UKMOD + WTC replication + HMRC/ONS aggregates | Credibility checks |
| Storage | Parquet/Arrow + DuckDB | Fast, inspectable, reproducible |
| Pipelines | Snakemake, Dagster or Prefect | Reproducible runs |
| Statistical modelling | PyMC / NumPyro | Bayesian top-tail and uncertainty modelling |
| Imputation / ML | scikit-learn + careful validation | Practical, inspectable |
| Validation | pandera / Great Expectations / custom tests | Prevent silent drift |
| Testing | pytest + golden-file policy tests | Legal/rule regression protection |
| Dashboard MVP | Streamlit | Fast iteration |
| Production dashboard | Plotly Dash / Next.js / Observable | Better public product |
| Reporting | Quarto | Reproducible papers and briefs |
| Output API | JSON REST endpoint + OpenAPI spec | Reuse by journalists, think tanks and researchers |
| Versioning | Git + DVC where permissible + Zenodo DOIs | Reproducibility and citation |
| Licensing | Follow PolicyEngine constraints; prefer open license (see §17.5) | Keeps derivative work open |

### 13.2 The "minimum viable demonstration" chart

Before building the public dashboard, decide what single output would convince a sceptical IFS/CenTax-style reader that WealthLens works. Best candidate:

> A side-by-side scorecard comparing **HVCTS as proposed**, **HVCTS with a £1m threshold**, **a £2m / 0.6% annual wealth tax**, **APR/BPR reform** and **an enforcement-only package** on revenue, top-tail distributional effect, liquidity stress, regional/nation incidence, administrative complexity and uncertainty.

Why this chart works: live policy case; wealth-tax-adjacent property reform compared with annual wealth-tax reform; forces regional/nation incidence; forces liquidity modelling; forces uncertainty intervals; makes clear whether enforcement dominates rate changes under some assumptions. If WealthLens cannot produce this chart defensibly, it is not ready for a public dashboard.

### 13.3 Versioning for live UK tax law

UK tax law moves on a fast calendar (two fiscal events per year, plus consultations). WealthLens versioning must include:

- `policy_version`: a semantic version of the rules-as-code (e.g. `uk_2026_05_21_v1`).
- `population_version`: dataset version (e.g. `frs_was_pareto_macro_v0_1`).
- `macro_baseline_version`: NBS release version.
- `consultation_state`: for announced-but-changing policies (e.g. `hvcts_consultation_open` vs `hvcts_consultation_closed`).
- `fiscal_event_anchor`: the most recent Budget or Spring Statement reflected.

Every published number carries all of these tags. Old releases remain runnable.

### 13.4 Internal API sketch

```python
scenario = WealthLensScenario(
    baseline="uk_2026_05_21_v1",
    population="frs_was_pareto_macro_v0_1",
    macro_baseline="ons_nbs_2025_final",
    nation="UK",
    policies=[
        HVCTS(mode="announced_2028_consultation", nation="England"),
        AnnualWealthTax(threshold=10_000_000, rate=0.01, base="comprehensive"),
        CGTReform(rate_alignment="income_tax", exit_charge=True),
        EnforcementScenario(reporting="enhanced_top_tail")
    ],
    uncertainty=UncertaintySpec(
        top_tail="bayesian_pareto_v1",
        valuation_error="asset_class_specific",
        behaviour="off_by_default"
    ),
    outputs=["revenue", "incidence", "liquidity", "region", "nation", "frontier"]
)

results = wealthlens.run(scenario)
results.scoreboard()
results.frontier(weights={
    "revenue": 0.3, "inequality": 0.3, "liquidity": 0.2, "admin": 0.2
})
results.provenance_manifest()   # full versioning + assumption_id graph
```

The `provenance_manifest()` call is the auditability anchor. Every number any user sees should trace back through it.

### 13.5 Computational cost

A typical release run, sized honestly:

- 5 macro baselines (synthetic, survey-only, Pareto-corrected, macro-reconciled, hidden-wealth sensitivity)
- × 7 policy families
- × ~10 representative scenarios per family
- × 5 behavioural calibration scenarios (§11.5)
- × 1000 Monte Carlo / posterior draws for uncertainty propagation

This is approximately **1.75 million scenario cells per release**. With per-cell runtimes of seconds for static and minutes for behavioural-wrapped runs, this is in single-machine-overnight territory for static and small-cluster territory for behavioural — *if* code is vectorised and `nation` is a proper indexed dimension rather than a loop variable.

Practical implications:

- early prototypes use **scenario sub-samples** to iterate on logic, with full sweeps only at release time;
- surrogate models (Gaussian process or neural emulators trained on the full simulator) become useful in Phase 4+ for interactive dashboards;
- ABM/RL extensions push compute requirements up materially; that is one reason they are Phase 5+.

The realistic compute budget for v0.1 is modest (a workstation plus burstable cloud). The realistic compute budget for v0.3+ with full behavioural uncertainty and dynamic accumulation is materially larger — funders should be told this when they ask "could you handle ten more scenarios?".

### 13.6 Repository layout

```text
wealthlens/
  data_registry/
    sources.yml
    assumptions.yml          # the machine-readable assumption registry (§7.6)
    baselines.yml            # policy_version / population_version / macro_baseline_version registry
  wealthlens_core/
    schema/                  # household / person / asset / tax schema; nation is first-class
    reconstruction/          # WAS / FRS / NBS reconciliation; top-tail fitting
    top_tail/                # Pareto, Bayesian Pareto, rich-list anchors, hidden-wealth sensitivity
    rules/                   # PolicyEngine-UK extensions for wealth-relevant rules
    policies/                # Families A–G, scenarios, packages, revenue-equivalent sets
    uncertainty/             # propagation, posterior sampling, surrogate models
    outputs/                 # scoreboard, frontier, dashboard backend, JSON API
    provenance/              # manifest generation, version tagging
  tests/
    test_schema.py
    test_ons_reconciliation.py
    test_policy_rules.py     # golden-file regression tests for tax law
    test_wtc_replication.py  # Gate 3
    test_hvcts.py            # Gate 3 sub-test
  notebooks/
    01_reproduce_ons_tables.qmd
    02_top_tail_variants.qmd
    03_hvcts_static_demo.qmd
    04_wtc_replication.qmd
  reports/
    methods_note.qmd
    hvcts_brief.qmd          # Phase 1.5 rapid-response brief
    minimum_viable_demo.qmd
  dashboard/
    backend/                 # shared with research API
    frontend/                # public dashboard
  docs/
    charter.md               # Gate 0
    contributing.md
    governance.md
    ai_disclosure.md         # §19
    glossary.md              # §30
```

The repository layout is part of the model charter. Reviewers should be able to navigate from a published number → notebook → policy module → rule code → assumption-ID → source within five clicks.

---

## 14. Validation gates

Nine gates, in order. Each must pass before the next phase opens. The structure combines the operational v4's reproduction gate (Gate 6) with the editorial v4's model-charter gate (Gate 0) and dashboard-safety gate (Gate 8).

### Gate 0: Model charter

- Published statement of what the model does and does not claim.
- Public assumption-registry format (§7.6).
- Baseline legal-status tags (§3.1).
- Privacy statement for top-end data.
- License and IP statement (§17.5).
- AI/LLM disclosure statement (§19).

**Fail condition:** any later gate succeeds while the charter is silent or contradictory. The charter is not optional documentation; it is the first deliverable.

### Gate 1: Data reconstruction

- Reconstructed median wealth matches ONS within documented tolerance.
- Top-10% threshold matches ONS within documented tolerance.
- Asset-component totals reconcile to ONS NBS version.
- Regional / nation medians are plausible.
- Top-tail variants bracket published top-share estimates.

**Fail condition:** model cannot explain gaps between synthetic baseline and official tables.

### Gate 2: Macro reconciliation

- Household asset totals reconcile to macro aggregates.
- Discrepancies are shown, not hidden.
- Model can re-run using old and current NBS versions.
- Reconciliation residuals are reported per asset class with a documented tolerance for each.

**Fail condition:** macro / micro gaps absorbed by silent reweighting.

### Gate 3: Tax-benefit and current-law baseline

- Core tax-benefit outputs align with PolicyEngine / UKMOD benchmarks.
- CGT and IHT modules reproduce public receipt aggregates where possible.
- HVCTS scenario reproduces OBR ~£0.4bn 2029–30 forecast within tolerance under matching assumptions.
- Fiscal-event versioning works (rebuilding a March 2026 baseline produces March-2026 era results).

**Fail condition:** differences between WealthLens current-law and known benchmarks are unexplained.

### Gate 4: Wealth Tax Commission replication

- Replicate Advani–Hughson–Tarrant (2021) annual wealth-tax revenue numbers within ±5%, or publish the reason for divergence.
- Replicate WTC one-off levy numbers within ±5%, or publish the reason for divergence.
- Liquidity metrics directionally comparable.

**Fail condition:** project advances to new policy claims before replication succeeds or divergence is documented.

### Gate 5: Policy package engine

- All seven policy families (A–G) run from a common API.
- Outputs use the same scoreboard.
- Uncertainty propagation works end-to-end.
- Dashboard and research API draw from the same backend (no parallel "public" toy model).

**Fail condition:** policy scenarios are too vague to be audited, or dashboard numbers differ from backend numbers.

### Gate 6: Behavioural layer

- Behavioural parameters documented in the assumption registry (§7.6).
- Default priors defensible.
- Transferability score attached to every parameter (§11.2).
- Static and behaviour-adjusted results shown side-by-side.
- No behavioural result presented as settled fact (§11.6).

**Fail condition:** behavioural assumptions hard-coded into the headline; transferability scores missing or rhetorical.

### Gate 7: Independent reproduction

- An outside person (not a project team member) clones the repository on a clean machine, runs the published replication notebook against public synthetic data, and reproduces the headline figures of v0.1 within numerical tolerance.
- All v0.1 figures are regenerable from public code and public/synthetic data without WealthLens team intervention.
- Replication log published openly, including any divergences and their causes.

**Fail condition:** v0.1 ships before independent reproduction succeeds. "We can reproduce our own results" is not a credible claim; the project does not declare v0.1 final until someone outside the team has done it.

### Gate 8: External review

- At least one microsimulation specialist, one UK tax economist (CenTax / IFS / academic), one tax/legal practitioner, and where top-end linkage is used one data/privacy reviewer, review the methodology before public launch.
- Review log published.
- Review either signs off or documents specific objections to which WealthLens publishes a response.

**Fail condition:** public launch before serious external critique.

### Gate 9: Dashboard safety

- No point estimates without uncertainty intervals.
- Share links preserve full assumption sets.
- Out-of-range scenarios visibly marked.
- No named-person outputs.
- Press pack contains a "what this does and does not say" sheet.
- Default landing page does *not* lead with a single revenue number.

**Fail condition:** dashboard ships with any of the above missing.

---

## 15. Publishable outputs

| # | Working title | Question | Target outlet |
|---:|---|---|---|
| 1 | **Reconstructing the UK Wealth Distribution under Survey Decline** | What is the credible range for top-1% / 0.1% UK wealth shares once WAS deterioration and macro reconciliation are handled? | SSRN/arXiv; *International Journal of Microsimulation*; *Fiscal Studies* |
| 2 | **Distributional and Regional Incidence of the HVCTS** | What does HVCTS do by region, age, tenure, liquidity and property value? | Consultation brief (before 14 July 2026); SSRN; think-tank co-publication |
| 3 | **Comparing UK Wealth-Focused Tax Packages under a Common Framework** | Which packages lie on the robust Pareto frontier? | *Fiscal Studies* / policy report |
| 4 | **Migration, Avoidance and Dynamic Wealth Responses in UK Wealth-Policy Simulation** | What is the credible UK behavioural-response range? | *Fiscal Studies* / public economics venue |
| 5 | **An Open, Uncertainty-Aware Microsimulation Stack for UK Wealth Policy** | How does the software and data stack work? | arXiv methods note / software paper |
| 6 | **Robust Policy Search for Wealth Taxation under Top-Tail Uncertainty** | Can optimisation help identify non-dominated policy packages? | Computational economics / ABM/RL venue, Phase 6 only |
| 7 | **HVCTS Rapid-Response Brief** *(not formal publication; consultation submission)* | What can be said about HVCTS distributional and revenue effects with v0.1-level data? | GOV.UK consultation submission + public companion note |

The first paper is the measurement paper. It is the least politically vulnerable and creates credibility for every later paper.

### Best first abstract (measurement paper)

> The UK's primary household wealth survey lost accredited official-statistics status in mid-2025 amid growing concern about response rates and top-tail coverage, exactly as wealth-policy interest has intensified. This paper rebuilds a public, reproducible UK wealth-distribution baseline by fusing the Wealth and Assets Survey, the Family Resources Survey, ONS National Balance Sheet aggregates, HMRC tax statistics and public ownership proxies, applying multiple top-tail correction methods (Pareto, rich-list-anchored, macro-reconciled, hidden-wealth sensitivity) and propagating measurement uncertainty as intervals rather than point estimates. The result is not a single best estimate of the UK top-1% wealth share but a defensible interval that exposes which method choices drive the headline. This baseline becomes the substrate for a fully open UK wealth-policy microsimulation platform that supports comparison across annual wealth taxes, one-off levies, CGT / IHT / property-tax reform, enforcement reform and devolved variants under a common scoreboard.

---

## 16. Partners, competition and engagement strategy

### 16.1 Competitive positioning

| Organisation / tool | Strength | WealthLens gap / distinction |
|---|---|---|
| IFS | Best UK tax-policy credibility | Not an open public simulator focused on wealth packages |
| CenTax | Strong top-end tax expertise | Not a public dashboard/simulation platform |
| PolicyEngine-UK | Open rules-as-code infrastructure | Needs wealth-distribution / top-tail extensions |
| UKMOD | Strong tax-benefit microsimulation benchmark | Not designed for wealth-policy packages |
| Resolution Foundation | Strong inequality and policy analysis | Not a reusable open simulator |
| WID.world / DINA | Long-run distributional series | Not a UK policy simulator |
| Tax Justice UK / TJN | Campaigning and tax-justice amplification | Lower perceived neutrality for core modelling |
| Tax Policy Associates | Technical tax communication | Not a full microsimulation platform |
| OBR | Authoritative fiscal forecasting | Not an open simulator; not designed for public scenario comparison |

The niche is the **intersection**: open-source UK wealth-policy simulation + top-tail reconstruction + policy-package comparison + public dashboard + uncertainty discipline. None of the elements is novel. The join is.

### 16.2 Comparator simulators

Neither prior blueprint was precise about which other simulators exist in adjacent space. WealthLens should be evaluated against these and should publish explicit comparisons.

| Simulator | What it models | Open source? | Wealth focus? | Uncertainty intervals? |
|---|---|---|---|---|
| PolicyEngine-UK | Tax-benefit (FRS-based) | Yes (AGPL) | No (income focus) | Limited |
| UKMOD | Tax-benefit microsimulation | Restricted (academic) | No (income focus) | Limited |
| TAXBEN (IFS) | Tax-benefit microsimulation | No (IFS internal) | No (income focus) | Limited |
| OBR distributional models | Fiscal forecasting | No (HMG internal) | Partial | Limited public |
| HMT internal models | Policy costing | No (HMG internal) | Partial | Limited public |
| EUROMOD | EU tax-benefit microsimulation | Restricted (academic) | No | Limited |
| PolicyEngine-US | US tax-benefit | Yes (AGPL) | No | Limited |
| AI-Economist (Salesforce) | RL tax-policy design | Yes | Stylised | None (single-scenario) |
| Wealth Tax Commission spreadsheets | One-off levy revenue | Partly public | Yes | Some sensitivity |
| WID.world / DINA pipelines | Long-run distributional series | Partly public | Yes (long-run shares) | Limited |

The gap WealthLens fills: an *open*, *wealth-focused*, *uncertainty-aware*, *public-dashboard-capable* UK simulator. Each adjective rules out at least one alternative.

### 16.3 The OBR positioning question

"Why doesn't OBR just do this?" is a question funders and journalists will ask. The honest answer:

1. **OBR's job is fiscal forecasting under government policy, not open scenario exploration.** It does not publish scenarios the government has not announced.
2. **OBR's models are not open source.** Reviewers cannot inspect them. Reproduction is limited to what is in the EFO.
3. **OBR does not publish uncertainty intervals at the scenario-design level.** Its forecast central estimates have ranges but its modelled policy effects rarely do.
4. **OBR does not run a public dashboard.** Its outputs are reports.
5. **OBR is structurally bound to the government's policy menu.** A genuine alternative menu — including options that are politically off-limits — is not in OBR's remit.

WealthLens is therefore not competing with OBR; it is occupying a space OBR is institutionally precluded from occupying. The same answer applies to HMT internal models, with the additional point that those models are not visible at all.

### 16.4 Stakeholder map

| Audience | What they need | WealthLens output |
|---|---|---|
| Treasury / OBR / policy advisers | Defensibility and current-law accuracy | Methods note, benchmark gates, static and behavioural ranges |
| Tax economists | Data/method credibility | Measurement paper, replication package, uncertainty model |
| Think tanks | Usable comparisons | Policy atlas, frontier report, scenario briefs |
| Tax practitioners | Legal precision | Assumption register, legal review, valuation/dispute modelling |
| Press | Clear claims without overstatement | Embargoed methods pack, "does/does not say" sheet |
| Public | Legibility and trust | Dashboard, explainers, shareable assumption-preserving scenarios |
| Funders | Impact and sustainability | Roadmap, governance, partnership letters, audit plan |
| CS / ABM community | Methodological novelty | Later ABM/RL paper, not v0.1 |

### 16.5 HMRC relationship strategy

HMRC matters for three reasons: (1) Datalab access to administrative microdata; (2) practical realism on enforcement and compliance modelling; (3) institutional credibility. Strategy:

- approach HMRC Datalab early for synthetic and aggregated data, not micro;
- propose enforcement scenarios (Family F) as the most directly useful contribution to HMRC's own evidence base;
- offer to share replication code for any analysis that uses HMRC aggregates;
- avoid framing that positions WealthLens against HMRC; the project benefits from HMRC's data and HMRC may benefit from WealthLens's enforcement scenarios.

### 16.6 The collaboration pitch line

> "We are not asking you to endorse a policy position. We are asking you to help make the assumptions, data and trade-offs visible enough that people can disagree productively."

### 16.7 Building credibility as a non-institutional team

1. Replicate first, extend second, claim novelty third.
2. Open-source aggressively within data constraints.
3. Publish benchmark failures honestly.
4. Obtain external review before public launch.
5. Separate methods outputs from policy commentary.
6. Avoid funder or campaigner control of scenario design.
7. Ship the boring foundation (Gate 1–3) before the interesting frontier (Gate 5–6).

---

## 17. Funding, governance and sustainability

### 17.1 Realistic cost envelope

A 24-month lean version with one lead researcher, one engineer, limited advisory time, data-access administration, modest compute and a public dashboard is plausibly **£250k–£500k**.

This is a planning envelope, not a validated cost model. The lower bound assumes founder labour, academic hosting and a lean dashboard. The upper bound assumes two paid staff, a designer/front-end contractor, advisory honoraria and more formal governance. Costs above £500k typically reflect institutional overheads, not additional research output.

### 17.2 Funding sources

Preferred funding profile:

- at least three independent funding sources within 24 months;
- no single advocacy-adjacent funder above 50%;
- public conflict-of-interest disclosure;
- separation between funders and modelling decisions;
- institutional host or fiscal sponsor by year 2.

Potential funding channels:

| Source | Fit | Caveat |
|---|---|---|
| Nuffield Foundation | Strong UK social-science fit | Academic partnership useful |
| Joseph Rowntree Foundation / JRCT | Strong inequality fit | Need neutrality discipline |
| ESRC / impact grants | Strong if academic host exists | Requires institutional partner |
| Open Society / Open Philanthropy | Possible | Depends on framing and contacts |
| PolicyEngine-related support | Strong software fit | Scope alignment needed |
| Government commissioning | Later-stage possibility | Avoid dependence before credibility established |
| Campaigning organisations | Useful for dissemination | Poor as primary funders |
| Individual donors | Possible | COI and advocacy-perception risk |

### 17.3 Sustainability beyond month 24

The main operational risk is that the project becomes one person's private model. Mitigations:

- documented baseline-update playbook;
- CI tests for policy rules;
- public changelog;
- multiple maintainers;
- archived releases with DOIs;
- reproducible examples;
- institutional partner or fiscal host;
- roadmap tied to Autumn Budget and Spring Statement cycles.

### 17.4 Governance

Minimum design:

- 3–5 person methods advisory group;
- public issue tracker;
- annual methodology audit/review note;
- conflict-of-interest page;
- release notes after each fiscal event;
- privacy review for linked top-end data;
- clear statement that WealthLens scores policies and does not endorse them.

### 17.5 License, IP and backwards-compatibility commitment

Neither prior blueprint specified a license or maintenance commitment. The omission matters.

**License.** WealthLens should be licensed under **AGPL-3.0** for the simulator code (matching PolicyEngine-UK), **CC-BY-4.0** for documentation and reports, and **CC0** for purely synthetic public datasets. AGPL prevents a closed fork being deployed as a hosted service without contributions flowing back; CC-BY-4.0 protects attribution; CC0 prevents licence friction on derivative reuse of synthetic data.

**Trademark.** "WealthLens UK" should be a registered or asserted project mark to prevent unrelated parties branding modified versions as if they were the project. A simple "What you can and cannot call your fork" page is sufficient.

**Data IP.** Microdata access agreements (UKDS, ONS SRS, HMRC Datalab) bind the team; published synthetic data is licensed separately and unambiguously.

**Backwards-compatibility commitment.** Every published baseline (`uk_2026_05_21_v1` and successors) is maintained as runnable for **at least three years from release**. A reviewer who cites a WealthLens number in 2027 must be able to regenerate it in 2030. This is a stronger commitment than most academic code makes; it is the price of being cited by Treasury and OBR.

**Deprecation policy.** Deprecated baselines are clearly marked but not deleted. Old numbers remain auditable.

---

## 18. Communications and ethics

### 18.1 The viral-misuse problem

A wealth-tax slider will be screenshotted, stripped of assumptions and used politically. Design for that.

Rules:

- Always render uncertainty intervals with headline numbers.
- Share links preserve full parameter sets and assumptions.
- Extreme scenarios carry "outside validated range" warnings.
- Defaults are methodologically conservative, not politically attractive.
- Every policy family has "case for" and "case against" panels.
- The dashboard shows when no scenario dominates.

### 18.2 Press strategy

Before public launch:

- publish methods note first;
- pre-brief technical reviewers before journalists;
- prepare a one-page "what this does and does not say" sheet;
- train spokespeople to use ranges;
- never let the headline be "WealthLens recommends X".

Correct line:

> WealthLens does not recommend a policy. It shows trade-offs under explicit assumptions. Different objectives and assumptions produce different non-dominated packages.

### 18.3 The discipline answer to "what does WealthLens think?"

Audiences will ask this. The standing answer is:

> WealthLens does not think anything about policy. It scores policies under explicit assumptions. Personal views of the team are held separately and not branded WealthLens.

### 18.4 The "what if the answer is depressing?" discipline

There is a real possibility that the robust finding is not "wealth tax yes". It might be that:

- avoidance/migration responses eat much of the gross revenue;
- liquidity-constrained populations are politically and administratively difficult;
- annual wealth taxation performs worse than CGT/IHT/property/enforcement packages;
- enforcement and information reform dominate new taxes on the robust frontier.

WealthLens must be ready to publish that. Specific commitments:

- pre-register the methodology, not the expected answer;
- reserve space in every output for "what conclusions this did not support";
- publish enforcement-as-frontier honestly if that is the result;
- treat funder pushback as a credibility test.

### 18.5 The "what if the answer is wildly optimistic?" symmetric discipline

The mirror failure mode is equally dangerous. If the model produces unusually attractive revenue or distributional results for a preferred policy, the credible reaction is suspicion, not celebration.

Specific commitments:

- any result more attractive than the best comparable estimate in the published literature triggers a methodology audit *before* publication;
- the audit checks for: missed behavioural response, missed avoidance margin, base-erosion not modelled, valuation optimism, double-counted enforcement gain, top-tail measurement that flatters the policy;
- if the result still stands after audit, publish the audit alongside it;
- if the result is downstream of a funder priority, the audit is mandatory and the audit log is published.

The discipline is symmetric: "wildly optimistic" and "depressing" are both signals that something might be wrong. The methodology must treat them identically.

### 18.6 Ethical guardrails on top-end data

- Never publish inferred wealth estimates for named individuals.
- Never combine public records in ways that create avoidable de-anonymisation.
- Do a privacy review before linking PSC, Land Registry, rich-list and admin proxies.
- Keep secure-data constraints separate from public synthetic outputs.
- Use aggregate cells large enough to prevent re-identification.

### 18.7 Politicisation hygiene

- If political actors cite WealthLens selectively, publish a neutral usage note.
- Do not be the sole technical input to a party-political document.
- Keep funder influence structurally separated from scenario design.
- Allow personal policy views only outside the WealthLens brand.

---

## 19. AI/LLM disclosure protocol

This section exists because LLMs are pervasive in 2026 academic and policy workflows and pretending otherwise is the new HARKing. The protocol is the disclosure standard WealthLens commits to.

### 19.1 What is declared

| Category | Disclosure requirement |
|---|---|
| Code generation | Lines or modules drafted with LLM assistance are tagged in commit messages; significant LLM-drafted sections noted in `CONTRIBUTING.md` |
| Literature search | LLM-assisted literature discovery declared in paper acknowledgements |
| Data labelling / classification | LLM-assisted labels disclosed in methods section; sample of labels validated by human reviewer |
| Imputation | Any use of LLMs for imputation requires explicit methods-section description and sensitivity analysis without the LLM-imputed values |
| Documentation / report drafting | Disclosed in paper acknowledgements; reviewed by human author before publication |
| Naming, schema design | Disclosed in repository, not in research outputs |

### 19.2 What is prohibited

- LLMs setting behavioural priors or policy parameters.
- LLMs writing quoted policy positions or interpretations attributable to WealthLens.
- LLMs generating model outputs (revenue figures, distributional estimates) directly.
- LLMs settling methodological disputes between the team and external reviewers.
- LLMs drafting peer-review responses without explicit author review and disclosure.

### 19.3 What is encouraged

- LLMs as coding assistants under standard code review.
- LLMs as documentation drafters under standard editorial review.
- LLMs as schema-design and naming aids.
- LLMs as initial literature-search filters before human verification.
- LLM-generated test cases that humans curate.

### 19.4 Why this matters

WealthLens's credibility depends on the chain of reasoning being inspectable. LLMs are inspectable when used as tools (the human reviewer can check the output); they are not inspectable when used as oracles (the LLM's reasoning is opaque). The protocol separates these two uses.

A secondary reason: a project that uses LLMs heavily and does not say so will eventually have that fact discovered and used against it. Pre-disclosure is the only sustainable position.

### 19.5 Pre-registration and replication infrastructure

To make the disclosure credible:

- methodology pre-registration on OSF before first public outputs;
- pre-specified hypotheses and analysis plan;
- replication packages on Zenodo with DOIs;
- public commit history (no `git rebase --interactive` to hide LLM-assisted commits);
- annual audit of LLM use, published with the year's release notes.

---

## 20. Phased roadmap

### Phase 0: Scoping (weeks 1–2)

Deliverables: model charter (Gate 0); repository scaffolded; source register; legal-status baseline tracker; first assumption registry; UKDS / SRS / HMRC Datalab access plan; license declared.

**Exit:** a reviewer can understand the model's scope, data dependencies and non-claims.

### Phase 1: Measurement baseline + static simulator (weeks 3–14)

Deliverables: synthetic wealth-augmented FRS-compatible baseline; WAS reproduction from public tables; top-tail variants; macro reconciliation; annual and one-off wealth-tax modules; basic CGT/IHT/property stubs; first WTC replication attempt.

**Exit:** static baseline and one WTC scenario run reproducibly. Gates 1, 2, 3 partially passed.

### Phase 1.5: HVCTS rapid-response brief (months 3–4)

Deliverables: HVCTS as-proposed module; regional/nation clarification; property-value and liquidity assumptions; consultation-sensitive scenario note.

**Exit:** produce a defensible brief **before or near the 14 July 2026 consultation deadline** if data quality permits. If it cannot be done defensibly by that date, publish a methods note instead of a weak estimate. The brief is a Phase 1.5 deliverable, not a Phase 2 deliverable — it cuts into Phase 2 if needed.

### Phase 2: Policy atlas (months 4–7)

Deliverables: all seven policy families; revenue-equivalent packages; robust-frontier prototype; dashboard skeleton.

**Exit:** package comparisons run on the same scoreboard. Gate 5 passed.

### Phase 3: Behavioural wrapper (months 7–11)

Deliverables: behavioural modules; transferability scores; sensitivity atlas; static versus behavioural-adjusted outputs.

**Exit:** every behavioural result is traceable to assumptions and sources. Gate 6 passed.

### Phase 4: External review and v0.1 release (months 11–13)

Deliverables: independent reproduction (Gate 7); external review (Gate 8); dashboard safety (Gate 9); public launch.

**Exit:** v0.1 in the public domain with all gates passed.

### Phase 5: Dynamic simulator (months 13–20)

Deliverables: multi-year accumulation model; inheritance/gifting paths; pension decumulation; CGT realisation timing; property price capitalisation sensitivity.

**Exit:** model reproduces baseline dynamic trends before counterfactuals.

### Phase 6: ABM/RL extension (after month 20, optional)

Deliverables: housing-market ABM or avoidance-network ABM; robust policy-search experiment; separate methods paper.

**Exit:** extension answers a question the microsimulation cannot answer.

### Decision points

- **End of Phase 1:** if static baseline does not reproduce ONS or WTC benchmarks within tolerance, pause. Do not move to Phase 2.
- **End of Phase 1.5:** if HVCTS brief is not defensible by 14 July 2026, publish methods note instead. Project survives that outcome; publishing a weak number does not.
- **End of Phase 3:** if behavioural layer cannot survive transferability discipline, restrict v0.1 to mechanical-only outputs. Behavioural release waits until v0.2.
- **End of Phase 4:** if independent reproduction or external review fails, do not launch publicly. Iterate privately.
- **Month 30:** if theory of change has not been confirmed (see "What would confirm" / "What would falsify" criteria above), re-scope or wind down. Do not extend by default.

---

## 21. Risk register

Thirty risks, plus ten named failure modes. The risk register is adversarial (see §21.5 on pre-mortem methodology), not descriptive.

| # | Risk | Likelihood | Impact | Mitigation |
|---:|---|---|---|---|
| 1 | False precision | High | Very high | Intervals by default; no naked point estimates |
| 2 | Advocacy capture | Medium | Very high | Diversified funding; advisory group; publish counterarguments |
| 3 | Top-tail undercount | High | Very high | Multiple top-tail baselines; macro/rich-list sensitivity |
| 4 | WAS quality decline | High | High | Data-fusion design; OSR status disclosed |
| 5 | Behavioural overclaiming | High | High | Transferability scores; wrappers; static comparator |
| 6 | ABM/RL distraction | Medium | High | Microsimulation first; ABM/RL as separate extension |
| 7 | Data-access delay (UKDS / SRS / Datalab) | High | Medium | Synthetic/public baseline first; secure-data pathway in parallel |
| 8 | Policy-baseline drift | High | High | Fiscal-event update playbook; versioned baselines |
| 9 | Legal-rule errors | Medium | High | Unit tests; practitioner review; HMRC guidance checks |
| 10 | Public misuse of dashboard | High | Medium | Share links with assumptions; out-of-range warnings |
| 11 | Privacy failure | Low/medium | Very high | No named inferences; privacy review; aggregate outputs |
| 12 | Single-founder fragility | High | High | Documentation, maintainers, institutional host |
| 13 | Front-end toy problem | Medium | Medium | Same backend for dashboard and research outputs |
| 14 | Underpowered funding | High | High | Staged scope; avoid premature dashboard polish |
| 15 | Consultation-stage policy drift | High | Medium | Separate legal-status and modelling-status tags |
| 16 | Devolved-tax errors (Scotland/Wales/NI) | Medium | High | Devolved-tax advisory; nation-specific review (§4.4) |
| 17 | Reproduction failure at Gate 7 | Medium | High | Build reproducibility in from day 1; not retrofitted |
| 18 | External-review failure at Gate 8 | Medium | High | Pre-circulate methods early; cultivate reviewer relationships |
| 19 | HVCTS brief misses 14 July 2026 deadline | Medium | Medium | Phase 1.5 cuts into Phase 2; fallback is methods note |
| 20 | Comms misframing on launch | Medium | High | Press pack discipline; trained spokespeople; "does/does not say" sheet |
| 21 | LLM-disclosure non-compliance | Medium | Medium | Protocol in place from day 1; annual audit (§19.5) |
| 22 | Computational cost overrun | Medium | Medium | Scenario sub-sampling; surrogates in Phase 4+ |
| 23 | Depressing-result discipline failure | Medium | High | Pre-registration; reserved space for non-supported conclusions |
| 24 | Wildly-optimistic-result discipline failure | Medium | High | Methodology audit trigger (§18.5) |
| 25 | Backwards-compatibility failure | Medium | High | 3-year run-ability commitment; archived environments |
| 26 | Licence ambiguity | Low | Medium | Declared in Gate 0 (§17.5) |
| 27 | Funder concentration above 50% | Medium | High | Diversification target; COI page |
| 28 | OBR / HMT publishing equivalent analysis | Low/medium | High | Differentiation strategy (§16.3); occupy the open-source / public-dashboard / scenario-explorer space they cannot |
| 29 | Key external collaborator drops out | Medium | Medium | Don't depend on any single named advisor; redundancy in reviewer pool |
| 30 | Project identity decays after HVCTS consultation closes | Medium | High | Post-HVCTS identity plan (§27) |

### 21.1 Named failure modes

These are the failure modes that have ended comparable projects elsewhere:

- **False-precision trap.** Intervals are ugly, so the project hides them. Do not.
- **RL legitimacy trap.** Leading with AI novelty and losing economists. Do not.
- **Advocacy-capture trap.** Funders want the answer to be "wealth tax yes". Build structural resistance.
- **Engineering vanity trap.** Elegant stack, weak empirical question. Validate before polishing.
- **Founder-bus trap.** Only one person understands the model. Document aggressively.
- **Policy-drift trap.** Fiscal events change the baseline faster than the model updates. Version everything.
- **Wildly-optimistic-answer trap.** The model produces a flattering number for a preferred policy and the team publishes without auditing. Audit, then publish.
- **AI-disclosure trap.** Heavy LLM use, no disclosure, eventual exposure. Disclose proactively.
- **Devolved-credibility trap.** Treating UK as homogenous; getting one Scottish/Welsh/NI number wrong; losing credibility everywhere. Recruit devolved-tax advisors early.
- **Post-consultation-identity trap.** Project's identity is built around HVCTS; HVCTS closes; project drifts. Plan for it (§27).

### 21.5 Pre-mortem as standing methodology

The risk register is adversarial, not descriptive. At each major decision point (end of phases, before major releases), the team runs a structured pre-mortem:

1. Assume the project has failed catastrophically in 18 months.
2. Each person writes the most plausible story of how it failed.
3. Stories are pooled and clustered.
4. The top clusters become mitigation priorities for the next phase.
5. Pre-mortem findings are published with the next release notes (anonymised where appropriate).

This is more useful than a one-shot risk register because it forces the team to imagine failure rather than catalogue it. Risks discovered in pre-mortems join the register; the register is a living document.

---

## 22. v0.1 build specification

### 22.1 v0.1 must include

- model charter (Gate 0);
- source registry (`sources.yml`);
- assumption registry (`assumptions.yml`) with at least 50 entries;
- legal-status baseline tracker (`baselines.yml`);
- synthetic wealth-augmented FRS-compatible dataset;
- top-tail variants (at minimum the five in §2.3);
- ONS/NBS reconciliation under the current `macro_baseline_version`;
- annual wealth-tax module (Family A);
- one-off levy module (Family B);
- HVCTS module (Family E, England-only, both as-proposed and variants);
- basic CGT / IHT / property / enforcement stubs (Families C, D, E, F);
- devolution scenario stubs (Family G);
- uncertainty intervals for top-tail and valuation;
- static incidence outputs;
- WTC replication attempt (Gate 4);
- minimum viable demonstration chart (§13.2);
- methods note;
- HVCTS rapid-response brief (Phase 1.5 — if delivered by 14 July 2026);
- public dashboard skeleton with Gate 9 safety features;
- replication notebook executable on synthetic data without team intervention;
- AI/LLM disclosure document (§19);
- license, governance, COI pages (§17.4, §17.5).

### 22.2 v0.1 must not include

- public claims about named individuals' wealth;
- behavioural-adjusted results as defaults;
- RL/ABM policy recommendations;
- single-number revenue headlines without ranges;
- public dashboard before all gates 0–6 pass;
- claims that WealthLens recommends a policy;
- Scottish, Welsh or NI-specific revenue headlines without nation-specific review;
- behavioural results described as "validated";
- any LLM-generated revenue figure, policy interpretation or quoted position.

### 22.3 v0.1 acceptance test

A reviewer should be able to:

1. clone the repository on a fresh machine;
2. run a single `make` or `python -m wealthlens.replicate` command;
3. regenerate the headline figures of the methods note and the HVCTS brief from public/synthetic data;
4. inspect the `provenance_manifest()` of every published number and trace it to source;
5. modify one assumption-ID and see the downstream effect propagate through scoreboard and frontier.

If any of these fails, v0.1 is not ready.

---

## 23. Immediate plan: the next 90 days

### Days 1–30

1. Create repository, model charter, baseline-status tracker.
2. Declare license, governance and AI/LLM disclosure protocol.
3. Build source register and assumption registry (target 25 entries).
4. Apply for UKDS access to FRS, WAS and UKHLS.
5. Start ONS SRS and HMRC Datalab pathways if feasible.
6. Fork or scaffold around PolicyEngine-UK.
7. Reproduce one existing PolicyEngine reform end-to-end.
8. Reproduce ONS wealth-distribution charts from public tables.
9. Draft a two-page methods note: "What WealthLens measures and where uncertainty enters."
10. Contact PolicyEngine-UK, CenTax and one microsimulation academic for feedback.
11. Recruit at least one devolved-tax advisory contributor (§4.4).
12. Draft funder one-pager and identify three initial funding targets.

### Days 31–60

13. Build first synthetic wealth-augmented FRS-compatible baseline.
14. Add top-tail correction variants (start with Pareto + rich-list anchor; full five-variant set by day 90).
15. Reconcile to ONS National Balance Sheet 2025 figures.
16. Implement annual and one-off wealth-tax modules (Families A, B).
17. Implement current-law CGT/IHT/property baseline stubs (Families C, D, E).
18. Implement HVCTS as-proposed module (Family E sub-module).
19. Create first static incidence outputs by region and nation.
20. Write baseline-limitations note.
21. First pre-mortem exercise (§21.5).

### Days 61–90

22. Attempt WTC / Advani–Hughson–Tarrant replication (Gate 4 first pass).
23. Reconcile outputs to HMRC CGT/IHT receipts where public data permit.
24. Produce minimum viable demonstration chart (§13.2).
25. Draft HVCTS rapid-response brief for 14 July 2026 consultation deadline.
26. Convene first advisory call.
27. Run first independent-reproduction attempt with an outside collaborator on the synthetic baseline (preparation for Gate 7).
28. Publish Gate 0 documents (charter, license, AI disclosure, COI).
29. First `provenance_manifest()` working end-to-end on any one output.
30. Decide whether public prototype is ready or needs another private iteration before public methods-note release.

### 90-day benchmark

> A reproducible static baseline with top-tail variants, one WTC replication attempt, one HVCTS scenario, and one defensible rapid-response brief or methods note submitted to the consultation. If that does not work, pause. Do not move into behavioural modelling, dynamic modelling or RL.

---

## 24. What success looks like at 24 months

Neither prior blueprint specified concrete 24-month success metrics. Without them, success becomes whatever the project happens to produce.

| Success dimension | Concrete metric at month 24 |
|---|---|
| **Methodological credibility** | At least one peer-reviewed publication in *Fiscal Studies*, *International Journal of Microsimulation* or equivalent; replication package on Zenodo with DOI |
| **Replication** | Gate 7 passed by at least two independent external reproductions |
| **Adoption** | WealthLens cited in at least one OBR, IFS, CenTax or Treasury working paper or commentary |
| **Policy influence** | HVCTS rapid-response brief on GOV.UK consultation record (delivered within deadline) |
| **Open-source health** | At least three external contributors (commits not from founding team); at least one external fork running independently |
| **Funding** | At least three independent funders; no single funder above 50% |
| **Governance** | Active advisory group meeting at least twice a year; annual methodology audit published |
| **Public uptake** | Dashboard usage from at least 50 distinct domains (think tanks, journalists, academics, civil service); not just visitor counts |
| **Devolved coverage** | Nation-specific outputs reviewed by at least one Scottish, one Welsh and one NI specialist (§4.4) |
| **Reproducibility** | Every v0.x release regenerable from public code and synthetic/public data |
| **Communication discipline** | No public WealthLens output containing a naked single-number headline (audited annually) |
| **Theory of change** | At least two of the four "what would confirm" criteria triggered (see theory-of-change section) |

If by month 24 fewer than half of these are met, the project should be re-scoped rather than extended. Specifically: if methodological credibility, replication and any of {adoption, policy influence} are met, the project is on track. If only governance and funding are met, the project has become a healthy organisation without research impact.

---

## 25. Year-1 project killers

The risk register (§21) is comprehensive but generic. This section is specific: things that, if they happen in year 1, would end the project. Each has a named pre-emptive mitigation.

| Killer | Likelihood (year 1) | Pre-emptive mitigation |
|---|---|---|
| **HMRC Datalab access denied or indefinitely delayed** | Medium | Synthetic baseline path (§7.4) is sufficient for v0.1; HMRC microdata is Phase 5+ requirement, not v0.1 |
| **PolicyEngine-UK changes licence or upstream architecture** | Low | Fork early; maintain compatibility layer; AGPL alignment (§17.5) keeps incentives aligned |
| **Lead researcher leaves before Phase 4** | Medium | Documentation discipline from day 1; second maintainer recruited by month 6 |
| **OBR or HMT publishes parallel public wealth-tax simulator** | Low/medium | Highly unlikely given institutional roles (§16.3); if it happens, WealthLens narrows to the open-source / public-dashboard niche they cannot occupy |
| **Funder withdraws after month 6 commitment** | Medium | Three-funder diversification target from start; cost envelope structured for graceful descaling, not graceful expansion |
| **Critical replication failure (Gate 4)** | Medium | Build replication into Phase 1 not Phase 4; treat Gate 4 failure as the project's defining test, not an embarrassment |
| **Public misattribution as advocacy organisation** | Medium/high | Press discipline (§18.2); separate personal views from WealthLens brand (§18.7); structural neutrality (§1.1) |
| **HVCTS consultation closes early or is withdrawn** | Low | The HVCTS brief is one of seven publishable outputs; project survives its loss but the political-economy window is harder to recover |
| **Devolved-tax credibility incident in first 6 months** | Medium | Devolved-tax advisor in place before any nation-specific output; nation-specific publication moratorium until reviewed |
| **First public-dashboard release shipped with a single-number headline** | Medium | Dashboard safety gate (Gate 9); make this a CI test, not a design preference |
| **LLM use disclosed retroactively after a third-party discovers it** | Low | Protocol from day 1 (§19); annual audit; commits tagged from start |
| **Top-tail estimate diverges dramatically from a high-profile published estimate without explanation** | Medium | Top-tail variants section (§2.3) is the standing answer; show the range, name the method |

The pattern: most year-1 killers are governance and discipline failures, not technical ones. The technical risks are well-understood (Gate 4 might fail, data access might be slow); the unrecoverable risks are reputational (advocacy capture, devolved error, dashboard misuse).

---

## 26. Policy levers no one is modelling

Neither WealthLens v4 nor any of its UK comparators models the policy space comprehensively. This section maps the gaps. WealthLens is not committing to model all of these in v0.1, but it is committing to *name* them — because a policy lab that quietly excludes options is doing the same thing as a campaign with a preferred answer.

| Gap | What it is | Why it matters | WealthLens treatment |
|---|---|---|---|
| **Accessions tax** | Tax on cumulative lifetime receipts of the recipient, not transfers from the donor | Breaks the "wealthy dynasty" dynamic; widely discussed academically; no UK simulator models it | Modelled as Family D variant from Phase 2; flagged as exploratory |
| **Mark-to-market for top-tail public holdings** | Annual taxation of unrealised gains on listed public-market wealth above a high threshold (Wyden-style) | Closes the largest single avoidance margin (deferral) for the top tail; politically live in the US | Modelled as Family C variant from Phase 3 |
| **Deemed disposal at retirement** | Treating retirement as a CGT realisation event | Addresses retirement-as-shelter behaviour; modest revenue but useful sensitivity | Phase 3 sensitivity scenario |
| **Exit charges for emigration** | Treating emigration as a CGT realisation event (variant of current trust exit charge) | Direct mitigation for migration-as-avoidance; well-evidenced in other jurisdictions | Modelled as Family C variant from Phase 2 |
| **Gift tax overhaul** | Replacing the seven-year PET system with a recipient-based gift tax | Closes the largest single transmission channel for dynastic wealth | Phase 3 family-D variant |
| **Land Value Tax** | Recurrent tax on unimproved land value | Long-discussed; deep methodological literature; would require land-data integration WealthLens does not yet have | Named but not in v0.1 scope; flag for v1.0+ |
| **Lifetime capital receipts tax (Meade-Atkinson variant)** | A tax on the sum of capital receipts received over a lifetime | Theoretically attractive; historically advocated but not implemented | Named; not in v0.1 scope |
| **Wealth-conditioned benefit recovery** | Means-testing benefits on net worth rather than income | Affects the bottom-end-fragility population materially; politically live | Phase 4+ scenario |
| **Information-only reforms** | Wealth-reporting requirements without rate changes (e.g. mandatory annual asset disclosure above £X) | The lowest-cost wealth-policy reform; quantifying its effect on observability and behaviour is itself useful | Family F variant from Phase 2 |
| **Sectoral wealth taxes** | Taxes on specific asset classes (e.g. residential property held by overseas owners; financial wealth above threshold) | Politically more tractable than comprehensive wealth taxes; under-modelled | Family E / F variants from Phase 2 |

The gap-map is part of the project's structural neutrality discipline. A project that compares only the policies currently on the table is implicitly endorsing the table.

---

## 27. The post-HVCTS identity problem

Both v4 blueprints anchor WealthLens to the May 2026 HVCTS consultation. That window closes on 14 July 2026 and, regardless of what HMG decides, will close as a live debate by April 2028 when (if) the policy comes into force. WealthLens's identity must not depend on it.

### 27.1 The risk

If WealthLens's public identity becomes "the HVCTS modeller", the project has a 14-month relevance window. After HVCTS is implemented, modified or dropped, the project is in trouble unless its identity has been built around something more durable.

### 27.2 The durable identity

WealthLens's standing identity is **the UK wealth-policy comparison platform under uncertainty**, not "the simulator for the current consultation". HVCTS is one of many policies the platform compares; the platform's value is in *comparison*, not in any single policy.

### 27.3 What this means operationally

- **The Phase 1.5 HVCTS brief is a use case, not the identity.** Press communications around it should frame WealthLens as "an open wealth-policy platform that has, among other things, produced a rapid-response brief on HVCTS", not "WealthLens's HVCTS analysis".
- **The dashboard's default landing page does not lead with HVCTS.** It leads with package comparison.
- **The roadmap does not have a Phase 7 "post-HVCTS pivot".** That would imply the project's centre of gravity was about to move. The roadmap continues into dynamic and ABM/RL extensions regardless of HVCTS's fate.
- **Public outputs are paginated by policy family, not by single-policy story.** Reform-first, high-threshold, one-off levy, property-heavy, anti-avoidance, current-trajectory-plus, revenue-equivalent, devolution-comparison: HVCTS appears across multiple of these but is not the headline of any.

### 27.4 If HVCTS is implemented

WealthLens models its actual incidence and uncertainty, continues to model variants and continues to compare it against alternatives. Implementation does not end the modelling question; it changes the baseline.

### 27.5 If HVCTS is modified during consultation

WealthLens updates the module; the consultation-sensitive baseline tag (§3.1) was designed for exactly this case. The "modelled as proposed" and "modelled as modified" become two named scenarios.

### 27.6 If HVCTS is withdrawn

WealthLens models it as a withdrawn-policy counterfactual ("what would have happened if HVCTS had been implemented?") and continues to publish analysis on the alternative property-tax-reform paths. The political-economy lesson — that proposed property-tax reform is fragile — itself becomes a publishable observation.

In all three cases, the project's identity survives the policy outcome. That is the test of whether the identity is durable.

---

## 28. Editorial bottom line

The strongest unified version is stricter, not broader:

> Build a credible open machine for comparing wealth-focused UK tax packages under uncertainty. Do not start by proving that a wealth tax is right. Start by showing when it is, when it is not, and what beats it.

The near-term success criterion is concrete:

> In 90 days, WealthLens should have a reproducible static wealth-policy baseline with top-tail variants, a documented ONS/NBS reconciliation, one Wealth Tax Commission replication attempt and one HVCTS static scenario or methods note. If that foundation is weak, nothing more advanced should be built yet.

The mid-term success criterion is publication and replication:

> By month 24, at least one peer-reviewed methods paper, Gates 7 and 8 passed, three independent funders, and at least one citation in the OBR/IFS/CenTax/Treasury ecosystem. If those are not met, the project's theory of change has not been confirmed and the project should be re-scoped or wound down rather than extended.

The long-run contribution is not a dashboard. The contribution is a public evidence standard for UK wealth-policy debate.

---

## 29. Glossary

This glossary defines terms that recur throughout the document. It exists because the wealth-policy and microsimulation literatures use overlapping but inconsistent terminology, and external reviewers should not have to look up acronyms in five places.

**ABDR / Business Asset Disposal Relief** — UK CGT relief on disposals of qualifying business assets; 18% rate from 6 April 2026.

**ABM** — Agent-based model. Simulation of policy effects through interactions between heterogeneous agents.

**Accessions tax** — Tax on cumulative lifetime receipts of gifts and inheritances received by an individual, computed at the recipient rather than the donor.

**Advani–Hughson–Tarrant (2021)** — Wealth Tax Commission paper providing the most-cited UK annual-wealth-tax revenue estimates; central benchmark for Gate 4.

**AGPL-3.0** — Affero General Public License v3; the open-source licence used by PolicyEngine-UK and proposed for WealthLens code (§17.5).

**Announced baseline** — A policy that has been formally announced but is not yet in force. Distinguished from current law and from hypothetical scenarios. Tagged in §3.1.

**APR / BPR** — Agricultural Property Relief / Business Property Relief; UK IHT reliefs. £2.5m cap on 100% relief from 6 April 2026.

**Assumption registry** — Machine-readable file (`assumptions.yml`) listing every behavioural, valuation, top-tail and compliance assumption with source, range and transferability score (§7.6).

**Bayesian Pareto** — A Bayesian approach to fitting the Pareto tail of the wealth distribution, with priors on the tail index and propagation of posterior uncertainty.

**Behavioural wrapper** — A module sitting on top of the static simulator that adjusts results for behavioural response, in a form that can be removed or replaced without altering the static engine (§11.1).

**CenTax** — UK research centre on tax and policy, focused on top-end taxation. Adjacent to WealthLens; not a competitor.

**CGT** — Capital Gains Tax. UK rates from 6 April 2026: 18%/24% for individuals, 24% for trustees, 18% for BADR/IR gains.

**Charter / model charter** — Published statement of what WealthLens models, claims and does not claim. Gate 0 deliverable.

**Consultation-sensitive baseline** — A policy whose design parameters are still moving through public consultation; modelled with explicit version-tagging for parameter changes (§3.1).

**Current law** — A policy in force on the modelling date. Tagged in §3.1.

**Datalab (HMRC Datalab)** — Restricted-access HMRC microdata environment.

**Death uplift** — UK CGT treatment whereby unrealised gains are not taxed at death; recipients inherit assets at market value, eliminating the unrealised gain.

**Deemed disposal** — Treating a non-sale event (retirement, emigration) as if it were a CGT realisation.

**DINA / Distributional National Accounts** — Methodology developed by WID.world for distributing national-accounts totals to individuals/households; reconciles micro and macro distributional measures.

**DSGE** — Dynamic Stochastic General Equilibrium. Macroeconomic modelling framework; not WealthLens's core engine.

**Enacted future law** — Legislation passed but with future commencement date. Tagged in §3.1.

**EFO** — Economic and Fiscal Outlook, OBR's twice-yearly forecast publication.

**Exit charge** — Tax triggered by emigration of an individual or migration of assets out of UK tax jurisdiction.

**Family A–G** — WealthLens policy families: A annual wealth tax, B one-off levy, C CGT reform, D IHT/transfer reform, E property-tax reform, F enforcement reform, G devolution-asymmetric reform (§9).

**FIG regime** — Foreign Income and Gains regime; replaced non-dom remittance basis from 6 April 2025.

**Fiscal event** — UK Budget or Spring Statement; triggers a `fiscal_event_anchor` version bump.

**Fragile frontier** — Set of policies that look attractive only under narrow assumptions (§10.2).

**FRS** — Family Resources Survey; DWP-published, UK-wide including NI; the FRS-2024-25 financial year is the current vintage.

**Gate 0–9** — WealthLens validation gates (§14). Each must pass before the next phase opens.

**Generalised Pareto distribution** — Statistical distribution used for fitting the upper tail of wealth.

**HANK** — Heterogeneous Agent New Keynesian. Macroeconomic modelling framework.

**HARKing** — Hypothesising After the Results are Known. Methodological vice in empirical research.

**Hidden-wealth sensitivity** — A baseline variant that adds stress-test assumptions for offshore, trust and private-business wealth not visible in surveys (§2.3).

**HMCTS / HMG / HMT / HMRC / MHCLG** — Standard UK government abbreviations: Courts and Tribunals Service / His Majesty's Government / Treasury / Revenue and Customs / Ministry of Housing, Communities and Local Government.

**HVCTS** — High Value Council Tax Surcharge. Consultation published 19 May 2026; closes 14 July 2026; planned for April 2028 in England. OBR forecast ~£0.4bn in 2029–30.

**Hypothetical** — A policy not announced, enacted or in force; modelled as a counterfactual. Tagged in §3.1.

**IFS** — Institute for Fiscal Studies. UK's leading tax-policy think tank.

**IHT** — Inheritance Tax. UK tax on estates above nil-rate-band thresholds, with reliefs.

**Independent reproduction** — Reproduction of headline figures by someone outside the project team, on a clean machine, using public/synthetic data. Gate 7 (§14).

**JRCT / JRF** — Joseph Rowntree Charitable Trust / Joseph Rowntree Foundation. UK funders with inequality focus.

**LBTT / LTT / SDLT** — Land and Buildings Transaction Tax (Scotland) / Land Transaction Tax (Wales) / Stamp Duty Land Tax (England, NI).

**Liquidity household typology** — WealthLens classification of households by asset/income/liquidity composition (§11.4).

**LLM** — Large Language Model. Disclosure protocol in §19.

**Mark-to-market** — Annual taxation of unrealised gains, typically on listed public-market holdings; "Wyden-style" in US debate.

**Methods note** — Public document describing methodology, intended to precede any policy-result publication.

**MVD** — Minimum Viable Demonstration. The single chart that proves the simulator works (§13.2).

**NAO** — National Audit Office. Publishes oversight reports including the 2025 wealthy-individuals report referenced for §3.6.

**Nation** — One of England, Scotland, Wales, Northern Ireland. First-class field in WealthLens schema (§4.1).

**NBS** — National Balance Sheet. ONS publication; current vintage is the final 2025 release with household net worth £10.8tn for 2024.

**Non-dom** — Pre-April-2025 UK regime for non-UK-domiciled residents (remittance basis). Replaced by FIG regime.

**OBR** — Office for Budget Responsibility. UK's independent fiscal forecaster.

**Open-lab framing** — Project framing as comparison platform, not advocacy tool (§1.1).

**OSF** — Open Science Framework; used here for methodology pre-registration (§19.5).

**OSR** — Office for Statistics Regulation. Suspended WAS accreditation in June 2025.

**Pareto correction** — Fitting a Pareto distribution to the upper tail of the wealth distribution to address survey undercoverage.

**PolicyEngine-UK** — Open-source UK tax-benefit microsimulation; AGPL-3.0; FRS-based. Adjacent infrastructure WealthLens builds on.

**Policy family** — One of the seven categories of reform WealthLens compares (§9).

**Pre-mortem** — Adversarial risk-discovery method that asks "imagine the project has failed; how?" (§21.5).

**Provenance manifest** — Audit-trail object emitted with every WealthLens output, listing every assumption-ID and version tag the result depends on (§13.4).

**PSC** — People with Significant Control; UK beneficial-ownership register at Companies House.

**Quarto** — Open-source publishing system used for reproducible reports.

**Replication package** — Code and synthetic data bundle that allows external reproduction of published results.

**Revenue-equivalent comparison** — Comparing packages that target the same revenue band, to isolate who-pays-how questions from how-much questions (§9).

**RL** — Reinforcement Learning. Used for policy-search experiments in Phase 6 only.

**Robust Pareto frontier** — Set of policies that remain non-dominated across the stated uncertainty space (§10.2, §10.4).

**Robustness, not accuracy** — WealthLens's claim about behavioural results. Behavioural validation is impossible; robustness is verifiable (§11.6).

**Rules-as-code** — Tax law represented as executable, testable, version-controlled code (§8.2).

**Saez–Zucman / Summers–Sarin** — US debate over annual-wealth-tax revenue (bullish vs sceptical priors). Useful as a transferability case study (§5.4).

**Scoreboard** — Multi-objective dashboard of policy effects with uncertainty intervals (§10.1).

**SRS / ONS SRS** — ONS Secure Research Service; restricted microdata environment.

**Static-first** — Mechanical incidence modelled before behavioural response (§8.2, §8.3).

**Stress-test only** — Transferability tier for behavioural priors too weak to use as default but useful for exploring sensitivity (§11.2).

**Surrogate model** — Lightweight model (typically Gaussian process or neural network) trained on the full simulator's outputs for interactive dashboard use.

**Synthetic dataset** — Statistically representative dataset constructed without reproducing real individuals; usable in public outputs.

**Tax gap** — Difference between theoretical tax liabilities and actual tax collected. HMRC 2023–24 estimate: 5.3%, £46.8bn.

**Transferability score** — Tag attached to every behavioural prior indicating how well it transfers from the source evidence to the UK 2026 wealth-tax context (§11.2).

**UKDS** — UK Data Service. Primary microdata access pathway for FRS, WAS, UKHLS.

**UKHLS / Understanding Society** — UK Household Longitudinal Study.

**UKMOD** — UK tax-benefit microsimulation; academic-restricted; CeMPA at University of Essex.

**VOA** — Valuation Office Agency; HMRC body responsible for property valuations including HVCTS scope.

**WAS** — Wealth and Assets Survey; ONS; covers Great Britain; current vintage covers April 2020 to March 2022; accreditation suspended June 2025.

**Wealth Tax Commission** — UK academic commission (2020) that produced influential one-off-levy estimates referenced in §5.5.

**WID.world** — World Inequality Database; Paris-based; produces long-run distributional series using DINA methodology.

**WTC** — Wealth Tax Commission (above).

---

## 30. Source anchors and bibliography

### Live-policy primary sources (footnoted in main text)

[^hvcts-gov]: GOV.UK, *High Value Council Tax Surcharge*, consultation published 19 May 2026. https://www.gov.uk/government/consultations/high-value-council-tax-surcharge/high-value-council-tax-surcharge

[^hvcts-obr]: Office for Budget Responsibility, *Economic and fiscal outlook – November 2025*, section on High Value Council Tax Surcharge. https://obr.uk/efo/economic-and-fiscal-outlook-november-2025/

[^ons-nbs]: Office for National Statistics, *National balance sheet estimates for the UK: 2025*. https://www.ons.gov.uk/economy/nationalaccounts/uksectoraccounts/bulletins/nationalbalancesheet/2025

[^ons-wealth]: Office for National Statistics, *Household total wealth in Great Britain: April 2020 to March 2022*. https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/april2020tomarch2022

[^cgt]: GOV.UK, *Capital Gains Tax rates and allowances*. https://www.gov.uk/guidance/capital-gains-tax-rates-and-allowances

[^aprbpr]: GOV.UK, *Changes to agricultural property relief and business property relief*. https://www.gov.uk/government/publications/changes-to-agricultural-property-relief-and-business-property-relief

[^pensions-iht]: GOV.UK, *Technical note: Inheritance Tax on pensions*. https://www.gov.uk/government/publications/inheritance-tax-on-pensions-technical-note/technical-note-inheritance-tax-on-pensions

[^osr-was]: Office for Statistics Regulation, *OSR suspend accreditation of Wealth and Assets Survey*, 13 June 2025. https://osr.statisticsauthority.gov.uk/news/osr-suspend-accreditation-of-wealth-and-assets-survey/

[^tax-gap]: HMRC, *Measuring tax gaps 2025 edition: tax gaps summary*. https://www.gov.uk/government/statistics/measuring-tax-gaps/1-tax-gaps-summary

[^nao-wealthy]: National Audit Office, *Collecting the right tax from wealthy individuals*, 16 May 2025. https://www.nao.org.uk/reports/collecting-the-right-tax-from-wealthy-individuals/

[^frs]: Department for Work and Pensions, *Family Resources Survey: financial year 2024 to 2025*. https://www.gov.uk/government/statistics/family-resources-survey-financial-year-2024-to-2025/family-resources-survey-financial-year-2024-to-2025

[^ons-tax-benefits]: Office for National Statistics, *Effects of taxes and benefits on UK household income: financial year ending 2024*. https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/theeffectsoftaxesandbenefitsonhouseholdincome/2024

[^wtc]: Advani, A., Chamberlain, E., Summers, A., et al. (2020). *A Wealth Tax for the UK*. Wealth Tax Commission Final Report. https://www.wealthandpolicy.com/wp/WTCFinalReport.pdf

### UK wealth-tax academic and think-tank literature

- Advani, A., Hughson, H., & Tarrant, H. (2021). *Revenue and distributional modelling for a UK wealth tax*. Wealth Tax Commission Evidence Paper.
- Advani, A., & Summers, A. (2020). *Capital gains and UK inequality*. CAGE Working Paper.
- Atkinson, A. B. (2015). *Inequality: What Can Be Done?*. Harvard University Press.
- Boadway, R., Chamberlain, E., & Emmerson, C. (2010). *Taxation of wealth and wealth transfers*. In Dimensions of Tax Design: The Mirrlees Review.
- CenTax. (ongoing). Working papers on top-end UK taxation. https://centax.org.uk
- Chamberlain, E. (2021). *Defining the tax base for a wealth tax*. Wealth Tax Commission Background Paper.
- Daly, S., & Loutzenhiser, G. (2020). *Valuation*. Wealth Tax Commission Background Paper.
- Institute for Fiscal Studies. *Tax by Design* (Mirrlees Review). Oxford University Press.
- Loutzenhiser, G., & Mann, E. (2021). *Liquidity issues: solutions for the asset rich, cash poor*. Wealth Tax Commission Background Paper.
- Resolution Foundation. *Annual wealth distribution publications and inequality reports*.
- Tax Justice UK. *Wealth-tax advocacy and analysis*. https://www.taxjustice.uk

### International wealth-tax and behavioural literature

- Brülhart, M., Gruber, J., Krapf, M., & Schmidheiny, K. (2022). *Behavioral responses to wealth taxes: evidence from Switzerland*. American Economic Journal: Economic Policy.
- Jakobsen, K., Jakobsen, K., Kleven, H., & Zucman, G. (2020). *Wealth taxation and wealth accumulation: theory and evidence from Denmark*. Quarterly Journal of Economics.
- OECD (2018). *The Role and Design of Net Wealth Taxes in the OECD*. OECD Tax Policy Studies.
- Piketty, T. (2014). *Capital in the Twenty-First Century*. Harvard University Press.
- Piketty, T., Saez, E., & Zucman, G. (2018). *Distributional National Accounts: methods and estimates for the United States*. Quarterly Journal of Economics.
- Ring, M. (2020). *Wealth taxation and household saving: evidence from assessment discontinuities in Norway*. Mimeo.
- Saez, E., & Zucman, G. (2019). *The Triumph of Injustice*. W.W. Norton.
- Saez, E., & Zucman, G. (2019). *Progressive wealth taxation*. Brookings Papers on Economic Activity.
- Sarin, N., & Summers, L. (2019). *A "wealth tax" presents a revenue estimation puzzle*. Washington Post / Brookings.
- Seim, D. (2017). *Behavioral responses to wealth taxes: evidence from Sweden*. American Economic Journal: Economic Policy.
- Zoutman, F. T. (2018). *The elasticity of taxable wealth: evidence from the Netherlands*. Mimeo.

### Microsimulation and data infrastructure

- Bourguignon, F., & Spadaro, A. (2006). *Microsimulation as a tool for evaluating redistribution policies*. Journal of Economic Inequality.
- CeMPA, University of Essex. *UKMOD documentation and country reports*. https://www.microsimulation.ac.uk/ukmod/
- ONS. *Wealth and Assets Survey methodology and quality reports*.
- PolicyEngine. *PolicyEngine-UK documentation and changelog*. https://policyengine.org/uk
- Sutherland, H., & Figari, F. (2013). *EUROMOD: the European Union tax-benefit microsimulation model*. International Journal of Microsimulation.
- UK Data Service. *Access pathways for FRS, WAS, UKHLS*. https://www.ukdataservice.ac.uk

### Macro, ABM and RL

- Axtell, R., & Farmer, J. D. (2025). *Agent-based modeling in economics and finance: past, present, and future*. Journal of Economic Literature.
- Kaplan, G., Moll, B., & Violante, G. (2018). *Monetary policy according to HANK*. American Economic Review.
- Zheng, S., Trott, A., Srinivasa, S., et al. (2022). *The AI Economist: optimal economic policy design via two-level deep reinforcement learning*. Science Advances.

### Source documents synthesised

- `WealthLens_UK_Unified_Blueprint_v4.md` (operational v4): theory of change, AI/LLM disclosure, glossary, computational cost, OBR positioning, comparator simulators, independent-reproduction gate, devolved-expertise disclaimer, £0.4bn↔£80bn anchor, symmetric optimism discipline, LLMs as dev tooling, 30-item risk register, decision points.
- `WealthLens_UK_Final_Unified_Blueprint_v4.md` (editorial v4): baseline-status matrix, repository layout, v0.1 must-include / must-not-include, model-charter and dashboard-safety gates, Bayesian second-pass top-tail spec, machine-readable assumption-registry schema, announced-vs-consultation-sensitive distinction.

### Notes on this fifth-pass synthesis

This document is a fifth-pass unification of two parallel fourth-pass blueprints. Earlier passes (v1–v3, plus two parallel v4s) are not cited here because they have been fully superseded; their material is either incorporated above or has been deliberately cut for the reasons given in §0 ("What this version cuts or weakens"). Anyone who wants to audit the synthesis trail should compare this document against the two v4 source files named in the previous block.

The work has been done with LLM assistance for synthesis, drafting and structural organisation. All policy facts cited above have been derived from the live-policy primary sources listed; the LLM has not been used as authority on any tax-policy claim. This is the disclosure standard this document recommends WealthLens itself adopt (§19).

---

*End of WealthLens UK Unified Research Blueprint v5.*

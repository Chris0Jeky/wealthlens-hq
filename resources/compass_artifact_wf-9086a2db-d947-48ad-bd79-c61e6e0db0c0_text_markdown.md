# WealthLens-Sim: Bridging the v5 Blueprint with Chris0Jeky/wealthlens-hq — A 24-Month Strategic, Technical and Institutional Plan

## TL;DR
- **Fork-and-extend PolicyEngine-UK** (which already contains a parametric `non_primary_residence_wealth_tax.yaml` scaffold and ships an "enhanced FRS" with WAS/LCFS/SPI imputations reweighted by gradient descent against a loss function that, per PolicyEngine's Max Ghenis writing in 2023, "has 2,664 elements") rather than re-implementing rules-as-code. Adopt PolicyEngine-Core (a fork of OpenFisca-Core) as the simulation engine, license the WealthLens-Sim core under AGPL-3.0 to remain compatible, and keep the existing Vue 3 / D3 / FastAPI dashboard as the public-facing layer connected via a new `wealthlens.replicate` Python package.
- **The £0.4bn ↔ £80bn revenue range is the project's single most defensible public anchor.** HMRC/OBR have certified the HVCTS at "around £430 million of revenue per year from 2028/29" (GOV.UK, *High Value Council Tax Surcharge*), while Advani–Hughson–Tarrant (2021, *Fiscal Studies*) score an annual 1% wealth tax above £2m at >£80bn after non-compliance and admin costs. The credible MVP is a static, top-tail-corrected (Pareto/GPD + rich-list anchor + ONS NBS reconciliation) microsimulator covering policy families A–G, shipped before the **14 July 2026 HVCTS consultation deadline**.
- **Funding and institutional path**: target the Nuffield Strategic Fund (£1–3m, with a £150m/5-year commitment per the Nuffield Foundation Strategic Review announced 24 July 2025: "The Foundation will commit £30 million annually over the next five years to generate rigorous evidence on, and shape solutions to, intersecting problems impacting UK society"); co-apply with **CenTax (Warwick/LSE, Advani & Summers)** as institutional host; JRF unrestricted grants ("In 2025 we want to make more unrestricted grants, putting an additional £50 million to £100 million behind our mission-focused work over the coming 5-10 years", per jrf.org.uk/funding) as second pillar; abrdn Financial Fairness Trust (already funding UKMOD) as third. Treat the IFS Green Budget 2025's explicit opposition to a new annual wealth tax as a constraint — WealthLens must frame itself as a *measurement, transparency and decomposition* platform, not an advocate.

---

## Key Findings

1. **The repository's current asset base is reusable, not throw-away.** The 10 existing data pipelines (WID 1820–2024, ONS WAS deciles, HMRC CGT, ONS GDHI, ONS housing affordability, productivity-pay, tax composition, BoE, child poverty, generational wealth) become the *macro-reconciliation and source registry* layer for the simulator. The Vue 3 + Pinia + D3 dashboard becomes the simulator's UI; FastAPI becomes the scenario-run API. The 874 passing tests provide a regression backstop. Nothing in the current repo conflicts with the blueprint; the gap is a Python rules engine, a synthetic FRS+WAS dataset, top-tail reconstruction, and provenance plumbing.

2. **PolicyEngine-UK already contains a wealth-tax scaffold.** The file `policyengine_uk/parameters/gov/contrib/cec/non_primary_residence_wealth_tax.yaml` defines a marginal-rate wealth tax with `rate` and `threshold` parameters (defaults zero — i.e. a no-op baseline waiting to be activated). PolicyEngine has also publicly scored Autumn Budget 2025's HVCTS, salary-sacrifice pension caps, and (with the UBI Center) a land-value-tax-funded UBI. This means WealthLens-Sim should not build a tax engine from scratch — it should contribute *new reform modules* and a *top-tail-corrected dataset* to the existing engine.

3. **The "enhanced FRS" is the right baseline.** PolicyEngine-UK ships `enhanced_frs_2022_23.h5` on Hugging Face — FRS fused with Wealth and Assets Survey (WAS), Living Costs and Food Survey (LCFS), Survey of Personal Incomes (SPI), reweighted by gradient descent. WealthLens-Sim's additional contribution is the *Pareto/GPD top-tail correction*, the *hidden-wealth sensitivity wrappers*, and the *devolution-asymmetric reweighting*.

4. **AGPL-3.0 is the correct licence and is non-negotiable downstream.** PolicyEngine-UK and PolicyEngine-Core are AGPL-3.0. A derivative simulator that imports PolicyEngine-Core or extends PolicyEngine-UK and exposes it over a network must itself be AGPL-3.0 (Section 13). This is *desirable* for WealthLens (it protects against private capture) but means the existing repo's MIT licence must be split: the simulator core (`packages/wealthlens-sim/`) becomes AGPL-3.0; the dashboard frontend and pre-existing chart pipelines can remain MIT; visualisations remain CC-BY 4.0.

5. **HVCTS rapid-response window is tight but tractable.** Consultation closes 14 July 2026; with current date 21 May 2026 that leaves ~8 weeks. A defensible HVCTS brief is *achievable* using public Land Registry Price Paid + ONS HPI + WAS round 8 + the Treasury/VOA's own figure ("The HVCTS is estimated to raise around £430 million of revenue per year from 2028/29 to support funding for local government services" — GOV.UK) as anchors. It does not require HMRC Datalab access. The deliverable should be a methods note + 4-band liquidity-constraint analysis + ~30 distributional charts + provenance manifest — not a counter-forecast.

6. **CenTax (Advani/Summers, launched Nov 2024) is the natural institutional host.** CenTax explicitly aims to become "the UK's leading centre for research excellence in UK wealth tax" (per its Warwick-published constitution). They were briefed by James Murray MP (Exchequer Secretary) at launch. Their existing data access (HMRC Datalab, IHT records), advisory weight, and joint Warwick/LSE in-kind support are exactly what WealthLens needs and cannot easily replicate. CenTax does not maintain an open-source simulator — there is a clear complementarity, not a competition.

7. **IFS Green Budget 2025 explicitly opposed an annual wealth tax.** In Chapter 4 "Options for tax increases" (Adam, Delestre, Miller, October 2025) Key Finding 10 states: "We caution against introducing an annual wealth tax, which would face huge practical challenges... If the Chancellor wants to raise more from the better-off, a better approach would be to fix existing wealth-related taxes." This *constrains* WealthLens's positioning. The project must be a *transparency and decomposition* infrastructure, not a wealth-tax advocate, or it loses IFS-adjacent credibility.

8. **Resolution Foundation has a 2025 wealth flagship.** "Before the fall" (Broome and Kanabar, 8 October 2025, DOI 10.63492/pcv793) reports household wealth reaching 7.5× GDP and documents that "It would now take 52 years' worth of typical earnings – £1.3 million in total – to move from the middle to the top of the wealth distribution." This is the natural distribution-partner output and a model for WealthLens's own public narrative.

9. **Capital taxes are growing fast and politically salient.** Per the Autumn Budget 2025 document, CGT "will more than double from £13.7 billion at the start of this Parliament to £30 billion in 2030/31"; IHT "raised £8.3 billion a year at the start of this Parliament; this is expected to rise to £14.5 billion in 2030/31." Families C (CGT reform) and D (IHT/transfer reform) are therefore the highest-revenue-relevance modules after HVCTS.

---

## Details

### Deliverable 1 — Executive Synthesis

The Chris0Jeky/wealthlens-hq repository is a credible *publication platform* but is not yet a *policy simulator*. The blueprint v5's WealthLens-Sim v0.1 specification can be reached in 24 months on a £250k–£500k envelope by following a "fork-and-contribute" path on top of PolicyEngine-UK rather than building from scratch. The path has three phases:

| Phase | Months | Goal | Output |
|---|---|---|---|
| 1: Replicate | M1–M3 | Stand up `wealthlens-sim` as a thin wrapper around PolicyEngine-UK; reproduce WTC 2020 one-off levy scenarios within ±5%; ship HVCTS rapid-response brief by 14 July 2026 | Methods note, brief, sources.yml v1 |
| 1.5: Top-tail | M4–M9 | Add Pareto/GPD top-tail correction with rich-list anchors and ONS NBS macro reconciliation; publish replication package with DOI on Zenodo | v0.1 simulator, replication package |
| 2: Policy families | M10–M18 | Implement seven policy families A (annual wealth tax), B (one-off levy), C (CGT reform), D (IHT/transfer), E (property), F (enforcement), G (devolution-asymmetric) | v0.2 simulator, public interactive dashboard with provenance tooltips |
| 3: Behavioural wrappers | M19–M24 | Static-with-behavioural-wrappers using prior intervals from Advani–Tarrant (2021), Brülhart et al. (2022), Jakobsen et al. (2020); robust-frontier visualisation | v0.3 simulator, sustainability plan |

**Decision-readiness verdict: proceed**, but only if Chris secures (a) an institutional host (CenTax preferred), (b) at least one core funder (Nuffield Strategic Fund preferred), and (c) at least one named senior advisor (Advani, Summers, or Hughson) by month 6. Without all three, the project's credibility ceiling is too low to merit the 24-month commitment.

---

### Deliverable 2 — Technical Architecture Document

#### 2.1 Target architecture (layered)

```
┌──────────────────────────────────────────────────────────┐
│  PUBLIC LAYER                                            │
│  - GitHub Pages dashboard (Vue 3 + Pinia + D3, MIT)      │
│  - Charts + interactive simulator + provenance tooltips  │
└──────────────────────────────────────────────────────────┘
                ▲ HTTPS / JSON
┌──────────────────────────────────────────────────────────┐
│  API LAYER  (FastAPI + Pydantic + Redis cache, MIT)      │
│  POST /scenarios/run    GET /scenarios/{id}              │
│  GET /assumptions       GET /baselines  GET /sources     │
│  OpenAPI 3.1 auto-generated; rate-limited; provenance    │
│  envelope on every response                              │
└──────────────────────────────────────────────────────────┘
                ▲
┌──────────────────────────────────────────────────────────┐
│  SIMULATOR CORE  (wealthlens-sim, AGPL-3.0)              │
│  - PolicyEngine-UK fork: variables/, parameters/,        │
│    reforms/ (Families A–G)                               │
│  - wealthlens.top_tail: Pareto/GPD POT + rich list       │
│  - wealthlens.reconcile: ONS NBS macro alignment         │
│  - wealthlens.uncertainty: SALib Sobol + joblib          │
│  - wealthlens.synth: SDV CTGAN + ipfn reweighting        │
│  - wealthlens.provenance: PROV-DM + Pydantic envelopes   │
│  - wealthlens.assumptions: YAML registry + queryable     │
└──────────────────────────────────────────────────────────┘
                ▲
┌──────────────────────────────────────────────────────────┐
│  DATA LAYER                                              │
│  Synthetic FRS+WAS+SPI (CTGAN, public)                   │
│  Enhanced FRS 2022-23 (Hugging Face, AGPL data)          │
│  ONS NBS 2025 (£10.8tn HH net worth 2024, Dec 2025)      │
│  Sunday Times Rich List anchors (annual)                 │
│  Land Registry Price Paid (HVCTS bands)                  │
│  WID.world UK series (1820–2024)                         │
└──────────────────────────────────────────────────────────┘
```

#### 2.2 Stack-decision matrix

| Layer | Primary choice | Alternatives considered | Rationale |
|---|---|---|---|
| Rules engine | PolicyEngine-Core (fork of OpenFisca-Core) | OpenFisca-Core direct; UKMOD/EUROMOD; pure NumPy | PolicyEngine-UK already has wealth-tax scaffold, FRS+WAS fusion, gradient-descent reweighting (loss function with 2,664 elements per Ghenis 2023), HMT/No.10 footprint |
| Language | Python 3.11+ | Julia, R | Already in repo; PolicyEngine is Python; pandas/numpy ecosystem |
| Data frames | pandas + numpy | Polars, Modin, DuckDB | PolicyEngine uses pandas; switch only if performance forces it (Phase 5+) |
| Bayesian | NumPyro (JAX backend) | PyMC, Stan, Pyro | JAX gives GPU + autodiff; needed for v0.2 hierarchical tail-shape model |
| Top-tail | scipy.stats.genpareto + pyextremes + powerlaw | Custom MLE | Vermeulen-style fits; Wildauer–Kapeller rank correction; published methods |
| Synthetic data | SDV (CTGAN/TVAE) + ipfn + StatMatch (R via rpy2) | mice (R), fancyimpute, IterativeImputer | Tabular SOTA; ONS WAS already uses nearest-neighbour donor imputation we can mirror |
| Reweighting | policyengine-reweight (gradient descent) + ipfn | quadprog entropy, survey-package equivalents | Already proven by PolicyEngine team; differential testing easy |
| Uncertainty | SALib (Sobol/Saltelli) + joblib | ray, dask | Right scale for FRS sample × N policies; minimal infra |
| Reproducibility | Snakemake + DVC + Quarto | Nextflow, Pixi | Snakemake for the data-pipeline DAG; DVC for data versioning; Quarto for methods notes |
| Containerisation | Docker + devcontainers + uv | Poetry, pip-tools, conda | `uv` is now PolicyEngine's recommendation; speed matters for CI |
| Dashboard frontend | Vue 3 + Pinia + Tailwind + D3 + Vite | React, Svelte | Already in repo; large existing investment; D3 unmatched for distribution viz |
| API | FastAPI + Pydantic v2 | Flask, GraphQL | Already in repo; auto-OpenAPI; provenance envelopes natural in Pydantic |
| Caching | Redis (managed, Upstash or Fly.io) | In-memory, SQLite | Scenario re-runs are expensive; share-links need persistence |
| Provenance | W3C PROV-DM + Pydantic + git commit SHA | MLflow, DVC alone | PROV-DM is the international standard; lightweight |
| Assumption registry | YAML + JSON Schema validation | Database | Versioned with code in git; queryable via simple Python loader |
| CI | GitHub Actions (already wired) | CircleCI, GitLab | Existing infrastructure |
| Tests | pytest + Hypothesis + pandera + great_expectations | nose, doctest | Hypothesis for property-based testing of tax rules; pandera for data contracts |
| Pre-commit | ruff + mypy + bandit + codespell + sigstore | black + flake8 + isort | ruff replaces all three; sigstore for signed commits |
| Hosting | GitHub Pages (frontend) + Fly.io / Railway (API) | Vercel + Render; AWS | Cheap, predictable, UK-region available |
| DOI / archive | Zenodo + Software Heritage Archive | Figshare | Standard in open-science; SWH for code permanence |

---

### Deliverable 3 — Repository Transition Plan

Proposed new structure (additive, not destructive):

```
wealthlens-hq/
├─ packages/
│  ├─ wealthlens-sim/              (NEW, AGPL-3.0)
│  │  ├─ wealthlens_sim/
│  │  │  ├─ engine/                # PolicyEngine-UK pinned dependency
│  │  │  ├─ reforms/
│  │  │  │  ├─ a_annual_wealth.py
│  │  │  │  ├─ b_one_off_levy.py
│  │  │  │  ├─ c_cgt_reform.py
│  │  │  │  ├─ d_iht_transfer.py
│  │  │  │  ├─ e_property_tax.py
│  │  │  │  ├─ f_enforcement.py
│  │  │  │  └─ g_devolution.py
│  │  │  ├─ top_tail/              # Pareto/GPD + rich list
│  │  │  ├─ reconcile/             # ONS NBS alignment
│  │  │  ├─ synth/                 # CTGAN, ipfn, statistical matching
│  │  │  ├─ uncertainty/           # Sobol, Monte Carlo, joblib
│  │  │  ├─ provenance/            # PROV-DM envelopes
│  │  │  └─ assumptions/           # registry loader
│  │  ├─ tests/                    # pytest + hypothesis + pandera
│  │  ├─ pyproject.toml            # uv-managed
│  │  └─ LICENSE                   # AGPL-3.0
│  ├─ wealthlens-replicate/        (NEW, MIT) — replication notebooks for WTC, HVCTS, IFS
│  └─ wealthlens-api/              (refactor existing FastAPI, MIT)
├─ projects/
│  └─ wealthlens-dashboard/        (KEEP, Vue 3 + D3, MIT)
│     ├─ src/components/
│     │  ├─ ScenarioSelector.vue
│     │  ├─ ObjectiveWeights.vue
│     │  ├─ TopTailPicker.vue
│     │  ├─ RobustFrontier.vue
│     │  ├─ ProvenanceTooltip.vue
│     │  └─ AssumptionRegistry.vue
├─ automation/
│  ├─ data-pipelines/              (KEEP, existing 10 pipelines become source registry)
│  ├─ snakemake/                   (NEW, DAG of pipelines)
│  └─ social-media/                (KEEP)
├─ registries/                     (NEW)
│  ├─ sources.yml
│  ├─ assumptions.yml              # 50+ entries target by v0.1
│  ├─ baselines.yml                # current / enacted / announced / consultation / hypothetical
│  └─ priors.yml                   # behavioural elasticities + transferability scores
├─ docs/
│  ├─ ARCHITECTURE.md
│  ├─ METHODS_v0_1.qmd             # Quarto
│  ├─ MODEL_CHARTER.md
│  ├─ AI_LLM_DISCLOSURE.md
│  ├─ COI.md
│  ├─ replication/                 # Jupyter + Quarto notebooks
│  └─ gates/                       # gate-0 through gate-9
├─ research/, strategy/, tasks/, .agents/, .claude/, .codex/   (KEEP)
├─ LICENSE-MIT (frontend + API + replication)
├─ LICENSE-AGPL (simulator core)
├─ LICENSE-CC-BY-4.0 (visualisations + methods notes)
└─ CONTRIBUTING.md, CODE_OF_CONDUCT.md  (expand)
```

**Keep**: all 10 data pipelines (become the source registry); Vue/D3 dashboard; FastAPI backend; GitHub Actions CI; AGENTS.md, ARCHITECTURE.md, CLAUDE.md, CHANGELOG.md.

**Refactor**: FastAPI must add provenance envelopes; Pinia stores need new state shapes for scenarios; existing data pipelines must emit `sources.yml` entries.

**Add**: everything under `packages/wealthlens-sim/`, `registries/`, `docs/replication/`, `docs/gates/`.

**Deprecate**: nothing in the v0.1 timeframe. The current chart-only deliverable continues to run, with a new "Simulator (beta)" route added alongside.

**Licence split** (critical): rename `LICENSE` → `LICENSE-MIT` and add it to non-simulator packages; add `LICENSE-AGPL` to `packages/wealthlens-sim/`; document the split in the root README. This is the only legally clean way to depend on PolicyEngine-Core (AGPL-3.0) while keeping the public dashboard and replication notebooks MIT.

---

### Deliverable 4 — PolicyEngine-UK Integration Guide

#### 4.1 Code patterns

A reform in PolicyEngine-UK follows this declarative pattern:

```python
from policyengine_uk.model_api import *

def change_tax_parameters(parameters):
    parameters.gov.hmrc.income_tax.rates.uk.brackets[0].rate.update(
        period=periods.period("year:2026:1"), value=0.23
    )
    return parameters

class IncreaseBasicRate(Reform):
    def apply(self):
        self.modify_parameters(change_tax_parameters)
```

A variable is defined in `variables/`:

```python
class income_tax(Variable):
    value_type = float
    entity = Person
    label = "Income tax"
    definition_period = YEAR
    def formula(person, period, parameters):
        ...
```

For WealthLens-Sim, the seven policy families become seven reform modules. Family A uses the existing CEC scaffold:

```yaml
# Existing: policyengine_uk/parameters/gov/contrib/cec/non_primary_residence_wealth_tax.yaml
description: "Annual tax on total wealth (includes all property and corporate wealth except primary residences)."
metadata:
  label: "Wealth tax excluding primary residences"
  type: marginal_rate
brackets:
  - rate:
      label: "Wealth tax rate on non-primary residence wealth"
      unit: /1
      values: { 2000-01-01: 0 }
    threshold:
      label: "Wealth tax exemption on non-primary residence wealth"
      period: year
      unit: currency-GBP
      values: { 2000-01-01: 0 }
```

WealthLens-Sim contributes:
1. A *parallel* `wealth_tax_all_assets.yaml` (total wealth, not just non-primary), with multiple brackets.
2. A *one-off levy* variant with five-year instalment logic.
3. A `total_wealth_corrected` variable that combines WAS imputations with Pareto/GPD top-tail correction.
4. A `nation` field (England/Scotland/Wales/NI) wired through every wealth-related variable to support Family G (devolution-asymmetric).

#### 4.2 Forking strategy

**Do not hard-fork PolicyEngine-UK.** Instead:
- Add `policyengine-uk` as a pinned dependency in `wealthlens-sim/pyproject.toml`.
- Place WealthLens contributions in `wealthlens_sim/reforms/` mirroring the structure of `policyengine_uk/reforms/`, importing from `policyengine_uk.model_api`.
- Upstream every wealth-related parameter and variable to PolicyEngine-UK via PR; this builds trust with Max Ghenis (CEO) and Nikhil Woodruff (CTO, former 10 Downing Street Innovation Fellow) and avoids divergence.
- Maintain a `wealthlens-uk-data` dataset on Hugging Face mirroring `policyengine/policyengine-uk-data` but with the top-tail-corrected weights as an additional sidecar artefact.

#### 4.3 AGPL implications

AGPL-3.0 Section 13 (the network clause) requires that anyone running modified AGPL code as a network service must offer the modified source to users. Therefore:
- The `wealthlens-sim` package must be AGPL-3.0.
- The FastAPI API that imports `wealthlens-sim` is *itself* effectively covered.
- The Vue dashboard is *not* a derivative — it only consumes HTTP/JSON — and may remain MIT.
- The 10 existing data pipelines may remain MIT provided they do not import from `wealthlens-sim`.
- Any organisation running a private fork of WealthLens-Sim as a service must offer their source to users. Google's organisational ban on AGPL does not apply to us; it is a feature not a bug.

#### 4.4 Contribution sequence to PolicyEngine

- Month 1: open three good-first-issue PRs (typo, doc, small test fix) to establish identity.
- Month 2: open a "tracking issue" describing the seven policy families, asking which they would accept upstream.
- Month 3: upstream Family A (annual wealth tax) and Family B (one-off levy) parameters + variables, keeping reform-application logic in wealthlens-sim.
- Months 4–6: upstream HVCTS variant under Family E.

---

### Deliverable 5 — Top-Tail Reconstruction Implementation Guide

#### 5.1 Mathematical recipe

Three estimators in parallel, triangulated:

1. **Vermeulen (2018) Pareto fit with rich list.** Survey sample augmented with Sunday Times Rich List records, with appropriate rescaling. Fit Pareto tail above multiple thresholds (£500k, £1m, £2m, £5m) and report sensitivity.

2. **Generalised Pareto Distribution (POT) following Kennickell (2025).** scipy.stats.genpareto + pyextremes; threshold selection via mean-excess function diagnostics and Gabaix–Ibragimov/Clauset–Shalizi–Newman tests. GPD's flexibility (shape parameter ξ) handles thinner tails than simple Pareto and supports a macro-total constraint.

3. **Wildauer–Kapeller (2022) rank correction.** Tracing-the-invisible-rich approach corrects for differential non-response by treating the empirical CCDF as observed only above a threshold, with the tail-rank function calibrated to rich-list rank.

#### 5.2 Python skeleton

```python
# wealthlens_sim/top_tail/pareto.py
from scipy.stats import genpareto
import numpy as np, pandas as pd
from typing import NamedTuple

class TopTailFit(NamedTuple):
    method: str
    threshold: float
    alpha_or_xi: float
    top1pct_share: float
    macro_total: float
    rich_list_anchored: bool
    ci_low: float
    ci_high: float

def fit_pareto_vermeulen(was_wealth, was_weights, rich_list_wealth,
                         threshold=2_000_000, n_boot=1000):
    """Vermeulen (2018) — survey + rich list, OLS on log CCDF."""
    combined = np.concatenate([was_wealth[was_wealth > threshold],
                               rich_list_wealth])
    combined_w = np.concatenate([was_weights[was_wealth > threshold],
                                 np.ones_like(rich_list_wealth)])
    order = np.argsort(combined)[::-1]
    log_x = np.log(combined[order])
    log_ccdf = np.log(np.cumsum(combined_w[order]) / combined_w.sum())
    alpha = -np.polyfit(log_x, log_ccdf, 1)[0]
    # bootstrap CIs ...
    return TopTailFit(method="vermeulen_pareto", threshold=threshold,
                      alpha_or_xi=alpha, ...)

def fit_gpd_pot(wealth, weights, threshold=2_000_000, macro_total=None):
    """Kennickell (2025) — GPD with optional macro-total constraint."""
    excess = wealth[wealth > threshold] - threshold
    xi, _, scale = genpareto.fit(excess, floc=0)
    if macro_total is not None:
        # constrained optimisation to match ONS NBS total
        ...
    return TopTailFit(method="gpd_pot", ...)
```

#### 5.3 Validation strategy

- Cross-validate against WID.world UK series (already in the existing repo's data pipelines).
- Reconcile to the ONS National Balance Sheet 2025 release (18 December 2025): household net worth £10.8 trillion in 2024, with £4.6 trillion non-produced (land), £2.0 trillion produced, £4.2 trillion financial net. The top-tail-corrected sum should hit £10.8tn ± 2%.
- Differential testing against PolicyEngine-UK's enhanced FRS for any overlapping calculation.
- Publish a "top-tail diagnostic" page on the dashboard showing the three estimators' top-1% share with credible intervals.

#### 5.4 Bayesian v0.2 plan

NumPyro hierarchical model with priors on (ξ, hidden-wealth fraction φ, asset-class composition vector π, macro-reconciliation scalar μ). MCMC at simulator scale (NUTS, 4 chains × 1000 draws) is feasible on a single 8-core machine in under an hour for a single year. Surrogate model for the interactive dashboard: scikit-learn Gaussian Process with RBF kernel trained on 10,000 MCMC posterior samples, queried in <50ms.

---

### Deliverable 6 — Synthetic FRS-WAS Data Generation Plan

Synthetic data is needed because UK Data Service Special Licence / SecureLab access takes time. Per UKDS's own guidance: "If the application is well prepared and approval is granted with no changes required, you can expect to gain access to the data in approximately 3-4 months." HMRC Datalab is multi-stage with up to 3-year dataset waits for some series.

#### 6.1 Pipeline

1. **Start from public FRS** (annual, EUL licence, no application needed).
2. **Statistically match WAS variables onto FRS households** using `StatMatch` (R, via `rpy2`) with matching variables age, region (now nation), tenure, employment status, household composition, dependent children — the same variables ONS WAS itself uses for nearest-neighbour donor imputation.
3. **Impute SPI top-income tail** via random-forest quantile regression (the PolicyEngine method).
4. **Reweight** with `policyengine-reweight` (gradient descent) or `ipfn` (iterative proportional fitting) to admin totals: HMRC SPI deciles, ONS WAS deciles, ONS NBS aggregates, HMRC IHT aggregates by estate band.
5. **Add top-tail-corrected synthetic households** above the WAS top-coding via the Pareto/GPD fit; zero-weight them, then non-zero-weight them in re-weighting (PolicyEngine's published technique).
6. **Generate synthetic copies** via SDV's CTGAN/TVAE on the augmented dataset for fully-public release; validate marginals and bivariate joints with `pandera` + KL divergence checks.

#### 6.2 Validation tests

- Aggregate income tax revenue within ±1% of HMRC published.
- Aggregate CGT revenue within ±5% of HMRC.
- Aggregate household net worth £10.8tn ± 2% (ONS NBS 2024).
- Top-1% wealth share within Vermeulen / WTC published range.
- Decile shares match ONS WAS round 8 within ±2 percentage points.

---

### Deliverable 7 — HVCTS Rapid-Response Brief Plan (countdown to 14 July 2026)

Current date: 21 May 2026. Deadline: 14 July 2026 (consultation close per GOV.UK and Propertymark).

| Week | Tasks |
|---|---|
| W1 (21–27 May) | Set up `packages/wealthlens-sim/` skeleton; pin policyengine-uk; pull Land Registry Price Paid (2023–2026 England); ONS HPI September 2025; WAS round 8 derived variables (EUL); tabulate every consultation question. |
| W2 (28 May–3 June) | Implement HVCTS reform under Family E using PolicyEngine-UK conventions. Apply 4 bands (£2,500–£7,500 by 2026 value: £2–2.5m, £2.5–3.5m, £3.5–5m, £5m+); inflate Price Paid sale prices to April 2026 values using regional HPI; estimate stock of properties in scope. |
| W3 (4–10 June) | Liquidity-stress modelling: link HVCTS-bearing properties to WAS households via property-value ventile; identify income-poor / asset-rich subgroups; estimate share unable to pay without selling, deferring or borrowing. Anchor to the HMT/OBR "around £430 million" central estimate, not as a contested counter-forecast. |
| W4 (11–17 June) | Devolution analysis: model HVCTS-equivalents in Scotland (LBTT-adjacent), Wales (LTT-adjacent), NI. Behavioural priors: bunching just below £2m; deeds-of-variation; company/trust ownership; foreign holders. |
| W5 (18–24 June) | Draft methods note (Quarto); draft 5-page consultation response; draft "does/does not say" sheet; generate ~30 distributional charts at constituency level using PolicyEngine-style constituency reweighting. |
| W6 (25 June–1 July) | Internal review; structured pre-mortem; advisory check (target: Advani, Hughson, Loutzenhiser, Chamberlain, one local-government expert). |
| W7 (2–8 July) | Address review comments; finalise provenance manifest; freeze code at tagged release (`v0.1.0-hvcts`); archive Zenodo replication package. |
| W8 (9–14 July) | Submit consultation response to GOV.UK; publish brief on GitHub Pages + Tortoise/Bluesky; brief friendly journalists (FT Alphaville, Dan Neidle, Tortoise). |

**What the brief should NOT claim**: that HVCTS will raise materially more than the HMT figure; that revaluation will succeed politically; that bunching at £2m will be small; or any counterfactual it cannot defend with public data.

---

### Deliverable 8 — 90-Day Execution Checklist

**Days 1–30 (21 May – 19 June 2026): Foundations + HVCTS week 1–4**
- Day 1: tag current repo `pre-blueprint`; create branch `wealthlens-sim-v0`.
- Day 2: stand up `packages/wealthlens-sim/` skeleton with AGPL-3.0 LICENSE, pyproject.toml, uv lockfile.
- Day 3: pin `policyengine-uk`; wire `enhanced_frs_2022_23.h5` from Hugging Face.
- Day 5: open three good-first-issue PRs to PolicyEngine-UK to establish identity.
- Day 7: create `registries/sources.yml`, `assumptions.yml`, `baselines.yml` with 10 entries each.
- Day 10: HVCTS week 2 work complete (data pull + reform skeleton).
- Day 12: send introductory emails to Advani, Summers, Hughson at CenTax; Helen Miller at IFS; Mike Brewer at Resolution Foundation. Tone: not asking for endorsement; offering replication code; flagging HVCTS brief as preview.
- Day 14: draft Nuffield Strategic Fund one-page summary; email `strategicfund@nuffieldfoundation.org` to test fit before next round.
- Day 18: email PolicyEngine team (Max Ghenis, Nikhil Woodruff); UKMOD team at CeMPA Essex (Matteo Richiardi); Tax Policy Associates (Dan Neidle).
- Day 21: complete HVCTS liquidity-stress analysis.
- Day 25: complete first WTC one-off levy replication (target ±5% on £500k threshold scenario).
- Day 30: publish 1500-word "What we've built so far" post on Bluesky/SSRN.

**Days 31–60 (20 June – 19 July 2026): HVCTS publication + Phase 1.5 kick-off**
- Day 35: submit HVCTS consultation response to GOV.UK.
- Day 38: publish Zenodo replication package with DOI for HVCTS analysis.
- Day 42: implement Pareto fit (Vermeulen 2018) in `wealthlens_sim.top_tail`.
- Day 49: implement GPD-POT fit (Kennickell 2025).
- Day 56: macro reconciliation to ONS NBS 2024 (£10.8tn).
- Day 60: publish "Top-tail diagnostic" page on dashboard with confidence intervals.

**Days 61–90 (20 July – 18 August 2026): Policy families + dashboard skeleton**
- Day 65: implement Family A (annual wealth tax) reform module.
- Day 72: implement Family B (one-off levy with five-year instalment).
- Day 79: implement Family C (CGT reform: 18%/24%, BADR phase-out).
- Day 85: dashboard "Scenario Selector" + "Provenance Tooltip" components live.
- Day 90: 90-day review + pre-mortem; publish methods note v0.1 (Quarto) on SSRN.

---

### Deliverable 9 — Funding Strategy and Outreach Sequence

#### 9.1 Funder map

| Funder | Programme | Budget per grant | Next deadline | Fit | Notes |
|---|---|---|---|---|---|
| Nuffield Foundation | Strategic Fund | £1–3m over 2–5 yrs | 16 March 2026 (current round); next likely autumn 2026 | Very high | Per the Nuffield Strategic Review of 24 July 2025: "The Foundation will commit £30 million annually over the next five years to generate rigorous evidence on, and shape solutions to, intersecting problems impacting UK society." Already funds PolicyEngine ("Enhancing, localising and democratising tax-benefit policy analysis"); contact `strategicfund@nuffieldfoundation.org`; Anvar Sarygulov is Research Grants Manager covering PolicyEngine. Direct fit with priority Q1 "prosperous and fair society" and Q5 "effective institutions". |
| Nuffield Foundation | Main Grants (R, D & A Fund) | Up to £500k (£750k exceptional) | Outline deadlines ~April and ~September | High | Two-stage; min 7 months to award. Co-apply with CenTax host. |
| Joseph Rowntree Foundation | Unrestricted (largely by invitation) | Variable | Rolling | Medium | Per jrf.org.uk/funding: "In 2025 we want to make more unrestricted grants, putting an additional £50 million to £100 million behind our mission-focused work over the coming 5-10 years." Recent focus on wealth narratives ("Talking about wealth inequality", June 2025). Contact `info@jrf.org.uk`; programme lead Victoria Hughes (Emerging Futures). |
| abrdn Financial Fairness Trust | Tax-benefit modelling | £100–500k | Rolling, by invitation | High | Already funds UKMOD 2023–2024; explicit interest in open-source modelling. |
| ESRC (UKRI) | Impact Acceleration via host university | £20k–£200k | Via host | Medium | Requires CenTax (Warwick) or LSE/STICERD as host. |
| Open Society Foundations UK | Tax justice | $50k–$500k | Rolling | Medium-low | Risk: advocacy-adjacent may compromise IFS-neutral positioning. |
| Open Philanthropy | UK policy | Variable | Rolling | Low | Not in current UK policy stack. |
| Mozilla Foundation | Open-source tooling | $50k–$300k | Periodic | Low-medium | Possible for "open infrastructure for democracy" framing. |
| Ford Foundation | Inequality | $100k–$1m | By invitation | Low-medium | Slow cycle; needs intermediary. |

#### 9.2 Institutional host options ranked

1. **CenTax (Warwick + LSE)** — *recommended*. Constitution explicitly aims at "the UK's leading centre for research excellence in UK wealth tax." James Murray MP keynoted launch. Advisory weight (Advani, Summers, Hughson, Lonsdale) is exactly what's needed. Risk: capacity-bound; may want WealthLens as subordinate rather than partner.
2. **III (International Inequalities Institute, LSE)** — high quality; Summers associated; less applied-policy than CenTax.
3. **STICERD (LSE)** — academic prestige; less policy-impact focus.
4. **IFS (associate fellowship)** — high credibility; but Green Budget 2025's opposition to annual wealth tax may cause friction on Family A.
5. **Resolution Foundation (associate fellow route)** — high impact; Mike Brewer + James Smith warm contacts; Torsten Bell now MP and conflicted.
6. **Bennett Institute (Cambridge)** — moderate fit.
7. **Nuffield College Oxford** — academic; Glen Loutzenhiser anchor.
8. **CAGE Warwick** — overlaps with CenTax (Advani); makes more sense as part of CenTax application.
9. **IPPR** — advocacy-adjacent, *avoid as primary host*.
10. **Tony Blair Institute** — *avoid*.

**Recommendation**: pursue CenTax as primary host with a Nuffield College Oxford or III/LSE secondary affiliation for non-Warwick advisors.

#### 9.3 Advisory board recruitment targets

| Name | Affiliation | Role | Approach |
|---|---|---|---|
| Arun Advani | CenTax / Warwick | Co-chair / methods lead | Personal email after small upstream PolicyEngine PR; reference 2021 *Fiscal Studies* paper |
| Andy Summers | CenTax / LSE | Co-chair / legal-design | Same |
| Helen Hughson | LSE | Top-tail / WAS lead | Direct; her replication is the most relevant precedent |
| Emma Chamberlain | Pump Court Tax | Legal-implementability | Through Advani introduction |
| Glen Loutzenhiser | Oxford | Tax law / oversight | Direct; Oxford Faculty of Law |
| Stuart Adam | IFS | CGT/IHT methodology | Through Helen Miller introduction; very busy |
| Helen Miller | IFS | Strategic credibility | Approach later (M6+); only after IFS-aligned framing locked |
| Mike Brewer | Resolution Foundation | Distributional methods | Direct |
| Matteo Richiardi | CeMPA Essex (UKMOD) | Microsimulation methodology | Direct; will appreciate not duplicating UKMOD |
| Max Ghenis / Nikhil Woodruff | PolicyEngine | Engine integration | Through upstream PRs first |
| David Eiser | Fraser of Allander | Scotland / devolution | Direct |
| Guto Ifan | Cardiff | Wales / devolution | Direct |
| Esmond Birnie | Ulster University | NI / devolution | Direct |
| Dan Neidle | Tax Policy Associates | Communications advisor | Bluesky/email; responsive |

Target 5–7 confirmed advisors by month 6.

---

### Deliverable 10 — Communications Playbook

#### 10.1 Three audiences, three voices

1. **Methodological audience** (academics, IFS, OBR, HMT, PolicyEngine): SSRN preprints, IDEAS-RePEc listings, Quarto methods notes, Zenodo replication packages with DOIs. Voice: cautious, credible intervals always visible. Cite Advani, Hughson, Tarrant, Vermeulen, Kennickell, Brülhart, Jakobsen by surname-year.

2. **Policy audience** (consultations, civil service, MPs, Lords): GOV.UK consultation responses, Westminster briefings, "does/does not say" one-pagers, 5-page executive summaries. Voice: neutral, decision-oriented, no advocacy framing. Always include a "what would change this conclusion" pane.

3. **Public audience** (FT, Tortoise, Bluesky, dashboard visitors): interactive dashboard, narrative essays, 90-second explainer videos. Voice: clear, comparative, visually rich. Always show baseline next to reform; always show distribution, never just a point estimate.

#### 10.2 Press pack discipline (per release)

- 5-page executive summary
- 1-page "does/does not say" sheet
- Quarto methods note (full)
- Provenance manifest (JSON)
- Zenodo DOI for replication package
- 3 social cards (Bluesky/Twitter format)
- Embargoed share for friendly journalists 48h before public release

#### 10.3 The £0.4bn ↔ £80bn explainer (flagship piece)

Format: long-form essay + interactive explorer (both). Structure:
1. The HMT figure (verbatim: "The HVCTS is estimated to raise around £430 million of revenue per year from 2028/29 to support funding for local government services").
2. The Advani–Hughson–Tarrant figure: >£80bn from an annual 1% wealth tax above £2m, after non-compliance and admin costs.
3. Why the ~200× difference is not a contradiction — it is a function of: base (property value above £2m vs total wealth above £2m), rate (£2,500–£7,500 banded vs 1%), compliance assumptions, behavioural responses, and revaluation politics.
4. Interactive tool: pick base, rate, threshold, compliance assumption — see the revenue range.
5. A "naked point estimate" warning: any single number in this space without bands is misleading.

Distribution: SSRN + Tortoise long-read + FT Alphaville Q&A + Bluesky thread + dashboard interactive.

#### 10.4 Spokesperson training and red lines

- Single spokesperson for technical questions (PI).
- Single spokesperson for distributional impact (advisor with academic standing).
- Red lines: never endorse a specific policy; never project beyond OBR forecast horizon without explicit "scenario, not forecast" framing; never publish without provenance manifest attached.

---

### Deliverable 11 — Risk Register Operationalisation

Convert the blueprint's 30-item register into a live GitHub Project with the following per-issue schema:

```yaml
id: R-007
title: "Top-tail Pareto fit unstable when STRL coverage is patchy"
domain: methodology     # methodology|funding|institutional|comms|technical|legal|behavioural
likelihood: medium
impact: high
last_reviewed: 2026-05-21
owner: chris0jeky
mitigation: |
  Triangulate three estimators (Vermeulen Pareto, Kennickell GPD,
  Wildauer–Kapeller rank). Publish sensitivity table in every revenue estimate.
trigger: "Top-1% wealth share moves >2pp between annual STRL updates."
escalation: "Pause public revenue estimates; consult advisory board within 14 days."
```

Cadence: weekly PI review of high-impact risks; monthly full-register skim; quarterly review with advisory board (publish anonymised summary); annual methodology audit (mandatory; rotating external auditor).

**Top 10 risks (prioritised)**:
1. Advocacy-capture by a funder. *Mitigation: scenario-design firewall + COI policy.*
2. Top-tail estimates publicly contested by OBR/HMRC. *Mitigation: triangulation + macro reconciliation.*
3. PolicyEngine-UK fork drifts from upstream. *Mitigation: upstream-first + monthly merge.*
4. HVCTS brief misses 14 July deadline. *Mitigation: reverse-engineered 8-week Gantt.*
5. Founder steps back. *Mitigation: Software Heritage archive + institutional handover.*
6. Funding gap month 13–18. *Mitigation: bridge from JRF unrestricted or abrdn FFT.*
7. Synthetic data marginals diverge from real WAS. *Mitigation: pandera contracts + KL checks.*
8. AGPL deters contributors. *Mitigation: DCO-only (no CLA); clear contributor docs.*
9. Behavioural priors mis-applied because of transferability errors. *Mitigation: transferability_score in priors.yml + sensitivity bands.*
10. Public confuses revenue range with prediction. *Mitigation: "naked point estimates blocked by UI" (Gate 9).*

---

### Deliverable 12 — Methodology Priorities and Peer-Review Pathway

Publishing order:
1. **HVCTS rapid-response brief** (July 2026) — venue: GOV.UK consultation + SSRN preprint.
2. **WTC one-off levy replication paper** (October 2026) — venue: *Fiscal Studies* (where Advani et al. 2021 published).
3. **Top-tail reconstruction methods note** (December 2026) — venue: *Review of Income and Wealth* (where Vermeulen 2018 and Kennickell 2025 published).
4. **Devolution-asymmetric reform paper** (March 2027) — venue: *Regional Studies* or *Scottish Affairs*; co-authored with Eiser/Ifan/Birnie.
5. **Provenance + assumption registry paper** (June 2027) — venue: *International Journal of Microsimulation* (where UKMOD published).
6. **v0.2 Bayesian top-tail paper** (October 2027) — venue: *Journal of Official Statistics* or *Empirical Economics*.

Peer-review pathway: every paper has a structured pre-mortem (anonymised internal review); SSRN preprint with DOI; submission to peer-reviewed journal; replication package on Zenodo with DOI; archived on Software Heritage.

Replication discipline (Gate 4):
- WTC scenarios reproduced within ±5%.
- HMRC distributional analyses reproduced within ±2%.
- WID UK top-1% share reproduced within ±1pp.
- ONS NBS aggregates within ±2%.

---

### Deliverable 13 — Open-Source Community Building Plan

#### 13.1 Diátaxis framework documentation
- **Tutorials**: "Run your first wealth-tax scenario in 5 minutes" (Vue dashboard); "Add a new reform to wealthlens-sim" (Python).
- **How-to**: "Replicate the WTC one-off levy scenario"; "Reconcile to ONS NBS 2024".
- **Reference**: API docs (OpenAPI 3.1); variable docs; parameter docs.
- **Explanation**: "Why we use AGPL-3.0"; "What the top-tail correction is and isn't"; "Why the HMT-figure ↔ WTC-figure range is honest, not confused".

#### 13.2 Community mechanics
- GitHub Discussions (not Discord/Slack — async, archived, search-indexable).
- Good-first-issue curation (target: 5 open at all times).
- Monthly "office hours" Zoom (1 hour, recorded, posted publicly).
- Quarterly reproducibility hackathon (online + UK universities; £500 prizes from grant).
- DCO (Developer Certificate of Origin), not CLA.
- Codespell + ruff + mypy + bandit in pre-commit hooks.

#### 13.3 Branch protection
- Main branch: required PR review (1+); required CI green; signed commits via sigstore (gitsign); no force-push.
- Release tags signed by PI; SBOM (CycloneDX) attached to each release.

---

### Deliverable 14 — 24-Month Roadmap

| Month | Phase | Key milestones | Funding state |
|---|---|---|---|
| M1 | 1: Replicate | Repo restructure; PolicyEngine PR #1; sources.yml v1 | Self-funded |
| M2 | 1: Replicate | HVCTS reform module; data pipelines | Self-funded |
| M3 | 1: Replicate | **HVCTS brief submitted (14 July 2026)** | Self-funded |
| M4 | 1.5: Top-tail | Vermeulen Pareto fit | Nuffield outline submitted (autumn) |
| M5 | 1.5: Top-tail | GPD POT fit; macro reconciliation | abrdn FFT enquiry |
| M6 | 1.5: Top-tail | WTC one-off levy replication ±5% | JRF informal scoping |
| M7 | 2: Families A–G | Family A (annual wealth tax) live | Nuffield full application |
| M8 | 2: Families A–G | Family B (one-off levy) live | abrdn application |
| M9 | 2: Families A–G | Family C (CGT reform) live | First funder TBC |
| M10 | 2: Families A–G | Family D (IHT/transfer) live | |
| M11 | 2: Families A–G | Family E (property) beyond HVCTS | |
| M12 | 2: Families A–G | **v0.1 release** (Zenodo DOI) | |
| M13 | 2: Families A–G | Family F (enforcement) live | Funding gap risk window |
| M14 | 2: Families A–G | Family G (devolution) live | |
| M15 | 2: Families A–G | Public dashboard beta launched | |
| M16 | 3: Behavioural | Priors registry; transferability scoring | Second funder ideally confirmed |
| M17 | 3: Behavioural | Behavioural-elasticity wrappers for Families A, B | |
| M18 | 3: Behavioural | Robust-frontier visualisation | |
| M19 | 3: Behavioural | NumPyro Bayesian top-tail v0.2 | |
| M20 | 3: Behavioural | Surrogate model in dashboard | |
| M21 | 3: Behavioural | **v0.2 release** | |
| M22 | Post-v0.2 | First peer-reviewed paper accepted (*Fiscal Studies*) | Year-3 funding secured |
| M23 | Post-v0.2 | Sustainability plan published | |
| M24 | Post-v0.2 | **Final 24-month methodology audit** | Handover or extension |

---

### Deliverable 15 — Stack-Decision Matrix (consolidated)
See Deliverable 2.2 above for the full table.

---

### Deliverable 16 — Policy Levers No One Else Is Modelling

| Lever | Status | Who has discussed | WealthLens implementation sketch |
|---|---|---|---|
| Accessions tax | Discussed academically (Atkinson 1972; Halliday 2018); no UK model | Tax Justice UK; some IPPR work | Family D variant: tax recipient of inheritance/gift on cumulative lifetime receipts. Implementation: add `lifetime_accessions` person variable; tax above £125k cumulative. |
| Mark-to-market on large public holdings | Saez–Zucman 2019; Schanzenbach-Wessel 2020 | Some US academics; no UK | Family C variant: deemed disposal annually on >£10m public-equity holdings; tax at CGT rate. |
| Deemed disposal at retirement | Discussed Australia | None in UK | Family C variant: trigger CGT on all unrealised gains at state pension age. |
| Exit charges | France; UK non-dom context | Advani (non-dom context) | Family C variant: tax on accrued gains at departure date for long-term residents. |
| Gift-tax overhaul | Various; gifts tax-free if donor survives 7 years | Wealth Tax Commission | Family D variant: tax gifts above lifetime threshold; PET 7-year rule replaced by indexed lifetime cumulative. |

WealthLens's unique contribution could be a "what-if accessions tax" toggle alongside the seven core families.

---

### Deliverable 17 — Behavioural Validation-Set Problem

There is no in-force UK comparator policy for an annual wealth tax. Therefore "accuracy" cannot be claimed. The blueprint asks for "robustness, not accuracy." This means:

1. **Synthetic-truth experiments**: generate a known data-generating process; run the full simulator; check whether the simulator recovers the true revenue within its credible interval. Publish recovery statistics.

2. **Cross-validation against comparators**:
   - **Switzerland (Brülhart, Gruber, Krapf, Schmidheiny 2022, AEJ:EP vol. 14, no. 4, pp. 111–150)**: verbatim — "a 1 percentage point drop in a canton's wealth tax rate raises reported taxable wealth by at least 43 percent after 6 years." Transferability score: medium (Switzerland's tax base is broad, mobility internal, evasion routes specific; no third-party reporting of financial wealth inflates elasticity vs likely UK setting).
   - **Denmark (Jakobsen et al. 2020)**: elasticity smaller for the moderately wealthy, larger at the very top.
   - **Norway (Ring 2020)**: real-asset response < portfolio response.
   - **Spanish (various)**: bunching evidence; mobility evidence inconsistent.
   - **France IFI**: real-estate-only since 2018; behavioural response observable.
   - **UK (Advani–Tarrant 2021)**: verbatim — "Under a well-designed wealth tax covering all asset classes – as we assume ours will – the overall magnitude of behavioural responses could be limited to a 7–17 per cent reduction in wealth in response to a 1 per cent tax rate on wealth."

3. **Sensitivity bands**: publish revenue estimates as ranges, with explicit annotation of which behavioural prior is binding (e.g. "low avoidance: £80bn; high avoidance: £55bn; central: £67bn").

4. **Pre-registration**: publish methods note before final results to prevent specification searching.

---

### Deliverable 18 — Sustainability Beyond Month 24

Year-3 options (in declining preference):
1. **Institutional integration**: WealthLens-Sim becomes a CenTax public infrastructure module, maintained by CenTax + community contributors.
2. **Nuffield Strategic Fund renewal**: apply Q4 of year 2 for years 3–5.
3. **PolicyEngine merger**: upstream all WealthLens contributions; project lives inside PolicyEngine-UK with a dedicated wealth-tax sub-team.
4. **Self-sustaining via consultancy income**: paid replication studies for think tanks, opposition parties, devolved governments.

Archival strategy (regardless of outcome): Software Heritage Archive identifier on every release; Zenodo DOI on every major version; ONS-deposited methods notes; UK Web Archive nomination for the dashboard.

If founder steps back: documented handover process in `docs/HANDOVER.md`; named successor in advisory board; Software Heritage guarantees code permanence.

---

### Deliverable 19 — Competitive Landscape Analysis (2026)

| Org | Current outputs (2025–2026) | Overlap with WealthLens | Gap WealthLens fills |
|---|---|---|---|
| PolicyEngine-UK | HVCTS scoring; Spring Statement 2026 dashboard; salary-sacrifice analysis | High (engine) | Wealth top-tail correction; provenance; Families A–G as first-class |
| CenTax | IHT/APR analysis (Aug 2025); IHT farm-estates report; tax reform coalition (Nov 2025) | Medium | Public-facing open simulator; reproducibility infrastructure |
| IFS | Green Budget 2025 (Adam, Delestre, Miller); CGT reform paper | Medium | Public-facing simulator; agnostic on annual-wealth-tax advocacy |
| Resolution Foundation | "Before the fall" (Broome/Kanabar, Oct 2025); Living Standards Outlook 2026 | Low | Static simulator; reproducible scenarios |
| Tax Justice UK / TJN | Campaigns; revenue estimates | Low | Methodological rigour; agnostic framing |
| Dan Neidle / Tax Policy Associates | Frequent posts; HVCTS commentary | Low | Quantitative simulator |
| WID.world UK | Top-1% wealth share time series | Low | Distributional scenario tooling |
| UKMOD (CeMPA Essex) | Open tax-benefit modelling 2023–2030 | Medium | Wealth tax not their focus; restricted CC BY-NC-ND licence |
| IPPR | Fiscal commentary; productivity briefs | Low | Neutrality; open-source code |
| Bennett Institute | Capital institutions research | Low | UK-specific simulator |

**Positioning**: WealthLens is the only project combining (a) open-source rules-as-code for wealth taxes, (b) top-tail correction with rich-list anchors, (c) devolution-asymmetric modelling, and (d) public-facing interactive dashboard with provenance. CenTax has analytical credibility but no public simulator. PolicyEngine has a simulator but no top-tail correction. WealthLens uniquely sits in the intersection.

---

### Deliverable 20 — 2025–2026 UK Wealth-Policy Landscape Update

- **Autumn Budget 2025 (26 November)**: HVCTS announced (£2m+ property surcharge, England, £2,500–£7,500/year by band, April 2028 commencement). OBR-certified revenue "around £430 million of revenue per year from 2028/29" (GOV.UK).
- **CGT trajectory**: per Autumn Budget 2025 document, CGT "will more than double from £13.7 billion at the start of this Parliament to £30 billion in 2030/31." From April 2026: Business Asset Disposal Relief (BADR) and Investors' Relief rate rises to match main CGT rate (24%).
- **IHT reforms**: APR/BPR capped at £1m combined relief from April 2026; pensions brought into IHT from April 2027. Per Autumn Budget 2025: IHT "raised £8.3 billion a year at the start of this Parliament; this is expected to rise to £14.5 billion in 2030/31."
- **Non-dom abolition**: FIG (Foreign Income and Gains) regime live since 6 April 2025; four-year exemption for new arrivals after 10 years of non-residence; OBR scored the package at £39.5bn across the scorecard. Real-world migration data not yet published.
- **Salary sacrifice pension cap**: £2,000/year from April 2029; OBR £4.7bn in 2029/30, £2.6bn in 2030/31.
- **Two-child UC limit**: removed April 2026.
- **Spring Statement 2026**: light-touch; main fiscal levers already set in November.
- **Election cycle**: Parliament runs to summer 2029 at latest; OBR's 5-year forecast covers to 2030/31.

Implication for WealthLens: the policy window for *responding* (HVCTS, CGT, IHT) is now; the window for *building infrastructure for the next wealth-tax debate* runs through 2027–2028 ahead of any potential election or wealth-tax announcement.

---

### Deliverable 21 — Synthetic-Data Plan + Data Access Pipeline

| Dataset | Access route | Realistic timeline | What we can do while waiting |
|---|---|---|---|
| FRS public (EUL) | UK Data Service registration (free) | 1 week | Everything FRS-only |
| WAS public (EUL) | UK Data Service | 1 week | Derived household totals; nation-level |
| WAS Special Licence | UK Data Service | 1–2 months | Geography-detailed analysis |
| FRS+WAS SecureLab | UK Data Service SecureLab | Per UKDS: "you can expect to gain access to the data in approximately 3-4 months" | Use enhanced FRS from PolicyEngine via Hugging Face (publicly available) |
| ONS NBS aggregates | Public ONS website | Immediate | All macro reconciliation |
| ONS SRS (admin data linkages) | ONS Secure Research Service | 4–6 months + Five Safes training | Public WAS + synthetic |
| HMRC Datalab | EOI + formal proposal (gov.uk/government/publications/hmrc-datalab) | "Applications are usually assessed several times a year"; some datasets up to 3 years' wait | Most analysis without admin tax records |
| Sunday Times Rich List | Public (annual May release) | Immediate | Rich-list anchoring feasible |
| Land Registry Price Paid | Public | Immediate | HVCTS analysis |

Letters of support strategy: secure named-academic letters from Advani (Warwick), Summers (LSE), Loutzenhiser (Oxford) by month 6; these dramatically shorten the SecureLab review.

---

### Deliverable 22 — Phase 5 (Dynamic) Preparation

Phase 5 turns the static simulator into a multi-year accumulation engine:
1. **Multi-year accumulation**: extend variables to year-on-year wealth dynamics; integrate ONS WAS panel structure (longitudinal weights in WAS round 8 user guide).
2. **Demographic ageing**: use ONS population projections; layer on top of the synthetic dataset.
3. **Inheritance flows**: model intergenerational transfers via IHT data + WAS gift histories; calibrate to ONS NBS household-sector gross transfers.
4. **Pension decumulation under new IHT rules (from April 2027)**: explicit module given the major policy change.
5. **Property-price capitalisation**: how an HVCTS-style annual charge would be capitalised into prices; reference Brülhart et al. (2022) finding that part of the Swiss wealth-tax response reflected concurrent housing price changes.

Tooling: UKMOD already does some multi-year work; borrow methodology openly. Frameworks: stick with PolicyEngine-Core's annual-period model; add a thin orchestration layer that re-runs N years with carried-state.

---

### Deliverable 23 — Phase 6 (ABM/RL) Preparation

This is *post-v0.3* and should not be promised in v0.1 communications.

1. **Housing-market ABM** for HVCTS responses: strategic agents (homeowners, developers, foreign buyers) responding to threshold and rate. Framework: Mesa (Python) or agentpy. Outcome: bunching at £2m; revaluation politics.
2. **Avoidance-network ABM** for wealth taxes: firms restructuring under wealth tax. Cite The AI Economist (Salesforce, Zheng et al.) as a *cautionary* tale — over-claimed; opaque reward function; learn what not to do.
3. **RL only when there is a credible reward function**. For wealth-tax design this means defining social welfare carefully; do not let RL agents "discover optimal policy" without transparent objective-function decomposition.

Frameworks: Stable Baselines3 or CleanRL for any RL; Ax/BoTorch for Bayesian optimisation of robust frontier. Do not commit to Phase 6 in any v0.1 funding application.

---

### Deliverable 24 — Post-HVCTS Identity Problem

After 14 July 2026 the consultation closes; HVCTS will either be implemented (most likely, per Autumn Budget 2025), modified, or dropped. WealthLens must not be defined by HVCTS alone:

1. By month 12, ship at least three Family-A/B/C/D scenarios publicly to demonstrate breadth.
2. By month 18, publish at least one scenario on each of Families E, F, G.
3. Position publicly as "the open-source rules-as-code platform for UK wealth-related taxes" — base, broader than any single policy.
4. Compare to PolicyEngine-UK's evolution: started with UBI scenarios, evolved into a full tax-benefit simulator. WealthLens should evolve from HVCTS into a wealth-tax simulator that also handles property tax reform, devolved taxation, and CGT/IHT scenarios.

---

### Deliverable 25 — EU/International Comparators

| Country | Wealth tax status | Useful for WealthLens |
|---|---|---|
| Spain | Wealth tax + temporary solidarity tax | Threshold design; regional asymmetry (Madrid 0%) |
| Norway | Annual wealth tax; reduced top rate 2017–2020 | Ring 2020 elasticity; mobility evidence |
| Switzerland | Cantonal wealth taxes; highest in developed world | Brülhart et al. 2022: "a 1 percentage point drop in a canton's wealth tax rate raises reported taxable wealth by at least 43 percent after 6 years" |
| France | IFI (real-estate-only since 2018) | Behavioural response when broader wealth tax abolished |
| Argentina | One-off solidarity contribution 2020 | Real-world one-off levy precedent |
| Denmark | Abolished 1997; rich administrative data | Jakobsen et al. 2020 elasticity |
| Sweden | Abolished 2007 | Seim 2017 elasticity |
| Netherlands | Box 3 wealth tax (presumptive) | Implementation challenges |

WealthLens should ship a "comparator card" for each country in the dashboard, citing the relevant paper and transferability score.

---

### Deliverable 26 — Pre-Mortem Methodology

At each phase gate (1, 1.5, 2, 3):
1. Convene 5–7 advisors anonymously (Google Form).
2. Ask: "Imagine v0.X has been published and is now publicly criticised. What is the most likely failure mode?"
3. Categorise responses (methodology / communication / governance / data / behavioural / political).
4. Anonymise; publish findings as a "what we worried about" appendix to the corresponding release.
5. Update risk register accordingly.

---

### Deliverable 27 — Governance Structure

- **Advisory board (5–7 members)**: meets quarterly; reviews methodology audits; signs off on major releases. COI policy: declare all consulting, advocacy, and political affiliations annually.
- **Scenario-design firewall**: funders may suggest scenario *families* but cannot specify *parameters*. Documented in `docs/MODEL_CHARTER.md`.
- **Annual methodology audit**: rotating external auditor publishes a brief; auditor cannot be a current funder.
- **Whistleblower process**: anonymous channel for staff/contributors to flag advocacy capture.
- **Conflicts**: founder + advisors + funders register published on GitHub; reviewed quarterly.

Comparators: PolicyEngine has lighter governance via academic affiliations; IFS has heavyweight charity governance built on decades of trust; OBR has a statutory mandate not replicable for an open-source project. WealthLens is closest to PolicyEngine, plus an explicit firewall.

---

### Deliverable 28 — Engagement Approach: HMRC, OBR, Treasury

| Body | First contact | What to offer | What NOT to ask |
|---|---|---|---|
| HMRC | EOI for Datalab via `hmrc.datalab@hmrc.gov.uk`; lead through CenTax's existing relationship | Replication code; enforcement-scenario library | Data on named taxpayers |
| OBR | "Note for OBR economists" PDF, sent to OBR feedback inbox | Open-source comparator for their HVCTS forecast; methods note | Endorsement of any policy scenario |
| HM Treasury | Through CenTax via James Murray's office (who keynoted CenTax launch); offer briefing | Independent revenue ranges; provenance discipline | Pre-budget briefing role; private modelling work |
| HMT (No.10 policy team) | Through PolicyEngine's Nikhil Woodruff (former Innovation Fellow) | Open-source benchmarking | Direct policy advice |

Trust-building sequence: 6 months of replication & methods notes before any direct policy ask.

---

### Deliverable 29 — Behavioural Priors Registry (priors.yml)

```yaml
- id: P-001
  domain: annual_wealth_tax
  context: switzerland_brulhart_2022
  prior_distribution: "lognormal(mu=log(0.43), sigma=0.2)"
  source_doi: 10.1257/pol.20200258
  source_quote: "a 1 percentage point drop in a canton's wealth tax rate raises reported taxable wealth by at least 43 percent after 6 years"
  transferability_score: medium
  notes: |
    Switzerland has no third-party reporting of financial wealth; this
    inflates elasticity vs likely UK setting with HMRC reporting.
  applies_to: [family_a, family_b]
  valid_range: [0.20, 0.80]

- id: P-002
  domain: annual_wealth_tax
  context: uk_advani_tarrant_2021
  source_quote: "Under a well-designed wealth tax covering all asset classes – as we assume ours will – the overall magnitude of behavioural responses could be limited to a 7–17 per cent reduction in wealth in response to a 1 per cent tax rate on wealth"
  prior_distribution: "uniform(0.07, 0.17)"
  transferability_score: high
  applies_to: [family_a, family_b]
```

Target: 50+ entries by v0.1. Each entry queryable from the dashboard so users see, on hover, which priors are driving each estimate.

---

### Deliverable 30 — Assumption Registry Schema (assumptions.yml)

```yaml
- id: A-014
  domain: top_tail
  value_or_distribution: "Pareto alpha = 1.5 (95% CI [1.4, 1.7])"
  source: "Vermeulen 2018; recalibrated to WAS round 8 + STRL 2025"
  transferability_score: high
  valid_range: [1.2, 1.9]
  applies_to: [all_revenue_estimates]
  last_reviewed: 2026-05-21
  notes: "Below 1.2 implies implausibly fat tail; above 1.9 contradicts STRL evidence."
```

Target: 50+ entries by v0.1. Surfaced in dashboard tooltips. Every published number's API response includes the assumption IDs that bind on it.

---

### Deliverable 31 — Provenance Manifest

```json
{
  "value": 0.43e9,
  "unit": "GBP/year",
  "credible_interval": [0.30e9, 0.55e9],
  "policy": "HVCTS_4_band_2026_values",
  "macro_baseline_version": "ons_nbs_2024_dec2025",
  "fiscal_event_anchor": "autumn_budget_2025",
  "code_version": "wealthlens-sim@v0.1.0-rc3",
  "git_commit": "a1b2c3d4...",
  "data_version": "enhanced_frs_2022_23_topcorrected_v1",
  "source_ids": ["S-021", "S-034", "S-067"],
  "assumption_ids": ["A-014", "A-019", "A-027"],
  "prior_ids": ["P-001", "P-002"],
  "generated_at": "2026-07-09T11:23:00Z",
  "generated_by": "wealthlens-sim/scenarios/run/family_e_hvcts.py",
  "uncertainty_method": "monte_carlo_sobol_n=10000"
}
```

This envelope rides on every API response and is surfaced in dashboard tooltips. It is the operational embodiment of the "no naked point estimates" rule.

---

### Deliverable 32 — Dashboard Safety Features (Gate 9)

UI patterns (all required for Gate 9 approval):
1. **Confidence intervals always visible** — never a point estimate without a band.
2. **Comparison-against-baseline always one click** — reform vs counterfactual always paired.
3. **Explainer tooltips on every chart** — clicking opens the provenance envelope + assumptions table.
4. **"What would falsify this?" pane** — for every revenue estimate, show which 2–3 assumption changes would flip the conclusion.
5. **"Out-of-range" warnings** — if user dials a parameter outside published transferability range, show a warning banner with the source paper.
6. **Shareable assumption-preserving links** — `/scenario/abc123` URL persists all assumptions; receiver sees exactly the same provenance.
7. **Naked point estimates blocked by UI** — no chart can render without uncertainty representation.

Inspiration: PolicyEngine's "household calculator" already does (1) and (2); Our World in Data's Grapher does (3); WealthLens is the first to do (4)–(7).

Frontend stack stays: Vue 3 + Pinia + Tailwind + D3 + Vite. New components: `ConfidenceFanChart.vue`, `BaselineCompareToggle.vue`, `ProvenanceTooltip.vue`, `FalsifierPane.vue`, `OutOfRangeBanner.vue`, `ShareableScenarioLink.vue`.

---

### Deliverable 33 — Testing Strategy

```
tests/
├─ unit/
│  ├─ test_tax_rules.py            # pytest, every tax variable
│  ├─ test_top_tail.py             # Vermeulen, GPD, rank correction
│  ├─ test_synth.py                # CTGAN, statistical matching
│  └─ test_uncertainty.py
├─ property/
│  ├─ test_tax_monotonicity.py     # Hypothesis — higher wealth ⇒ higher tax
│  └─ test_revenue_invariants.py
├─ snapshot/
│  ├─ test_wtc_replication.py      # WTC scenarios within ±5%
│  ├─ test_hmrc_aggregates.py      # within ±2%
│  └─ test_ons_nbs_reconciliation.py
├─ differential/
│  └─ test_policyengine_uk_parity.py
├─ data/
│  ├─ test_pandera_contracts.py
│  └─ test_great_expectations.py
├─ performance/
│  └─ test_simulator_perf.py       # full FRS × 1 scenario < 30s
└─ integration/
   ├─ test_scenario_run.py
   └─ test_provenance_envelope.py
```

Coverage target: 90%+ for `wealthlens_sim/`. Differential testing against PolicyEngine-UK for any shared computation. Snapshot tests on the WTC scenarios are the most important credibility signal.

---

### Deliverable 34 — Compute & Cost Envelope

Realistic monthly compute cost in steady state (v0.1):

| Component | Service | Monthly cost |
|---|---|---|
| Frontend hosting | GitHub Pages | £0 |
| API hosting | Fly.io 2× shared-cpu-1× | £30 |
| Redis cache | Upstash free tier | £0 |
| GitHub Actions CI | Free public minutes | £0 |
| Hugging Face data hosting | Free tier | £0 |
| Domain + SSL | Cloudflare | £8 |
| Monitoring | Sentry team | £25 |
| Zenodo | Free | £0 |
| **Subtotal infra** | | **£63** |
| Bayesian batch (monthly) | DigitalOcean GPU on-demand 4h | £30 |
| Monte Carlo full sweep | self-hosted or Fly.io machine | £40 |
| **Subtotal compute** | | **£70** |
| **Total** | | **~£135/month** |

Phase 5+ (multi-year + ABM): potentially 10× compute, still <£1,500/month — trivial against a £250–500k grant. GPU needed only for Phase 3+ (NumPyro Bayesian + any future RL). Not needed for v0.1.

---

### Deliverable 35 — DevOps Specifics

- **Branch protection** on `main`: require PR review (1+); require CI green; require signed commits via Sigstore gitsign; no force-push.
- **Pre-commit hooks**: ruff (lint + format), mypy (types), bandit (security), codespell (typos), nbstripout (notebook outputs stripped), Sigstore signing.
- **Releases**: semver; tagged; signed; SBOM (CycloneDX) attached; Zenodo DOI minted; Software Heritage archived.
- **Dependency management**: uv for Python; pnpm for JS; renovate-bot for automatic PRs.
- **Contributors**: DCO not CLA (lower friction; widely accepted by both academic and corporate contributors).
- **Code of Conduct**: Contributor Covenant 2.1.

---

### Deliverable 36 — AI/LLM Disclosure Policy

Document at `docs/AI_LLM_DISCLOSURE.md`:
- LLMs are used for code review, prose drafting, and methods-paper editing.
- LLMs are *not* used to generate revenue estimates, fit statistical models, or write tax-rule code that ships unreviewed.
- Every release notes which LLMs were used in production of the release notes.
- Any LLM-generated text in published outputs is reviewed by the PI; reviewed text is the PI's responsibility.
- Aligns with Nuffield Foundation's emerging norms on AI in research grants.

---

## Recommendations

**Stage 0 — Decide (this week)**:
1. Confirm AGPL-3.0 licence split. Add `LICENSE-AGPL` for the simulator core.
2. Email Arun Advani at CenTax with a 200-word project summary and a one-page "what we want, what we offer." Tone: methodological partnership, not endorsement-seeking.

**Stage 1 — Build (days 1–60)**:
3. Stand up `packages/wealthlens-sim/` skeleton; pin PolicyEngine-UK; open three good-first-issue PRs upstream.
4. Pull Land Registry, ONS HPI, WAS round 8 (EUL); build HVCTS reform module.
5. Submit HVCTS consultation response by 14 July 2026. **This is the single most important short-term deliverable**.

**Stage 2 — Fund (months 2–6)**:
6. Submit a Nuffield Foundation Strategic Fund one-pager to `strategicfund@nuffieldfoundation.org` once an institutional host is confirmed.
7. Apply to abrdn Financial Fairness Trust in parallel; their UKMOD support pattern is the strongest precedent.
8. Approach JRF Emerging Futures (Victoria Hughes) by warm introduction.

**Stage 3 — Publish (months 6–12)**:
9. Replicate WTC 2020 one-off levy scenarios within ±5%; submit replication paper to *Fiscal Studies*.
10. Ship top-tail diagnostic page with Vermeulen + GPD + rank-correction triangulation.
11. Implement Families A, B, C, D as reform modules; publish v0.1.

**Stage 4 — Mature (months 12–24)**:
12. Implement Families E, F, G.
13. Add behavioural wrappers with priors registry.
14. Publish robust-frontier visualisation.
15. Methodology audit + sustainability plan by month 24.

**Benchmarks/thresholds that would change these recommendations**:
- If CenTax declines partnership by month 3 → pivot to III/LSE as host; delay funding application by 3 months.
- If Nuffield outline declined twice → pivot to abrdn FFT + JRF as primary funders; reduce v0.1 scope.
- If HVCTS is dropped before April 2028 → de-prioritise Family E; accelerate Families A and C.
- If PolicyEngine-UK refuses upstream PRs for wealth tax → fork hard, but only as last resort.
- If annual wealth tax becomes politically hot pre-2027 → accelerate Families A and B; delay Families F and G.
- If a second funder is not secured by month 12 → scope back to an 18-month MVP and delay Phase 3.

---

## Caveats

1. **The CEC wealth-tax YAML in PolicyEngine-UK is a parameter scaffold with default rate=0 and threshold=0, not a working wealth-tax module.** Anyone citing "PolicyEngine has a wealth tax" should clarify it is an extension point, not a complete implementation.

2. **IFS Green Budget 2025 explicitly opposes a new annual wealth tax** (Adam, Delestre, Miller, October 2025; Key Finding 10: "We caution against introducing an annual wealth tax, which would face huge practical challenges... If the Chancellor wants to raise more from the better-off, a better approach would be to fix existing wealth-related taxes."). This must shape WealthLens's positioning — as transparency infrastructure, not as wealth-tax advocate. Any messaging that reads as advocacy will cost IFS-adjacent credibility.

3. **The Wealth Tax Commission headline figures must be cited precisely.** Advani–Hughson–Tarrant (2021, *Fiscal Studies*): an annual wealth tax of 0.17% on wealth above £500k would generate £10bn; a one-off 4.8% tax (effectively 0.95%/year over 5 years) on wealth above £500k would generate £250bn; at a £2m threshold, the same 1% rate would still raise more than £80bn after non-compliance and admin costs. The £0.4bn ↔ £80bn explainer must precisely characterise both poles to be defensible.

4. **HMRC Datalab assessment timeline is genuinely uncertain.** GOV.UK guidance says only "Applications are usually assessed several times a year" with "up to 3 years" wait for some series. Plan synthetic-data work to be 100% independent of Datalab in case the wait exceeds the grant horizon.

5. **The Sunday Times Rich List is a paywalled commercial product with opaque methodology** (Kennickell 2025 makes this point forcefully). Rich-list anchoring should always be presented as *one* of three estimators (Vermeulen, GPD, rank correction), never the primary.

6. **PolicyEngine-UK's enhanced FRS uses 2022-23 base data**; for 2026 analyses the model uprates rather than re-runs primary data. Worth flagging in methods notes — WAS round 9 (covering 2022–2024) was suspended from "accredited official statistics" status pending quality work, per ONS.

7. **AGPL-3.0 will deter some contributors**, particularly corporate ones who follow Google-style bans. The trade-off is worth it for a public-interest simulator but should be communicated openly in CONTRIBUTING.md.

8. **The 24-month, £250–500k envelope is tight.** PolicyEngine-UK's comparable budget over a similar period was higher and they had a head start. Plan for an 18-month MVP within the envelope and a deliberate stretch to 24 months only if a second funder is secured by month 12.

9. **None of the named advisors have agreed to anything**; all introductions are speculative until accepted. Treat the advisory board section as a target, not a roster.

10. **Synthetic FRS+WAS quality is bounded by what's publicly disclosable.** Any claim of "FRS-compatible" must be evaluated by comparison to the real enhanced FRS PolicyEngine ships, not to ground truth (which requires SecureLab access). Expect a 6–12 month iteration cycle on synthetic-data fidelity.

11. **HVCTS revenue is conditional on revaluation succeeding politically.** Some commentary expects mass valuation appeals; the £430m figure could be revised. WealthLens should track the consultation outcome and re-publish the brief if material changes occur.

12. **Phase 6 (ABM/RL) is speculative.** Frameworks named (Mesa, agentpy, Stable Baselines3, CleanRL) are reasonable but require dedicated team capacity not budgeted in the 24-month envelope. Do not promise Phase 6 in any funding application.
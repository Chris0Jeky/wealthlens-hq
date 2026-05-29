# Done

Completed tasks go here with completion date.

## 2026-05-29 — Merge cycle + Gate-1 simulator + Wave 12 start

Autonomous end-to-end cycle. Started with 38 open PRs; ended with 0 open PRs, main
CI green, 564 simulator tests passing, 0 Dependabot alerts. Every PR got 2
independent adversarial reviews; all findings of every severity addressed.

**Merge train (the entire Gate-1 simulator → `main`):**
- [x] Merge docs PRs: Model Charter #284, AI/LLM Disclosure #285 (@Chris)
- [x] Merge `packages/wealthlens-sim` skeleton + registries (#286); recreate auto-closed children as #314–#319 and merge (license split, sources/assumptions/baselines registries, Pydantic schema) (@Chris)
- [x] Fix broken inverted PR #293; merge assumption+baselines loaders (#319) (@Chris)
- [x] Merge the policy-family chain #295–#303 (top-tail Pareto reconstruction, provenance, Families A–G) rebased onto main (@Chris)
- [x] Merge prior-round review fix PRs #305–#308; redo #309→#320 (effective_date docs) (@Chris)
- [x] Resolve all Dependabot: batch #291 merged + #273–#283 closed; #311/#312/#313 merged (@Chris)
- [x] Delete 21 merged branches from origin; clean up stale locked worktrees (@Chris)

**Adversarial-review findings fixed (each its own reviewed PR):**
- [x] #321 top-tail: coerce int wealth to float (no silent truncation) + validate ci∈(0,1) (@Chris)
- [x] #322 provenance: faithful schedule preservation (replaced a silent-drop) + strict bool/int typing (@Chris)
- [x] #323 CI gap: add `ci-sim.yml` (ruff+mypy+pytest on py3.11/3.12 + weekly) — the simulator was never run in CI; + types-PyYAML + scipy mypy override (@Chris)
- [x] #324 IHT: deduct charitable gifts from estate + cap RNRB at residence value (data-integrity) (@Chris)
- [x] #325 security: npm overrides patch tmp (HIGH) + uuid (MED) → 0 Dependabot alerts (@Chris)
- [x] #326 packaging: bundle registries into wheel **and sdist** via conditional hatch build hook (review caught a sdist-uninstallable bug) (@Chris)

**Wave 12 (microsimulation engine) — design + first two PRs:**
- [x] Wave 12 design doc `docs/WAVE12_SIMULATION_ENGINE_DESIGN.md` (@Chris)
- [x] Wave 12 PR1 #327: `synth/` deterministic synthetic-population generator (lognormal body + Pareto tail; clearly-labelled synthetic) (@Chris)
- [x] Wave 12 PR2 #328: `rules/` Scenario + `run_scenario` dispatching revenue families A–E → total + revenue_by_nation (@Chris)

## 2026-05-16

- [x] Deploy Vue frontend to GitHub Pages as master site — live at https://chris0jeky.github.io/wealthlens-hq/ (@Chris)
- [x] Merge all ~192 PRs in 10 review waves (155 feature PRs merged, 21 duplicates closed, 10 Dependabot merged, 6 risky majors closed) (@Chris)
- [x] Post-merge health check — fix lint (ruff), types (mypy, vue-tsc), tests; 874 tests passing across all suites (@Chris)
- [x] Build 7 additional data pipelines: wealth-by-decile, productivity-pay, GDHI, tax-composition, BoE-rates, child-poverty, generational-wealth (@Chris)
- [x] Build FastAPI backend: health, data listing, metadata, columns, summary stats, CSV download, security headers, GZip, rate limiting, error envelope (@Chris)
- [x] Build Vue 3 frontend: AppHeader, AppFooter, NavBar, dark mode toggle, DatasetCard, DatasetDetailView, ChartView with broadsheet redesign, About page, 404 page, PWA manifest (@Chris)
- [x] Build 40+ frontend components and composables: Tooltip, Modal, Toast, Badge, ProgressBar, SkeletonLoader, CopyButton, EmptyState, NumberStat, TabGroup, Accordion, FilterChips, DropdownMenu, ConfirmDialog, StatusDot, AlertBanner, ResponsiveGrid, PageHeader, ChartContainer, SourceCitation, plus composables for fetch, debounce, clipboard, localStorage, intersectionObserver, mediaQuery, eventListener, keyboardShortcut, clickOutside, reducedMotion (@Chris)
- [x] WCAG audit and fixes: colour contrast, focus indicators, skip links, reduced motion, ARIA labels (@Chris)
- [x] Frontend analytics integration (privacy-respecting) (@Chris)
- [x] chart_to_social.py — generate social media images in 4 platform sizes (@Chris)
- [x] Merge 10 Dependabot dependency bumps (safe minor/patch) (@Chris)
- [x] Close 6 risky major version bumps: pandas 3, TypeScript 6, Vite 8, vue-router 5, vue-tsc 3 (deferred for careful migration) (@Chris)
- [x] Clean up 292 stale local branches + 204 stale remote branches — repo now only has `main` (@Chris)
- [x] Update README, ORCHESTRATION.md, active-sprint, done.md, inbox.md to reflect actual state (@Chris)

## 2026-05-15

- [x] Scaffold FastAPI backend with `/health` and `/api/data/{name}` endpoints (@Chris)
- [x] Scaffold Vue 3 + TypeScript + Pinia + TailwindCSS frontend (builds clean) (@Chris)
- [x] Deploy v0.1 to GitHub Pages — site live with 4 Plotly charts (@Chris)
- [x] Create 10 waves of reviewed PRs (stacked PRs with adversarial multi-agent review) (@Chris)

## 2026-05-14

- [x] Create initial WealthLens HQ scaffold (@Codex) [due: 2026-05-14]
- [x] Extract all research insights into `research/synthesised/key-insights.md` — 48 insights across 8 categories (@Chris)
- [x] Populate `tasks/inbox.md` with ~200 action items from all research (@Chris)
- [x] Create `tasks/active-sprint.md` with 7 highest-priority tasks for this week (@Chris)
- [x] Populate `tasks/outreach/contacts.md` with 120+ people and organisations (@Chris)
- [x] Populate `tasks/social-media/accounts-to-follow.md` with 80+ accounts across X, Bluesky, LinkedIn, podcasts, newsletters (@Chris)
- [x] Populate `tasks/outreach/emails-to-send.md` with 8 draft emails + 3 templates (@Chris)
- [x] Populate `research/data-sources/data-source-registry.md` with 80+ data sources including URLs, formats, licences (@Chris)
- [x] Populate `research/reading-list/queue.md` with 60+ books, 30+ papers, 10+ courses, subscriptions (@Chris)
- [x] Populate `tasks/social-media/content-calendar.md` with 2-week plan + content pillars + recurring formats (@Chris)
- [x] Order *The Trading Game* (Gary Stevenson) and *A Brief History of Equality* (Piketty); started reading *The Trading Game* (@Chris)
- [x] Create Twitter/X and Bluesky accounts with mission-focused bios (@Chris)
- [x] Build 3 reproducible data pipelines in `automation/data-pipelines/`: fetch_wid_data.py, fetch_ons_housing.py, fetch_hmrc_stats.py (@Chris)
- [x] Generate 3 interactive Plotly charts in `projects/wealthlens-dashboard/charts/`: WID wealth shares (1820-2024), ONS housing affordability by region (1997-2025), HMRC CGT concentration by gain size (@Chris)
- [x] Send volunteer email to Democracy Club (hello@democracyclub.org.uk) (@Chris)
- [x] Send volunteer email to mySociety (whofundsthem@mysociety.org) (@Chris)
- [x] Subscribe to 5 newsletters: Resolution Foundation "Top of the Charts", Dan Neidle's Tax Policy Associates, Branko Milanovic, Adam Tooze "Chartbook", IFS publications (@Chris)
- [x] Move "Gaps and Contradictions" guidance to `research/synthesised/gaps-and-contradictions.md` for permanent reference (@Claude)

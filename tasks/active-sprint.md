# Active Sprint

Last updated: 2026-05-23

This week's focus. Keep this list to 5-7 tasks.

## Sprint: 2026-05-21 to 2026-05-28

1. - [x] Sim skeleton: package structure, pyproject.toml, AGPL licence (@Chris) [completed: 2026-05-22]
2. - [x] Pydantic schema module: households, policies, results (PR #292) (@Chris) [completed: 2026-05-23]
3. - [x] Assumption registry loader with validation (PR #293) (@Chris) [completed: 2026-05-23]
4. - [ ] Baselines registry loader with validation (@Chris) [due: 2026-05-25]
5. - [ ] Top-tail Pareto reconstruction module (Blueprint §5.1-5.3) (@Chris) [due: 2026-05-27]
6. - [ ] Family A: annual wealth tax calculator (Blueprint §9.1) (@Chris) [due: 2026-05-28]
7. - [ ] Provenance manifest system (Blueprint §13.4) (@Chris) [due: 2026-05-28]

## Why These Seven

- **Sim skeleton (1-3):** Gate 1 deliverables complete. Schema layer and assumption loader provide the type foundation for all policy modules.
- **Baselines loader (4):** Parallel to assumption loader; loads registries/baselines.yml with policy status matrix.
- **Top-tail (5):** Blueprint §5 is the critical data-quality layer — without Pareto reconstruction, wealth totals undercount the top by ~£600bn.
- **Family A (6):** The headline policy module — annual wealth tax. Most requested, most visible, drives the revenue simulator.
- **Provenance (7):** Blueprint §13.4 requires every published number to carry a provenance manifest. Wire this early before outputs proliferate.

## Completed This Sprint

- [x] Extract all research insights, action items, contacts, and data sources into structured files (@Chris) [completed: 2026-05-14]
- [x] Create initial WealthLens HQ scaffold (@Codex) [completed: 2026-05-14]
- [x] Order *The Trading Game* by Gary Stevenson and *A Brief History of Equality* by Piketty; begin reading (@Chris) [completed: 2026-05-14]
- [x] Create Twitter/X account and Bluesky account (@Chris) [completed: 2026-05-14]
- [x] Build 3 data pipelines + interactive Plotly charts: WID wealth shares, ONS housing affordability, HMRC CGT concentration (@Chris) [completed: 2026-05-14]
- [x] Send volunteer emails to mySociety and Democracy Club (@Chris) [completed: 2026-05-14]
- [x] Subscribe to 5 key newsletters: Resolution Foundation, Tax Policy Associates, Milanovic, Tooze, IFS (@Chris) [completed: 2026-05-14]
- [x] Scaffold FastAPI backend with health, data, metadata endpoints (@Chris) [completed: 2026-05-15]
- [x] Scaffold Vue 3 + TypeScript + Pinia + TailwindCSS frontend (@Chris) [completed: 2026-05-15]
- [x] Deploy Vue frontend to GitHub Pages as master site (@Chris) [completed: 2026-05-16]
- [x] Merge all ~192 PRs (10 waves of reviewed, stacked PRs) — zero open PRs remain (@Chris) [completed: 2026-05-16]
- [x] Resume interrupted PR cleanup and merge remaining reviewed PRs through #272; final main CI green and zero open PRs remain (@Codex) [completed: 2026-05-17]
- [x] Post-merge health check — fix lint, types, tests; 874 tests passing, all CI green (@Chris) [completed: 2026-05-16]
- [x] Clean up 292 local + 204 remote stale branches (@Chris) [completed: 2026-05-16]

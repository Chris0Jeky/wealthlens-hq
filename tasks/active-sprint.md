# Active Sprint

Last updated: 2026-05-29

This week's focus. Keep this list to 5-7 tasks.

## Sprint: 2026-05-29 to 2026-06-05

**Context:** The entire Gate-1 simulator (skeleton, schema, loaders, top-tail
reconstruction, provenance, all 7 policy families A–G) is now MERGED to `main`
via the 2026-05-29 merge train (PRs #284–#322). 515 sim tests pass locally.

1. - [x] CI gap: add `packages/wealthlens-sim` to CI — ci-sim.yml (ruff+mypy+pytest, py3.11/3.12, weekly) + types-PyYAML + scipy mypy override (PR #323) (@Chris) [completed: 2026-05-29]
2. - [x] IHT v0.1 limitations: deduct charitable bequest from estate; cap RNRB at residence value (PR #324) (@Chris) [completed: 2026-05-29]
3. - [ ] Package registries as data files (importlib.resources) so `pip install wealthlens-sim` can load sources/assumptions/baselines (@Chris) [due: 2026-06-03]
4. - [ ] Wave 12: static microsimulation engine module (`engine/`) — apply policy families to synthetic households (Blueprint §8) (@Chris) [due: 2026-06-05]
5. - [ ] Wave 12: synthetic FRS+WAS household generator (`synth/`) so the engine has inputs (Blueprint §6) (@Chris) [due: 2026-06-05]

## Why These Five

- **CI gap (1):** Highest priority — the simulator is currently untested in CI; a regression could land on `main` undetected. Discovered during the merge-train audit.
- **IHT limitations (2):** Adversarial review flagged charitable-bequest and RNRB-cap simplifications that bias revenue; must fix or fence off before any published figure.
- **Packaging (3):** Registries live outside the package; distribution is broken until resolved via importlib.resources.
- **Engine + synth (4,5):** Wave 12 — the policy families exist but nothing drives them yet. A static engine over synthetic households turns the library into a working simulator (the next visible milestone).

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

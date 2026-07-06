# AGENT_MAP — WealthLens HQ seam map

Last verified: 2026-07-06 · Update this map as part of Definition of Done when a seam
moves. Task prompts should name a region; log a one-line reason before reading outside it.

## Regions

| Region | Entry points | Invariants | Verify |
| --- | --- | --- | --- |
| **dashboard-frontend** `projects/wealthlens-dashboard/frontend/` | `src/views/` (chart pages), `src/config/chartArticles.ts`, `src/constants/datasetProvenance.ts` (single source of truth for Data Sources + Methodology provenance), `src/components/` | Every public figure cites source + URL + access date; WCAG AA; WAS charts carry the accreditation caveat (`research/methodology/was-caveats.md`); `public/data/` is GENERATED — never `git add` | `make frontend-lint frontend-typecheck frontend-test` (build: `frontend-build`; CI: ci-frontend + e2e + lighthouse) |
| **dashboard-backend** `projects/wealthlens-dashboard/backend/` | `app/` FastAPI (health, data, metadata, columns, summary, CSV) | Fail loudly; no endpoint fabricates or transforms figures silently | `make ci-quick` (= backend-lint + backend-test; CI: ci-backend) |
| **sim** `packages/wealthlens-sim/` | `wealthlens_sim/engine.py::simulate` (NOT `run_scenario` — that name is taken by `rules.run_scenario`), registries at repo-root `registries/` (bundled via `hatch_build.py`), `outputs/to_dashboard_json` (versioned public schema) | Every parameter cites a registry source; behavioural layer stays default-OFF until cited base-share data exists (decision D-B); synth population is labelled illustrative (~£26tn overshoot vs ~£15–16tn real) | `cd packages/wealthlens-sim && python -m pytest -q` (853 tests; CI: ci-sim, 3.11+3.12 + 90% coverage gate) |
| **data-pipelines** `automation/data-pipelines/` | `fetch_*.py`, `run_all.py` (`SCRIPTS` is the single pipeline list, guarded by `test_run_all.py`), `validate.py` | Reproducible; outputs land in `projects/wealthlens-dashboard/data/processed/` + `charts/`; every dataset records source, URL, access date, licence | `make pipeline-test` + `make validate` (CI: ci-pipelines; weekly refresh is manual `workflow_dispatch` — see #494) |
| **ops / command-centre** `tasks/`, `docs/`, `.github/` | `tasks/ACTION-REQUIRED.md` (Chris-only items — surface every summary), `tasks/active-sprint.md`, `docs/agentic/` (protocols), `docs/adr/` | Task/date formats per AGENTS.md; merges via `docs/agentic/REVIEW_GATE.md`; ACTION-REQUIRED cleared only by Chris | markdown only — no test lane |

Repo-wide harness: `.claude/tier.json` (T3, push free / merge gated), floor smoke test
`python .claude/hooks/smoke_test.py`, pre-push gate `make ci-quick`.

## Do NOT read by default

Skip unless the task explicitly requires them — they are large, generated, private-path,
or decided-and-closed:

- `research/raw/**` — raw LLM research dumps (large, low signal)
- `strategy/**`, `vision/**` — only for content/strategy/prioritisation tasks
- `docs/product/rfc/**` + `docs/product/frontier-candidates-2026-07.md` — post-launch
  portfolio; scored and sequenced, do not re-litigate (see the anti-portfolio)
- `tasks/inbox.md` (~765 lines) — untriaged backlog; open only when triaging
- `projects/wealthlens-analyst/` — EXTRACTED to `Chris0Jeky/wealthlens-analyst`
  (PR #491); only `POINTER.md` remains
- `node_modules/`, `.venv/`, `.claude/worktrees/`, `.idea/`, `__pycache__/`
- `../hq-private/**` — private sibling repo; Chris-only paths, skip on volunteer machines

## Minimum handoff shape

```text
## Changed / ## Verified / ## Not verified / ## Failures-workarounds / ## Status sync / ## Next slice
```

Region-local rules live in each region's own `CLAUDE.md` (auto-loaded when files there
are touched), detail stays out of this map.

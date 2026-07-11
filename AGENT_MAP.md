# AGENT_MAP — WealthLens HQ seam map

Last verified: 2026-07-06 · Update this map as part of Definition of Done when a seam
moves. Task prompts should name a region; log a one-line reason before reading outside it.

## Regions

| Region | Entry points | Invariants | Verify |
| --- | --- | --- | --- |
| **dashboard-frontend** `projects/wealthlens-dashboard/frontend/` | `src/views/` (chart pages), `src/config/chartArticles.ts`, `src/constants/datasetProvenance.ts` (single source of truth for Data Sources + Methodology provenance), `src/components/` | Every public figure cites source + URL + access date; WCAG AA; WAS charts carry the accreditation caveat (`research/methodology/was-caveats.md`); `public/data/*` is generated + gitignored except the committed JSON whitelist in `.gitignore` — regenerate via the static-API script, do not hand-add new files there | `make frontend-lint frontend-typecheck frontend-test` (build: `frontend-build`; CI: ci-frontend + e2e + lighthouse) |
| **dashboard-backend** `projects/wealthlens-dashboard/backend/` | `app/` FastAPI (health, data, metadata, columns, summary, CSV; `/api/simulator` router serves the sim's dashboard JSON) | Fail loudly; no endpoint fabricates or transforms figures silently | `make ci-quick` (= backend-lint + backend-test; CI: ci-backend) |
| **sim** `packages/wealthlens-sim/` | `wealthlens_sim/engine/` package — entry point `engine.simulate` (NOT `run_scenario`, which is `rules.run_scenario`), registries at repo-root `registries/` (bundled via `hatch_build.py`), `outputs/to_dashboard_json` (versioned public schema) | Every parameter cites a registry source; behavioural layer stays default-OFF until cited base-share data exists ([D-B]); synth population is illustrative — calibrated to the cited ONS WAS GB total (£13.568tn, `ONS_WAS_TOTAL_WEALTH_GBP`), a `test_synth` marginal pins it | `cd packages/wealthlens-sim && python -m pytest -q` (853 tests; CI: ci-sim, 3.11+3.12 + 90% coverage gate) |
| **data-pipelines** `automation/data-pipelines/` | `fetch_*.py`, `run_all.py` (`SCRIPTS` is the single pipeline list, guarded by `test_run_all.py`), `validate.py` | Reproducible; outputs land in `projects/wealthlens-dashboard/data/processed/` + `charts/`; every dataset records source, URL, access date, licence | `make pipeline-test` + `make validate` (CI: ci-pipelines; weekly refresh is manual `workflow_dispatch` — see #494) |
| **ops / command-centre** `tasks/`, `docs/`, `.github/` | `tasks/ACTION-REQUIRED.md` (Chris-only items — surface every summary), `tasks/active-sprint.md`, `docs/agentic/` (protocols), `docs/adr/` | Task/date formats per AGENTS.md; merges via `docs/agentic/REVIEW_GATE.md`; ACTION-REQUIRED cleared only by Chris | markdown only — no test lane |

Repo-wide harness (installed by the T3 migration, PR #492): `.claude/tier.json`
(T3, push free / merge gated), floor smoke test `python .claude/hooks/smoke_test.py`,
pre-push gate `make ci-quick`. Decision refs `[D-B]`/`[D-D]` are recorded in the private
`../hq-private/.../memories/decisions/` (Chris-only; skip on volunteer machines).

## Do NOT read by default

Skip unless the task explicitly requires them — they are large, generated, private-path,
or decided-and-closed:

- `research/raw/**` — raw LLM research dumps (large, low signal)
- `strategy/**`, `vision/**` — only for content/strategy/prioritisation tasks
- `docs/product/rfc/**` + `docs/product/frontier-candidates-2026-07.md` — post-launch
  portfolio; scored and sequenced, do not re-litigate (see the anti-portfolio)
- `tasks/inbox.md` (~765 lines) — untriaged backlog; open only when triaging
- `projects/wealthlens-analyst/` — being extracted to `Chris0Jeky/wealthlens-analyst`
  (PR #491); once that merges only `POINTER.md` remains. Until then the live Hero #1
  build is still here — read it only for analyst work, which now continues in the new repo
- `node_modules/`, `.venv/`, `.claude/worktrees/`, `.idea/`, `__pycache__/`
- `../hq-private/**` — private sibling repo; Chris-only paths, skip on volunteer machines

## Minimum handoff shape

```text
## Changed / ## Verified / ## Not verified / ## Failures-workarounds / ## Status sync / ## Next slice
```

Region-local rules live in each region's own `CLAUDE.md` (auto-loaded when files there
are touched), detail stays out of this map.

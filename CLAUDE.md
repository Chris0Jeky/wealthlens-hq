# CLAUDE.md — WealthLens HQ

T3 workshop · authority `.agent-harness/tier.json` (push free / merge free on the T3 gate).
Merge, review, worktree and question doctrine is the global twelve laws (`~/.claude/CLAUDE.md`,
auto-injected) — this file never restates them. Repo rules: [AGENTS.md](./AGENTS.md) ·
seams: [AGENT_MAP.md](./AGENT_MAP.md).

## What this repo is

Command-centre monorepo for WealthLens UK: a public source-cited wealth-inequality dashboard
(Vue 3 + TS frontend on GitHub Pages, FastAPI backend), the `wealthlens-sim` policy
microsimulation package, reproducible data pipelines, and the non-code workspace (tasks,
research, strategy, outreach). Multi-domain — decide whether a task is code, content, research
or outreach *before* reaching for tools. Public repo; sensitive material lives in the private
sibling `../hq-private` (never copy it here; skip private paths when the sibling is absent —
volunteer machines). Hero #1 (Analyst RAG) was extracted 2026-07-06 to
`Chris0Jeky/wealthlens-analyst`; only `projects/wealthlens-analyst/POINTER.md` remains.

## First five minutes

1. Read the SessionStart hook output — it prints tier/authority, open ACTION-REQUIRED items and
   a failure-ledger nudge. No file reads needed for that.
2. `AGENT_MAP.md` → pick the region the task names; that region's own `CLAUDE.md` binds when you
   touch its files. Honour the map's Do-Not-Read index (`research/raw`, `strategy/`, `vision/`,
   `tasks/inbox.md` are large and low-signal by default).
3. Chris's box only: newest RESUME block of
   `../hq-private/projects/wealthlens/memories/session_notes/ORCHESTRATION.md`, then
   `.../memories/00_ACTIVE.md`.

`tasks/ACTION-REQUIRED.md` = Chris-only items. Surface the open ones in **every** summary and
handoff under a `⚑ Action required:` banner; only Chris clears them, never infer completion.

## Proving checks by seam

Narrowest command that exercises the change. Timings measured 2026-07-27 on Chris's Windows box
(Git Bash; `PYTHON=python` is required — see pitfalls).

| Changed | Run | Measured |
| --- | --- | --- |
| backend `projects/wealthlens-dashboard/backend/**` | `make PYTHON=python ci-quick` | 77s green — ruff + mypy (34 files) + 207 passed / 28 skipped |
| frontend, one component/module | `cd projects/wealthlens-dashboard/frontend && npx vitest run <spec>` | ~3s per spec |
| frontend, before merge | `npx vitest run --maxWorkers=2` | 64s — 137 files / 1406 tests (default workers can OOM this box) |
| frontend types | `npm run typecheck` (= `vue-tsc -b --noEmit --force`) | 5s — build mode is load-bearing, see pitfalls |
| frontend lint | `npx eslint .` | 6s (warnings only, exit 0) |
| sim `packages/wealthlens-sim/**`, `registries/**` | `cd packages/wealthlens-sim && python -m pytest -q` | 7s — 853 passed |
| pipelines `automation/**` | `make PYTHON=python pipeline-test` | 4s — 75 passed |
| processed CSVs | `make PYTHON=python validate` | needs data present — main checkout, or after `make pipelines` (network) |
| hooks `.claude/hooks/**` | `python .claude/hooks/smoke_test.py` | **5m32s** — 2232/2232; budget for it, it is the floor's contract |
| docs / tasks / strategy markdown | no test lane — proofread and go | — |

`make PYTHON=python ci-quick` is the pre-push minimum; `ci-full` adds automation/tests mypy,
pipeline tests and the frontend lane. CI mirrors these as ci-backend / ci-frontend / ci-sim /
ci-pipelines + CodeQL, each path-filtered with a weekly catch-all cron; deploy, e2e and
lighthouse run on frontend pushes.

## Windows pitfalls (all measured 2026-07-27)

- **`make` alone dies.** `PYTHON := $(shell command -v python3 …)` resolves to the Windows Store
  stub → `Python was not found`, exit 49. Always `make PYTHON=python <target>`. Make itself needs
  Git Bash (GNU Make 3.81 + POSIX shell); it does not run from PowerShell.
- **`vue-tsc --noEmit` without `-b` proves nothing here.** Root `tsconfig.json` is `files: []` +
  project references, so it exits 0 in ~1s having checked no source (that was the `typecheck`
  script until 2026-07-27; the Build step's `vue-tsc -b` was the only real gate). Keep the `-b`
  in any type-check command you write.
- **`npm run format:check` is red locally, green in CI.** `core.autocrlf=true` + `* text=auto`
  give a CRLF worktree; prettier defaults to LF, so `--check` flags ~310 files. Never
  `prettier --write` to "fix" it — the ubuntu CI lane is the gate for formatting.
- **Lighthouse and Playwright e2e are CI-only.** Both need a built app (+ chromium); do not try
  to reproduce them locally — read the workflow logs instead.
- **`git worktree add` fails with `Filename too long`.** `research/raw/**` names blow MAX_PATH
  under a deep worktree root. Use `git -c core.longpaths=true worktree add …`, then
  `git -C <wt> config core.longpaths true` so later ops in that tree work.
- **`npm test` runs `pretest` = `git clean -fX src scripts vite.config.js vitest.config.js`**,
  deleting ignored shadow files in those paths — prefer `npx vitest run` if you keep scratch
  files there.
- **A fresh worktree has no processed data.** `projects/wealthlens-dashboard/data/processed/` is
  gitignored, so `make validate` and data-dependent scripts only work where pipelines have run.

## Repo-specific invariants

- Every public figure cites source + URL + access date; never change a headline number without a
  cited source (a Chris decision). No fabricated statistics, ever.
- Charts: WCAG AA minimum, mobile-responsive; WAS-derived charts carry the June-2025
  accreditation-loss caveat (`research/methodology/was-caveats.md`).
- New behaviour ships toggleable, default OFF. Narrow diffs over rewrites.
- `frontend/public/data/*` is generated by the static-API script and gitignored except a
  deliberate whitelist — regenerate, never hand-add.
- Hard guardrails (secrets, data integrity, auth, backward compatibility): AGENTS.md.

## Key paths

`tasks/ACTION-REQUIRED.md` (Chris-only) · `tasks/active-sprint.md` (priorities) ·
`tasks/deadlines.md` · `tasks/inbox.md` (untriaged, ~765 lines) ·
`research/data-sources/data-source-registry.md` · `strategy/branding-playbook.md` (public voice) ·
`docs/product/PRODUCT_FRONTIER_2026-07.md` (scored portfolio — do not re-litigate) ·
`docs/agentic/` (question protocol, failure ledger, git posture) ·
`../hq-private/.../memories/00_ACTIVE.md` (status board, private).

Skills: `wl-repo-onramp` (broad/unfamiliar) · `wl-safe-slice` (implement) ·
`wl-verify-and-sync` (close out) · `wl-question-batch` (ask vs assume).

## Who this is for

Chris — London software engineer, founder of WealthLens UK (BSc CS First, Middlesex 2025;
Springer SGAI-AI 2025 lead author; C#/.NET, Python, TypeScript; fuller context in
`../hq-private/identity/`). Mission: make UK wealth-inequality data accessible, interactive and
impossible to ignore — data first, opinion second; open source; accessible by default;
non-partisan. Prioritise: ship something real → make it visible → connect with the right people,
in that order. Volunteers read this code — clear docstrings; commit subjects
`<area>: <imperative summary>`.

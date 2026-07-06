# Region: data-pipelines

Reproducible fetch/process/chart scripts feeding the dashboard. Root seam map:
`/AGENT_MAP.md`.

## Invariants

- `run_all.py::SCRIPTS` is the ONE list of pipelines (guarded by `test_run_all.py`);
  never maintain a second list in Makefiles or workflows.
- Every dataset records source name, URL, access date, format, licence, update pattern
  (registry: `research/data-sources/data-source-registry.md`; licences additionally in
  `projects/wealthlens-dashboard/docs/data-licences.md`).
- Outputs land in `projects/wealthlens-dashboard/data/processed/` and `charts/` —
  committed last-good data is what the site serves (decision D-D); a fetch failure must
  fail closed, never publish partial data.
- No fabricated statistics, ever. A pipeline that cannot cite its source does not ship.

## Verify

- `make pipeline-test` (offline unit tests) + `make validate` (CSV validation).
- Live fetches: `make pipelines` (network; known upstream breakage tracked in #494 —
  weekly cron disabled, manual `workflow_dispatch` only).

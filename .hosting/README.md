# WealthLens hosting reference

Reference-only preparation, 2026-09-10. `manifest.json` is inert hosting-intake metadata. No chart, pipeline, backend, domain, account, name or deployment trigger is changed. Existing workflows still apply after a future merge.

This slice concerns the public static chart/site surface. Preserve its current published paths, embeds and source citations. Do not provision a separate FastAPI service or database solely to keep static charts reachable. The separate application and simulation workloads retain their existing contracts; a later feature can justify an independently reviewed host.

WL1 prepares canonical/base-path and embed compatibility for an owned hostname. Test each published chart, source/data download link, responsive layout and iframe/embed route. WL2 defines a publication allowlist using approved public build inputs only; private HQ/outreach content, account records and unregistered naming candidates must never be copied into this repository or site. WL3 prevents speculative shared SSO, paid data/model activation or extra services in a static-hosting migration.

Follow `AGENTS.md`, `CLAUDE.md`, the relevant map/region and existing task ownership. This is a reference, not a new agent workflow. Syntax: `python -m json.tool .hosting/manifest.json`. The repository's stated pre-push check is `make PYTHON=python ci-quick`; future chart/pipeline/code changes additionally need their relevant existing checks. JSON validation does not establish those results or data correctness.

Preserve the previous public build and stable chart aliases before any cutover. Do not rewrite published data meanings or source attributions to fit branding. Existing owner actions remain in `tasks/ACTION-REQUIRED.md`; this compatibility slice clears none of them.

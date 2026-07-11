---
name: wl-repo-onramp
description: Orient to the WealthLens HQ workspace before editing. Use at session start, when scope is vague, or when crossing into an unfamiliar area.
user-invocable: true
---

# WealthLens HQ Repo Onramp

Establish current truth before editing code, content, or docs.

## Use when / Do NOT use when

Use for broad or ambiguous work and unfamiliar areas. Do NOT use when the task
already names a region and files — go straight to that region via `AGENT_MAP.md`.

## Read first

1. `AGENT_MAP.md` — regions, invariants, verify commands, do-not-read index.
2. The head of `../hq-private/projects/wealthlens/memories/00_ACTIVE.md`
   (private sibling repo; skip if absent).

The SessionStart hook already printed tier/authority and the open ACTION-REQUIRED
items — do not re-read what it surfaced. Everything else loads on demand: the
region's own `CLAUDE.md` auto-loads when you touch its files.

## Produce a working summary

Extract only what the task needs: the region and domain (code, content, research,
outreach, strategy), the constraints that must not break (data integrity,
accessibility, non-partisan voice), and the likely files, tests, and docs affected.

## Guardrails

- Trust the private status board over older docs when they conflict.
- Do not bulk-read strategy/vision/identity/research archives (the map's
  Do-Not-Read index is the default).
- Keep the first implementation slice small and measurable.

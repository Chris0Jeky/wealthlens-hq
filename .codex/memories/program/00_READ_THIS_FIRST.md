# WealthLens HQ — Program Index

> Cross-cutting program context. Read after `00_ACTIVE.md`.

Last updated: 2026-05-14

## What is WealthLens HQ?

WealthLens HQ is the command-centre repository for WealthLens UK — an open-source project making UK wealth inequality data visible, interactive, and impossible to ignore.

This repo contains strategy, research, tasks, outreach, community planning, automation, and planned software products. It is not just a coding project.

## Program structure

```
wealthlens-hq/
├── projects/           ← planned software products
│   ├── wealthlens-dashboard/   ← main product (v0.1 planned)
│   ├── landing-page/           ← project website (planned)
│   ├── newsletter/             ← newsletter infrastructure (planned)
│   └── social-media-assets/    ← brand assets (planned)
├── automation/         ← data pipelines, analysis, social media, CI/CD
├── research/           ← raw inputs, synthesised insights, data sources
├── strategy/           ← branding, content, growth, outreach, funding
├── vision/             ← mission, theory of change, north stars
├── identity/           ← about Cristian, CV, principles, skills
├── tasks/              ← active sprint, inbox, outreach, learning
├── .codex/             ← agent control plane (this directory)
├── .claude/            ← Claude Code skills and settings
├── .agents/            ← Codex skills
├── docs/agentic/       ← shared protocols (question, failure, git)
└── autodoc/            ← agent-facing code orientation (once code exists)
```

## Decision framework

When prioritising, optimise for:
1. Shipping something real
2. Making it visible
3. Connecting with the right people

## Key references

- [CLAUDE.md](../../CLAUDE.md) — Claude Code session contract
- [AGENTS.md](../../AGENTS.md) — repo-wide agent operating rules
- [00_ACTIVE.md](../00_ACTIVE.md) — current status board
- [tasks/active-sprint.md](../../tasks/active-sprint.md) — current priorities
- [vision/north-stars.md](../../vision/north-stars.md) — success metrics
- [strategy/branding-playbook.md](../../strategy/branding-playbook.md) — voice and positioning
- [research/data-sources/data-source-registry.md](../../research/data-sources/data-source-registry.md) — data catalogue

## Reading rules

- Always read `00_ACTIVE.md` before assuming what is in progress.
- Do not bulk-read strategy, vision, or identity docs unless the task requires them.
- Research raw files can be large — read only what the task needs.
- Session notes in `.codex/memories/session_notes/` are for multi-session continuity.

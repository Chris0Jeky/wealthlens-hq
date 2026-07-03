# Review Gate

How a change earns a merge in `wealthlens-hq`. This is the standing merge gate
for agent-driven work; it does not depend on any single external bot.

## Why this doc exists

The repo has leaned on third-party PR bots (gemini-code-assist, codex, Copilot)
as a review safety net. **gemini consumer code review is being sunset — all
review activity ceases 2026-07-17.** The merge gate must not degrade when it
does, so the load-bearing part of the gate is the agent's own **multi-lens
adversarial review**, with bots as a bonus pass, not a dependency.

## The gate (all must hold before merge)

1. **Two or more independent adversarial reviews.** Run as a `Workflow` with
   distinct lenses that do NOT share context or conclusions — e.g. correctness /
   edge-cases, security / data-integrity, tests / API-completeness. Each lens
   tries to *refute* the change and to find bugs, security holes, regressions,
   and missed requirements. Prefer distinct lenses over duplicate passes.
2. **Per-finding adversarial verification.** Every raised finding is checked by a
   separate verifier that defaults to REFUTED and only CONFIRMS if it can name a
   concrete failure (specific inputs → wrong outcome) against the code as
   written. This kills plausible-but-wrong findings before they cost a fix.
3. **Every confirmed finding, every severity, is resolved.** Fix it, or (if
   genuinely out of scope) seed a concrete follow-up task/issue and link it. No
   "non-blocking" hand-waving. Record each finding and its resolution.
4. **Bots are addressed, not required.** codex / Copilot / (until 2026-07-17)
   gemini comments are read and each is fixed or answered with reasoning. A bot
   being quota-limited or absent never blocks the gate — the workflow review
   above is what carries the rigor.
5. **Verification is real and green.** `make ci-quick` (or the package's
   lint + type-check + tests) passes locally on the exact diff, and CI is green.
   For code with a runtime surface, exercise the changed seam (a live check where
   one exists) — never claim tests passed unless they actually ran.
6. **Aged appropriately.** The PR stays open long enough for CI and any bots to
   weigh in — don't merge fresh.
7. **No unresolved blockers; backward compatibility preserved.** New behaviour
   ships toggleable, default OFF, unless the task says otherwise.

## What "independent" means

The lenses must not see each other's output before reporting, and the verifier
must not be the finder. In a `Workflow`, that means separate `agent()` calls with
no shared state, and a `Verify` phase that receives only the finding text plus the
code — not the other lenses' conclusions. See the review-workflow pattern in the
`Workflow` tool docs (find → adversarially verify → resolve).

## Merge mechanics

Squash-merge + delete the branch by default. For stacked PRs, merge tip-first or
retarget children to the base first, and never `--delete-branch` a stacked base
(it closes the children). Never force-push, rebase a shared branch, or amend after
pushing.

## Related

- `docs/agentic/QUESTION_PROTOCOL.md` — when to ask vs. proceed on an assumption.
- `docs/agentic/GIT_WORKFLOW.md` — safe vs. blocked git commands.
- `docs/agentic/FAILURE_LEDGER.md` — where unresolved failures/workarounds are recorded.

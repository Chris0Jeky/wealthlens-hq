# ⚑ ACTION REQUIRED — Chris's outstanding tasks

Last updated: 2026-06-13 (private-repo split EXECUTED under decision C; item 1 awaits Chris's confirm)

> **This file is the single curated list of things that need _Chris_ (a human),
> not the autonomous agent.** It exists so high-leverage actions never get lost in
> the 370-line `inbox.md` or the date-table in `deadlines.md`. Each item has a
> short _why_ and a step-by-step _how_.

## Protocol (for the agent — do not skip)

- **Read this file at the start of every session** (it is listed in CLAUDE.md /
  AGENTS.md "First 5 minutes" and the SessionStart hook).
- **Surface the open items in every summary, status update, handoff, and
  end-of-turn wrap-up.** Lead with anything time-sensitive (a `[due: …]` that is
  today/overdue) under a one-line `⚑ Action required:` banner. Keep it short — a
  numbered list of the open titles + due flags, then point here for the guides.
- **Only clear an item when Chris explicitly says it is done** (e.g. "I sent the
  emails", "mark the LinkedIn post done"). When he does: check the box, move it to
  the `## Done` section with `[completed: YYYY-MM-DD]`, and update the date.
  Do **not** auto-clear from inference.
- **Chris can add items** by describing them; convert each into the item format
  below (title, priority, why, how, done-when).
- If an item is genuinely agent-doable once Chris gives a go-ahead, note that under
  the item — but it still belongs here until he approves, because it is blocked on
  his decision.
- Keep this list **focused** (aim ≤ ~8 open items). The full backlog lives in
  `inbox.md`; all dated items live in `deadlines.md`. Promote into this file only
  what is currently actionable and important.

---

## Open items

### ⏰ Time-sensitive (act this week)

1. - [ ] **Private-repo split: EXECUTED (decision C) — say "done" to close** — **P1**
   - **Decision (Chris, 2026-06-13):** option **C** — remove from the public tip, accept history exposure (no rewrite). Recorded in `hq-private/MIGRATION.md`.
   - **Executed (agent, 2026-06-13):** all sensitive material lives in **`Chris0Jeky/hq-private`** (clone: `C:\Users\jekyt\source\hq-private`) and was removed from this public repo's tip; every doc/hook/skill reference repointed to `../hq-private/...`; `.gitignore` guards added so the paths can't be re-committed. Note: pre-2026-06-13 history still contains the files (that is what C accepts) — treat CVs/contacts as already-seen.
   - **Done when:** you confirm, and this item moves to Done.

2. - [ ] **BGV: prep for Spring 2027** (Autumn 2026 SKIPPED — decided 2026-06-05) — **P2 (no longer this-week-urgent)**
   - **Decision (2026-06-05):** skip the BGV Autumn 2026 round (deadline was 21 June) and target **Spring 2027** (~early-Jan 2027 deadline), to clear the two blockers first rather than rush a weak 16-day application against ~3-4% odds. Full rationale: `../hq-private/projects/wealthlens/funding/bgv-go-no-go-2026.md` (private repo).
   - **How (over summer/autumn 2026):** decide the legal structure (UK for-profit Ltd vs keep the CIC/charity option — BGV only funds for-profit-companies-limited-by-shares, so this forecloses one path either way); line up at least one co-founder; draft a one-page impact + revenue thesis. Then apply when Spring 2027 opens.
   - **Done when:** Spring 2027 application submitted, OR re-decided.

### 🚀 Unblocked & high-leverage (v0.1 is live — these were waiting on a public URL)

3. - [ ] **Publish the first LinkedIn post + update your LinkedIn profile** — **P1**
   - **Why:** "Make it visible" is north-star #2. The site is live; the launch story is the single highest-visibility action available and it has been blocked only on you.
   - **How:**
     1. **Post:** "Why I'm building WealthLens UK" — personal story (housing/wages/opportunity, your WP work), the problem (UK wealth inequality is invisible), the build (live link + one chart screenshot), the ask (volunteers/feedback). Tone per `strategy/branding-playbook.md`: confident, data-driven, non-partisan.
     2. **Profile:** headline + About + Featured (WealthLens, Springer paper, WP outreach, Taskdeck) + add skills (Data Visualisation, Open Data, Economic Research, Widening Participation). Copy guidance is in `strategy/`.
   - **Done when:** post is live and profile updated. (Then tell me — I'll tick the related `inbox.md` content items too.)

4. - [ ] **Send the four unblocked outreach emails** — **P1**
   - **Why:** Partnerships are north-star #3 and these were all gated on "v0.1 live", which is now true.
   - **Targets:** Tax Justice UK (`info@taxjustice.uk`), Patriotic Millionaires UK (website contact form), The Equality Trust (`info@equalitytrust.org.uk`), Gary Stevenson (DM `@garyseconomics` on X).
   - **How:**
     1. **Check `../hq-private/projects/wealthlens/outreach/contacts.md` and `emails-sent.md` first** (private repo) — never double-contact (AGENTS.md outreach rule).
     2. Per email: professional, specific, value-offering (not asking favours); include the **live link** and one concrete chart relevant to them; one clear ask.
     3. Log each in `../hq-private/projects/wealthlens/outreach/emails-sent.md` with the date.
   - **Done when:** all four sent and logged. (I can draft any/all of these for you on request.)

5. - [ ] **Register the `wealthlens.uk` domain** — **P2 (foundational)**
   - **Why:** Unblocks a project email (`hello@wealthlens.uk`), a custom deploy domain, and Bluesky handle verification. Cheap, one-time, and several other tasks depend on it.
   - **How:** Buy via any UK registrar (`.uk` is cheap). Also grab `wealthlensuk.org` if available. Then I can wire Cloudflare Pages / DNS when you're ready.
   - **Done when:** domain owned (note the registrar + renewal date here or in `deadlines.md`).

### 🛠 Decision needed (agent is blocked on your go-ahead)

6. - [ ] **Hero #1: review the 20 DRAFT golden questions (H1-02)** — **P1, ~1 focused hour**
   - **Why:** Every eval claim in the WealthLens Analyst inherits its credibility from this file. The agent is forbidden from writing the answers (no fabricated ground truth) — only you can. M2's recall measurement and everything after it waits on this.
   - **How:**
     1. Open `projects/wealthlens-analyst/evals/golden/golden_set.jsonl` (20 records: 15 in-corpus, 5 refusal probes; each has a reviewer note).
     2. Rewrite any question freely; for the 15 in-corpus ones fill `expected_answer` + `required_citations` (source_id from `registries/sources.yml`); flip `status` to `REVIEWED`.
     3. Leave the 5 refusal probes' answers EMPTY (the deterministic check enforces this).
     4. Run `make PYTHON=python eval-golden-validate` — it must pass.
   - **Done when:** no `status: DRAFT` remains in the first 20.

7. - [ ] **Hero #1: rule on ADR 0003 D3 — hosting** — **P1, small decision (needs your account + card)**
   - **Why:** The only still-open locked-plan decision (D1/D2/D4 were adopted under your delegation). M6's live URL needs a host; the memo in `docs/adr/0003-reranker-embedding-hosting-selection.md` compares Hetzner / Fly+Neon / Railway / Supabase with verified prices.
   - **How:** Read the D3 table + Langfuse sizing note. Recommendation: **Hetzner CAX21** (8GB, ~£7/mo, everything on-box incl. Langfuse) or CAX11 (~£4.2/mo) with Langfuse placed separately. Decide, create the account, then tell the agent — provisioning (Docker Compose, Caddy, pg_dump cron) is agent-doable from there (H1-30).
   - **Done when:** D3 is ticked in the ADR's decision record and ADR 0003 flips to Accepted.

8. - [ ] **Merge the `make ci-quick` reliability fix (PR #350)** — **P2, authorized + done, pending merge**
   - **Status (2026-06-05):** you authorized this; **fixed in PR #350**. The Makefile no longer swallows failures (`|| echo …` removed), so `make ci-quick` now runs real ruff + mypy + pytest and fails loudly. The dashboard-backend failures it used to hide are already resolved — a real run now shows **201 passed**. PR #350 also installs dev deps in `backend-install`, adds job timeouts, and enables Dependabot auto-merge.
   - **Repo-setting actions for you (3, one-time)** — for Dependabot auto-merge to work end-to-end:
     1. **Settings → General → Allow auto-merge** (ON), else `gh pr merge --auto` errors.
     2. **Branch protection on `main`** requiring the CI checks (so auto-merge only completes on green).
     3. **Settings → Actions → General → Allow GitHub Actions to create and approve pull requests** (ON) — personal repos default this OFF, and without it the workflow's `gh pr review --approve` step fails. (Surfaced by review on #350; the workflow now documents this prerequisite.)
   - **Note:** #350 was hardened further during review this session — `requirements-dev.txt` now pins ruff/mypy/httpx/pandas-stubs so a clean `make install && make ci-quick` genuinely passes, and `pipeline-test`/`frontend-install` were fixed. All findings addressed; CI green.
   - **Done when:** PR #350 merges (then move this to Done).

---

## Done

_(Cleared items move here with `[completed: YYYY-MM-DD]` once Chris confirms.)_

- [x] **Prepare for mySociety interview (if shortlisted)** — **not shortlisted: application rejected** (Chris confirmed 2026-06-11). Recorded per the item's done-when. Interview-prep habits (daily no-AI Python practice, Exercism) remain useful for future applications — see `../hq-private/career/applications/interview-prep-general.md` (private repo). [completed: 2026-06-11]

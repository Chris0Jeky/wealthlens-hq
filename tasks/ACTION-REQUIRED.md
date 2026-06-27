# ⚑ ACTION REQUIRED — Chris's outstanding tasks

Last updated: 2026-06-27 (session 12; added item 9 — OPENAI_API_KEY blocks the Analyst's dense-retrieval chain H1-11→H1-13→H1-18)

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

1. - [ ] **BGV: prep for Spring 2027** (Autumn 2026 SKIPPED — decided 2026-06-05) — **P2 (no longer this-week-urgent)**
   - **Decision (2026-06-05):** skip the BGV Autumn 2026 round (deadline was 21 June) and target **Spring 2027** (~early-Jan 2027 deadline), to clear the two blockers first rather than rush a weak 16-day application against ~3-4% odds. Full rationale: `../hq-private/projects/wealthlens/funding/bgv-go-no-go-2026.md` (private repo).
   - **How (over summer/autumn 2026):** decide the legal structure (UK for-profit Ltd vs keep the CIC/charity option — BGV only funds for-profit-companies-limited-by-shares, so this forecloses one path either way); line up at least one co-founder; draft a one-page impact + revenue thesis. Then apply when Spring 2027 opens.
   - **Done when:** Spring 2027 application submitted, OR re-decided.

### 🚀 Unblocked & high-leverage (v0.1 is live — these were waiting on a public URL)

2. - [ ] **Publish the first LinkedIn post + update your LinkedIn profile** — **P1**
   - **Why:** "Make it visible" is north-star #2. The site is live; the launch story is the single highest-visibility action available and it has been blocked only on you.
   - **How:**
     1. **Post:** "Why I'm building WealthLens UK" — personal story (housing/wages/opportunity, your WP work), the problem (UK wealth inequality is invisible), the build (live link + one chart screenshot), the ask (volunteers/feedback). Tone per `strategy/branding-playbook.md`: confident, data-driven, non-partisan.
     2. **Profile:** headline + About + Featured (WealthLens, Springer paper, WP outreach, Taskdeck) + add skills (Data Visualisation, Open Data, Economic Research, Widening Participation). Copy guidance is in `strategy/`.
   - **Done when:** post is live and profile updated. (Then tell me — I'll tick the related `inbox.md` content items too.)

3. - [ ] **Send the four unblocked outreach emails** — **P1**
   - **Why:** Partnerships are north-star #3 and these were all gated on "v0.1 live", which is now true.
   - **Targets:** Tax Justice UK (`info@taxjustice.uk`), Patriotic Millionaires UK (website contact form), The Equality Trust (`info@equalitytrust.org.uk`), Gary Stevenson (DM `@garyseconomics` on X).
   - **How:**
     1. **Check `../hq-private/projects/wealthlens/outreach/contacts.md` and `emails-sent.md` first** (private repo) — never double-contact (AGENTS.md outreach rule).
     2. Per email: professional, specific, value-offering (not asking favours); include the **live link** and one concrete chart relevant to them; one clear ask.
     3. Log each in `../hq-private/projects/wealthlens/outreach/emails-sent.md` with the date.
   - **Done when:** all four sent and logged. (I can draft any/all of these for you on request.)

4. - [ ] **Register the `wealthlens.uk` domain** — **P2 (foundational)**
   - **Why:** Unblocks a project email (`hello@wealthlens.uk`), a custom deploy domain, and Bluesky handle verification. Cheap, one-time, and several other tasks depend on it.
   - **How:** Buy via any UK registrar (`.uk` is cheap). Also grab `wealthlensuk.org` if available. Then I can wire Cloudflare Pages / DNS when you're ready.
   - **Done when:** domain owned (note the registrar + renewal date here or in `deadlines.md`).

### 🛠 Decision needed (agent is blocked on your go-ahead)

5. - [ ] **Hero #1: review the 20 DRAFT golden questions (H1-02)** — **P1, ~1 focused hour**
   - **Why:** Every eval claim in the WealthLens Analyst inherits its credibility from this file. The agent is forbidden from writing the answers (no fabricated ground truth) — only you can. M2's recall measurement and everything after it waits on this.
   - **How:**
     1. Open `projects/wealthlens-analyst/evals/golden/golden_set.jsonl` (20 records: 15 in-corpus, 5 refusal probes; each has a reviewer note).
     2. Rewrite any question freely; for the 15 in-corpus ones fill `expected_answer` + `required_citations` (source_id from `registries/sources.yml`); flip `status` to `REVIEWED`.
     3. Leave the 5 refusal probes' answers EMPTY (the deterministic check enforces this).
     4. Run `make PYTHON=python eval-golden-validate` — it must pass.
   - **Done when:** no `status: DRAFT` remains in the first 20.

6. - [ ] **Create the Hetzner CAX21 account so the Analyst can be provisioned** — **P1 (D3 decided; needs your card)**
   - **Decided (2026-06-13):** D3 hosting = **Hetzner CAX21** (8GB Arm, ~£7/mo, Docker Compose, everything on-box incl. self-hosted Langfuse). ADR 0003 flipped to Accepted; the decision is recorded — this item is now just the account-creation step.
   - **How:** create a Hetzner Cloud account (hetzner.com/cloud) + add a card; spin up a CAX21 server (Ubuntu LTS, Arm, an EU region); give the agent SSH access (server IP + a key). Then I run **H1-30**: Docker Compose (app + Postgres/pgvector + Langfuse) + Caddy TLS + nightly `pg_dump` cron + Alembic + ingest.
   - **Done when:** the CAX21 server exists and I have access (then H1-30 provisions it).

7. - [ ] **Merge the `make ci-quick` reliability fix (PR #350)** — **P2, authorized + done, pending merge**
   - **Status (2026-06-05):** you authorized this; **fixed in PR #350**. The Makefile no longer swallows failures (`|| echo …` removed), so `make ci-quick` now runs real ruff + mypy + pytest and fails loudly. The dashboard-backend failures it used to hide are already resolved — a real run now shows **201 passed**. PR #350 also installs dev deps in `backend-install`, adds job timeouts, and enables Dependabot auto-merge.
   - **Repo-setting actions for you (3, one-time)** — for Dependabot auto-merge to work end-to-end:
     1. **Settings → General → Allow auto-merge** (ON), else `gh pr merge --auto` errors.
     2. **Branch protection on `main`** requiring the CI checks (so auto-merge only completes on green).
     3. **Settings → Actions → General → Allow GitHub Actions to create and approve pull requests** (ON) — personal repos default this OFF, and without it the workflow's `gh pr review --approve` step fails. (Surfaced by review on #350; the workflow now documents this prerequisite.)
   - **Note:** #350 was hardened further during review this session — `requirements-dev.txt` now pins ruff/mypy/httpx/pandas-stubs so a clean `make install && make ci-quick` genuinely passes, and `pipeline-test`/`frontend-install` were fixed. All findings addressed; CI green.
   - **Done when:** PR #350 merges (then move this to Done).

8. - [ ] **Wealth-shares chart: reconcile the stat-card / lede numbers with the WID series** — **P2, data-integrity, source decision**
   - **Why:** PR #409 fixed a 100x unit bug so the WID chart now draws the CORRECT shares (top 10% ≈ 57% in 2023, top 1% ≈ 21%). That fix surfaced a pre-existing mismatch in `frontend/src/config/chartArticles.ts`: the **"Top 1% alone: 28%"** stat card and the **"Postwar low (1980): 50%"** card + lede are **not** supported by the WID p99p100/p90p100 series the page plots (WID top-1% 2023 ≈ 21%, never 28% post-1900; WID 1980 top-10% ≈ 58%, the modern low ≈ 52% in ~1990). Data-integrity guardrail: every figure must cite its source.
   - **Decision needed:** for each card, EITHER (a) cite the specific alternative source/definition that yields 28% / 50% (e.g. a different vintage, income vs wealth, or household basis) on the card, OR (b) approve correcting them to the WID values the chart draws (and re-check the "more than the bottom 70% combined" / "bottom 50% = 6%" claims against a cited source). The 57% headline card is already correct.
   - **Agent-doable once you decide:** I can apply (b) with WID-cited values, or wire (a) citations, in a small reviewed PR. I did NOT change your public headline numbers unilaterally.
   - **Done when:** the stat cards + lede either cite their source or match the WID series, with no within-page contradiction.

9. - [ ] **Provide an `OPENAI_API_KEY` (+ a small spend cap) to unblock the Analyst's dense retrieval** — **P1 (blocks the M2→M3 chain)**
   - **Why:** As of 2026-06-27 the ingestion write path (H1-09, #450) and FTS retrieval (H1-10, #451) are MERGED, so the corpus is searchable lexically. The next steps — **H1-11** (embed the corpus via OpenAI `text-embedding-3-small`, ADR 0003 D2), then **H1-13** hybrid retrieval, **H1-18** answer composition — all make **real, paid model calls**. The agent will not incur spend without your authorisation, so the whole dense/hybrid/answer chain is blocked on this one credential. (FTS-only retrieval works today; embeddings add the semantic leg.)
   - **How:**
     1. Create an OpenAI API key (platform.openai.com) and set a **low usage limit** on the project (e.g. $5) so a bug can't run up a bill. Embedding the ~23-chunk frozen slice with `text-embedding-3-small` costs well under 1 cent; this is for safety, not capacity.
     2. Give me the key via the environment (do **not** commit it): `export OPENAI_API_KEY=sk-...` before `make ingest-slice` / `make dev`, or set it in the deploy env. It is already in `.env.example` as a placeholder; `config.py` reads it.
     3. Tell me the monthly cap you want for `BUDGET_MONTHLY_CAP_GBP` (the in-app hard cap, ADR 0002) — default in `.env.example` is £10.
   - **Done when:** a key is available in the agent's environment (then I build H1-11: embed the corpus, verify cosine neighbours, and wire H1-13 hybrid retrieval).

---

## Done

_(Cleared items move here with `[completed: YYYY-MM-DD]` once Chris confirms.)_

- [x] **Hero #1 ADR 0003 D3 — hosting decision**: chosen **Hetzner CAX21** (8GB Arm, ~£7/mo, Docker Compose, all on-box incl. self-hosted Langfuse) per the memo; ADR flipped to Accepted. Provisioning (H1-30) now waits only on the account (see open item 6). [completed: 2026-06-13]
- [x] **Private-repo split (decision C)**: sensitive material moved to the private `Chris0Jeky/hq-private` repo, removed from the public tip, every doc/hook/skill reference repointed to `../hq-private/...`, and `.gitignore` guards added; pre-split history exposure accepted (no rewrite). Chris confirmed complete. [completed: 2026-06-13]
- [x] **Prepare for mySociety interview (if shortlisted)** — **not shortlisted: application rejected** (Chris confirmed 2026-06-11). Recorded per the item's done-when. Interview-prep habits (daily no-AI Python practice, Exercism) remain useful for future applications — see `../hq-private/career/applications/interview-prep-general.md` (private repo). [completed: 2026-06-11]

# ⚑ ACTION REQUIRED — Chris's outstanding tasks

Last updated: 2026-05-31

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

1. - [ ] **Apply to mySociety SocietyWorks Developer role** `[due: 2026-05-31]` — **P0, due today/overdue**
   - **Why:** £42–52k, remote, Python — the best-paid civic-tech match and directly aligned with the mission. Listed in `deadlines.md`.
   - **How:**
     1. Find the live posting (mySociety / SocietyWorks careers page or Civil-Service-adjacent board). If the 2026-05-31 date has passed, check for an extension or the next cohort and note it here.
     2. Tailor the CV in `identity/` (lead with the GE Digital DevSecOps internship, the Springer publication, and WealthLens as live open-source civic tech).
     3. Cover letter: link the **live** dashboard (`chris0jeky.github.io/wealthlens-hq/`) and the WealthLens-Sim microsimulator as proof of shipping.
   - **Done when:** application submitted (or consciously skipped — record which).

2. - [ ] **Check the Bethnal Green Ventures Autumn 2026 window** `[due: ~2026-05-31]` — **P1**
   - **Why:** ~£60k for ~7% equity accelerator; the application window is around now (`deadlines.md`).
   - **How:** Confirm exact open/close dates on the BGV site; if open and you want to pursue it, start the EOI; if not yet open, replace this with the real date.
   - **Done when:** dates confirmed and either applied or scheduled.

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
     1. **Check `tasks/outreach/contacts.md` and `tasks/outreach/emails-sent.md` first** — never double-contact (AGENTS.md outreach rule).
     2. Per email: professional, specific, value-offering (not asking favours); include the **live link** and one concrete chart relevant to them; one clear ask.
     3. Log each in `tasks/outreach/emails-sent.md` with the date.
   - **Done when:** all four sent and logged. (I can draft any/all of these for you on request.)

5. - [ ] **Register the `wealthlens.uk` domain** — **P2 (foundational)**
   - **Why:** Unblocks a project email (`hello@wealthlens.uk`), a custom deploy domain, and Bluesky handle verification. Cheap, one-time, and several other tasks depend on it.
   - **How:** Buy via any UK registrar (`.uk` is cheap). Also grab `wealthlensuk.org` if available. Then I can wire Cloudflare Pages / DNS when you're ready.
   - **Done when:** domain owned (note the registrar + renewal date here or in `deadlines.md`).

### 🛠 Decision needed (agent is blocked on your go-ahead)

6. - [ ] **Authorize the `make ci-quick` reliability fix** — **P2, decision**
   - **Why:** `make ci-quick` currently **exits 0 even when the dashboard backend tests fail** — the Makefile guards backend commands with `|| echo …`, so a real POSIX-shell run hides **11 failures + 2 errors**. Pre-push verification is therefore giving a false green. (Surfaced 2026-05-30; tracked in `inbox.md` "Reliability follow-ups".)
   - **Root causes observed:** (a) `plotly` missing for the productivity-pay pipeline tests; (b) `cgt-concentration` emits non-finite JSON (NaN/Inf) the API can't serialise; (c) invalid dataset names return **404** where tests expect **422**.
   - **The decision:** these are in the **dashboard backend**, a different domain from the simulator work the agent has been doing. Fixing them will make `ci-quick` correctly go **red** until all three are fixed. Do you want the agent to take this on as a reviewed PR (fix the Makefile to propagate exit codes **and** fix the three root causes together), or leave it parked?
   - **Agent-doable once you say go.** Reply "do the ci-quick fix" to authorise.
   - **Done when:** you decide (and, if approved, the PR merges).

---

## Done

_(Cleared items move here with `[completed: YYYY-MM-DD]` once Chris confirms.)_

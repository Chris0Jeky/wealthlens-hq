# Today — 2026-05-15

## 5 Things To Do Today

### 1. Fix the CGT Chart and Create an Index Page

Two quick fixes before deployment:

**Fix the nan% bug:** The HMRC CGT chart shows "nan%" for the £3,000+ band's taxpayer share — there's a missing data point in that row. Either interpolate, show "n/a", or skip the band.

**Create `projects/wealthlens-dashboard/charts/index.html`:**
- Simple page linking to all 3 charts with titles and one-line descriptions
- Include the WealthLens name and mission statement at the top
- Add a footer: "Built by Chris Tcaci · Source code on GitHub · Data sources cited on each chart"
- Keep it clean — this is what every email and post will link to

Estimated time: 30-45 minutes.

### 2. Deploy v0.1 to a Live URL

This is the highest-leverage thing you can do today. Nothing is real until it has a URL.

**Option A — GitHub Pages (recommended for speed):**
1. Make the repo public (or use a separate `wealthlens-charts` repo for just the charts)
2. Push the `charts/` directory
3. Enable GitHub Pages from Settings → Pages → Deploy from branch
4. URL: `chris0jeky.github.io/wealthlens-charts/` (or similar)

**Option B — Cloudflare Pages:**
1. Connect to GitHub repo
2. Build command: none (static files)
3. Output directory: `projects/wealthlens-dashboard/charts/`
4. Custom domain later: `charts.wealthlens.uk` or similar

Either way, the goal is: **by tonight, you can paste a URL in a DM and someone sees your charts.**

Estimated time: 30-60 minutes.

### 3. Update LinkedIn Profile

Deferred from yesterday. Quick 15-minute job:

- **Headline:** "Software Engineer | Building open-source tools for economic justice | Published Researcher | Widening Participation Advocate"
- **About section:** Rewrite around "engineer making inequality data visible" — see `tasks/outreach/emails-to-send.md` for the narrative.
- **Featured section:** Add the live charts URL (from step 2), Springer publication link, one WP-related post.
- **Skills:** Add Data Visualisation, Open Data, Economic Research, Widening Participation.

Estimated time: 15-20 minutes.

### 4. Draft First LinkedIn Post

Don't publish yet — draft it tonight, sleep on it, publish tomorrow morning. The content calendar says the first post should be "Why I'm building WealthLens UK."

**Structure (aim for ~150-200 words):**
1. Hook: a single striking stat from one of your charts (e.g., "The top 1% own more wealth than the bottom 70% combined")
2. Personal angle: one sentence connecting your WP work or housing experience
3. What you're doing: "I'm building WealthLens — open-source tools to make this data impossible to ignore"
4. What's live: link to the charts URL (in first comment, not in post body — LinkedIn algorithm penalises external links)
5. Call to action: "Follow along" or "What data would you want to see?"

**Rules from content calendar:**
- No external links in post body
- One number, one chart, one sentence
- Use hashtags sparingly: #WealthInequality #OpenData #EconomicJustice

Estimated time: 30 minutes for a solid draft.

### 5. Find a Good-First-Issue for Your First Open-Source PR

Browse the repos you emailed about. You don't need to submit the PR today — just find the issue and understand the codebase.

**Democracy Club:**
- GitHub: `github.com/DemocracyClub`
- Look at `yournextrepresentative` or `uk-election-data` repos
- Filter by `good first issue` or `help wanted` labels

**mySociety:**
- GitHub: `github.com/mysociety`
- Look at `theyworkforyou` or `parlparse` repos
- Filter by `good first issue` labels

**What to look for:** Python/Django bugs, documentation fixes, or data-processing tasks that match your skills. One small merged PR is worth more than a dozen unfinished ideas.

Estimated time: 20-30 minutes browsing.

---

## Evening Reading

Continue *The Trading Game*. If you finish a chapter that sparks a chart idea or data angle, note it in `tasks/inbox.md`.

## Follow-Up Reminders

- Check for replies from Democracy Club and mySociety by 2026-05-21 — if no reply, send a gentle follow-up.
- *A Brief History of Equality* should arrive soon — start when it does.

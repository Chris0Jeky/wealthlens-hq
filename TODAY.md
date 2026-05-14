# Today — 2026-05-14

## 5 Things To Do Today

### 1. Order *The Trading Game* and *A Brief History of Equality*

Buy both today. Start *The Trading Game* tonight — it's a fast read and it's the emotional foundation for everything. *A Brief History of Equality* is Piketty's most accessible book and gives you the intellectual backbone without needing to tackle the 700-page *Capital* yet.

- *The Trading Game* — Gary Stevenson (Penguin). Amazon, Waterstones, or Audible.
- *A Brief History of Equality* — Thomas Piketty (2022). Amazon or Waterstones. Free summary of the underlying data at wir2022.wid.world.

### 2. Create Twitter/X and Bluesky Accounts

This is a one-time setup that blocks everything else — you can't post, engage, or tag people without accounts.

**Twitter/X:**
- Sign up with jeky.tck@gmail.com or a dedicated email.
- Handle: @CristianTcaci or @CrisTcaci (check availability).
- Bio: "Engineer. Turning inequality data into public knowledge. Springer SGAI-AI 2025. ex-GE Digital. Building @WealthLensUK."
- Pin: leave empty for now — you'll pin your manifesto thread after v0.1.

**Bluesky:**
- Sign up at bsky.app.
- Handle: @cristiantcaci.bsky.social (later verify via personal domain).
- Bio: mission-first variant of the X bio.

**LinkedIn (update today, 10 minutes):**
- Headline: "Software Engineer | Building open-source tools for economic justice | Published Researcher | Widening Participation Advocate"
- About section: rewrite around "engineer making inequality data visible" — see `tasks/outreach/emails-to-send.md` for the narrative.
- Featured section: add WealthLens repo (once public), Springer publication, one WP-related post.
- Add skills: Data Visualisation, Open Data, Economic Research, Widening Participation.

### 3. Pull ONS + WID Data Into a Python Notebook

Nothing else matters until there's a live URL. Start the first chart today.

```bash
# Create the project structure
mkdir -p projects/wealthlens-dashboard/notebooks
cd projects/wealthlens-dashboard/notebooks

# Create a virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install basics
pip install pandas matplotlib requests openpyxl

# Start a notebook
pip install jupyter
jupyter notebook
```

**First chart: Top 1% wealth share over time (WID data)**
1. Go to wid.world/data/
2. Select: Country = United Kingdom, Indicator = "Net personal wealth", Percentile = "Top 1% share"
3. Download CSV
4. Load in pandas, plot with matplotlib
5. Add source citation, title, and date

**Second chart: Housing affordability by region**
1. Go to ons.gov.uk, search "Housing affordability in England and Wales"
2. Download the XLSX (Dataset 9 has LA-level data)
3. Plot median house price to median earnings ratio by region, 1997-2024

**Third chart: Capital gains concentration**
1. Go to gov.uk/government/statistics/capital-gains-tax-statistics
2. Download the ODS/XLSX
3. Show that 92% of gains accrue to top 1% of taxpayers

### 4. Email Democracy Club and mySociety

These don't need a prototype. Send today.

**Democracy Club** — copy from `tasks/outreach/emails-to-send.md` Draft 6:
- To: hello@democracyclub.org.uk
- Keep it short. Mention Python/Django, GE Digital, Springer paper, WealthLens.
- Ask Sym Roe which issue to start on.

**mySociety** — copy from Draft 5:
- To: whofundsthem@mysociety.org
- Offer to join the volunteer cohort for register-of-interests scrutiny.
- Mention Python/FastAPI/Vue 3 skills.

### 5. Subscribe to 5 Key Newsletters

10 minutes. Compounds forever.

1. **Resolution Foundation "Top of the Charts"** — resolutionfoundation.org (weekly, Friday)
2. **Dan Neidle's Tax Policy Associates** — taxpolicy.org.uk or find on Substack
3. **Branko Milanovic "Global Inequality and More 3.0"** — Substack (28k+ subs)
4. **Adam Tooze "Chartbook"** — Substack (polycrisis context)
5. **IFS publications** — ifs.org.uk/publications (sign up for email alerts)

---

## Gaps and Contradictions — How To Handle Them

### 1. Gary Stevenson: Inspiration vs Methodology

**The tension:** Gary is the emotional catalyst and audience-building model, but the research warns he's not a methodological source. His claims are sometimes imprecise.

**How to adjust:** Use Gary for audience-finding, framing, and proof that popular inequality content works in the UK. But source your data from the primary economists (Piketty, Atkinson, Saez, Zucman, Advani/Summers). When quote-tweeting Gary, always add the primary source. Never cite "Gary said X" — cite "ONS data shows X." The research calls this avoiding the "Gary trap."

**In practice:**
- Quote-tweet Gary with ONS/HMRC/WID data, not just agreement.
- Read the books Gary's thinking is built on (Piketty, Atkinson).
- Position yourself as "engineer who builds tools" not "Gary's disciple."

### 2. WAS Accreditation Withdrawal

**The tension:** The ONS Wealth and Assets Survey lost accredited official statistics status in June 2025 (response rate collapsed 66% to 41%). It also systematically undercounts top-tail wealth by ~£800bn. But it's still the primary UK wealth distribution dataset.

**How to adjust:** Create a methodology page (`research/methodology/was-caveats.md`) that:
- Explains the accreditation withdrawal and what it means
- Documents the December 2024 DB pension methodology change (~£2.3tn impact)
- Describes Pareto adjustment for top-tail (Vermeulen 2018, Tippet & Wildauer STRL reconstruction)
- Every WAS-sourced chart gets a visible caveat badge
- Offer a source toggle: ONS WAS / WID DINA / RF corrected — treat disagreement as a feature

### 3. "Build Fast" vs "Read First"

**The tension:** The 26-week curriculum says study 260 hours before publishing credibly. ChatWithClaude says "v0.1 live in two weeks." Both are right for different things.

**How to adjust:** Ship immediately from well-understood data. Defer complex analysis.

| Ship now (well-understood) | Defer (needs study first) |
|---|---|
| WID top shares (clean CSV, clear methodology) | WAS-derived distributional claims |
| HMRC capital gains/IHT (simple counts) | Wealth tax revenue modelling |
| ONS housing affordability (straightforward ratio) | Cross-source wealth comparisons |
| Land Registry price trends | Policy recommendations |

**Rule:** If you can link to the exact ONS/HMRC/WID methodology page and explain it in one paragraph, ship it. If you'd need to hedge with "depending on the definition of..." then study first.

### 4. LSE MSc: Now vs Later

**The tension:** ChatWithClaude treats it as worth applying immediately. The career docs say "only if AFSEE-funded" and "pauses critical momentum."

**How to adjust:** Hold as a medium-term option. Don't spend time on it now.
- Note the AFSEE fellowship deadline (typically January 2027).
- Attend LSE public lectures and III seminars as free credibility-building.
- If in 12 months WealthLens has traction + AFSEE is available, reconsider.
- Meanwhile, Georgia Tech OMSCS (applications Aug-Sep 2026) is higher-ROI: part-time, ~£8-10k total, no career interruption, signals CS depth for research engineering roles.

### 5. 200-Item Inbox vs "One Sharp Spear"

**The tension:** The inbox has ~200 action items. The research consistently warns against scattering.

**How to adjust:** The inbox is a reference library, not a to-do list. Only the active sprint matters this week. Rules:
- Maximum 7 items in active sprint at any time.
- Do not start items from the inbox unless they're promoted to the sprint.
- The priority chain is: **charts -> deploy -> first post -> first outreach emails -> everything else.**
- Taskdeck, quant startup, LSE, OMSCS, LeetCode, C++ all stay at maintenance level for 30 days.
- Review the inbox every Sunday evening and promote 1-2 items to the next week's sprint.
- Check `tasks/deadlines.md` weekly for upcoming time-sensitive items.

---

## New Structural Files Created

These four files were created to fill gaps identified during the research extraction:

### 1. `research/methodology/was-caveats.md`
Documents the ONS Wealth and Assets Survey accreditation withdrawal (June 2025), the December 2024 DB pension methodology change, top-tail undercoverage (~£800bn), Pareto adjustment methods, and standard caveat text for charts. Also covers Gini vs Palma and measurement unit requirements. Every WAS-sourced chart should reference this file.

### 2. `tasks/outreach/pitch-tracker.md`
Consolidates all conference CFPs, podcast pitches, newsletter submissions, and grant applications with specific deadlines. Organised by time period (May 2026 through 2027) plus rolling/ongoing items. Check this monthly to avoid missing windows.

### 3. `identity/personal-story.md`
A template and prompt for Chris to write his personal narrative — the single strongest content hook identified across all research. Contains the themes to cover (housing, wages, education, the contradiction, the turn, the commitment), a narrative arc template, content hooks the story unlocks, and framing rules. **Chris needs to write his version — the template shows what to cover but the authenticity must be his.**

### 4. `tasks/deadlines.md`
All time-sensitive items from across the entire inbox consolidated into one chronological file. Covers May 2026 through early 2027 plus rolling deadlines. Check weekly on Sunday evenings.

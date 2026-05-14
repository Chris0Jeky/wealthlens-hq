# Gaps and Contradictions — How To Handle Them

Last updated: 2026-05-14

Strategic guidance on tensions identified across all research sources. These are the traps to avoid and the judgment calls to get right.

## 1. Gary Stevenson: Inspiration vs Methodology

**The tension:** Gary is the emotional catalyst and audience-building model, but the research warns he's not a methodological source. His claims are sometimes imprecise.

**How to adjust:** Use Gary for audience-finding, framing, and proof that popular inequality content works in the UK. But source your data from the primary economists (Piketty, Atkinson, Saez, Zucman, Advani/Summers). When quote-tweeting Gary, always add the primary source. Never cite "Gary said X" — cite "ONS data shows X." The research calls this avoiding the "Gary trap."

**In practice:**
- Quote-tweet Gary with ONS/HMRC/WID data, not just agreement.
- Read the books Gary's thinking is built on (Piketty, Atkinson).
- Position yourself as "engineer who builds tools" not "Gary's disciple."

## 2. WAS Accreditation Withdrawal

**The tension:** The ONS Wealth and Assets Survey lost accredited official statistics status in June 2025 (response rate collapsed 66% to 41%). It also systematically undercounts top-tail wealth by ~£800bn. But it's still the primary UK wealth distribution dataset.

**How to adjust:** Create a methodology page (`research/methodology/was-caveats.md`) that:
- Explains the accreditation withdrawal and what it means
- Documents the December 2024 DB pension methodology change (~£2.3tn impact)
- Describes Pareto adjustment for top-tail (Vermeulen 2018, Tippet & Wildauer STRL reconstruction)
- Every WAS-sourced chart gets a visible caveat badge
- Offer a source toggle: ONS WAS / WID DINA / RF corrected — treat disagreement as a feature

## 3. "Build Fast" vs "Read First"

**The tension:** The 26-week curriculum says study 260 hours before publishing credibly. ChatWithClaude says "v0.1 live in two weeks." Both are right for different things.

**How to adjust:** Ship immediately from well-understood data. Defer complex analysis.

| Ship now (well-understood) | Defer (needs study first) |
|---|---|
| WID top shares (clean CSV, clear methodology) | WAS-derived distributional claims |
| HMRC capital gains/IHT (simple counts) | Wealth tax revenue modelling |
| ONS housing affordability (straightforward ratio) | Cross-source wealth comparisons |
| Land Registry price trends | Policy recommendations |

**Rule:** If you can link to the exact ONS/HMRC/WID methodology page and explain it in one paragraph, ship it. If you'd need to hedge with "depending on the definition of..." then study first.

## 4. LSE MSc: Now vs Later

**The tension:** ChatWithClaude treats it as worth applying immediately. The career docs say "only if AFSEE-funded" and "pauses critical momentum."

**How to adjust:** Hold as a medium-term option. Don't spend time on it now.
- Note the AFSEE fellowship deadline (typically January 2027).
- Attend LSE public lectures and III seminars as free credibility-building.
- If in 12 months WealthLens has traction + AFSEE is available, reconsider.
- Meanwhile, Georgia Tech OMSCS (applications Aug-Sep 2026) is higher-ROI: part-time, ~£8-10k total, no career interruption, signals CS depth for research engineering roles.

## 5. 200-Item Inbox vs "One Sharp Spear"

**The tension:** The inbox has ~200 action items. The research consistently warns against scattering.

**How to adjust:** The inbox is a reference library, not a to-do list. Only the active sprint matters this week. Rules:
- Maximum 7 items in active sprint at any time.
- Do not start items from the inbox unless they're promoted to the sprint.
- The priority chain is: **charts -> deploy -> first post -> first outreach emails -> everything else.**
- Taskdeck, quant startup, LSE, OMSCS, LeetCode, C++ all stay at maintenance level for 30 days.
- Review the inbox every Sunday evening and promote 1-2 items to the next week's sprint.
- Check `tasks/deadlines.md` weekly for upcoming time-sensitive items.

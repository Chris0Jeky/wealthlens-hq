# Key Insights

Last updated: 2026-05-14

The distilled 20% of research that should drive 80% of action. Extracted from all research documents in `research/raw/` plus personal sources (`ChatWithClaude.txt`, `identity/` — now in the private `hq-private` repo).

---

## Mission

1. **The UK has world-class inequality data that almost nobody can see.** ONS, HMRC, and WID publish incredible datasets buried in spreadsheets and PDFs written for experts. The gap is visibility, not data -- and that is an engineering problem.
2. **Start with small, shareable, permanent chart pages -- not a large dashboard.** A few source-backed, embeddable charts with methodology notes will ship faster, earn trust, and spread further than a generic dashboard.
3. **Each chart must be self-contained and trustworthy.** Every public chart needs: source URL, access date, methodology note, downloadable CSV, version date, plain-language description, and share/embed buttons.
4. **Inequality should be reframed as personal.** Connect to housing, wages, opportunity, and generational decline -- not abstract Gini coefficients. "You can't fix what you can't see."
5. **Never claim to "solve" or "disrupt" inequality.** Frame work as making systems visible, testable, and discussable. "We let the numbers speak" -- not "AI for good" or "democratising X."
6. **Wealth concentration is measurable, not opinion.** WealthLens tools should inform, not manipulate. Non-partisan by design: "This isn't left vs right. This is seeing the numbers clearly."
7. **UK household wealth is ~17 trillion pounds (~7x GDP) while wealth-related taxes raise ~3% of GDP.** This gap defines every serious UK distributional debate.
8. **Educational inequality is the first valve in a multi-stage wealth funnel.** WP access at 18 maps to wealth distribution at 60 -- each stage is quantifiable with public data.

## Career

9. **The strongest positioning is "engineer making unequal systems legible."** Not commenting on economics. This avoids needing economist credentials while leveraging existing technical skills.
10. **The combination of trading systems + inequality tools + widening participation is nearly unique.** Very few people in UK economic-justice discourse have this credential stack.
11. **The Springer paper + GE Digital + First Class Honours compensate for Middlesex not being a "prestige" institution.** External validation through delivery, not institutional affiliation.
12. **Research engineering is the strongest career track** -- combining public-interest credibility with transportable engineering depth.
13. **The first 20k pay rise (from ~33k to ~55k) is the single highest-leverage financial move** -- converting the budget from break-even to saving ~1,400/month.
14. **Civil Service DDaT roles are financially competitive once Alpha pension (28.97% employer contribution) is properly costed** -- effectively adding ~25k in value.
15. **Most mission-led roles reward people who arrive having already shipped public-interest work.** Open-source contributions and a credible WealthLens repo buy this credential for free.
16. **INET Oxford may be the single most natural institutional home** for someone with a game-theory, multi-agent cooperation background working on UK wealth inequality.

## Technical

17. **Python/FastAPI is the lingua franca of civic tech and data journalism orgs** (Full Fact, ONS Data Science Campus, Alan Turing, Nesta, mySociety). Chris's existing stack is directly deployable.
18. **The single highest-impact engineering habit is linking a GitHub repo with data + notebook from every post.** This doubles the hit rate with newsletter curators and triples credibility.
19. **Reproducibility is the moat.** Data pipelines must be scripts (`fetch_ons_wealth.py`, `fetch_hmrc_stats.py`, `fetch_wid_data.py`), not manual downloads.
20. **The WAS lost accredited official statistics status in June 2025.** Any WAS-derived claim must be explicitly hedged. The December 2024 ONS methodology change for DB pensions cut measured UK wealth by ~2.3 trillion.
21. **Report both Gini and Palma ratio.** The Gini is not subgroup-decomposable and is insensitive to tails. The Palma (top 10% / bottom 40%) is more policy-relevant.
22. **Keep eligibility logic out of code** for the WP pathway tool. Implement as declarative JSON-Logic or a small DSL so non-engineers on the WP team can maintain rules.
23. **Geography-first data model** (postcode -> LSOA/MSOA/local-authority) serves both Pathway Explorer and WealthLens UK.

## Outreach

24. **Build first, ask permission later.** Don't email organisations asking what to do -- email showing what you've already started building. Orgs get hundreds of "I want to help" emails; they reply to "I've built this thing."
25. **Target smaller orgs over huge ones.** Tax Justice UK and Equality Trust are more likely to respond than Oxfam. Gary Stevenson is essentially solo, not a company to join.
26. **Specificity beats ambition in all communications.** "I've started building" beats "I want to build a comprehensive platform."
27. **Bluesky is where UK civic-tech and economic-justice discourse has migrated.** 43% of major news influencers now have Bluesky accounts; engagement runs 2-4x higher per follower than X under 100K.
28. **The reply-into-big-accounts strategy is the highest-ROI activity at the 0-1K follower stage on X.**
29. **Newsletter inclusion compounds.** One Pragmatic Engineer link drives more durable subscribers than a viral X moment.
30. **Name prior workers in every piece** (IFS, Resolution Foundation, IPPR, NEF, ONS researchers, specific journalists) -- crediting forward is a citation practice that builds trust and relationships.

## Content

31. **Personal accounts get more algorithmic reach than brand accounts.** Run everything from personal accounts initially. Chris's personal story IS the brand story right now.
32. **Content mix: 50% explanatory, 20% build-in-public, 20% personal-professional story, 10% direct opinion.** Personal story should be scaffolding for structural argument (10-20% personal, 80-90% structural).
33. **LinkedIn document-post carousels outperform every other format** -- ~596% more engagement than text-only posts (Buffer analysis of 4.8M posts). No external links in the main body (kills reach); put links in the first comment.
34. **The most effective narrative structure is progression, not redemption.** Constraint -> Craft -> Contradiction -> Turn -> Commitment.
35. **Four content pillars: public-interest engineering, inequality by the numbers (40%), widening participation, and power and systems.**
36. **Lead with the finding, never the topic; lead with the engineering, never the politics.** Both inversions protect credibility and expand audience.
37. **The widening participation work is the "emotional proof"** that makes everything credible and non-performative. It's not a side detail -- it's the core of the personal narrative.
38. **Permanently ban phrases like:** "disrupting inequality," "democratising X," "AI for good" (without specifics), "data will save us," "empowering," "scaling impact."

## Learning

39. **The curriculum assumes ~10 hours/week for 26 weeks (260 hours total).** Protect this time: ~2 hours per weekday morning and ~3 hours on Saturday.
40. **Read primary sources, not YouTube summaries.** Gary's thinking is built on Piketty, Atkinson, Saez, and Zucman. Reading these separates credible engagement from surface-level enthusiasm.
41. **The decisive quantitative skill is not formal cleverness** but being able to say exactly what a statistic measures, what it omits, and what assumptions sit underneath it.
42. **"Inequality has not changed much" is often true for one metric (disposable-income Gini at 32.9%) and false for the mechanisms that drive politics** (housing wealth, top incomes, intergenerational mobility).
43. **OMSCS is the strongest educational multiplier** for research-engineering and technically selective roles (~8-10k total, part-time, no career interruption). LSE MSc only worth it if AFSEE-funded.
44. **Game theory and multi-agent cooperation provide genuine comparative advantage** that almost nobody else in UK inequality discourse holds: mechanism design for wealth-tax valuation, yard-sale models of wealth condensation, coalition analyses of tax politics.

## Finance and Structure

45. **Premature fundraising kills credibility.** Do not ask for money until there is something to show. All finances should be public on Open Collective.
46. **A CIC Limited by Shares preserves the most optionality** -- founder-director pay, equity-style impact investment (BGV, Zinc), and acceptance by most grant funders. Defer incorporation to month 3-4.
47. **Broad "civic tech" missions rarely get funded on mission language alone.** What gets funded is grant-and-contract public benefit, social enterprises with institutional buyers, or venture-backed products with clear route to scale.
48. **The biggest risk is trying to do everything at once** (WealthLens, Taskdeck, quant startup, WP tooling, LSE, OMSCS, LeetCode, C++, meetups) and doing nothing well. One sharp spear is worth more than ten blunt ones.

---

## Processed

All insights extracted from:
- `research/raw/Combined/` (7 files)
- `research/raw/Claude_Resources/` (10 files)
- `research/raw/Codex_Resources/` (7 files)
- `ChatWithClaude.txt`
- `identity/` (9 files)

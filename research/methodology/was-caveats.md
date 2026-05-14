# WAS Caveats and Methodology Notes

Last updated: 2026-05-14

This file documents known issues with the ONS Wealth and Assets Survey that must be addressed in any WealthLens chart sourced from WAS data.

## Accreditation Withdrawal (June 2025)

The Office for Statistics Regulation (OSR) withdrew the WAS's accredited official statistics status in June 2025 (Assessment Report 396). The primary reason was a collapse in response rate from 66% in earlier rounds to 41% in Round 8 (April 2020 - March 2022), raising questions about the representativeness of the sample.

**What this means for WealthLens:**
- WAS data is still published and usable, but it no longer carries the "National Statistics" quality mark.
- Any chart sourced from WAS must carry a visible caveat: "Source: ONS Wealth and Assets Survey. Note: WAS lost accredited official statistics status in June 2025 due to response-rate decline."
- Do not present WAS figures as definitive without noting this limitation.

## DB Pension Methodology Change (December 2024)

In December 2024, ONS changed how it values defined-benefit pensions in the WAS, cutting measured UK total wealth by approximately £2.3 trillion. This is a methodology change, not an actual change in wealth — the underlying pensions are the same.

**What this means for WealthLens:**
- Time-series charts spanning the methodology change must note the break.
- Do not compare pre-change and post-change figures without adjustment.
- Clearly state which methodology is used in chart metadata.

## Top-Tail Undercoverage (~£800bn)

The WAS systematically undercounts the wealthiest households. Estimates suggest ~£800bn in top-tail wealth is missing. This is because:
- Ultra-high-net-worth individuals are unlikely to respond to surveys.
- The WAS does not oversample the top tail (unlike the US Survey of Consumer Finances).
- Response rates are lowest among the wealthiest postcodes.

**How to correct:**
- The canonical correction is Pareto adjustment combining WAS with the Sunday Times Rich List (Vermeulen 2018; Tippet & Wildauer 2024 PEGFA Greenwich reconstruction).
- The `gpinter` R package (generalised Pareto interpolation) from WID can be used to reconstruct fine-grained distributions from coarse public tables.
- WealthLens should offer a source toggle on wealth charts: ONS WAS (raw) / WID DINA / RF corrected — treating source disagreement as a feature, not a bug.

## Key References

- OSR Assessment Report 396 (June 2025) — accreditation withdrawal
- Vermeulen (2018) "How fat is the top tail of the wealth distribution?" *Review of Income and Wealth*
- Tippet & Wildauer (2024) PEGFA Greenwich — reconstructed Sunday Times Rich List 1989-2024
- Crawford, Innes & O'Dea (2016) IFS WAS foundational paper, *Fiscal Studies* 37(1)
- Blake & Orszag (1999) — historical wealth-to-GDP reconstruction

## Standard Caveat Text for Charts

Use this text (or a shortened version) on any WAS-sourced chart:

> Source: ONS Wealth and Assets Survey, Round 8 (April 2020 - March 2022). The WAS lost accredited official statistics status in June 2025 due to declining response rates. The survey is known to undercount top-tail wealth by an estimated £800bn. See our methodology notes for details.

## Measurement Units to Always State

Every wealth chart must explicitly state:
- **Unit:** households, adults, or taxpayers (these are different populations)
- **Measure:** AHC or BHC (after/before housing costs) for income; net or gross for wealth
- **Currency:** nominal or real (CPI/RPI-adjusted), and base year if real
- **Tax treatment:** pre-tax or post-tax (for income)
- **Geography:** GB (WAS) or UK (other sources) — WAS excludes Northern Ireland

## Gini vs Palma

- The Gini coefficient is the most commonly cited inequality measure but has known limitations: it is not subgroup-decomposable and is more sensitive to transfers around the mode than to changes at the tails.
- The Palma ratio (top 10% share / bottom 40% share) is more policy-relevant and more sensitive to the extremes that actually drive politics.
- **WealthLens policy:** report both Gini and Palma on any inequality chart. For international comparisons, always state whether figures are PPP or MER.

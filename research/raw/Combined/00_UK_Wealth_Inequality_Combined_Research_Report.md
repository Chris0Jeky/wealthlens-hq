# UK Wealth Inequality Data Visualisation Project — Combined Foundational Research Report

This document is a foundational reference for an open-source UK wealth inequality data visualisation project. It merges and reconciles two independent deep-research passes into a single working brief, organised around the five research questions originally posed. It serves both developers (data formats, APIs, schemas, ingestion strategy) and strategists/designers (which statistics matter, which visual formats travel, which gaps in the existing UK ecosystem represent the strongest strategic openings). Geographic granularity throughout treats London as a distinct region from the rest of England, with separate coverage for Scotland, Wales and Northern Ireland.

## Two methodological frames to keep in mind throughout

**Frame 1 — the top-tail correction.** The Wealth and Assets Survey (WAS) systematically undercovers the top of the UK wealth distribution by an estimated ~£800bn (Advani, Bangham & Leslie 2021, *Fiscal Studies*). Most credible UK wealth research now applies a Pareto adjustment combining WAS with the Sunday Times Rich List. Any dashboard that uses raw WAS without adjustment will understate top-1% share by 2–6 percentage points. The project should surface this caveat prominently and ideally show adjusted and unadjusted figures side-by-side. Compounding this: in June 2025, the Office for Statistics Regulation suspended WAS's "Accredited Official Statistics" status (OSR Assessment Report 396) on account of falling response rates and quality concerns. An honest product cannot pretend one source gives the final answer — a source toggle between ONS survey estimates and WID's tax-and-national-accounts-adjusted top-share view is not just nice UX, it is good statistical practice.

**Frame 2 — the synthesis problem.** No existing UK tool gives a user one coherent path from "who owns what?" → "how did they get it?" → "how is it taxed?" → "where does housing fit in?" The ecosystem is rich in fragments and poor in synthesis. WID is best for long-run top shares but weak on UK tax detail and housing. Resolution Foundation has excellent housing and intergenerational interfaces but is not a joined-up wealth-tax-inheritance explorer. IFS Taxlab is strongest on "what does this tax actually do?" but its wealth, housing and tax stories live in separate products. Bank of England has the best machine-readable infrastructure but is not trying to be a wealth-inequality explainer. The strategic positioning for a new project is exactly this gap: end-to-end coherence over single-domain depth.

---

## Section 1 & 2: UK datasets — sources, formats, accessibility

This combined section catalogues the relevant UK datasets and rates their accessibility. Before the source-by-source detail, the engineering takeaway: the stack divides into three machine-friendliness tiers.

### Engineering tier summary

| Tier | Sources | Why |
|---|---|---|
| **Easy (API-first or parameterised CSV)** | Bank of England IADB; WID.world (bulk download + R/Stata packages); ONS Beta API for those datasets it covers; Nomis API; Companies House API; Land Registry SPARQL | Documented endpoints, stable URL patterns, JSON/CSV-native |
| **Medium (spreadsheet-first, scriptable)** | Most ONS wealth releases (WAS, ETB, housing affordability); HMRC (SPI, CGT, IHT, receipts); Resolution Foundation chart Excels; IFS Taxlab spreadsheets; DWP Stat-Xplore (REST API but registration + key) | Files are easy to script-download but stay publication-plus-table rather than API-first |
| **Hard (analysis layer, not a data feed)** | IPPR; The Equality Trust | Strong evidence and modelling but no maintained machine-readable repository |

A workable ingestion architecture should assume **a hybrid model**: use APIs where they exist (BoE, WID, ONS Beta where covered, Nomis, Stat-Xplore, Companies House), but build reliable spreadsheet parsers for the high-value wealth releases that remain XLSX/ODS-only.

### 1.1 Office for National Statistics (ONS) and DWP household surveys

#### Wealth and Assets Survey (WAS)
- **URL**: https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/totalwealthingreatbritain/latest
- **Microdata**: UKDS SN 7215 (https://beta.ukdataservice.ac.uk/datacatalogue/studies/study?id=7215)
- **Latest release**: Round 8 (April 2020 – March 2022), released 24 January 2025. Round 9 (Apr 2022 – Mar 2024) in field.
- **Format**: HTML bulletin, XLSX reference tables, Stata/SPSS microdata via UKDS. **No REST API.**
- **Frequency**: Biennial 2-year rounds; ~34-month publication lag.
- **Granularity**: Great Britain only (excludes NI); household-level totals; four wealth components (financial, property, pension, physical); decile/percentile in microdata; ITL1 regions including London — but **London estimates are volatile due to smaller sample**.
- **Time series**: Wave 1 (Jul 2006 – Jun 2008) → Round 8 (Apr 2020 – Mar 2022).
- **Headline decile cut-offs (Round 8)**: wealthiest 10% of households hold £1,200,500 or more; the least wealthy 10% hold £16,500 or less. These specific thresholds anchor the most-shared "ranking" visualisations.
- **Known issues**: (i) **WAS lost ONS "Accredited Official Statistics" status in June 2025** (OSR Assessment Report 396) — surface this caveat prominently. (ii) **~£800bn of top-tail wealth missing** (Advani, Bangham & Leslie 2021); Wealth Tax Commission EP13 (Advani, Hughson & Tarrant 2021) adds ~£280bn after STRL+Pareto adjustment for business wealth. (iii) **Series break Round 7 → Round 8** in DB pension valuation methodology (new GAD-recommended SCAPE discount rate). (iv) COVID-era telephone collection in Round 8.
- **Licence**: OGL v3.0 for publications; UKDS EUL for microdata; Secure Lab for richer geography under Digital Economy Act 2017 accreditation.

#### Households Below Average Income (HBAI) / Family Resources Survey (FRS)
- **HBAI URL**: https://www.gov.uk/government/collections/households-below-average-income-hbai--2
- **FRS URL**: https://www.gov.uk/government/collections/family-resources-survey--2
- **Stat-Xplore (interactive + API)**: https://stat-xplore.dwp.gov.uk/ (free registration; SuperWEB REST API with key)
- **Latest release**: HBAI FYE 2025 (April 2024 – March 2025) published March 2026.
- **Format**: ODS/XLSX tables, CSV via Stat-Xplore, microdata via UKDS (HBAI SN 5828; FRS SN 4969).
- **Frequency**: Annual (March).
- **Granularity**: UK; ITL1 regions including London; Scotland, Wales, NI separately; deciles/quintiles/percentiles BHC and AHC; child/working-age/pensioner breakdowns.
- **Time series**: GB 1994/95 – 2001/02; UK 2002/03 onwards.
- **Known issues**: (i) **Series break from FYE 2022** — linked to DWP admin benefits data; pre/post not directly comparable. (ii) Material deprivation questions overhauled FYE 2024. (iii) **Top-tail undercoverage**: FRS, like WAS, underestimates incomes above ~97th percentile vs HMRC SPI; ONS applies an "SPI adjustment" but it is partial.
- **Licence**: OGL v3.0 (publications); UKDS EUL (microdata).

#### Regional GVA and Gross Disposable Household Income (GDHI)
- **GDHI URL**: https://www.ons.gov.uk/economy/regionalaccounts/grossdisposablehouseholdincome
- **GVA URL**: https://www.ons.gov.uk/economy/grossvalueaddedgva
- **Nomis API**: https://www.nomisweb.co.uk/datasets/gdhi (REST + bulk CSV; no auth required)
- **Latest**: GDHI 1997–2023 released 10 September 2025.
- **Format**: XLSX, CSV via Nomis API.
- **Frequency**: Annual (~21-month lag).
- **Granularity**: UK, 4 nations, 12 ITL1 regions, ~40 ITL2, ~180 ITL3, ~370 local authorities. **London fully broken out** — Westminster & City of London GDHI per head £79,555 (2023) vs UK average £24,836 (3.2× UK average).
- **Known issues**: Latest year heavily revised; LSOA-level tables withdrawn (Dec 2024) pending investigation. Per-capita measure, not per-household.
- **Licence**: OGL v3.0.

#### Housing affordability ratios
- **URL**: https://www.ons.gov.uk/peoplepopulationandcommunity/housing/bulletins/housingaffordabilityinenglandandwales/latest
- **HPSSA (small-area prices)**: https://www.ons.gov.uk/peoplepopulationandcommunity/housing/datasets/medianhousepricesforadministrativegeographieshpssadataset09
- **Format**: XLSX, downloadable CSV; not on Beta API.
- **Frequency**: Annual (workplace/residence ratio); quarterly rolling (HPSSA).
- **Granularity**: **England & Wales only** for workplace/residence ratio. LA, parliamentary constituency, MSOA. London boroughs broken out — Kensington & Chelsea 25.2× vs Hyndburn 4.1× (2024 data).
- **Time series**: 1997–2024.
- **Known issues**: Uses individual full-time earnings via ASHE — distinct from household-income-based affordability. Self-employed excluded.
- **Licence**: OGL v3.0.

#### Life expectancy by deprivation
- **URL**: https://www.ons.gov.uk/peoplepopulationandcommunity/healthandsocialcare/healthinequalities
- **Latest**: Healthy Life Expectancy 2022–2024 (England & Wales separately).
- **Format**: XLSX + HTML bulletin.
- **Frequency**: Annual/biennial.
- **Granularity**: England and Wales separately (IMD vs WIMD); national IMD deciles; LSOA-level base; LE at birth, HLE, DFLE; sex disaggregation.
- **Headline 2022–24**: Male LE 73.2y (most deprived decile) vs 83.6y (least) — 10.4-year gap; female 78.3y vs 86.4y — 8.1-year gap. Healthy LE SII: 19.3 years (male), 20.1 years (female).
- **Licence**: OGL v3.0.

#### Effects of Taxes and Benefits on Household Income (ETB)
- **URL**: https://www.ons.gov.uk/peoplepopulationandcommunity/personalandhouseholdfinances/incomeandwealth/bulletins/theeffectsoftaxesandbenefitsonhouseholdincome/latest
- **Format**: XLSX (also tidy long format from 2019/20).
- **Frequency**: Annual (September); series since 1977.
- **Granularity**: UK; quintile/decile; country and region; tenure.
- **Known issues**: Living Costs and Food Survey sample only ~5,000 households; top-tail underestimation; SPI adjustment now applied at the top.
- **Licence**: OGL v3.0.

#### ONS Beta API (cross-cutting)
- **Endpoint**: https://api.beta.ons.gov.uk/v1
- **Docs**: https://developer.ons.gov.uk/
- **Auth**: None required. **Rate limit: 120 req/10 s and 200 req/minute.**
- **Format**: JSON, CSV, XLSX.
- **Caveat**: WAS reference tables, ETB datasets and housing affordability ratios are **not currently on the Beta API** — require direct XLSX download. The ONS developer hub describes the API as open and unrestricted with JSON plus filtered CSV/XLSX output, but the most useful inequality and wealth pages remain classic dataset downloads. Plan for a hybrid ingestion layer.

### 1.2 HMRC

#### Personal Wealth Statistics ("Identified Estates")
- **URL**: https://www.gov.uk/government/collections/distribution-of-personal-wealth-statistics
- **Status**: **Effectively dormant** — last tables 2014–2016 averaged period, published January 2019. Users redirected to WAS.
- **Granularity**: UK only; age × sex; estate-size bands; asset composition.

#### Capital Gains Tax Statistics
- **URL**: https://www.gov.uk/government/statistics/capital-gains-tax-statistics
- **Latest**: 2023/24 data, released 24 July 2025. New Table 9 on carried-interest gains added 2025.
- **Format**: ODS/XLSX; annual (July/August).
- **Granularity**: UK; gains by size band, asset class, taxpayer income decile/percentile, region (limited), age, sex.
- **Known issues**: Highly concentrated — **92% of taxable capital gains accrue to top 1%** (Advani & Summers). Volatile due to forestalling around rate changes (Oct 2024 Budget raised main rates). Realised gains only.
- **Licence**: OGL v3.0.

#### Inheritance Tax Statistics
- **URL**: https://www.gov.uk/government/statistics/inheritance-tax-liabilities-statistics
- **Latest**: 2022/23 tax year (annual).
- **Format**: ODS/XLSX.
- **Granularity**: UK; estate-size bands; asset composition; region of deceased; reliefs.
- **Known issues**: Captures only taxable estates above frozen nil-rate band (£325k since 2009, plus £175k RNRB). **Only ~4–5% of estates pay IHT.** Lifetime gifts >7 years before death excluded.
- **Licence**: OGL v3.0.

#### Income Tax Statistics / Survey of Personal Incomes (SPI)
- **Collection URL**: https://www.gov.uk/government/collections/personal-incomes-statistics
- **Latest**: SPI 2023/24 published 2025–26 (typical ~2-year lag).
- **Format**: ODS/XLSX tables (3.1, 3.1a percentile points; 3.11 region; 3.12–3.15a LA/constituency; 3.16–3.17 Scotland/Wales).
- **Granularity**: UK; percentile points; gender × age; **region/country, local authority, parliamentary constituency** with London broken out; Scottish/Welsh taxpayer indicator.
- **Known issues**: **Excludes non-taxpayers below personal allowance** (£12,570, frozen to 2031); 2018/19 grossing-factor revision creates a break; capital gains excluded; non-doms partly out of scope.
- **Microdata**: HMRC Datalab (accredited researcher only).
- **Licence**: OGL v3.0.

#### Tax receipts and NICs annual bulletin
- **URL**: https://www.gov.uk/government/statistics/hmrc-tax-receipts-and-national-insurance-contributions-for-the-uk
- **Format**: HTML bulletin + linked ODS table.
- **Frequency**: Annual long-run bulletin (latest released 23 April 2026); monthly receipts updates.
- **Use**: The cleanest source for the receipts-composition chart underpinning "tax leans heavily on work, lightly on wealth" — broken down by Income Tax, NICs, VAT, business taxes, stamp taxes, CGT, IHT.
- **Licence**: OGL v3.0.

### 1.3 Bank of England

#### Money & Credit, Bankstats, Interactive Database (IADB)
- **URL**: https://www.bankofengland.co.uk/boeapps/database/
- **Format**: CSV via parameterised URL pattern (`https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp?csv.x=yes&SeriesCodes=...`); XLSX.
- **Auth**: None; no documented rate limit (be courteous).
- **Frequency**: Monthly Money & Credit (~1-month lag); quarterly Bankstats.
- **Granularity**: **UK-aggregate only.** No regional, no decile.
- **Key series**: LPMVTVK (net mortgage lending), LPMB4B7 (mortgage approvals), LPMVZRI (consumer credit), LPMBI2O (household deposits), LPMBC8M (effective mortgage rate).
- **Status**: This is the most machine-friendly UK public-finance source in the stack after WID. CSV and XML query URLs are explicitly documented.
- **Licence**: BoE terms — re-usable for non-commercial use with attribution; functionally OGL-equivalent for stats.

#### NMG Household Survey
- **URL**: https://www.bankofengland.co.uk/statistics/research-datasets
- **Latest**: Microdata file updated 22 December 2025.
- **Format**: XLSX microdata + Stata `.do` file.
- **Frequency**: Was biannual; transitioning to annual.
- **Granularity**: ~6,000 GB households per wave; representative weights.
- **Coverage**: Mortgage DSR, income, savings flow, unsecured debt, financial distress, expectations. Timeliness advantage over LCF/WAS.
- **Known issues**: Smaller sample, less reliable than FRS/LCF for tails; selection-on-unobservables risk (Anderson et al. 2016).
- **Licence**: Free re-use with attribution.

#### Mortgage Lenders and Administrators Statistics (MLAR)
- **URL**: https://www.bankofengland.co.uk/statistics/mortgage-lenders-and-administrators
- **Frequency**: Quarterly; long back-run.
- **Use**: LTV/LTI risk distribution, arrears, regulated lending — the cleanest source for "are first-time buyers stretching further?" charts.

#### Financial Stability Report
- **URL**: https://www.bankofengland.co.uk/financial-stability-report
- **Format**: PDF + HTML + per-chart XLSX downloads.
- **Frequency**: Semi-annual (July, December).
- **Distributional content**: COLA-DSR distribution, FTB deposit-to-income ratios — illustrative, not a primary microdata release.

### 1.4 Think tanks

#### Resolution Foundation
- **URL**: https://www.resolutionfoundation.org/
- **Licence**: CC-BY-NC-ND 3.0 England & Wales.
- **Key publications**: *Who owns all the pie?* (Bangham & Leslie 2019); *Wealth Gap Year* (Leslie & Shah 2021); *Inequality Control* (Broome & Leslie Nov 2024); *Peaked Interest?* (2023); **Living Standards Outlook** (annual ~Feb); **Living Standards Audit** (annual mid-year); **Intergenerational Audit** (annual).
- **Public products**: Housing Indicators / Housing Outlook (quarterly/annual, with downloadable chart data beneath the charts) and the Intergenerational Audit dashboard (cohort, gender and regional exploration across jobs, housing, income, poverty, wealth and inheritances).
- **Access**: PDF + embedded chart Excels; chart data downloadable beneath the visualisations. **No REST API.**

#### Institute for Fiscal Studies (IFS)
- **URL**: https://ifs.org.uk/
- **Green Budget**: Annual since 1982 (Oct); chapter PDFs + chart Excels.
- **Deaton Review of Inequalities**: https://ifs.org.uk/inequality — ~30 evidence papers; closed 2025 with *Challenging Inequalities* OUP volume.
- **TAXBEN**: IFS microsimulation model — **not publicly distributed**. Open alternatives: UKMOD (Essex), EUROMOD.
- **Taxlab**: https://ifs.org.uk/taxlab — interactive charts and downloadable data on revenue composition, inheritance-tax distributions, rates and thresholds. The closest thing the UK has to a public tax-system explorer.
- **Living standards, poverty and inequality in the UK**: Long-run interactive (60+ years of data); annual companion to HBAI (~July).
- **Access**: PDF + per-figure Excel downloads. No central data hub or API.

#### Wealth Tax Commission (wealthandpolicy.com)
- **URL**: https://www.wealthandpolicy.com/
- **Key outputs**: Final Report (Dec 2020, DOI 10.47445/114); EP1 Advani, Bangham & Leslie on wealth distribution; EP2 Advani, Hughson & Tarrant on revenue modelling; 24 background papers.
- **Format**: PDF + companion revenue/distributional spreadsheets.

#### IPPR
- **Key publications**: *Wealth in the 21st Century* (Roberts et al. 2017); Commission on Economic Justice *Prosperity and Justice* (2018); *Just Tax* (2019).
- **Status**: Repeatedly describes its tax-benefit model in press notes and report pages, with occasional "download the data" links, but **no maintained public data hub**. Treat IPPR as an analysis/interpretation layer, not a backbone data provider.
- **Access**: PDFs, CC-BY-NC. No API.

#### Equality Trust
- **URL**: https://equalitytrust.org.uk/scale-economic-inequality-uk/
- **Role**: Aggregator/advocate — compiles charts from ONS, OECD, WID, Credit Suisse; publishes *Billionaire Britain*, evidence-base pages, and notes on sources and methods.
- **Status**: Excellent for claim framing and moral clarity; weak for programmatic reuse. **No interactive tools at all** — purely article-based with embedded PNG charts.
- **Access**: HTML pages, easily scrapable.

#### World Inequality Database (WID.world)
- **UK page**: https://wid.world/country/united-kingdom/
- **Bulk data**: https://wid.world/data/
- **Programmatic access**: Stata package `wid` (`ssc install wid`); R package `wid` (https://github.com/WIDworld/wid-r-tool); URL-based CSV fetches. No published rate limit.
- **Time series**: Income/wealth top shares back to early 1900s.
- **Methodology**: DINA (Distributional National Accounts) — Piketty/Saez/Zucman framework. UK pre-1995: Alvaredo/Atkinson/Morelli estate multipliers. Post-1995: Blanchet/Martínez-Toledano splice.
- **Licence**: CC-BY.

### 1.5 Supplementary sources

| Source | URL | Format | Frequency | Auth | Notes |
|---|---|---|---|---|---|
| UK Data Service | https://ukdataservice.ac.uk | Stata/SPSS/CSV | Per dataset | EUL/SL/SecureLab | Gateway to WAS, FRS, HBAI, LCF, UKHLS microdata |
| Understanding Society (UKHLS) | https://www.understandingsociety.ac.uk/ | Stata/SPSS | Annual | EUL/SL | Wave 14 (2025); panel data; intergenerational links |
| ELSA | https://www.elsa-project.ac.uk/ | Stata/SPSS | Biennial | EUL | Wealth in later life, England only |
| Land Registry Price Paid Data | https://www.gov.uk/government/statistical-data-sets/price-paid-data-downloads | CSV (~5GB) | Monthly | None | England & Wales; 1995–present |
| Land Registry SPARQL | https://landregistry.data.gov.uk/landregistry/sparql | SPARQL → JSON/CSV/Turtle | Monthly | None | Linked data, 400m+ triples |
| UK House Price Index | https://www.gov.uk/government/statistical-data-sets/uk-house-price-index | CSV / SPARQL | Monthly | None | UK-wide; LA granularity |
| Companies House API | https://developer-specs.company-information.service.gov.uk/ | JSON | Live | Free API key, **600 req/5min** | Filings, officers, PSCs |
| Companies House PSC bulk | https://download.companieshouse.gov.uk/en_pscdata.html | JSON-Lines (3GB compressed) | Weekly | None | Beneficial ownership |
| Open Ownership BODS | https://bods-data.openownership.org/source/UK_PSC/ | JSON-Lines | Weekly | None | CC-BY; cleaned PSC |
| Sunday Times Rich List | https://www.thetimes.com/sunday-times-rich-list | HTML | Annual (May) | Paywalled | Tippet & Wildauer (Greenwich PEGFA, 2024) reconstructed 1989–2024 |
| Forbes Billionaires | https://www.forbes.com/billionaires/ | HTML / scraped | Annual + live | Paywalled effectively | No official API |
| Knight Frank Wealth Report | https://www.knightfrank.com/wealthreport | PDF | Annual (March) | Free with reg | Proprietary Wealth Sizing Model |
| Wealth-X / Altrata | https://altrata.com/reports/world-ultra-wealth-report | PDF | Annual | Free abridged; full paid | Proprietary |
| LSE III | https://www.lse.ac.uk/international-inequalities | PDF working papers | Rolling | Free | No data API; OAI-PMH metadata via eprints.lse.ac.uk |
| Centre for Cities | https://www.centreforcities.org/data/data-tool/ | Interactive + CSV | Annual + monthly | None | 63 cities, 575 constituencies; includes Gini |
| Centre for Progressive Policy | https://www.progressive-policy.net/ | Interactive + Excel | Per publication | None | Sub-regional inequality |

### 1.6 Licence access tier summary

| Tier | Examples |
|---|---|
| **Open (OGL v3.0)** | All ONS/HMRC/BoE bulletins; Land Registry; Companies House; Nomis CSVs; ONS Beta API |
| **UKDS End-User Licence** | WAS (SN 7215), FRS (SN 4969), HBAI (SN 5828), LCF (SN 5986), ELSA, UKHLS — free registration |
| **UKDS Secure Lab / ONS SRS** | Detailed-geography microdata; accredited researcher under Digital Economy Act 2017 |
| **HMRC Datalab** | SPI, IHT, CGT, PAYE/RTI microdata — accredited researcher only |
| **Proprietary** | Sunday Times Rich List, Forbes, Knight Frank, Wealth-X/Altrata |

### 1.7 Critical methodological papers for the dashboard

1. **Advani, Bangham & Leslie (2021)** "The UK's wealth distribution and characteristics of high-wealth households", *Fiscal Studies* 42(3): 397–430. WAS + STRL + Pareto adjustment; **~£800bn missing from WAS at the top**.
2. **Advani, Hughson & Tarrant (2021)** Wealth Tax Commission EP13. Pareto adjustment refined with individual-level data.
3. **Alvaredo, Atkinson & Morelli (2018)** "Top wealth shares in the UK over more than a century", *J. Public Economics* 162: 26–47. Estate-multiplier wealth series 1895–.
4. **Blanchet & Martínez-Toledano (2022)** DINA UK 1995– WID working paper.
5. **Advani, Summers & Tarrant (2025)** *European Economic Review*: top-1% share varies 14.4–16.5% depending on aggregate choice; ~40% of top-1% identity changes.
6. **Advani & Summers (2024)** "Measuring and taxing top incomes and wealth", *Oxford Open Economics*.
7. **Vermeulen (2018)** "How fat is the top tail of the wealth distribution?", *Review of Income and Wealth* — Pareto framework.
8. **Tippet & Wildauer (2024)** PEGFA Greenwich — openly reconstructed STRL 1989–2024.
9. **Crawford, Innes & O'Dea (2016)** IFS WAS foundational paper, *Fiscal Studies* 37(1).
10. **OSR Assessment Report 396 (June 2025)** — WAS lost Accredited Official Statistics status.

---

## Section 3: The most compelling statistics — what campaigners cite, and how verifiable each one is

This section inventories the headline statistics most frequently used by Gary Stevenson, Tax Justice UK, Patriotic Millionaires UK, Richard Murphy, Equality Trust and Oxfam UK, and rates each for citizen verifiability. The campaign ecosystem is more concentrated than it first appears: the same handful of claims recur because they are legible in one sentence and point directly to a reform — wealth is extremely concentrated; houses have outperformed work; tax leans too heavily on labour and too lightly on wealth; inheritance tax is politically salient but economically narrow; and normal income statistics understate what capital gains do at the top.

### 3.1 Wealth share concentration
- **Top 10% own ~43–57% of household wealth.** WAS (April 2018–March 2020) gives 43%; Rich-List-augmented figure (used by JRF, Patriotic Millionaires, Oxfam) is 57%.
- **Top 1% share: ~12.6% (raw WAS) or ~21% (with Sunday Times Rich List Pareto adjustment)** — Advani, Bangham & Leslie 2020.
- **Top 0.1% share doubled between 1984 and 2013, reaching ~9%** (WID/Atkinson).
- **"50 families own more than the bottom 50% (~34 million people)"** — Equality Trust/Tax Justice UK/Patriotic Millionaires.
- **Wealth of UK billionaires up £11bn in 2024–25** (Oxfam/Tax Justice UK joint analysis).
- **Verifiability: MODERATE.** ONS WAS is free but underestimates the top; Rich List augmentation requires paywalled commercial data; different sources give materially different top-1% figures. The "50 families vs the bottom half" framing in particular combines billionaire/rich-list estimates at the top with survey-based estimates for everyone else — the methodology bridge matters as much as the headline.

### 3.2 Wealth-to-GDP ratio
- **UK household wealth rose from ~3× GDP in the 1980s to ~6.3× in Q1 2024**, peaking at ~8.4× in early 2021. Resolution Foundation *Wealth Check* / *Peaked Interest?*
- Gary Stevenson's most-used framing: "wealth was 2.5× national income 1955–1980s; today closer to seven."
- **Verifiability: MODERATE–HARD.** Requires combining ONS National Accounts household net worth with nominal GDP; historical pre-1995 figures rely on Blake & Orszag (1999) academic reconstruction; ONS does not publish the chart directly.

### 3.3 Wealth Gini vs Income Gini
- **Income Gini (disposable, AHC): ~0.39; BHC: ~0.35** (DWP HBAI 2023/24).
- **Wealth Gini: ~0.62–0.63** (ONS WAS).
- Equality Trust headline: "Top fifth take 36% of income and 63% of wealth; bottom fifth get 8% of income and 0.5% of wealth."
- **Verifiability: EASY for income; MODERATE for wealth.**

### 3.4 House price to earnings ratios (ONS Housing Affordability 2024 data)
- **England median home £290,000 = 7.7× median earnings £37,600** (down from 8.4× in 2023; up from ~3.5× in 1997).
- **Wales 5.9×; Northern Ireland <5× (only UK country under affordability threshold).**
- **London 11.1×** (peaked 12.9× in 2021).
- **North East 5.0×.**
- **Kensington & Chelsea 27.1× (most unaffordable LA); Blaenau Gwent 3.8× (most affordable).**
- In 1997 57.4% of London homes sold for <5× earnings; by 2024 only 3.0%. In the North East ~49.9% still under 5× in 2024.
- **Verifiability: EASY.** ONS publishes interactive tools and Excel back to 1997 at LA level.

### 3.5 Intergenerational wealth transfer / inheritance
- **Annual inheritance value forecast to ~double over 20 years** (Resolution Foundation).
- **"Bank of Family" funded ≈£8.1–9.4bn in 2023; supporting ~318,400 transactions**; set to climb to £10bn by 2025 (Legal & General/Cebr).
- **47–58% of first-time buyers receive parental support** (L&G 2023; Savills 2024); academic estimates suggest the share rose from ~10% in mid-1990s to ~60% today.
- **London: 67% of homeowners had parental help; average gift £30,200** (L&G).
- Children of non-homeowner parents are **60% less likely to be homeowners by age 30** (Resolution Foundation).
- **Only ~4–5% of estates pay inheritance tax** (HMRC) — paired with IFS estimates that scrapping it would disproportionately benefit the top 1%, this is one of the strongest myth-busting hooks in the field.
- **Verifiability: MODERATE–HARD.** RF forecasts use microsimulation on ELSA; commercial Bank-of-Mum-and-Dad surveys give widely differing estimates (47–60%); HMRC IHT distributions are buried in ODS spreadsheets and Taxlab items rather than one simple public explorer.

### 3.6 Effective tax rates — the "millionaires pay less than nurses" stat
Based on Advani, Hughson & Summers (2023) *Oxford Review of Economic Policy* "How much tax do the rich really pay?", using anonymised HMRC admin data on the entire UK taxpayer population:
- **EATRs peak at ~38% at total remuneration of £500,000; above £500k, EATRs FALL as remuneration rises** — the UK personal tax system is regressive above £500k.
- **A quarter of those in the top 1% pay at least 9pp less than the headline rate.**
- **92% of all taxable capital gains, by value, accrue to the top 1%.**
- Closing this gap (all >£100k paying headline rates) would raise **~£23bn/year**.
- Tax Justice UK extended framing (including indirect tax): **bottom 10% face effective rate of 44% vs top 0.01% on 21%**.
- **Verifiability: HARD.** Underlying papers use HMRC Datalab confidential admin data; citizens cannot replicate; methodology is technical; the 44% vs 21% framing is contested (depends on indirect taxes included).

### 3.7 The "tax on work vs tax on wealth" framing
- Patriotic Millionaires UK argues that taxes on work bring in almost half of UK receipts while taxes related to wealth bring in less than 5%; Tax Justice UK makes the same rhetorical move in its reform packages.
- **Important caveat the project must surface**: "taxes on wealth" is not a standard official category. Campaigners construct the basket, and different baskets include different combinations of CGT, IHT, stamp duties, council tax, property taxes and taxes on returns to saving. A credible visualisation needs a methodology toggle showing what is and isn't in the wealth-tax basket.
- **Verifiability: MODERATE.** HMRC tax receipts and NICs annual bulletin gives the raw numbers cleanly; the interpretive packaging is where contention sits.

### 3.8 The capital-gains-included top-share story
- Tax Justice UK explicitly cites analysis showing the **top 1% income share looks roughly flat near ~14% on ordinary measures since the late 1990s, but rises to ~17% when capital gains are included.**
- This is arguably **the single most important and least accessible idea in the whole debate**: conceptually central, empirically powerful, and extremely hard for ordinary people to reproduce because CGT data sits partly outside the headline household-income dashboards everyone sees.
- A capital-gains toggle on a top-shares chart is one of the highest-leverage explanatory moves the project can make.
- **Verifiability: HARD.** Requires combining SPI with CGT statistics and applying consistent treatment.

### 3.9 CEO-to-worker pay ratios (High Pay Centre annual report, FY2024/25)
- **Median FTSE-100 CEO pay £4.58m = 122× median full-time worker pay.**
- Mean FTSE-100 CEO pay £5.91m.
- **13 FTSE-100 CEOs paid >£10m in 2024/25.**
- **"High Pay Day": CEOs surpass median annual UK worker salary by midday/early-afternoon on the 3rd working day of January.**
- Top earner 2023: Pascal Soriot (AstraZeneca) £16.85m = 482× median worker.
- Denise Coates (Bet365, non-listed): £280m+ in 2025.
- **Verifiability: EASY–MODERATE.** UK Companies Act 2006 mandates single-figure remuneration disclosure plus pay-ratio reporting since 2019. High Pay Centre publishes its spreadsheet free; but compiling requires reading 100 annual reports.

### 3.10 Regional inequality
- **ONS Regional GDHI per head (2023): UK average £24,836; Westminster & City of London £79,555 (3.2× UK avg); Leicester £16,067 (lowest LA); North East £19,977 (lowest region).**
- **GVA per worker in rest-of-UK is 71% of London+SE** — wider than East/West Germany (80%) or South/North Italy (78%). Stansbury, Garretsen, McCann (2024).
- **McCann (2019) Regional Studies**: UK ranks in the top quarter on 21 of 28 regional-inequality measures; most unequal on 5. "Almost certainly the most interregionally unequal large high-income country."
- Kensington & Chelsea income/head (2019) £52,000 vs Nottingham £11,700 — 4.5× gap (Resolution Foundation Economy 2030).
- **Verifiability: MODERATE.** ONS Regional GDHI is free; McCann's ranking is a peer-reviewed paper not a dataset; productivity comparisons require OECD cross-walks.

### 3.11 Life expectancy gaps by deprivation
- **Male LE at birth: most deprived 73.2y vs least deprived 83.6y — 10.4-year gap.**
- **Female: 78.3y vs 86.4y — 8.1-year gap.**
- **Healthy LE Slope Index of Inequality: 19.3y (male), 20.1y (female).**
- Most-deprived areas remain below pre-pandemic LE (2017–19) by 0.8y male / 0.4y female.
- Marmot 10 Years On (2020): "England's health is faltering, and the social gradient is steepening."
- **Verifiability: EASY.** ONS Excel by IMD decile and sex; SII published.

### 3.12 Child and pensioner poverty (DWP HBAI)
- **2024/25: 4.0 million children in relative poverty AHC (27%); 2.8 million in deep poverty; 72% of poor children in working families.**
- **Trend: child poverty rose by ~900,000 since 2010/11** under old methodology.
- **Two-child limit (April 2017) capped UC/CTC at 2 children; scrapped April 2026 by Labour. DWP modelling: removal lifts ~450,000 children out of poverty.**
- **Total UK relative poverty AHC: 13.4m people (~20% of population).**
- **Pensioner poverty: rose from 13% AHC in 2012 to ~16% (1.9m) by 2022/23.**
- **Verifiability: EASY–MODERATE.** HBAI free; 2025 methodology change creates discontinuity; constituency breakdowns require modelled End Child Poverty data.

### 3.13 Tax gap (contested)
- **HMRC official 2022/23 figure: £39.8bn (4.8% of liabilities).**
- **Richard Murphy / Tax Research UK: "well in excess of £100bn/year."** No agreed methodology; IFS and Oxford Centre for Business Taxation say Murphy's number is overstated. **Any visualisation should show both ranges.**
- **Verifiability: HARD.**

### 3.14 The polling layer
Patriotic Millionaires UK and Tax Justice UK both repeatedly publicise polling showing majority public, MP and even millionaire support for a wealth tax — used to neutralise the "popular but impossible" objection. Survation, YouGov and Oxfam-commissioned polls are the typical sources. Verifiability is moderate at toplines (the polls themselves are public) but ordinary readers rarely see question wording, subgroup detail or fieldwork breakdown — a "polling explorer" with these layers exposed would be a strong differentiator.

### 3.15 Gary Stevenson's "core canon"
From his YouTube, TED, Diary of a CEO and Prof G appearances, the most-used stats:
1. UK wealth ≈ 7–8× GDP today vs ~3× in the 1980s.
2. Billionaire wealth doubled in two years of the pandemic.
3. Top 1% have 3× the wealth of the next 1%.
4. <50 families own more than the bottom 30 million.
5. Median CEO pay 122× median worker.
6. Foodbank use up ~10× since 2012 (Trussell Trust).

Notably, Stevenson's most effective rhetorical move is usually a **mechanism claim** rather than a canonical table: concentrated wealth bids up asset prices (especially housing) while work does not keep up. He repeatedly frames housing as an asset market first and a shelter market second. This is hard to verify not because the components are missing but because **no existing public tool cleanly chains asset-price inflation → wealth concentration → inheritance → household tax burden in one evidence stream**. Building that chain is itself a strategic opportunity.

### 3.16 Verifiability summary

| # | Statistic | Source | Verifiability | Bottleneck |
|---|---|---|---|---|
| 1 | Top 1/10% wealth share | WAS + STRL | Moderate | Rich List paywall; methodology choice |
| 2 | Wealth-to-GDP | ONS Blue Book + RF | Moderate-Hard | Derived ratio; no ONS chart |
| 3 | Gini income vs wealth | HBAI; WAS | Easy / Moderate | WAS publication lag |
| 4 | House price/earnings | ONS HA | **Easy** | Choice of measure |
| 5 | Inheritance / BoMaD | RF; L&G; HMRC | Moderate-Hard | Microsim/commercial surveys |
| 6 | Effective tax rates | Advani et al. via HMRC Datalab | **Hard** | Confidential admin data |
| 7 | Tax on work vs wealth | HMRC receipts (re-categorised) | Moderate | Basket is constructed, not official |
| 8 | Top 1% income share +/- CG | SPI + CGT | **Hard** | Combining tables; CGT distribution not public-friendly |
| 9 | CEO pay ratio | High Pay Centre | Easy-Moderate | 100 annual reports |
| 10 | Regional inequality | ONS GDHI; McCann | Moderate | OECD cross-walks |
| 11 | LE by deprivation | ONS | **Easy** | SII concept |
| 12 | Child/pensioner poverty | HBAI | Easy-Moderate | 2025 methodology break |
| 13 | Tax gap | HMRC; Murphy | **Hard** | No agreed methodology |
| 14 | Wealth-tax polling | Survation / YouGov | Moderate | Crosstabs rarely surfaced |

**Strongest candidates for citizen-facing explorable tools** (high salience + reliable free sources + clear definitions): house-price-to-earnings (#4), regional GDHI (#10), LE by deprivation (#11), CEO-to-worker pay (#9), child poverty (#12).

**Hardest to make explorable but most rhetorically powerful**: wealth concentration (#1), effective tax rates (#6), capital-gains-inclusive top shares (#8), inheritance flows (#5). These are precisely where a new tool adds the most public value — they are where the public-debate-vs-public-tool gap is widest.

---

## Section 4: Existing UK tools and dashboards — landscape and gap analysis

The strongest framing of this landscape is that it is **rich in fragments and poor in synthesis**. WID has top shares; Resolution Foundation has housing and intergenerational; IFS Taxlab has tax mechanics; BoE has the most machine-readable infrastructure; Trust for London has methodological transparency. None of them traces the spine of public debate — *who owns what → how did they get it → how is it taxed → where does housing fit in?* — end to end. The remaining gap analysis flows from there.

### 4.1 Office for National Statistics (ONS)

**"Income, spending and wealth: how do you compare?"** (https://www.ons.gov.uk/visualisations/dvc1802/calculator/index.html). Four-measure framework (income, spending, financial wealth, property wealth) with equivalisation. Excellent design but **uses April 2018–March 2020 data and has not been updated since March 2022** — pre-pandemic, pre-cost-of-living-crisis. No regional drill-down. No embed code. GB-wide only.

**ONS Census 2021 Interactive Maps** (https://www.ons.gov.uk/census/maps). OA-level granularity, mobile-friendly, embeddable, **open source on GitHub** (Svelte Kit + Maplibre GL JS). Strong UX. **No wealth data** (Census doesn't ask); England & Wales only; snapshot only.

**"Build a custom area profile"** (https://www.ons.gov.uk/visualisations/customprofiles). Innovative: draw polygon → aggregate Census + EPC + house sales. Embeddable via Pym JS, **open source**. May 2025 LSOA update. Census-only for most variables — no wealth.

### 4.2 Institute for Fiscal Studies

**"Where do you fit in?"** (https://ifs.org.uk/tools_and_resources/where_do_you_fit_in). The most-cited UK inequality calculator, widely shared on Mumsnet/Reddit. Annual HBAI update. **But: income only — ignores wealth entirely; no regional breakdown (UK single distribution); no policy simulation despite TAXBEN existing internally; visually dated.**

**Taxlab** (https://ifs.org.uk/taxlab). The closest thing in the UK to a public tax-system explorer — revenue composition, IHT distributions, rates and thresholds, distributional charts. Strong where the question is "what does this tax actually do?" Limitation: the wealth-distribution story, the housing story and the tax story still live in different IFS products.

**Living standards, poverty and inequality in the UK** — long-run interactive (60+ years of data). Strong on incomes, poverty and inequality; weaker on wealth.

**TAXBEN** is not user-facing. **Deaton Review** has produced authoritative chapter PDFs but **no interactive landing page** — a major missed opportunity.

### 4.3 Resolution Foundation

**Intergenerational Audit Dashboard** (https://www.resolutionfoundation.org/major-programme/intergenerational-centre/dashboard/). One of the best UK wealth dashboards in existence: cohort decomposition, wealth-and-assets module, regional and gender breakdowns. **But charts are largely static; no personal comparator; not embeddable; not open source; does not consistently split London out; organised around cohorts and life stages more than around the top tail or tax justice.**

**Housing Outlook / Housing Indicators** (https://www.resolutionfoundation.org/major-programme/housing-indicators/). Quarterly/annual updates; regional breakdowns; **data downloads beneath each chart**. The sharpest public-facing housing-affordability layer in the UK — but housing-only and not embeddable.

**Living Standards Outlook**: static PDF/web essay format; **no interactive equivalent**.

### 4.4 World Inequality Database (WID.world) UK page

(https://wid.world/country/united-kingdom/). Long historical series (back to early 20th century); methodologically rigorous; open API; cross-country comparable. **But: clunky academic UI; five-indicator selection cap; UK national only — no regions, no London; not mobile-optimised; updates irregular; weak on housing affordability, inheritance, UK tax detail and subnational geography.**

### 4.5 Tax Justice Network

**Financial Secrecy Index** (https://fsi.taxjustice.net/) and **Corporate Tax Haven Index**. Rigorous methodology, downloadable CSV. UK ranks high due to Crown Dependencies/OTs. **Cross-country only — doesn't show how UK individuals or regions interact with secrecy.**

### 4.6 Equality Trust

(https://equalitytrust.org.uk/scale-economic-inequality-uk/). **No interactive tools at all** — purely article-based with embedded PNG charts. The UK's lead inequality campaigner has effectively zero interactive infrastructure. Clear opportunity for a new project.

### 4.7 Our World in Data

(https://ourworldindata.org/economic-inequality). All charts embeddable under CC-BY; clean UX; mobile-friendly; the gold standard of inequality charting globally. **But UK is a filter option, not a dedicated dashboard; no UK sub-national content; no personal comparator.**

### 4.8 Trust for London — London's Poverty Profile

(https://trustforlondon.org.uk/data/). 100+ indicators across 32 boroughs; **best-in-class London-vs-rest-of-England comparison**; per-chart exports; explicit confidence intervals; well-funded ongoing maintenance. **Inside-London only by design.**

### 4.9 Centre for Cities — Data Tool

(https://www.centreforcities.org/data/data-tool/). 17 indicators across 63 cities and 575 constituencies. **Includes a Gini coefficient indicator (rare at city level).** Time series, data downloads. **No household wealth metrics; mostly economic activity rather than distribution; not open source.**

### 4.10 Joseph Rowntree Foundation

**UK Poverty Statistics dashboard** (https://www.jrf.org.uk/uk-poverty-statistics) — companion to annual UK Poverty report, broad demographic dimensions; **RAPID** (Real-time Analysis of Poverty Indicators Dashboard) uses administrative benefits data for near-real-time regional poverty estimates; **Cost of Living dashboard** based on JRF/Savanta tracker survey.

### 4.11 Constituency-level tools

**End Child Poverty constituency map** (https://endchildpoverty.org.uk/) — annual; Loughborough CRSP methodology. **House of Commons Library constituency dashboards** — authoritative but plain UX. **Open Innovations hex maps** (https://constituencies.open-innovations.org/) — **open source on GitHub, embeddable, beautiful cartograms**.

### 4.12 LSE International Inequalities Institute

(https://www.lse.ac.uk/international-inequalities). Cutting-edge research (Savage, Advani, Summers, Glucksberg). **Almost entirely PDF/report-driven — no interactive flagship dashboard.** A massive missed opportunity for the UK's leading academic inequality centre.

### 4.13 Health inequality

**OHID Fingertips** Wider Determinants of Health profile; **Institute of Health Equity / Marmot Indicators**. Functional but government-portal UX; not wealth-focused.

### 4.14 International comparators (for inspiration)

**OECD "Compare Your Income"** (https://www.compareyourincome.org/) — best-in-class design (Veyssière); gamified UX; asks normative redistribution questions. Most countries' data 2012–2014 baseline.

**Federal Reserve Distributional Financial Accounts** (https://www.federalreserve.gov/releases/z1/dataviz/dfa/) — **the gold-standard wealth dashboard.** Quarterly updates reconciling Financial Accounts with SCF; from 1989 onwards; top 0.1%/0.9%/9%/40%/bottom 50% with age, generation, education, race breakdowns. **A direct UK equivalent does not exist — this is arguably the single biggest gap.**

**INSEE / Le Figaro French wealth map** — spatial self-comparison across ~300 employment zones. **Urban Institute Upward Mobility Dashboard** (https://upward-mobility.urban.org/dashboard) — exemplary peer-comparison design, open source. No UK equivalent.

### 4.15 Comparison table

| Tool | Geo granularity | Wealth? | London/Rest split | Open source | Embeddable | Last updated |
|---|---|---|---|---|---|---|
| ONS "How do you compare?" | UK only | ✓ partial | ✗ | ✗ | ✗ | **Mar 2022 (stale)** |
| ONS Census Maps | OA→LAD | ✗ | London boroughs | ✓ | ✓ | 2023 |
| ONS Build a custom area | Polygon→OA | ✗ | Yes | ✓ | ✓ | May 2025 |
| IFS "Where do you fit in?" | UK only | ✗ | ✗ | ✗ | ✗ | Annual HBAI |
| IFS Taxlab | UK only | Tax mechanics | ✗ | ✗ | Per-chart | Rolling |
| RF Intergenerational Dashboard | UK + some regional | ✓ | Partial | ✗ | ✗ | 2024 |
| RF Housing Indicators | UK/GB/England regions | Property only | ✗ | ✗ | ✗ | Quarterly |
| Trust for London | London borough | ✗ | **Yes (best)** | ✗ | Per-chart | 2025/26 |
| Centre for Cities Data Tool | 63 cities + 575 constituencies | Gini included | London = 1 city | ✗ | Custom export | Jan 2025 |
| Open Innovations hex maps | Constituency | Partial | Yes | ✓ | ✓ | Rolling |
| WID.world UK | UK only | ✓ | ✗ | API | Limited | Irregular |
| US Fed DFA | US only | **Gold standard** | n/a | Partial | ✓ | **Quarterly** |

### 4.16 Gap analysis — where the new project can add value

1. **No UK equivalent of the Fed DFA.** The single biggest gap: no quarterly (or even annually-refreshed) interactive showing UK wealth distribution by top 0.1%/1%/10%/middle 40%/bottom 50% with age/generation/region/ethnicity breakdowns.
2. **ONS "How do you compare?" is effectively abandoned** (stale pre-pandemic data).
3. **No tool treats "London vs rest of England" as a first-class axis.** Yet London median wealth is roughly twice the North's (£503k vs ~£250k per WAS 2022). The income 90:10 ratio in London diverged from rest of England from 2.5 to 4.9 over 25 years.
4. **Personal comparators ignore wealth.** IFS is income-only; ONS uses pre-pandemic data. **A live, well-maintained wealth-and-income personal comparator with regional context does not exist.**
5. **No tool combines macro distribution with micro personal data** (à la OECD asking normative questions).
6. **No tool synthesises the four-step debate spine end-to-end** — who owns what → how did they get it → how is it taxed → where does housing fit in.
7. **Most tools are not embeddable.** First-class embed codes are a real differentiator.
8. **Open source is rare.** No canonical open-source GitHub repo for "UK wealth inequality charts you can clone and extend."
9. **Methodology is opaque almost everywhere.** WAS lost ONS accreditation in June 2025 but no tool surfaces this. Visible, dated methodology with source links is differentiating.
10. **No public tool exposes the capital-gains-inclusive top-share story.** SPI + CGT need to be combined; nobody is doing it for the public.
11. **No tool tracks tax-haven/offshore wealth at UK individual or geographic level.**
12. **Health-inequality is siloed from wealth.** A tool connecting wealth deciles to LE/HLE at LA level would be novel.
13. **Mobile-first design is rare.**
14. **Wealth time-series is missing.** Most tools show snapshots.
15. **No live policy-counterfactual tool.** "What would the wealth distribution look like under a 1% tax above £10m?" is unprecedented in UK public-facing tooling.
16. **Constituency-level wealth is missing entirely.** WAS sample size limits this; synthetic estimation à la End Child Poverty is possible.

---

## Section 5: Shareable visualisation formats and concrete recommendations

The strategic principle, drawing across both research passes: do not start with a giant general dashboard. Start with **a small family of atomic charts that each make one claim, expose one source, and survive a phone screen**, and progressively let them compose into a coherent synthesis tool. The most successful UK inequality content of the past three years — Burn-Murdoch's FT charts, Stevenson's whiteboard clips, Trust for London's per-chart exports — has worked because individual artefacts each make one point cleanly, then accumulate into a worldview.

### 5.1 Historically viral inequality visualisations — what worked

**Wilkinson & Pickett's Spirit Level scatterplots** (2009). 25+ scatters of national inequality (x) vs social outcomes (y). The repetition across radically different outcomes is what made them sticky — a **visual argument by accumulation**. Lesson: **a family of charts with one consistent visual grammar** beats one clever chart.

**Piketty / WID top-share lines**. The U-shaped top-1% curve (1913–today) carries a book-length argument. Lesson: **one number, one century, one line.**

**Mona Chalabi**. Won the 2023 Pulitzer for "9 Ways to Imagine Jeff Bezos' Wealth" — rendered as cake slices, decibels, lifetimes-of-Amazon-work. Hand-drawn aesthetic signals fallibility. Lesson: **hand-drawn imperfection + analogy stack + a single absurd celebrity number** is a viral formula.

**FT John Burn-Murdoch**. "A poor society with some very rich people" (US/UK, Sep 2024); "Britain is a poor country with one wealthy region"; "Inequality hasn't risen — here's why it feels like it has" (Jan 2025). Formula: **declarative, counter-intuitive headline + one well-designed distribution chart + tweet thread.**

**Matt Korostoff "Wealth, shown to scale"** (https://mkorostoff.github.io/1-pixel-wealth/). Pure horizontal scroll. 1 pixel = $1,000. Users scroll for minutes past Bezos's wealth. **Open source on GitHub.** Lesson: **physical scale shock via boring repetition** is more powerful than any chart.

**Dollar Street** (Anna Rosling Rönnlund). 200+ homes in 50 countries, ordered by income. Lesson: **photographs as data points** beat abstractions for general audiences.

**NYT Upshot "Income Mobility Charts for All US Colleges"** (Chetty/Opportunity Insights). Most-emailed NYT piece in its week. Lesson: **personal-search dimension** (find your college/postcode) drives engagement.

**Pew "Are you middle class?" calculator**. Re-skinned by CNBC, Kiplinger, Yahoo annually. Lesson: a **single-input calculator yielding a personally surprising verdict** generates evergreen pickup.

**IFS "Where do you fit in?"** — the UK equivalent of Pew. Still going strong; regularly trends on Mumsnet/Reddit when households are shocked to discover £70k = top 15%.

**Oxfam billionaire framings.** Annual Davos "richest X own as much as bottom Y" headlines — convert percentages into time, football, or single-person comparators.

**Bloomberg Billionaires Index** live ticker. Lesson: **live data = press pick-up engine.**

**Gary Stevenson** ("Gary's Economics") — ~1.3m YouTube subs; whiteboard explainers; viral TikTok clips (~80k likes for Novara/BWB Question Time re-cuts). Lesson: a **face + a marker + a working-class voice** outperforms infographics on TikTok.

**Pudding.cool "Why the super rich are inevitable"** (Yard-Sale Model, 2022). Playable simulator + simple bars. Among Pudding's most-shared.

### 5.2 Visualisation patterns — when to use each

| Pattern | Why it works | Best examples | Risks |
|---|---|---|---|
| **Personal comparator** ("where do you fit") | Self-relevance triggers sharing; surprise that you rank higher/lower than expected | IFS, Pew, ONS, NYT How Class Works | Privacy worries; top-decile underestimate |
| **Scale shock / unit comparator** | Converts abstract billions into time, distance, cakes | Korostoff, Chalabi, Oxfam | Forced analogies easy to mock |
| **Time-lapse animated share** | "Look what changed" GIF for X | Piketty U-curve; WID animations | Muted by default; mobile playback |
| **Before/after slider** | Forces engagement; "then vs now" housing | NYT, Pudding | Doesn't autoplay on social |
| **Scrollytelling** | Long-form on mobile; stepped argument | Pudding, Reuters, ONS Svelte template | Heavy build; performance |
| **Isotype / pictogram** | Friendly, scannable for Instagram | Chalabi, Otto Neurath | Imprecise for fine differences |
| **Small multiples by region** | UK's regional polarisation made inescapable | FT regional charts | Hard to read on mobile if too many panels |
| **Cleveland dot plots** | Best for league-table X vs Y | Centre for Cities | Boring unless annotated |
| **Treemap of wealth composition** | Shows pensions vs housing vs financial | RF | Squarified treemaps awkward on mobile |
| **Lorenz/Gini animation** | Useful for education | CORE Econ | Looks academic; doesn't shock |
| **Powers-of-ten zoom** | Works for many-orders-of-magnitude differences | Korostoff | One-trick |
| **Source / methodology toggle** | Source disagreement becomes a feature, not a footnote | NYT, ourworldindata.org | Easy to add too late; design from day one |
| **Personal-input calculator** | High dwell-time; screenshot-friendly result | Pew, IFS, ONS | Privacy + share-card design matters |

Underlying principles (Tufte, Cairo, Few) converge: **clear comparisons + emotional anchor + personal relevance** beats virtuosic complexity.

### 5.3 Mobile-first design

- **70%+ of social inequality content is consumed on mobile.** Build mobile-first.
- **Vertical first** for Stories/Reels/TikTok (9:16); square (1:1) is universal fallback.
- **Touch targets ≥44px.**
- **Performance budgets**: <200KB JS, time-to-interactive <3s on 4G. Static SVG/PNG fallback for heavy interactives.
- **No hover-only interactions** — tap or always-visible labels.
- **Annotate inside the chart**, not in a separate caption — when re-uploaded to social, surrounding context is lost.
- **Branded screenshot/share-card auto-generated** for every calculator output.
- **Specific dimensions**:
  - X/Twitter inline: 1200×675 (16:9) and 1080×1080 (1:1)
  - Instagram feed: 1080×1080 (1:1) and 1080×1350 (4:5)
  - Stories / Reels / TikTok: 1080×1920 (9:16)
  - LinkedIn link preview: 1200×627; document carousel: 1080×1080
  - Open Graph hero: 1200×630

### 5.4 Platform-specific guidance

**X / Twitter** — Static images dominate; threads outperform single tweets (FT/Burn-Murdoch model). Embed video clips ≤2:20. Declarative headline as alt-text + on-chart annotation.

**Instagram** — Carousels (10 slides) are the most-shared inequality format (Chalabi playbook): slide 1 hook number, 2–8 unpack, last slide CTA. Reels (9:16, 15–60s) for "Did you know..." with text overlay + captions. Stories for ephemeral polls.

**TikTok** — 9:16, 15–60s. Most shareable UK inequality content here is *people, not charts*: Gary Stevenson clips. Chart-only content rarely breaks 50k views. Hybrid (presenter pointing at on-screen chart) works.

**LinkedIn** — Document carousels (PDF, 1:1) get 3–10× engagement of link posts. Always include takeaway annotation directly on the chart.

**YouTube** — Long-form for Stevenson-style whiteboard explainers; Shorts (9:16, <60s) for animated single-chart explainers.

**Substack/email** — Static PNG + one-paragraph commentary outperforms embedded interactives.

### 5.5 UK-specific viral inequality content (proven travel)

- **Resolution Foundation** "Top of the Charts" weekly email + chart packs. 2025 viral moment: "wealth-to-income ratio doubled since 1980 vs flat Gini" — punctures the "inequality hasn't risen" claim.
- **Gary Stevenson** whiteboard explainers (1.3m YT subs, 140m views).
- **FT John Burn-Murdoch** "Britain = poor country with one wealthy region."
- **Centre for Cities Cities Outlook 2025**: "London wages 68% higher than Burnley" — BBC/Times/Personnel Today pick-up.
- **"High Pay Day"** (CIPD/High Pay Centre, every January) — reliable press cycle.
- **"Britain has the only widening lifespan gap among rich countries"** (Burn-Murdoch / Mayhew at Bayes, 2024).
- **"Half the country's wealth is now inherited not earned"** (Resolution Foundation framing).
- **Oxfam GB Davos splash**, annual.

### 5.6 Concrete recommendations — 16 named visualisations the team should build

**1. "Where Do You Fit in UK Wealth?" — personal comparator**
Data: WAS + RF processed micro-data. Type: Calculator (income + savings + housing equity + pension) → percentile + auto-generated 1:1 share card "I'm in the top X% of UK wealth." Platform: web hub with share cards for X/IG/LinkedIn. Why it shares: people consistently underestimate their rank. Mobile: single-column form, numeric keypad. Pitfalls: pension valuation is conceptually tricky — provide tooltip; don't store user data.

**2. "Regional house-price-to-earnings scrolly: London vs NE England vs Wales vs NI vs Scotland"**
Data: ONS HPSSAs + ASHE earnings; Nationwide regional series; Land Registry. Type: Scrollytelling, stacked area/line charts, inline maps; build on Svelte (ONS open-source template at github.com/ONSvisual/income-scrolly). Platform: web + still frames for IG carousel + Twitter thread. Mobile: charts pinned, text scrolls. Pitfalls: 12 regions = too many panels on mobile — reduce to 5 nations/regions.

**3. "House for the price of a house: what £200k buys you across the UK"**
Data: Land Registry / Rightmove. Type: Dollar-Street-style photo grid: same budget, 10 cities, real listings. Platform: Instagram carousel (10× 1:1) + Twitter thread + LinkedIn document. Pitfalls: image rights — commission or get permission; refresh quarterly.

**4. "Animated UK wealth concentration: 1980 → 2025"**
Data: WID UK series + RF historical. Type: 15-second GIF/MP4 of top-1% share line rising plus stacked bar of top-10/middle-40/bottom-50 reshuffling. Platform: X video, IG Reel, LinkedIn. Mobile: 1:1 and 9:16 cuts with burnt-in captions (85% of social video plays muted). Pitfalls: UK wealth Gini is flatter than US — pair with wealth-to-income ratio to avoid Burn-Murdoch "inequality hasn't risen" rebuttal.

**5. "Inheritance Britain: who inherits what, and when?"**
Data: WAS + IFS inheritance research; HMRC IHT. Type: Sankey from parental wealth quintile → child inheritance quintile + age-at-inheritance histogram. Platform: web scrolly; PNG cuts for social. Why it shares: speaks directly to millennials/Gen-Z. Mobile: Sankeys are hard — fallback to two ranked dot plots side-by-side. Pitfalls: timing-of-inheritance data sparse; flag estimates.

**6. "The Two Englands: London vs the rest, in 10 charts"**
Data: Stansbury/Garretsen/McCann 2024; OECD; ONS. Type: Small-multiples grid of dot plots, consistent x-axis (UK regions) with London highlighted. Platform: LinkedIn document carousel; Twitter image thread. Replicates Burn-Murdoch's "poor country with one rich region" with multiple supporting charts. Mobile: 4:5 portrait stack, one panel per slide. Pitfalls: avoid London-bashing tone; include AHC measure where London actually drops.

**7. "Marmot postcode life-expectancy gap"**
Data: ONS LE-by-ward + Marmot indicators (fingertips.phe.org.uk). Type: Postcode lookup → "babies born here live X years less than [richest ward]" + map. Platform: web + auto-share card. Why it shares: ultra-local, emotional. Mobile: postcode-only single field; geolocation opt-in. Pitfalls: small-area mortality CIs wide — show range; frame as "the system" not "your neighbours."

**8. "Compare your effective tax rate to a billionaire"**
Data: HMRC personal tax bands + ETI from Advani/Summers; Forbes/Bloomberg UK billionaires. Type: Two-bar calculator: your effective rate (income tax + NI + VAT + council tax as % of income) vs a UK billionaire's (capital-gains-dominated). Platform: X image, IG Reel walkthrough, LinkedIn carousel. Why it shares: punctures "the rich pay all the tax"; outputs personal screenshot. Pitfalls: definitions of "effective rate" contested — link to methodology and allow toggle.

**9. "The CEO-vs-worker pay clock" — UK FTSE-100 version**
Data: High Pay Centre / CIPD; FTSE-100 single-figure remuneration. Type: Live countdown clock animation: "as of HH:MM today, the median FTSE-100 CEO has out-earned the typical UK worker's annual salary." (Currently first working week of January.) Platform: pinned site widget + animated GIF. Why it shares: live ticker urgency; renewed every January for free press cycle.

**10. "Lifetime tax burden by income percentile" — the missing UK calculator**
Data: IFS TAXBEN or open UKMOD; ONS effects-of-taxes-and-benefits. Type: Interactive — input age, income, region → simulated lifetime VAT + council tax + NI + income tax + SDLT, as £ total and % of lifetime earnings. Platform: web + per-decile share cards. Why it shares: nobody has built this for the UK. Pitfalls: requires future-policy assumptions — show "based on current 2026 system."

**11. "1 pixel = £1,000: UK wealth to scale"**
Data: STRL (Tippet & Wildauer reconstruction) + WAS bottom 50%. Type: Horizontal scroller à la Korostoff, UK-flavoured: median household → top-decile threshold → Premier-League footballer → top 1% threshold → Hinduja family / Reuben Brothers. Platform: standalone microsite; auto-screenshot landmarks for X/IG. Mobile: native horizontal touch-swipe; use CSS not SVG for the long strip.

**12. "If the UK were 100 people"**
Data: WAS + Census. Type: Pictogram of 100 stick figures, animated: "1 of them owns 21% of wealth … 50 of them share 4.6%" — Chalabi-style hand-drawn. Platform: IG/TikTok Reel (15–30s); IG carousel for static; X video. Mobile: 9:16 native; subtitle burn-in. Pitfalls: 100-people metaphor over-simplifies — use one composition per Reel.

**13. "Gary-style whiteboard explainer series"**
Type: 60-second talking-head + marker + one number, replicating Stevenson's TikTok format (which has demonstrably outperformed any UK think-tank infographic on TikTok). Platform: TikTok + YT Shorts + IG Reels (single 9:16 export, all three). Mobile: native vertical; captions burnt in. Pitfalls: presenter risk — choose credible voice; link to data in pinned comment.

**14. "UK Spirit Level 2.0" — regional scatterplots**
Data: ONS regional inequality + LE / mental health / obesity / educational outcomes. Type: Family of 6–10 scattergrams, UK local authorities, one consistent layout (Wilkinson–Pickett accumulation strategy). Platform: PDF/PNG bundle for press; LinkedIn carousel; X thread. Pitfalls: ecological-fallacy risk — show within-area variance.

**15. "The wealth detective" — find the UK billionaire near you**
Data: Companies House + Land Registry corporate ownership + STRL. Type: Postcode → nearest UK billionaires + estimated wealth + property holdings within 10 miles. Platform: web; map-image share cards. Why it shares: hyper-local + investigative. Pitfalls: UK defamation/privacy law is harsher than US — only verified public data; legal review essential.

**16. "The capital-gains toggle" — top 1% share with and without**
Data: HMRC SPI percentile points + CGT statistics; Tax Justice UK analysis as the public reference. Type: Single line chart of top 1% share since the late 1990s, with a prominent toggle that flips between "ordinary income only" (~14% flat) and "income plus capital gains" (~17%, rising). Platform: web (interactive toggle); animated GIF cut for X/IG showing the flip. Why it shares: it visibly *changes the answer*. This is the single best public-education visual in the whole field — it reveals a hidden driver of top-end inequality that the usual household-income charts miss. Pitfalls: methodology footnote essential; CGT is realised gains only — flag the unrealised-gains caveat.

**17. "The methodology honesty card" — companion to every wealth chart**
Data: ONS WAS + WID + STRL reconstruction. Type: Small repeating UI element shown beside every top-tail chart, with three states: "ONS WAS", "WID DINA", and "WAS + Rich List Pareto adjustment". Tapping cycles the chart between them and shows a one-line explanation of why the answer changes. Platform: web; share cards for X include the active source on the image. Why it shares: in this space, transparency *is* the feature — especially after WAS lost accredited status in June 2025. No major UK campaign tool does this. Pitfalls: the explanations must be jargon-free and the default state needs a defensible choice (recommend WAS + Pareto adjustment as the labelled headline).

### 5.7 Top-5 build priority (highest viral potential per build-hour)

1. **"Where do you fit in UK wealth?"** calculator (#1) — guaranteed evergreen pickup, IFS/Pew template proven.
2. **"1 pixel = £1,000" UK scroller** (#11) — single-developer build, Korostoff has shown the ceiling is enormous.
3. **CEO Pay Clock** (#9) — automatic January press cycle.
4. **"House for £200k across the UK"** carousel (#3) — fast to produce, IG-native.
5. **Gary-style whiteboard Shorts series** (#13) — lowest production cost, highest TikTok reach.

Strong honourable mention: the **capital-gains toggle** (#16) — lower viral ceiling than the calculator but unmatched explanatory leverage; pair with whiteboard Shorts to amplify.

### 5.8 Health warnings for the team

1. **Gini-only is a trap.** Burn-Murdoch's most-recent UK piece argues headline inequality has been flat; always pair Gini with wealth-to-income ratio and top-1% share to avoid rebuttal.
2. **Mobile dominates** — never design desktop-first.
3. **Auto-share-cards** for every interactive — what isn't designed to be screenshotted, won't be.
4. **One number, one chart, one sentence** per social post; save complexity for the website.
5. **Localise everything** — postcode lookups consistently outperform national averages.
6. **The face matters on TikTok/Reels** — pure animated charts underperform a presenter pointing at the chart.
7. **Surface the WAS undercoverage caveat prominently** — most public-facing UK wealth content does not, and credible critics will use this against you.
8. **Show methodology and source dates** on every chart — Trust for London is the template.
9. **Treat source disagreement as a feature.** A toggle between ONS, WID and Rich-List-augmented figures is more honest *and* more engaging than picking one number.
10. **Flag constructed categories.** "Taxes on wealth" is not an official basket — show what's in and out.

### 5.9 Open-source build references

- Pudding scrollytelling library & responsive guide: pudding.cool/process/responsive-scrollytelling; scrollama.js
- ONS open-source Svelte scrolly template: github.com/ONSvisual/income-scrolly
- ONS Census Maps stack: Svelte Kit + Maplibre GL JS (GitHub-hosted)
- Korostoff "Wealth, shown to scale" open source: github.com/mkorostoff/1-pixel-wealth
- Open Innovations hex map templates: github.com/open-innovations
- Our World in Data Grapher: github.com/owid/owid-grapher (CC-BY embeds)
- Information is Beautiful Awards showcase: informationisbeautifulawards.com
- Sigma Awards: sigmaawards.org

---

## Conclusion: foundational priorities

Three asymmetric opportunities define the project's strategic position.

**First**, the UK has no equivalent of the Federal Reserve's Distributional Financial Accounts — a credible, regionally-aware, regularly-refreshed wealth-distribution dashboard. Building this with London-vs-rest-of-England as a first-class axis is genuinely unprecedented in UK public tooling.

**Second**, the ONS "How do you compare?" calculator is effectively abandoned with pre-pandemic data and no regional dimension, while IFS's "Where do you fit in?" ignores wealth entirely — leaving the most evergreen viral format (the personal comparator) wide open for a wealth-and-income, regionally-aware reboot.

**Third**, the open-source landscape is barren: outside ONS Census Maps and Open Innovations hex maps, there is no canonical GitHub repository for "UK inequality charts you can clone and extend." First-class embeds and a permissive licence convert the project from a tool into a piece of campaigning infrastructure that journalists, educators and campaigners will reuse for years.

The data infrastructure exists and is open: ONS Beta API, Nomis, Stat-Xplore, BoE IADB, Land Registry SPARQL, Companies House API and WID's Stata/R wrappers cover most of what is needed. The methodological backbone is established: Resolution Foundation and the Wealth Tax Commission's WAS+STRL+Pareto adjustment is the canonical UK top-tail correction; the Deaton Review supplies authoritative analytical framing; Advani/Summers/Hughson provide the "millionaires pay less than nurses" core fact. The visualisation playbook is well-documented: personal comparators, scale-shock scrollers, hand-drawn pictograms, postcode-lookup tools and whiteboard explainer Shorts all have proven viral track records.

The strongest message from the research is that **the bottleneck is not data or design technique — it is integration**. A single project that combines Trust for London's methodological transparency, the Fed DFA's regular refresh and top-tail granularity, OECD Compare-Your-Income's design polish, Open Innovations' open-source ethos, and Gary Stevenson's mobile-native voice would occupy a niche that no existing tool fills, and would have demonstrably viral component parts.

## Open questions and known limitations of this research pass

Two things remain materially incomplete after this combined pass. First, neither IPPR nor the Equality Trust maintains a clean public raw-data hub; what they have is strong evidence, modelling write-ups and campaign pages. Building on their work means parsing PDFs and extracting from chart-embedded spreadsheets, not subscribing to a feed. Second, Gary Stevenson's most-used headline numbers are easier to observe across video, podcast and social content than in one single auditable public repository — which is itself diagnostic: the public debate currently lacks a proper claim-checking layer. That gap is a strategic opening for the project itself.

The deeper structural limitation is that top-tail wealth is genuinely hard to measure. Survey data, fiscal data, national-accounts adjustments and rich-list estimates do not line up perfectly; even the best public sources are reconciling imperfect views of the distribution. A serious public product in this area should not hide disagreement between sources. It should surface it, explain it, and let users explore it. The methodology honesty card (recommendation #17) is the simplest expression of that principle, but it should pervade the whole product, not just one component.

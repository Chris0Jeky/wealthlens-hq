# WealthLens UK: combined research synthesis

*A merge of two parallel deep-research passes. Where the two sources agreed, the stronger phrasing is kept. Where they disagreed, the more specific recommendation wins and the alternative is noted. Where one had something the other missed, it has been grafted in.*

## Bottom line up front

A v0.1 of WealthLens UK is achievable in two weeks of part-time solo work by shipping **four high-impact charts** (top 1% wealth share, regional house-price-to-earnings, FTSE 100 CEO-to-worker pay ratio, and UK tax revenue mix) on a static **Astro 5 + Vue 3 islands + Observable Plot** site hosted free on **Cloudflare Pages + R2**, with a **GitHub Actions + Python (`dlt` + `pdfplumber` + `pandera`) pipeline** writing Parquet. A fifth chart — a postcode-driven local house-price-to-earnings lookup — is a stretch goal for week 2 if scope allows; it is the single strongest "personal hook" you can ship cheaply.

This combination matters because the existing UK landscape has a structural gap: there is no quarterly, embeddable, shareable, mobile-first, single-statistic-per-page wealth dashboard equivalent to the US Federal Reserve's Distributional Financial Accounts, ProPublica's tax tool, or Opportunity Insights. Tax Justice UK, Patriotic Millionaires UK and Gary Stevenson currently cite numbers locked inside Oxfam press releases, a 270-page Wealth Tax Commission PDF, paywalled UBS/Credit Suisse reports, and an ONS Wealth and Assets Survey whose official accreditation was withdrawn in June 2025. The minimum viable thing that would genuinely replace those references is a small set of **clean, embeddable, dated, well-sourced static charts at stable URLs with auto-generated 1200×675 social cards**.

Two product differentiators are non-obvious but worth committing to from day one. First, **a definitions layer**: every chart should make explicit whether the unit is households or adults, survey or admin data, taxpayers or estates, and where possible let the user toggle the definition. Most existing UK tools paper over these differences and lose researcher trust as a result. Second, **per-source licence and caveat metadata** stored alongside each dataset, not as a blanket assumption — because OGL, CC-BY, HESA's CC-BY-4.0 and Resolution/IFS reusable downloads each have slightly different attribution requirements.

Defer DuckDB-WASM, a heavier FastAPI backend, and the full postcode→percentile comparator to v0.2 where their cost is justified by a single killer feature.

## 1. The UK data landscape: what's open, what's locked, what's gone

The good news is that nearly every dataset the project needs is published under the **Open Government Licence v3.0**, which permits redistribution in a derivative dashboard with a standard attribution string. The bad news is that the official UK wealth survey is in crisis. In **June 2025 the Office for Statistics Regulation removed accreditation from the ONS Wealth and Assets Survey** (WAS), citing a response-rate collapse from 66% (Round 4) to 41% (Round 8) and known top-tail under-coverage. IFS analysis suggests WAS reports the top 1% wealth share at ~18% when the true figure is closer to **23%**. The latest WAS covers April 2020–March 2022; the next round is not expected until 2026, and the series is now labelled "experimental." Any chart sourced from WAS must carry a prominent caveat and ideally a top-tail correction from WID or Resolution Foundation methodology.

The dataset map below covers the highest-value sources for v0.1–v0.3, distinguishing **fully open and bulk-downloadable** sources from those that are **PDF-locked**, **restricted to the Secure Research Service (SRS)**, or **FOI-only**.

### Primary datasets (first ingestion layer)

| Dataset | Publisher | Format | Frequency | Granularity | Series start | Access | Licence |
|---|---|---|---|---|---|---|---|
| Wealth in Great Britain (WAS aggregates) | ONS | XLSX | Biennial (suspended) | National, region, decile, age | 2006 | Direct XLSX | OGL v3 |
| Households Below Average Income (HBAI) | DWP | ODS + Stat-Xplore JSON API | Annual (March) | UK/region; LA from 2026 | 1994/95 | API key (free) | OGL v3 |
| Effects of Taxes & Benefits on Household Income | ONS | XLSX + Beta API | Annual | UK, decile, household type | 1977 | `api.beta.ons.gov.uk/v1/datasets/tax-benefits-statistics` | OGL v3 |
| HMRC Tax receipts & NICs | HMRC | CSV/ODS | Monthly + annual | UK by tax type | 2006/07 | CSV download | OGL v3 |
| HMRC Survey of Personal Incomes (SPI) tables | HMRC | ODS + PDF commentary | Annual | UK, income band, region | 1990s | ODS; **no API** | OGL v3 |
| HMRC Percentile points 1–99 | HMRC | XLSX | Annual | UK individual income | 1999 | Direct XLSX | OGL v3 |
| Capital Gains Tax statistics | HMRC | ODS + PDF | Annual (Aug) | Gain range, asset type, region | 2007/08 | ODS | OGL v3 |
| Inheritance Tax statistics (12.1–12.9) | HMRC | ODS + PDF | Annual (July) | Estate band, asset, region | 1968 | ODS | OGL v3 |
| Non-domiciled taxpayer stats | HMRC | ODS + PDF | Annual (July) | UK, RBC payers | 2008 | ODS | OGL v3 |
| HMRC Personal Wealth Statistics (Identified Wealth) | HMRC | **PDF (legacy)** | Triennial (on hold) | UK, sex, age, asset | 2001–03 | **Scraping required** | OGL v3 |
| HMRC ATED statistics | HMRC | ODS | Annual | Value band | 2013/14 | ODS | OGL v3 |
| HMRC Annual Stamp Tax Statistics | HMRC | ODS | Annual | Property type, region | 2008 | ODS | OGL v3 |
| HMRC tax-relief statistics | HMRC | ODS | Annual | Relief type | Varies | ODS | OGL v3 |
| UK House Price Index | HMLR/ONS | CSV, JSON, **SPARQL**, RDF | Monthly | LA, region, county, borough | Jan 1995 | `landregistry.data.gov.uk/landregistry/query` | OGL v3 |
| HMLR Price Paid Data | HMLR | CSV (5.3 GB full) | Monthly | Per transaction, postcode | Jan 1995 | `prod.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/pp-complete.csv` | OGL v3 |
| Overseas Companies Owning Property (OCOD) | HMLR | CSV | Monthly | Title-level, jurisdiction | 1999 | Registered API | OGL v3 |
| Housing affordability in England & Wales | ONS | XLSX | Annual | LA, region, MSOA | 1997 | Direct XLSX | OGL v3 |
| Small-area income estimates | ONS | XLSX + interactive | Annual | MSOA | 2004 | Direct XLSX | OGL v3 |
| Private rents (PIPR) | ONS | XLSX, CSV, JSON | Monthly | LA, BRMA | 2015 (linked to 2005) | ONS Beta API | OGL v3 |
| Regional GDP per head (all ITL regions) | ONS | XLSX | Annual (April) | ITL1–3, LA | 1998 | Direct XLSX | OGL v3 |
| ASHE earnings | ONS | XLSX | Annual | Region, occupation, age | 1997 | Direct XLSX | OGL v3 |
| English Housing Survey | DLUHC | XLSX live tables | Annual | Tenure, region, dwelling | 1967 | Direct XLSX (microdata via UKDS) | OGL v3 |
| Family Resources Survey | DWP | XLSX | Annual | Income, tenure, demography | 1992 | Direct XLSX | OGL v3 |
| FCA Financial Lives Survey | FCA | XLSX tracker tables | Biennial → annual updates | Adults, by region, age, vulnerability | 2017 | Direct XLSX | OGL-style with attribution |
| Companies House Public Data API | Companies House | JSON REST | Real-time | Company-level | Live | 600 req/5 min | Crown free reuse |
| Companies House PSC bulk | Companies House | JSONL | Daily | Person+company | Live | Direct ZIP | Crown free reuse |
| Bank of England IADB | BoE | CSV/XLS/JSON | Daily/monthly | National | 1975+ for some | URL-templated API | OGL v3 |
| WID UK series | World Inequality Database | CSV/XLSX + R/Stata package | Annual | UK; top 1/0.1/0.01% | 1895 | `wid.world` + `WIDworld/wid-r-tool` | Open with citation |
| OECD Income Distribution Database | OECD | SDMX (CSV/JSON/XML) | 2–3x/year | UK series | 2012 (Wave 7) | `sdmx.oecd.org` | OECD terms |
| Our World in Data (Grapher) | OWID | CSV + metadata.json | Continuous | Per chart slug | Varies | `ourworldindata.org/grapher/{slug}.csv` | CC-BY |
| Children in Low Income Families (local) | DWP/HMRC | XLSX | Annual | LA, constituency, ward | 2014 | XLSX | OGL v3 |
| Centre for Cities data tool | Centre for Cities | XLSX export | Annual | 63 urban areas | 2014+ | Site export | Free with attribution |
| High Pay Centre CEO pay report | HPC | PDF | Annual (Aug/Sept) | FTSE 100 aggregate | 2009 | PDF (data entry) | Free with attribution |
| Trussell food parcel statistics | Trussell | PDF + ODS | Bi-annual → annual 2026 | UK nations | 2008/09 | PDF | Free with attribution |
| JRF UK Poverty charts | JRF | XLSX | Annual | UK, region, demography | 2018+ | XLSX | Free with attribution |
| Resolution Foundation chart downloads | RF | XLSX/CSV | Per publication | Various | Varies | Direct from RF pages | Free with attribution |
| IFS TaxLab data hub | IFS | XLSX + interactive | Continuous | UK tax revenues, rates | Varies | Direct from TaxLab | Free with attribution |
| Wealth Tax Commission code bundle | WTC / UK Data Service ReShare | R code + data | One-off (2020) | UK wealth distribution model | n/a | UKDS ReShare | Open with citation |
| HESA open data | HESA | CSV/XLSX | Annual | Provider, student | Varies | Direct download | CC BY 4.0 |
| UCAS end-of-cycle / equality data | UCAS | CSV + dashboards | Annual | Applicants, school type, FSM | Varies | Direct download | Free with attribution |

### Three categories of access difficulty

**PDF-locked data** — meaningful scraping work, deferrable. HMRC Personal Wealth Statistics tables 13.1–13.8 are almost entirely PDF for historical years (2001–03 through 2014–16). Older HMRC IHT tables and HMRC SPI geography tables (3.12–3.15a) for pre-2018 years are PDF-only. The Bank of England's NMG Household Survey publishes only PDF chart packs — no machine-readable household data is released. The High Pay Centre's annual CEO pay report is PDF-only and requires manual data entry. **The recommended tool in 2026 is `pdfplumber`** (9.5k★, active); use the `camelot-dev/camelot` fork as a fallback after the original repo was archived in January 2025.

**SRS / UKDS-restricted data** — out of scope for an open dashboard unless you partner with an accredited researcher. This includes WAS microdata with linked HMRC admin data, the HMRC Datalab (full SPI, CGT, IHT, non-dom individual data), the ONS Longitudinal Study, the full VOA record-level dataset, HBAI raw underlying records, and EHS / FRS microdata. The dashboard must rely on published aggregates only; flag SRS-derived figures (e.g. Advani–Summers effective tax rates) as citations, not as series you recompute.

**High-value FOI targets** for a v0.3 "we asked HMRC for this" feature: top 0.01% effective tax rates by income decile; non-dom counts and tax paid by gross income band; trust ownership of UK property at LA level; ATED dwellings by region; SDLT by buyer category (corporate / foreign individual / trust); HMRC High Net Worth Unit caseload aggregates; **and subnational income percentiles by region and London borough** (there is at least one prior WhatDoTheyKnow precedent where HMRC released this in spreadsheet form, which makes it a high-probability FOI). HMRC's tax-confidentiality exemption (s.18 CRCA 2005) means requests must be framed for aggregated cells with minimum thresholds (typically n≥10) — drafting a few of these FOIs in parallel with the v0.1 build is essentially free and the responses arrive in 20 working days.

### Critical caveats to bake into the dashboard UI

WAS lost accreditation (June 2025); HBAI back-series being revised in summer 2026; non-dom regime abolished from April 2025 (historic series ends, new "long-term resident" regime starts 2026/27); WAS top-tail under-coverage ~5 percentage points on the top-1% share; LCF historic methodology errors (2019/20). A standing **"data status" badge** on every chart — last updated, source, known issues — is non-negotiable for researcher credibility.

### Licensing in plain English

OGL v3 is the default for ONS, HMRC, HMLR, DWP, Bank of England and most GOV.UK statistical tables. HESA is explicitly CC BY 4.0. WID is open with citation but check page-specific Creative Commons terms. Resolution Foundation, IFS TaxLab, IPPR, Equality Trust and High Pay Centre publish freely but are not standardised open-data products — treat them as "free with attribution" and link to the originating page. UCAS sits in the same category. The implication: **store licence metadata per dataset family**, not as a blanket assumption.

## 2. What campaigners actually cite, and the verification gap

A careful pass over Tax Justice UK, Patriotic Millionaires UK, Oxfam UK joint releases, Equality Trust, Fairness Foundation, and Gary Stevenson's public content surfaces a remarkably tight list of recurring statistics. The ten most-cited, ranked by frequency across press releases, parliamentary briefings and viral content between 2023 and 2026:

1. **"2% wealth tax on assets over £10m raises ~£24bn/year, affects ~20,000 people."** Source: Arun Advani & Andy Summers, **Wealth Tax Commission, December 2020**, plus Advani's interactive simulator at `arunadvani.com/taxreform.html`. Accessibility: the figure lives inside a 270-page PDF and a non-exportable simulator; the underlying model code is in the UK Data Service ReShare bundle. **Replacement: a wealth-tax revenue simulator with rate, threshold, exemption and behavioural-response sliders.**
2. **"Top 1% own more wealth than the bottom 70%" / "Four richest Britons own more than 20 million."** Source: Oxfam UK analysis (Jan 2023) of **Credit Suisse Global Wealth Databook 2022** (now UBS, paywalled) plus the live Forbes list. Replacement: a maintained top-share series, live-refreshed.
3. **"UK billionaire wealth +£11bn last year; 171 billionaires hold more than 40 million people; +12× over 30 years."** Source: joint Oxfam/PMUK/TJUK March 2025 analysis using Forbes snapshots and Sunday Times Rich List. Replacement: an annual UK billionaire-wealth tracker.
4. **"50 richest families own more wealth than the bottom half of the country."** Source: Equality Trust / Tax Justice UK, stitched from Sunday Times Rich List against WAS bottom-50 totals. This is the single most scroll-stopping campaign chart but also the most methodologically fragile, because it combines billionaire/rich-list top-end data with survey-based population-scale wealth estimates — two worlds that do not naturally live in the same table. A chart that does the stitch transparently (with both sources, the assumption set, and a one-paragraph "what this comparison does and does not mean") would be unusually trustworthy compared to existing renderings.
5. **"Top 0.1% wealth share doubled 1984–2013 to 9%."** Source: WID UK long-run estate-tax series (Alvaredo, Atkinson, Morelli). Accessibility: WID is open but navigationally hostile for non-economists.
6. **"Top 0.1% pay 21% effective tax, bottom decile pays 44%."** Source: Advani, Summers & Hughson at **CenTax / Warwick / LSE** (Oxford Review of Economic Policy 2023, IFS Deaton Review chapter). Tax Justice UK's repeated framing of "a person with £10m total income paying ~21%" comes from the same paper family. Accessibility: locked in academic PDFs. **Replacement: an effective-tax-rate-by-percentile chart citing and reproducing the academic numbers.** This is the single highest-value image WealthLens could host.
7. **"Wealth-to-national-income ratio risen from ~3× to ~7×."** Source: ONS National Balance Sheet ÷ GDP; cross-referenced with WID. Requires combining national accounts with WAS — no single accessible series exists. This is Gary Stevenson's macroeconomic core.
8. **"Median household wealth £293,700; top decile owns 43–45%; bottom 50% owns 9%; wealth Gini 0.59."** Source: ONS WAS — **now suspended**. Critical caveat needed.
9. **"Top 5,000 people receive more than half of all UK capital gains."** Source: WID UK capital-gains piece; HMRC CGT statistics support a similar concentration story but at coarser granularity. Underused visually relative to its rhetorical strength.
10. **"Trussell food parcels: 2.89m in 2024/25 (1.02m for children); ~50× the 2010/11 figure."** Source: Trussell statistics. Best-served of the ten for accessibility, but historical comparison series is scattered across press releases.

Honourable mentions to include in copy: "78% of the British public, including 77% of Conservative voters, support a 2% wealth tax; 80% of UK millionaires agree" (YouGov March 2025; Survation for PMUK June 2025); and "disposable incomes £10,000–£11,000/year below pre-2010 trend per person" (Centre for Cities Cities Outlook 2024; Resolution Foundation Living Standards Outlook).

**Claims to treat more cautiously.** "70% of land is owned by under 1% of the population" — politically useful and genuinely interesting, but the primary-data trail is fragmented across titles, companies, trusts and historical estates, and the headline figure depends on definitional choices about what counts as "owned" and "the 1%." Similarly some very long-range inheritance-transfer projections depend on modelled futures rather than a single official publication. These are good phase-two explainers, not launch bets.

A pattern emerges. **The replacement that has the highest leverage is not a new statistic but a stable, embeddable, dated chart at a permalink that campaigners can hotlink in tweets and embed in blog posts in place of static infographics or paywalled report links.** Gary Stevenson's most-viewed videos use third-party FT or ONS charts overlaid with verbal commentary — his audience does not need new data, it needs a clean primary source he can point to. Tax Justice UK's "Talking Tax" reports use static PNGs that go stale within months. The lowest-effort thing that genuinely replaces this ad-hoc citation chain is a small set of well-sourced charts with a `wealthlens.uk/chart/{slug}` URL pattern, auto-generated OG images, and an explicit "data as of {date}" stamp.

The second-highest leverage move is the **definitions layer**. Most existing UK tools quietly conflate units — households vs adults, taxpayers vs estates, survey aggregates vs distributional national accounts — and lose researcher trust when journalists notice. WealthLens should make the definitional choice explicit on every chart, and where possible let the user toggle (e.g. "show this top-share series using ONS WAS / using WID DINA / using Resolution Foundation top-tail-corrected"). This single design decision is what would make the product credible to IFS researchers and embeddable by FT journalists, not just shareable by campaigners.

## 3. The competitive landscape and the gaps that matter

The existing UK interactive inequality tool landscape is **thin, fragmented, and architecturally stuck in 2015**. Of the fifteen tools surveyed:

- **IFS Deaton Review** is the deepest research resource but has no genuine interactive explorer, no personal calculator, no iframe embeds, and many flagship charts are 3+ years old as the Review wound down.
- **IFS TaxLab** is excellent for tax mechanics — interactive and spreadsheet-backed — but is a tax-policy explainer/data hub rather than a shareable inequality visual platform connecting taxes to housing, assets and lived experience.
- **Resolution Foundation's Intergenerational Centre dashboard** and **Housing Outlook** are analyst-facing and dense; charts are not individually shareable in the embed-first sense, though RF does make per-chart data downloadable, which is better than most. Their framing is topic- or generation-specific, not a reusable public data platform.
- **ONS interactive visualisations** are released alongside bulletins and frozen; obscure `/visualisations/dvc####/` URL paths; no embed support; no central catalogue. Some prominent ONS inequality/wealth-style tools are visibly stale (2021 mapping microsites; Wealth Calculator drawing on 2019–20 sources). The "Compare your income" tool that everyone assumes is ONS is actually **OECD's `compareyourincome.org`** using UK data — there is no ONS-native percentile calculator.
- **ONS small-area income interactives and housing-affordability pages** are the closest the UK has to good public local-data tools, but they live on individual bulletin pages with no embed or shared-URL design.
- **Our World in Data** has best-in-class embed support and a UK long-run inequality page but UK is just one country among 200; no UK-specific narrative.
- **WID** is uniquely valuable for top shares and long-run history, but conceptually heavy — most users will not naturally understand adult-equal-split income, pretax/posttax national income, or top-tail reconciliation methods without substantial explanation.
- **HMRC publishes zero public-facing interactive content.** This is the single largest institutional gap.
- **The Equality Trust** runs static PNGs sourced from WAS data that is increasingly stale; its public evidence base is mostly static pages and reports, not machine-readable products.
- **JRF's UK Poverty dashboard and RAPID tool** (with Policy in Practice) are the most actively developed interactive products in the UK third sector but are poverty-focused, not wealth-focused, and RAPID is currently London-only.
- **Tax Justice UK has no interactive tooling at all** — it is a campaigning site of petitions and PDFs.
- **HM Land Registry** is data-rich and developer-friendly (CSV, RDF, SPARQL, account-and-licence APIs) but the public-facing tools are property-data tools, not inequality-first explainers.
- **mySociety's Local Intelligence Hub** is excellent at constituency-level data but climate-focused and partly member-gated. Their **MapIt** postcode-to-geography service is a strong open-source precedent for the v0.2 geography layer.
- **The Hills Review "Anatomy of Economic Inequality in the UK"** (LSE/CASE 2010), the canonical UK inequality reference, has never had a live web version.
- **Inequality Briefing** (inequalitybriefing.org) was the pioneer of shareable single-statistic UK inequality infographics; it has been **dormant since 2015**.
- **The Office of Tax Simplification was abolished in 2022** and produced no interactive content during its existence.

The US comparison is brutal. **The Federal Reserve's Distributional Financial Accounts** publishes a quarterly, interactive UK-equivalent of WAS with five percentile groups and breakdowns by income, age, generation, education and race — released 10–11 weeks after each quarter, with CSV downloads. **ProPublica's "Secret IRS Files"** uses leaked individual returns to compute true tax rates for named billionaires; their **Nonprofit Explorer API** is a good architectural model for any structured-records explorer WealthLens might build. **Opportunity Insights' Opportunity Atlas** maps intergenerational mobility at US Census-tract granularity (~4,250 people per cell). **The Economic Policy Institute's State of Working America Data Library** offers per-chart embed codes, version stamps, and an interactive state-comparator. **Inequality.org** runs a real-time top-12 billionaire wealth tracker. **USAFacts** packages a single civic state-of-the-nation dashboard standardising dozens of government sources into plain-language charts.

The UK has nothing equivalent to any of these. The gap that is most uniquely addressable by WealthLens — because it does not require a leak, an academic partnership, or admin-data access — is the **quarterly-or-better-refreshed, embeddable, shareable wealth dashboard with a personal-position component and an explicit definitions layer**. Build something that occupies the white space between OWID (global), IFS (research-paper-static), JRF (poverty-focused) and the Equality Trust (campaigning PNG).

## 4. The viral-chart aesthetic that actually performs

The single most consistent winner on X/Twitter for economic content in 2024–2026 is the **John Burn-Murdoch / FT template**: a single annotated line chart on cream or pale background, with a declarative headline naming the finding (not the variable), in-chart annotations replacing the legend, one accent colour for the line of interest with all other series muted to grey, and methodological detail in a smaller subhead. JBM's most-shared 2024 chart — gender ideological divergence — exceeded 27 million views with exactly this structure. The same template scales down: small multiples beat one spaghetti chart on mobile, with "the UK is the only country where X" framing.

The technical specs that follow from this:

- **Primary share asset 1200×675 px (16:9 PNG)** matches both Twitter card and Open Graph; **1080×1350 portrait** for Instagram and LinkedIn feed; **1080×1920** for stories with content kept inside a 1080×1400 safe zone. Avoid 1:1 square unless targeting LinkedIn specifically.
- **Headline at ~48pt is the finding in active voice; subhead at ~24pt is the methodological hedge.**
- **Cream (#FAF7F2) or pale pink (#FFF1E5) backgrounds** out-perform pure white in-feed because the background colour becomes a brand signal.
- **One accent colour for the data series of interest; everything else muted to `#888888`–`#CCCCCC`.** This is the single most powerful attention-direction technique.
- **PNG, not JPEG, for charts with text overlays;** keep files under 1 MB to avoid Twitter recompression artefacts on type.
- **Datawrapper-aesthetic minimal charts beat heavy bespoke D3 on social media** because they remain legible at thumbnail size. The right pattern is two assets per chart — a clean static PNG that drives the click, and an interactive on-site companion (iframe or full page) that earns the dwell time.
- **Mobile-first by force, not choice.** Most users will see WealthLens inside a social-app browser on a narrow screen. ONS's own visualisation manual warns that chart annotations may not display on mobile and should never carry essential information alone — keep the headline and the data inside the chart frame, not as floating overlays.

The effective-tax-rate chart is the highest-leverage single image WealthLens could host but cannot be recomputed without HMRC Datalab access. The right answer is to **license, reproduce and credit the Advani-Summers / CenTax chart** with the original authors' permission, packaged as an interactive component with a "this chart is from {paper} — see source for methodology" caveat. CenTax (`centax.org.uk`) is the live successor body and is likely receptive to such a partnership.

The **personal comparator** (postcode/income → percentile) is feasible for v0.2 using **HMRC's "Percentile points 1 to 99 for total income before and after tax"** (free annual XLSX) for income, **DWP HBAI via Stat-Xplore JSON API** for the full distribution including non-taxpayers, and **ONS ASHE table 1.7a** for regional benchmarks. Postcode → ITL1 region uses a free ONS lookup. Wealth percentile lookup is harder because **ONS suspended WAS in June 2025**; the v0.2 wealth component should use the last published WAS regional medians with an explicit "data frozen at April 2022" disclaimer until ONS resumes the series. Sub-postcode wealth granularity is genuinely unavailable in open data and would require expensive commercial Mosaic/Acorn segmentation — out of scope.

A lighter but immediately useful precursor for v0.1 is a **postcode-driven local house-price-to-earnings lookup** using ONS housing-affordability ratios (which are published at LA level) and ASHE workplace-based median earnings. This gives users an instant "your area's affordability ratio is X; the England-and-Wales median is Y; here are the ten most and least affordable LAs" experience without needing the full percentile-comparator stack. Ship it as the fifth chart if week-2 scope allows.

## 5. Recommended technical stack

The recommended stack is **Astro 5 + Vue 3 islands + Observable Plot + DuckDB-WASM (v0.2 only) on Cloudflare Pages + R2, with a GitHub Actions + Python pipeline modelled on Our World in Data's five-stage ETL workflow**.

### Mental model: OWID's five-stage ETL

The right mental model for the pipeline is OWID's published five-stage workflow: **snapshot → format → harmonise → import → publish**. Raw upstream files are snapshotted into immutable object storage (you never re-download the same ONS XLSX twice); the format stage parses each into a typed intermediate table; the harmonise stage applies unit conversions, deflators and definition mappings; the import stage joins into chart-ready datasets; and the publish stage emits the public artefacts (JSON, CSV, PNG, OG image, methodology metadata). This shape is much more important than the specific tools chosen at each stage — it is what lets you re-run any historical chart from frozen sources and prove how each number was derived, which is the difference between a hobby dashboard and a researcher-trusted product.

### Frontend

The choice sits between **Observable Framework** (purpose-built for this use case, ISC-licensed, ships D3/Plot/DuckDB-WASM out of the box, written by D3's author Mike Bostock) and **Astro 5 with Vue islands**. Observable Framework is the more natively-fitted answer; Astro is the better answer for someone who already knows Vue and wants to keep idiomatic component code. Astro's islands architecture is genuinely better than Nuxt's `routeRules`-driven partial hydration for a content-led site with interactive charts on a few pages, and `@astrojs/vue` lets every interactive component stay in Vue. A reasonable third option for a developer who wants to minimise new tooling is **Vue 3 + Vite with `vite-ssg` for prerender**; this stays closer to the existing skillset but loses Astro's content-collection ergonomics. The Astro+Vue path is the recommendation.

Use **Observable Plot** for the majority of charts (declarative, responsive, small bundle, D3 under the hood) and reach for raw D3 only for bespoke Lorenz curves or Gini ribbons. **Apache ECharts via `vue-echarts`** is the right choice for any dashboard-style aggregated view and has good ARIA defaults.

### Data pipeline

Resist orchestrators. A solo dev with ≤10 data sources refreshing weekly does not need Dagster (which removed free credits in May 2026), Prefect or Airflow. The pipeline is `GitHub Actions cron → Python scripts → Parquet → commit/upload`. Use **`dlt`** (Apache-2.0, code-first, PyArrow-backed) for the extract layer; **`pandera`** (MIT) for DataFrame validation; **`pydantic` v2** at the API boundary for record-level validation; **`pdfplumber`** for HMRC PDF tables with `camelot-dev/camelot` as fallback. GitHub Actions' 2,000 free minutes per month for public repos is far more than weekly pulls require.

Use **DuckDB or Polars** for in-process transformations rather than Postgres-for-everything. Both read Parquet natively, both run in CI without infrastructure, and DuckDB in particular is the same engine you may later promote to the browser via WASM, which means the same SQL works locally, in CI, and in v0.2 client-side queries.

Write outputs as **Zstd-compressed Parquet** — a 10 MB JSON dataset compresses to ~1–2 MB. Commit small Parquets directly to the Git repo for free history; push raw snapshots to **Cloudflare R2** if total size exceeds ~100 MB. Skip DVC and lakeFS for v0.1.

### Storage and in-browser query

For v0.1, **plain JSON (or pre-aggregated CSV) per chart** is faster to render and easier to debug than DuckDB-WASM. **DuckDB-WASM v1.5.2 (March 2026) is production-ready** — used by Observable Framework, Evidence.dev, Rill, Mosaic and many newsrooms — but its 4–6 MB bundle and ~2 GB browser memory ceiling are only worth paying when you need ad-hoc SQL. The right pattern is to lazy-load DuckDB-WASM only on the personal-comparator page in v0.2, using a `client:visible` Astro island, while serving plain JSON for the four headline charts. This gives Lighthouse 100 on the homepage with the killer feature intact.

A small **PostgreSQL or SQLite layer behind FastAPI** is reasonable for v0.2 metadata, search, FOI-tracking and any user-submitted comparator results — but only if a feature genuinely requires it. Do not introduce it for v0.1.

### Hosting

The current free-tier landscape strongly favours Cloudflare. **Cloudflare Pages free** offers **unlimited bandwidth**, 500 builds per month (≈16/day), 20-minute build limit; **Cloudflare R2 free** is 10 GB storage with **zero egress fees ever**, 1M Class A and 10M Class B operations per month; **Cloudflare Workers free** is 100,000 requests/day with 10 ms CPU per request — plenty for an oEmbed endpoint or runtime OG image generation. Avoid Vercel Hobby (commercial-use prohibition is a real account-suspension risk for any project soliciting donations) and Netlify (credit-based since September 2025, revised down again in April 2026, giving ~15 GB bandwidth before the site pauses — too tight for a Hacker News spike). Fly.io's free tier is gone (2-hour trial only). When self-hosting later, **Hetzner CX22 at €3.79/month** (20 TB included bandwidth, 2 vCPU, 4 GB RAM) is unbeatable value.

### Embedding and social cards

Use **`@newswire/frames`** (Rich Murphy, ISC, ~1 KB gzipped, Pym-compatible) for responsive iframe embeds — pym.js still works but is effectively superseded; NPR's `nprapps/sidechain` is a fine alternative. Implement `/oembed?url=…&format=json` on a Cloudflare Worker for automatic CMS embed discovery. For social cards, **pre-generate PNGs at build time** with `vercel/satori` plus `@resvg/resvg-js` in a Node CI task — zero runtime cost, zero failure surface, CDN-cached forever. Move to runtime generation on Cloudflare Workers only if user-generated chart URLs need it (the v0.2 comparator).

### Geography service

For the v0.2 postcode-to-percentile feature, the cleanest open-source precedent is **mySociety's MapIt**. The lightweight option is to host a slim FastAPI service that wraps a static ONS postcode-to-ITL1/LA lookup table; MapIt is a more capable reference if the geography needs grow (constituency, ward, MSOA). Standardise on official ONS geography codes throughout the pipeline.

### Accessibility

Follow the **gov.uk Analysis Function "Accessible charts" checklist** and the **BBC GEL Infographics guidance**. Every chart should be SVG (not Canvas) with `role="img"`, `<title>` and `<desc>`; wrapped in a `<figure>` with `<figcaption>`; and paired with a hidden but accessible `<table>` of the underlying data. Use the Amy Cesal alt-text formula: *"{Chart type} of {data type} where {reason for chart}."* Pass WCAG 2.2 AA (text contrast 4.5:1, non-text 3:1) — this also improves screenshot legibility. **Apache ECharts has good ARIA defaults** and is fully free. Highcharts has best-in-class accessibility and sonification but requires applying for a non-profit licence. Skip sonification for v0.1; it is a v0.3 feature.

### What WealthLens is not

It is not Our World in Data Grapher — do not copy their MySQL-backed admin UI or custom SSG; their stack reflects a much bigger team (but their ETL workflow and chart-data-as-public-artefact contract are worth copying directly). It is not mySociety's 20-year-old Rails/Perl monolith — though their Docker Compose dev-environment ergonomics are a model worth copying. It is not 538 (defunct), Quartz Chartbuilder (unmaintained since 2019), or USAFacts (Drupal-backed CMS). The closest spiritual model is **Evidence.dev** (SvelteKit + DuckDB-WASM + Markdown/SQL static export) or **Observable Framework** itself.

### The embed-first chart contract

Every chart should expose, by convention, the same six artefacts at predictable URLs:

- the interactive page at `/chart/{slug}`
- the 1200×675 PNG at `/chart/{slug}/share.png`
- the responsive embed at `/chart/{slug}/embed`
- the raw data at `/chart/{slug}/data.csv` and `/chart/{slug}/data.json`
- the metadata at `/chart/{slug}/meta.json` (source, licence, last updated, methodology, version hash)
- an oEmbed discovery endpoint at `/oembed?url=…`

This contract is the public-facing surface; any chart that ships without all six is not finished.

## 6. The chart shortlist, ranked

Evaluating each candidate on data accessibility, pipeline complexity, shareability, campaigner alignment, and whether someone has already done it well, the v0.1 shortlist becomes clear. The table below merges both research passes; "v?" is the recommended release window.

| # | Chart | Pipeline | Quality | Existing UK version | Shareability | Campaigner | v? |
|---|---|---|---|---|---|---|---|
| 1 | Top 1% wealth share over time (with definition toggle: ONS WAS / WID DINA / RF corrected) | EASY (OWID CSV + WID) | High | Yes (RF, OWID) | 5 | Extreme | **v0.1** |
| 3 | House price to earnings ratio by region | EASY (ONS XLSX) | Very high | Yes (ONS, dull) | 5 | High | **v0.1** |
| 7 | CEO-to-median-worker pay ratio (FTSE 100) | EASY (HPC PDF) | High | Yes (HPC static) | 5 | High | **v0.1** |
| 10 | Tax revenue mix over time (work vs wealth, with definition toggle: narrow / broad / campaign) | EASY (HMRC CSV) | Very high | Partial (OBR) | 4 | Extreme | **v0.1** |
| 3b | **Postcode-driven local affordability lookup** (ONS LA-level ratios + ASHE) | EASY-MED | High | Partial (ONS) | 5 (personal hook) | High | **v0.1 stretch** |
| 4 | Real wage stagnation + counterfactual | MEDIUM | High | Yes (RF owns) | 5 | Extreme | v0.2 |
| 9 | Regional GDP per head | EASY (ONS) | High | Yes (CfC, ONS) | 4 | Medium | v0.2 |
| 12 | Productivity-pay gap (scissor chart) | MEDIUM | Contested | Partial | 4 | High | v0.2 |
| 11 | Child poverty by region | MEDIUM (Stat-Xplore API) | High | Yes (ECP) | 5 | Medium | v0.2 |
| 2 | Wealth-to-income ratio β | EASY-MED | High (WID) | No clean UK | 3 | Medium | v0.2 |
| 13 | **Capital gains concentration** (top 5,000 receive >50% of gains) | MEDIUM (HMRC CGT) | High (WID + HMRC) | No | 4 | High | v0.2 |
| 14 | **Inheritance tax: few estates, rising receipts** | EASY (HMRC IHT) | High | Partial (IFS) | 4 | Medium | v0.2 |
| 15 | **Share of adults with almost no financial buffer** (FCA Financial Lives) | MEDIUM (FCA XLSX) | High | No | 5 | Medium | v0.2 |
| 16 | **Ownership by age and tenure** (owner-occupied / private rent / social rent by cohort) | MEDIUM (EHS) | High | Yes (RF) | 4 | Medium | v0.2 |
| 8 | Generational wealth gap | HARD (WAS microdata) | Medium (WAS issues) | Yes (RF owns) | 5 | Medium | v0.3 |
| 6 | Inheritance by income decile | HARD (WAS + SRS) | Medium | Yes (RF/IFS) | 4 | Medium | v0.3 |
| 5 | Effective tax rate by wealth percentile | **CITE, do not rebuild** | High (academic) | Yes (Advani-Summers) | 5 | Extreme | v0.3 |
| 17 | **50 richest families vs bottom half** | HARD (rich list + WAS stitch) | Fragile but explicable | Yes (ET static) | 5 (top scroll-stopper) | Extreme | v0.3 |
| 18 | UK billionaire wealth tracker (Forbes-driven, weekly refresh) | MEDIUM | High | No | 4 | High | v0.3 |
| 19 | Wealth tax revenue simulator (rate / threshold / behavioural response) | HARD (WTC model) | High | Buried (Advani simulator) | 4 | Extreme | v0.3 |

The four v0.1 charts together form a complete elevator pitch: **the top 1% own X% of UK wealth, CEOs earn 122× the median worker, houses cost 7.6× median earnings, and the tax system barely touches wealth at all**. Every dataset is bulk-downloadable, every series updates at least annually, every chart is high on both shareability and campaigner alignment. The fifth chart — local affordability lookup — is the strongest personal hook you can ship cheaply, and is the recommended stretch goal for week 2.

Real wage stagnation (chart 4) is deliberately deferred despite its viral potential because Resolution Foundation owns the "£11,000 lost wages gap" narrative and adding marginal value without their microdata is hard — better to revisit it for v0.2 once an audience exists.

The **50 richest families** chart (17) deserves a specific note. It is the single most scroll-stopping campaign claim in UK inequality discourse, but its methodological fragility — stitching a billionaire/rich-list top against survey-based bottom-50 estimates — means an honest version is harder than the existing campaign renderings imply. Ship it in v0.3 with the WTC code-bundle methodology displayed prominently, not in v0.1 where a flawed first attempt would damage credibility.

The **effective-tax-rate chart** (5) is the highest-leverage single image WealthLens could host but cannot be recomputed without HMRC Datalab access. The right answer is to **license, reproduce and credit the Advani-Summers / CenTax chart** with the original authors' permission, packaged as an interactive component with a "this chart is from {paper} — see source for methodology" caveat. CenTax (`centax.org.uk`) is the live successor body and is likely receptive to such a partnership.

## 7. Content strategy and site structure

The three audiences — casual sharers, campaigners and researchers — pull in compatible directions if the site is layered correctly. The recommended structure:

- **Homepage** is a single grid of the four headline charts, each a 1200×675 PNG hero with the headline-as-finding, a one-sentence interpretation underneath, and a "see the data" link to the chart page. The homepage exists to be screenshot-shared on X.
- **Per-chart pages** at `wealthlens.uk/chart/{slug}` carry the interactive version, the static PNG (downloadable), the source citation, methodology notes, an embeddable iframe snippet, the underlying data as both CSV and JSON, a `last updated` badge, known caveats, "how to cite" boilerplate, and **a definitions box that names the unit (households, adults, taxpayers, estates, gains, modelled) and offers a toggle where alternative definitions exist**. This URL is what campaigners link to and journalists embed.
- **Topic index** pages at `/topic/{wealth,tax,housing,income,methods}` group charts thematically; this is the navigation researchers and journalists use when they arrive without a specific chart in mind.
- **Methodology pages** at `/methodology/{topic}` explain top-tail under-coverage, WAS accreditation withdrawal, deflator choices, effective-rate definitions, and the survey/admin-data distinction. Researchers' trust depends on this being honest about limitations.
- **About / sources** at `/sources` is the dataset map of section 1, with direct download URLs, OGL/CC-BY/HESA-specific attribution strings, and per-dataset licence metadata.
- **FOI tracker** at `/foi` (v0.2+) lists outstanding and fulfilled FOI requests, their references, and any unique data released — this is how WealthLens earns "we asked HMRC for this" credibility.
- **GitHub link** in the footer to a public repo with full pipeline code, raw data snapshots versioned by date, and an issues tracker so researchers can challenge methodology in the open.

A **"story" or "explainer" mode is deferred to v0.2**. It is tempting to ship a scrolly first but the comparative advantage in v0.1 is having the cleanest single-chart pages on the UK internet, not the most elaborate longform. Add a scrolly only when there is a specific narrative — for example, "How Britain became the world's most wealth-unequal G7 economy" — that synthesises multiple WealthLens charts.

**Tone is neutral data presentation with sourced campaigner quotes.** "Data-led" not "advocacy-led" in the dashboard's own voice. Use phrasing like "The latest HMRC data shows…" rather than "Britain is rigged for the rich." This decision matters because it keeps the door open for FT, Reuters and BBC journalists to embed without quoting an obviously aligned source — and it does not stop campaigners from doing the editorialising themselves around the embed. **The chart titles are the findings**, in JBM style (e.g. "House prices are 8 times average earnings — double the 1997 ratio"), but the surrounding copy is descriptive. This is the same neutral-research-aligned-with-campaigner-utility positioning that the IFS occupies; it has been validated for two decades as the highest-trust UK economic-research voice.

**Naming and positioning.** "WealthLens UK" is fine but slightly clinical; consider whether a sharper second-line strap ("UK wealth and inequality, charted") helps SEO and shareability. Domain: `wealthlens.uk` (.uk for credibility; cheaper than .co.uk).

## 8. Prioritised build plan

**Week 1 (v0.1 part 1) — infrastructure and two charts.**

- Register `wealthlens.uk` and lock in the canonical URL pattern (painful to change later).
- Set up the Astro 5 + Vue 3 islands + Observable Plot scaffold.
- Configure Cloudflare Pages deploy from GitHub and a Cloudflare R2 bucket for raw data snapshots.
- Build the GitHub Actions cron skeleton with one Python ETL job using the OWID five-stage model: snapshot → format (`dlt` extract, `pdfplumber` for HMRC PDFs) → harmonise (`pandera` validation) → import (Polars/DuckDB transforms) → publish (Parquet + chart-ready JSON/CSV + meta.json).
- Write the OG-image build task with `satori` + `resvg-js`.
- Ship the **Top 1% wealth share** and **House-price-to-earnings by region** charts end-to-end, including chart pages, social cards, embed iframes, downloadable CSV/JSON, methodology notes, source citations, and the definitions box.
- Set up `@newswire/frames` so the iframes are responsive.

**Week 2 (v0.1 part 2) — two more charts and polish.**

- Ship the **FTSE 100 CEO pay ratio** and **UK tax revenue mix** charts using the same template.
- Add the homepage grid.
- Write the methodology pages for top-tail under-coverage and WAS accreditation withdrawal.
- Run an a11y pass: keyboard navigation, `role="img"`, alt text, hidden data tables, WCAG 2.2 AA contrast check.
- Set up a public GitHub repository with the pipeline code, an MIT or Apache-2.0 licence on the code, and a CC-BY 4.0 licence on the chart outputs (compatible with all upstream OGL v3 and HESA CC-BY sources).
- **Stretch goal:** the postcode-driven local affordability lookup. If shipped, this is the v0.1 hero chart for social sharing because it is the only one that personalises.
- File **2–3 FOI requests in parallel** during week 2 — HMRC top 0.01% effective rates, ATED by region, non-dom counts by income band, and subnational HMRC income percentiles by London borough — so responses arrive in time for v0.2.
- **Soft-launch by emailing the four (or five) chart URLs to one person at Tax Justice UK, one at Resolution Foundation, and one freelance journalist (Burn-Murdoch is the obvious test-case)** with an explicit "feel free to embed" line. The minimum viable definition of v0.1 success is that **at least one of those three embeds or links to a WealthLens chart within four weeks of launch**.

**v0.2 (weeks 3–6) — depth.**

- Add the **real wage stagnation chart** (chart 4) with its counterfactual trendline and OECD comparator.
- Add the **productivity-pay scissor** (chart 12), the **regional GDP per head** map (chart 9), the **child poverty by region** map (chart 11), the **capital gains concentration** chart (13), the **IHT estates / receipts** chart (14), and the **financial buffer** chart from FCA Financial Lives (15).
- Add the **personal comparator**: postcode → ITL1 region → income percentile (national + regional) using HMRC percentile-points data and ASHE, with a "compare to median FTSE 100 CEO / top 1% threshold / median worker" toggle. This is where DuckDB-WASM finally earns its bundle weight — load it lazily on `/compare`. Geography lookup can use a static ONS postcode-to-LA table for v0.2 and graduate to MapIt if constituency/ward granularity becomes worthwhile.
- Add an Open Graph card per chart with the user's percentile baked in (using runtime Workers OG generation) so a personal-comparator result can be shared on X with the user's percentile in the preview image.
- Add the FOI tracker page so the responses obtained during v0.1 become visible.
- Begin **light scrollytelling** on a single multi-chart page tying together the four headline findings.

**v0.3 (months 2–4) — depth and novelty.**

- Add the **Advani-Summers effective-tax-rate-by-percentile chart** with permission and full citation (chart 5). Open the partnership conversation with CenTax in week 4 of v0.2 to leave time.
- Add the **UK billionaire wealth tracker** (Forbes-driven, refreshed weekly) and the **wealth tax revenue simulator** with rate, threshold, exemption and behavioural-response sliders (the explicit replacement for the buried Wealth Tax Commission interactive, built directly on the WTC code bundle from UKDS ReShare).
- Add the **50 richest families vs bottom half** chart (17) — only after the WTC methodology is properly displayed and the stitch is honest. This is the rhetorically most powerful chart in the entire roadmap; do it right or not at all.
- Add the **β = W/Y wealth-to-income ratio** chart (chart 2), the **generational wealth gap** (chart 8) and **inheritance by income decile** (chart 6) — the latter two require careful WAS-data handling and ideally an academic partnership with CenTax, IFS or Resolution Foundation for top-tail correction.
- Use the FOI responses obtained during v0.1 to publish previously-unpublished cuts of HMRC data with explicit FOI-reference attribution.
- Add **chart sonification** (Highcharts non-profit licence) and a full **screen-reader audit**.
- If self-hosting becomes necessary (e.g. for a heavier comparator backend or a richer FOI tracker with user submissions), migrate to a single Hetzner CX22 running Docker Compose with Caddy reverse-proxy in front of the Astro static build, the FastAPI personal-comparator service, and a Postgres or DuckDB persistence layer.

## 9. Open questions and limitations

Three areas of this synthesis are weaker than the rest and should be revisited before shipping:

- **A full page-by-page licence audit for every think-tank dataset.** OGL coverage is clear for ONS, HMRC, HMLR, DWP, Bank of England. HESA is clearly CC BY 4.0. Resolution Foundation, IFS, IPPR, Equality Trust, High Pay Centre and UCAS are all "public and free with attribution" but their pages are not standardised open-data products and individual chart-download pages can carry caveats. Before any chart that derives from a non-OGL source is published, the specific page's terms should be checked and the attribution string verified.
- **A definitive list of every potentially valuable FOI-only inequality dataset.** Section 1 lists the highest-confidence FOI targets (HMRC top-0.01% effective rates, ATED by region, non-dom counts, SDLT by buyer category, subnational income percentiles, HNW Unit caseload), but the full universe of useful FOIable cuts is larger than this synthesis covers. The FOI tracker page in v0.2 should be live well before the FOI universe is fully mapped — it is itself the discovery mechanism.
- **Some campaign claims about land ownership and long-horizon inheritance transfers.** The "70% of land is owned by under 1%" line and the projected-inheritance-transfer claims sit on primary-data chains that are harder for a general user to inspect from first principles than ONS/HMRC releases. Either avoid these in v0.1–v0.2, or — if included later — pair them with an unusually thorough "what this comparison does and does not mean" methodology page.

The most important practical implication of these three limitations is the same as the second-highest-leverage product decision in section 2: ship WealthLens with **source-by-source caveats and definition toggles**, not with a pretence that all inequality numbers mean the same thing. Doing this well makes the product more trustworthy than most existing UK tools immediately.

## Conclusion: the strategic shape of WealthLens

The clearest conclusion from this research is that **the UK inequality data is already substantially open**, **the campaigner demand is already substantially organised**, and **the technical tooling has matured to the point where a solo developer can credibly build something that fills a gap the FT, IFS and ONS have not filled**. The work is not data acquisition or visualisation primitives; it is **packaging** — taking a small number of well-sourced, well-caveated, embeddable, dated, mobile-first charts and putting them at stable URLs with social-optimised previews.

Four non-obvious takeaways shape what comes next.

First, **the WAS accreditation withdrawal in June 2025 is a feature for WealthLens, not a bug** — it creates a vacuum of authority on UK wealth data that an honest, methodology-transparent dashboard can occupy, provided it pairs WAS aggregates with WID top-tail corrections and labels its caveats unmistakably.

Second, **the highest-impact chart is one the project cannot compute itself** — the Advani-Summers effective-tax-rate-by-percentile — which means strategic partnerships (CenTax, IFS, Resolution Foundation) are at least as valuable as data engineering work, and the v0.3 roadmap should plan for them explicitly.

Third, **the right competitive frame is not "another UK inequality website" but "what does the UK lack that the US has?"** — quarterly distributional accounts, named-tax-rate transparency, intergenerational mobility mapping, real-time billionaire tracking, a single state-of-the-nation civic dashboard. None of those individual gaps is closeable by a solo developer in two weeks; but the **embeddable, shareable, dated, mobile-first chart-at-permalink-with-social-card pattern** is closeable in two weeks, and is the missing primitive that everything else depends on.

Fourth, **the definitions layer is the differentiator that compounds**. Most existing UK tools quietly conflate units; the ones that do not (IFS) are too dense for casual sharers. A product that makes the unit (households / adults / taxpayers / estates / gains / modelled) explicit on every chart, and where useful lets the user toggle between definitions, will be the rare UK inequality tool that researchers will trust *and* campaigners will share *and* journalists will embed. That is the strategic moat. Build the four charts first; build the definitions layer at the same time, not later.

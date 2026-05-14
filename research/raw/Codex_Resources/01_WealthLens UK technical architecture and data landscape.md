# WealthLens UK technical architecture and data landscape

## Bottom line

The strongest backbone for **WealthLens UK** is a hybrid of official statistics from entity["organization","Office for National Statistics","uk statistics office"], entity["organization","HM Revenue & Customs","uk tax authority"], entity["organization","HM Land Registry","england and wales registry"], the entity["organization","Department for Work and Pensions","uk welfare department"], and the entity["organization","Financial Conduct Authority","uk financial regulator"]; long-run top-end context from entity["organization","World Inequality Database","inequality data consortium"]; and interpretive layers from entity["organization","Resolution Foundation","uk think tank"], entity["organization","Institute for Fiscal Studies","uk policy research institute"], entity["organization","IPPR","uk progressive think tank"] and entity["organization","Equality Trust","uk equality charity"]. The single biggest product gap is not “more data”; it is a **public, shareable, embeddable, mobile-first explanation layer** that turns awkward XLSX/ODS/SPARQL/admin-data outputs into plain-English charts with methodology, downloads, and one-click embeds. citeturn26view0turn27view1turn38search9turn25view1turn24view4turn30search1turn34search0

If you want something genuinely useful within two weeks, do **not** start by trying to recreate the whole UK inequality field. Start with five canonical charts, each with a permanent URL, downloadable CSV, a short methods note, and a clean iframe/embed card. That is much closer to what entity["people","Gary Stevenson","economist and commentator"], entity["organization","Tax Justice UK","uk tax campaign group"] and entity["organization","Patriotic Millionaires UK","uk wealth tax campaign"] can actually share than a giant exploratory dashboard. citeturn12search0turn13search1turn14search0turn25view1turn24view4

## Public data landscape

The most important thing to understand is that the UK does **not** have one canonical, public, programmatic “wealth inequality API”. Instead, the landscape is split into: wealth survey tables, tax-admin tables, housing/open-property data, income-and-poverty survey tables, and a handful of think-tank model outputs. That fragmentation is your opportunity. citeturn26view0turn27view1turn38search9turn30search1

**Core official datasets you should treat as the first ingestion layer**

- **ONS household wealth family**: the ONS wealth release is built from the Wealth and Assets Survey and currently publishes seven dataset families: total wealth, financial wealth, property wealth, pension wealth, physical wealth, household debt, and quality indicators. Public access is mainly through downloadable XLSX tables on release pages; ONS’s developer platform does support JSON plus filter-based CSV/XLSX for many standard datasets, but the wealth release is still much more download-first than API-first. Update cadence is effectively biennial because the WAS is biennial, and the latest wealth tables I reviewed were released on 24 January 2025 with the next release “to be announced”. Reuse is generally straightforward under the OGL for most ONS content. This is the best public source for broad wealth composition, but it is not the best source for top-tail concentration claims on its own. See urlthe ONS developer hubturn0search1 and urlthe household total wealth methods guideturn9search5. citeturn28view0turn26view0turn26view2turn26view3turn26view4turn28view1

- **ONS housing affordability and income inequality family**: for housing, the high-value ONS dataset is the house-price-to-earnings ratio series, released annually for England and Wales; the current dataset page shows a 26 March 2026 release and March 2027 next release. For income, the most useful public outputs are average household disposable income, the household disposable income/inequality bulletins, and the small-area income estimates with downloadable XLS/CSV and embeddable interactives. These are excellent for postcode/area storytelling and are much easier for non-experts than tax tables. See urlthe housing affordability datasetturn9search8 and urlthe small-area income bulletinturn31search4. citeturn26view1turn32view5turn32view6turn9search0

- **HMRC personal income statistics**: HMRC’s Survey of Personal Incomes is the key administrative distribution dataset for income liable to UK tax. It is annual, published as GOV.UK HTML commentary plus spreadsheet tables, and it is highly important for percentile and top-income work. Programmatic access is middling: there is no modern HMRC statistical API comparable to ONS’s Beta API, so practical access means downloading and normalising ODS/XLSX tables. If you build parsers once, it becomes manageable. See urlPersonal Incomes Statisticsturn9search3. citeturn26view5turn9search15turn9search3

- **HMRC capital gains, inheritance, property-tax and tax-revenue statistics**: HMRC publishes annual pages for capital gains tax, inheritance tax liabilities, annual stamp taxes, ATED, non-domiciled taxpayers, tax reliefs, and tax receipts/NICs. These are some of the most politically salient UK wealth-tax data sources and some of the least ordinary-user-friendly, because they mostly arrive as HTML commentary attached to ODS workbooks. The update cadence is generally annual for CGT, IHT, stamp, non-doms and reliefs, and monthly/annual for receipts. Programmatic access is workable only if you are willing to ingest ODS. This is where you can add huge value just by transforming tables into clean chart JSON. See urlCapital Gains Tax statisticsturn11search0, urlInheritance Tax liabilities statisticsturn11search1, urlAnnual Stamp Tax Statisticsturn10search2, urlATED statisticsturn10search1, urltax receipts and NICsturn9search10 and urltax relief statisticsturn9search2. citeturn26view6turn27view5turn26view7turn27view6turn26view8turn26view9turn27view1turn27view0turn27view7turn32view3

- **HM Land Registry open property data**: this is the best public property-data layer for WealthLens. Price Paid Data can be downloaded as CSV or RDF/Turtle, and the service exposes SPARQL plus an API for some bulk datasets. The UK House Price Index tool also supports CSV downloads and queryable linked data. Licensing is OGL v3.0 for most content, with some caveats around address reuse. Programmatic access ranges from easy to advanced: CSV for most developers, SPARQL/linked data for power users, account-and-licence APIs for some bulk datasets such as overseas or company ownership records. See urlHM Land Registry Price Paid Data downloadsturn38search1, urlthe SPARQL consoleturn8search5 and urlthe Land Registry API guideturn38search9. citeturn38search1turn24view5turn38search9turn38search14turn38search15turn38search8

- **DWP and FCA household conditions data**: for ordinary-life context, the DWP’s Households Below Average Income and Family Resources Survey series are essential, and the FCA’s Financial Lives survey is a strong public source on savings, assets, debts, mortgages and product ownership. Financial Lives 2024 publishes tracker data tables across assets, debts, banking, investments and pensions, which makes it unusually re-usable for public storytelling. This layer is perfect for connecting “wealth inequality” to “how many people have less than £1,000 in assets?” or “who owns investments or pensions?”. See urlHBAI methodologyturn8search2, urlFamily Resources Survey 2024 to 2025turn31search1 and urlFinancial Lives 2024turn8search3. citeturn8search2turn8search6turn32view4turn28view4turn8search11

- **English Housing Survey**: this is one of the best secondary sources for tenure, resilience, housing quality, private renting, households in difficulty and landlord structure. Public reports and live tables are annual; underlying microdata are made available via the UK Data Service, so casual users can read the tables, while researchers can do deeper analysis. See urlthe English Housing Survey collectionturn8search0. citeturn25view7turn8search8

**Important enrichment layers rather than first-ingest layers**

- **Bank of England**: the Bank’s regular database is very programmatic by official-statistics standards, with CSV/XML downloads, and its legal page explicitly places database reuse under the UK OGL in most cases. That makes it a good source for macro-financial context such as mortgage rates, deposits, lending and asset-price context. Its research datasets are more specialised: useful, but not the first thing to surface for the public. See urlthe Bank database help pageturn2search0 and urlthe Bank research datasets pageturn2search1. citeturn24view1turn24view2turn28view3

- **HESA and UCAS**: these are not direct wealth datasets, but they are very useful if you want a “mobility and life chances” section later. HESA’s open data is explicitly CC BY 4.0. UCAS publishes large downloadable end-of-cycle CSVs and equality-entry explorers, including measures tied to deprivation, school type and free school meals. In practice, I would classify both as phase-two datasets for WealthLens unless you want a strong education-mobility chapter from day one. See urlHESA data and analysisturn3search3, urlUCAS data and analysisturn5search10, urlUCAS end-of-cycle data resources 2025turn5search2 and urlUCAS equality and entry rates explorersturn5search1. citeturn23search0turn4search11turn25view5turn25view6turn28view6

- **Resolution Foundation, IFS, IPPR, Equality Trust, WID, Wealth Tax Commission code**: these are critical not because they are always primary data sources, but because they translate official data into claims people repeat. Resolution’s public dashboards explicitly say their charts update quarterly or yearly and make chart data downloadable under the figures. IFS TaxLab’s data hub exposes interactive charts and spreadsheets on revenues, spending, tax rates, inheritance tax and distributional issues. WID adds long-run top-share and adult-equal-split distributional national accounts that official UK sources generally do not. IPPR often publishes model outputs in reports or press notes rather than maintained open datasets. Equality Trust is very important for campaign framing, but its public evidence base is mostly static pages and reports, not machine-readable data products. The Wealth Tax Commission’s open code bundle, hosted through the UK Data Service ReShare, is unusually valuable because it shows how top-tail corrections are actually implemented. See urlResolution Foundation Housing Outlookturn25view1, urlthe Resolution Foundation dashboardturn16search0, urlIFS TaxLab data hubturn2search3, urlWID United Kingdom pageturn30search0 and urlthe Wealth Tax Commission code bundleturn23search15. citeturn25view1turn25view0turn24view4turn30search0turn30search1turn29view4turn33search0turn34search0

**The licensing picture in plain English**

Licensing is easiest with ONS, Bank of England, Land Registry and most GOV.UK statistical tables, where OGL-style reuse is the norm subject to page-level caveats; HESA is clearly CC BY 4.0; WID country pages and reports are openly shared, though you should check page-specific Creative Commons terms; UCAS, Resolution, IFS, IPPR and Equality Trust are public and linkable, but their pages are not always presented as standardised “open-data products” in the same way as ONS or HESA. That means WealthLens should store **licence metadata per dataset family**, not assume one blanket rule. citeturn28view1turn28view2turn28view3turn38search14turn23search0turn30search0turn30search18turn6search0

## The campaign claims that matter most

The most repeated campaign claims fall into two groups: **solid but hard-to-explore public facts**, and **high-impact summary claims built from stitched or corrected datasets**. Your biggest opportunity is the second group. citeturn12search0turn13search1turn34search1turn16search15

The claims I would prioritise are these:

- The **“50 richest families own more wealth than half the country”** claim is extremely powerful and already used heavily by the Equality Trust and Tax Justice UK. It is also hard for an ordinary person to verify because it combines billionaire/rich-list style top-end data with population-scale wealth estimates for the bottom half. Those two worlds do not naturally live in the same public table. citeturn12search0turn12search5turn12search2turn34search2

- The **“top 10% hold the majority of wealth”** family of claims is foundational, but definition-heavy. Equality Trust currently uses a line about the share held by the top 10% rising since 1990, while another Equality Trust explainer cites ONS 2020 wealth shares and WID top-tail estimates. Ordinary users struggle because ONS, WID and campaigners may be using different units: households versus adults, survey totals versus distributional national accounts, and different wealth concepts. A chart that makes those definitional differences explicit would be genuinely valuable. citeturn34search2turn12search2turn30search1

- The **“income from wealth is taxed less than income from work”** claim is central for Tax Justice UK and Patriotic Millionaires UK. Tax Justice UK currently describes a person with £10 million total income paying an effective rate of around 21%, while also highlighting much heavier burdens lower down the distribution once work taxes and benefit withdrawal are considered. The public finds this persuasive because it feels concrete, but it is hard to test because it mixes effective rates, marginal rates, multiple tax bases, and sometimes policy-simulation assumptions. This is a great target for a transparent explainer chart with a “what this does and does not mean” box. citeturn13search2turn12search5turn13search7

- The **“CGT is highly concentrated”** claim is underused visually and very strong. WID’s UK capital-gains piece says the top 5,000 people receive more than half of all gains, and Tax Justice UK’s public messaging similarly stresses that gains are concentrated among a very small number of people. This is hard for ordinary people to explore because HMRC’s underlying publication lives in official-statistics tables and background-quality reports, not a public explorer. citeturn16search15turn13search8turn26view6turn27view5

- The **“wealth tax on assets above £10 million would hit very few people and raise a lot”** claim now appears repeatedly in Patriotic Millionaires UK and Tax Justice UK materials. Both groups cite thresholds affecting roughly 0.03% to 0.04% of the population and annual revenues in the tens of billions. What makes this hard to verify is that the underlying numbers come from **modelled wealth-tax work**, not a simple HMRC or ONS table, and that work uses corrections for top wealth that ordinary users never see. The UK Data Service code deposit for the Wealth Tax Commission is therefore unusually important for your methods section. citeturn13search4turn13search3turn13search11turn29view4

- The **“taxes on work raise vastly more than taxes on wealth”** claim is rhetorically effective and broadly grounded in HMRC receipts data, but it is still harder than it looks because “wealth taxes” is a chosen taxonomy, not an official HMRC master category. WealthLens could add real value by letting users toggle definitions: narrow wealth taxes only, broad capital/property taxes, or “work versus wealth” campaign framing. citeturn12search7turn27view0turn27view1

The claims I would treat more cautiously are the **“70% of land is owned by under 1% of the population”** line and some very long-range inheritance-transfer claims. They are politically useful and genuinely interesting, but the primary-data trail is much harder for a general user to inspect from first principles because UK land ownership is fragmented across titles, companies, trusts and historical estates, and because some inheritance claims depend on modelled future transfers rather than a single official publication. Those are good phase-two explainers, not your launch bet. citeturn3search4turn34search1turn34search5

**The best FOI lead I found**

The most promising FOI-type opportunity is **subnational HMRC percentile/distribution cuts** that are not routinely published as official releases. There is a public WhatDoTheyKnow example in which HMRC released income percentiles by region and London borough in spreadsheet form. That is exactly the sort of “campaigners reference it, ordinary people cannot easily find or explore it” territory where WealthLens can win. I would actively build an FOI pipeline or request log for borough/regional percentile cuts, especially where they intersect with housing, children, or specific asset/income types. See urlthis HMRC FOI example on regional and London-borough percentilesturn7search0. citeturn7search0

## Existing tools and the gap they leave

There are already useful public tools, but they are fragmented.

The closest UK precedents today are urlONS local housing pagesturn35search3, urlONS housing affordability toolsturn35search1, urlONS small-area income interactivesturn35search11, urlResolution Foundation Housing Outlookturn25view1, urlthe Resolution Foundation intergenerational dashboardturn16search0, urlIFS TaxLab data hubturn2search3, urlWID’s income comparatorturn16search1 and urlHM Land Registry’s open data toolsturn38search8. They are useful in isolation, but none of them gives the public a single, UK-specific journey from **wealth concentration → taxation → housing → everyday financial precarity**. citeturn35search3turn35search1turn32view5turn25view1turn25view0turn24view4turn16search1turn38search8

The main limitations are straightforward:

- **Official ONS tools are often good chart components, not a unified product.** Some pages do expose downloads and embed code, which is great, but the experience is still distributed across many pages, methods notes and microsites. Some prominent ONS inequality/wealth-style tools are also visibly stale, such as the 2021 mapping microsites and the Wealth Calculator drawing on 2019–20-era sources. citeturn32view5turn35search0turn35search6turn35search7

- **Resolution Foundation is strong on public storytelling and downloadable chart data, but the framing is topic- or generation-specific.** It is better than most think-tank sites for public navigation, but it is not designed as a reusable public data platform in the way your product could be. citeturn24view3turn25view1turn25view0

- **IFS TaxLab is excellent for tax mechanics, not for the whole wealth story.** It is interactive and spreadsheet-backed, which matters, but it is still mainly a tax-policy explainer/data hub rather than a shareable inequality visual platform connecting taxes to housing, assets and lived experience. citeturn24view4

- **WID is uniquely valuable for top shares and long-run history, but it is conceptually heavy for ordinary UK users.** It gives you the long-run framing and international comparators, yet most users will not naturally understand adult-equal-split income, pretax/posttax national income, or the reconciliation methods without substantial explanation. citeturn30search0turn30search1turn16search5

- **Land Registry is data-rich and developer-friendly, but not inequality-first.** You can get CSV, RDF, SPARQL and some API access, but the public-facing tools are property-data tools rather than social-explainer products. citeturn38search1turn38search9turn38search15

That leads directly to the product gap: WealthLens should behave like a **public-interest chart library plus explainer system**, not just a dashboard.

The clearest US-style comparators that the UK lacks are: an **Opportunity Atlas-style neighbourhood mobility tool** from entity["organization","Opportunity Insights","us research institute"]; a **ProPublica-style searchable tax/ownership/exemption explorer** from entity["organization","ProPublica","us nonprofit newsroom"] built around raw structured records and human-readable reconstructions; and a **USAFacts-style unified public-finance explainer layer** from entity["organization","USAFacts","us civic data initiative"] that standardises dozens of government sources into plain-language charts. The UK has pieces of each, but not the combination. See urlOpportunity Atlas neighbourhood mapsturn37search0, urlProPublica Nonprofit Explorer API docsturn20search0 and urlUSAFacts government spending pagesturn37search5. citeturn37search0turn37search9turn20search0turn24view6turn37search5turn21search3

## Recommended architecture

Your existing stack is already close to the right answer. I would recommend a **hybrid static-first architecture with a thin dynamic layer**, not a fully dynamic dashboard application. That recommendation is based both on the shape of the data and on how successful public-data projects tend to publish. citeturn24view7turn25view2turn20search0turn19search0

The core shape should be:

- **Data pipeline in Python** using snapshots, normalisation, harmonisation, derived metrics and publication artefacts. The best model here is the five-stage workflow described in entity["organization","Our World in Data","global data publication org"]’s ETL docs: snapshot, format, harmonise, import, publish. That is the right mental model for WealthLens too. Use raw-source snapshots, then typed intermediate tables, then chart-ready outputs. See urlOWID ETL workflow docsturn18search0. citeturn24view7

- **Static chart pages and explainer pages** generated ahead of time, ideally with your Vue stack through a static-capable framework layer. The point is that every shareable chart should have a permanent route, metadata, social preview, source notes and downloads without depending on expensive live queries. Fast load speed and stable URLs matter more than “dashboard-ness”. citeturn25view2turn35search7turn32view5

- **FastAPI as the thin control plane**, not the main analytics engine. Use it for search, dataset metadata, chart manifests, embed endpoints, OG-image generation, and perhaps postcode or geography lookup. Do not make it the place where large statistical datasets are recomputed per request. citeturn25view2turn38search9turn19search0

- **Columnar storage plus published artefacts**: raw snapshots in object storage, transformed tables in Parquet, chart-ready JSON/CSV for the frontend, and perhaps PostgreSQL only for metadata/search. For local and CI processing, DuckDB or Polars is a better fit than trying to use Postgres for everything. This is an architectural inference from the publication patterns above, but it is the pragmatic route for open-data civic tech. citeturn24view7turn25view3

- **Embed-first chart contract**: every chart should expose share URL, iframe embed, PNG/SVG export, CSV download and a short machine-readable metadata JSON. OWID’s chart system is instructive here because chart data and metadata are separate, directly fetchable artefacts. See urlOWID Charts API docsturn18search1. citeturn25view2turn25view3

- **Geography service**: standardise on official ONS geography codes and keep a postcode-to-geography resolver. If you want a reference implementation for this kind of service, the open-source MapIt codebase from entity["organization","mySociety","uk civic tech org"] is a good precedent. See urlMapIt UK READMEturn19search0. citeturn19search0turn20search5

- **Accessibility and mobile-first constraints from day one**: target WCAG 2.2 AA; work to GOV.UK-style responsive guidance; and assume many users will only ever see your work inside a social app browser on a narrow screen. ONS’s own visualisation manual explicitly warns that annotations may not display on mobile and should not carry essential information alone. See urlWCAG 2.2turn22search0 and urlthe GOV.UK accessibility guidanceturn22search1. citeturn22search0turn22search1turn22search3turn22search2turn22search13

**The practical stack I would use for WealthLens in 2026**

Stay close to what you already know: Python + Polars/DuckDB + FastAPI + Vue 3 + TypeScript + D3 + Docker. Add static generation and object-storage publishing rather than a heavier BI stack. For a two-week v0.1, I would use simple scheduled GitHub Actions instead of overbuilding orchestration. If the project becomes a permanent public-data platform, move later to a DAG-oriented orchestrator and richer data-catalog tooling. citeturn24view7turn18search2turn18search20

## Build priorities and the first charts

The first release should be built around **single-message charts**, not “analysis workspaces”. The shareable unit is not the dashboard home page; it is the chart page someone can drop into WhatsApp, Bluesky, X, LinkedIn, a campaign newsletter or an iframe on a partner site. citeturn35search7turn32view5turn25view1

These are the ten single-chart ideas I would prioritise, in order:

- **Who owns UK wealth?** A stacked share-of-total chart: bottom 50, middle 40, next 9, top 1, over time. Include a clear definition toggle for ONS versus WID where possible. citeturn12search2turn30search0turn30search1

- **The richest 50 families versus the poorest half** as a two-bar or population-vs-wealth comparator with an aggressive methodology note. This is the most scroll-stopping campaign chart if you can explain the stitching honestly. citeturn12search0turn12search5turn34search2

- **House prices versus earnings since 2000** indexed on one axis, with a line for wages and a line for median house prices or affordability ratios. IPPR’s “your house has outvalued you” framing works because it is instantly legible. citeturn33search1turn9search0turn35search7

- **How affordable are homes near you?** A postcode-search local chart using ONS affordability ratios and/or local price pages. This is the strongest “personal hook” visual you can ship quickly. citeturn26view1turn35search3turn35search7

- **Taxes on work versus taxes on wealth** with a toggle for narrow and broad definitions. The key is not to hide the definitional argument; make it explorable. citeturn12search7turn27view0turn27view1

- **Capital gains are not ordinary income**: a concentration chart showing how much of total gains go to a tiny number of people. This is underdeveloped in the current UK public visual space. citeturn16search15turn13search8turn26view6

- **Inheritance tax: few estates, rising receipts**. This is powerful because it punctures two myths at once: “everyone pays it” and “it raises nothing”. citeturn26view7turn27view0

- **How many people have almost no financial buffer?** Use FCA Financial Lives or related asset/debt tables to show the share of adults with very low investible assets. This connects macro-inequality to everyday insecurity. citeturn8search11turn28view4

- **Ownership by age and tenure**: owner-occupied, private rented, social rented, with an age or cohort split. That gives you the intergenerational housing story without requiring users to read a report. citeturn25view1turn25view7turn8search16

- **Regional inequality within the UK**: wealth or income percentile distributions by nation/region using ONS and any compatible enrichment series. This is highly shareable because people search for themselves first. citeturn26view0turn32view5

**What to pull first**

If I were sequencing the data pulls, I would do them in this order:

- **First**: ONS wealth tables, ONS housing affordability, ONS small-area income, HMRC receipts, HMRC SPI, HMRC CGT, HMRC IHT. Those are your canonical public-interest datasets. citeturn26view0turn26view1turn32view5turn27view1turn26view5turn26view6turn26view7

- **Second**: HM Land Registry PPD/UKHPI and FCA Financial Lives. These make the product feel tangible and local. citeturn38search1turn38search15turn28view4

- **Third**: WID UK series and the Wealth Tax Commission code bundle. These are how you handle top-end concentration honestly instead of pretending the survey tables are enough. citeturn30search0turn29view4

- **Fourth**: Resolution/IFS reusable downloads for chart enrichment, copy validation and alternative views. citeturn25view1turn24view4

## What v0.1 should look like

A v0.1 that campaign groups would actually share is much smaller than most engineers initially imagine.

It should be a site with:

- **Five chart pages** only.
- Each chart page has: headline, subhead, one chart, one paragraph of plain-English interpretation, one download dropdown, one “copy embed” action, one “download image” action, one methodology box, one data-source box, and one version/date stamp. citeturn25view2turn32view5turn35search7
- A **simple topic index**: wealth, taxes, housing, income, methods.
- A **researcher mode** on the same pages: raw CSV, metadata JSON, citation text, transformation notes, and source links.
- A **partner-ready embed endpoint** so organisations can drop charts into their CMS without dealing with your full app shell.
- A **definitions layer** that makes clear when a figure is about households, adults, taxpayers, estates, gains, or modelled estimates. That definitions layer is one of the main product differentiators. citeturn30search1turn26view5turn26view7turn27view5

A credible two-week build plan would look like this:

**Week one**: define dataset manifests; implement snapshot-and-transform jobs; publish versioned chart JSON/CSV for the first three ONS/HMRC charts; build one chart template and one methodology template; ship share routes and OG images. citeturn24view7turn25view2

**Week two**: add Land Registry or FCA enrichment; finish embeds/downloads; do keyboard testing and mobile testing; add source-attribution/licensing metadata; write short chart copy and caveat notes; publish to a static host behind a CDN with a thin FastAPI service for metadata/search. citeturn38search10turn22search1turn22search2turn22search3

If I had to define the exact first five charts for launch, I would choose:

- Who owns UK wealth?
- The richest 50 families versus the poorest half.
- House prices versus earnings since 2000.
- Taxes on work versus taxes on wealth.
- Capital gains concentration.

That combination covers the full public argument in one glance: **who has wealth, how that affects housing, and how the tax system treats it**. citeturn12search0turn12search5turn9search0turn27view0turn16search15

## Open questions and limitations

This research pass is high-confidence on the **official public-data backbone**, the shape of public tools, and the technical architecture direction. It is lower-confidence on three narrower points: a full page-by-page licence audit for every think-tank dataset; a definitive list of every potentially valuable FOI-only inequality dataset outside the HMRC percentile example; and some campaign claims about land ownership or long-horizon inheritance transfers where the public primary-source chain is not as clean or inspectable as ONS/HMRC releases. citeturn7search0turn34search1turn34search5

The most important practical implication of those limitations is simple: ship WealthLens with **source-by-source caveats and definition toggles**, not with a pretence that all inequality numbers mean the same thing. If you do that well, the product becomes more trustworthy than most existing tools immediately. citeturn30search1turn26view0turn27view5turn27view6
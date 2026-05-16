# Inbox

Last updated: 2026-05-16

Every concrete action item extracted from research. Triage into active-sprint, backlog, or done.

---

## Build: Charts and Visualisations

- [ ] Build "Where Do You Fit in UK Wealth?" personal comparator calculator
- [ ] Build "Top 1% wealth share over time" chart with definition toggle (ONS WAS / WID / RF corrected)
- [ ] Build "Regional house-price-to-earnings scrollytelling" chart
- [ ] Build "House for the price of a house: what £200k buys across the UK" photo carousel
- [ ] Build "Animated UK wealth concentration: 1980-2025" GIF/MP4
- [ ] Build "Inheritance Britain: who inherits what, and when?" Sankey diagram
- [ ] Build "The Two Englands: London vs the rest, in 10 charts" small-multiples
- [ ] Build "Marmot postcode life-expectancy gap" lookup tool
- [ ] Build "Compare your effective tax rate to a billionaire" calculator
- [ ] Build "CEO-vs-worker pay clock" — UK FTSE-100 version (for "High Pay Day" in January)
- [ ] Build "Lifetime tax burden by income percentile" calculator
- [ ] Build "1 pixel = £1,000: UK wealth to scale" horizontal scroller (a la Korostoff)
- [ ] Build "If the UK were 100 people" pictogram / Instagram Reel
- [x] Build UK tax revenue composition chart ("tax on work vs tax on wealth") [completed: 2026-05-16]
- [x] Build capital gains concentration chart (top 5,000 receive >50% of gains) [completed: 2026-05-15]
- [ ] Build inheritance tax chart (only 4-5% of estates pay IHT)
- [ ] Build real wage stagnation + counterfactual chart
- [x] Build regional GDP per head map [completed: 2026-05-16 — GDHI pipeline built]
- [x] Build child poverty by region map [completed: 2026-05-16 — pipeline built]
- [x] Build productivity-pay gap (scissor chart) [completed: 2026-05-16 — pipeline built]
- [x] Build generational wealth gap by birth cohort chart [completed: 2026-05-16 — pipeline built]
- [ ] Build ownership by age and tenure chart (owner-occupied / private rent / social rent)
- [ ] Build "Share of adults with almost no financial buffer" chart (FCA Financial Lives)
- [ ] Build wealth-to-income ratio chart
- [ ] Build UK billionaire wealth tracker (Forbes-driven, weekly refresh)
- [ ] Build wealth tax revenue simulator with rate/threshold/exemption/behavioural-response sliders
- [ ] Build "The capital-gains toggle" — top 1% share with and without capital gains
- [ ] Build effective tax rate by wealth percentile chart (with CenTax permission)
- [ ] Build 50 richest families vs bottom half chart (needs careful methodology)
- [ ] Build FTSE 100 CEO pay ratio chart
- [ ] Build Trussell foodbank use chart (2.89m parcels, ~50x 2010/11)
- [ ] Build university access by household income decile visualisation (UCAS data)
- [ ] Build WP Sankey: access at 18 -> wealth distribution at 60
- [ ] Build postcode-driven local house-price-to-earnings lookup
- [ ] Build "UK Spirit Level 2.0" — regional scatterplots
- [ ] Build "The wealth detective — find the UK billionaire near you" postcode lookup
- [ ] Build "Methodology honesty card" — source toggle UI beside every wealth chart

## Build: Infrastructure and Platform

- [ ] Register `wealthlens.uk` domain
- [ ] Set up Astro 5 + Vue 3 islands + Observable Plot scaffold
- [ ] Configure Cloudflare Pages deploy from GitHub
- [ ] Set up Cloudflare R2 bucket for raw data snapshots
- [x] Set up GitHub Actions cron skeleton with Python ETL using OWID five-stage model [completed: 2026-05-16 — weekly-update.yml]
- [ ] Write OG-image build task with `satori` + `resvg-js`
- [ ] Set up `@newswire/frames` for responsive iframe embeds
- [ ] Implement `/oembed?url=...&format=json` endpoint on a Cloudflare Worker
- [x] Set up public GitHub repository with MIT/Apache-2.0 licence on code, CC-BY 4.0 on charts [completed: 2026-05-14]
- [ ] Build a "data status" badge for every chart
- [x] Run WCAG 2.2 AA accessibility pass: keyboard navigation, role="img", alt text, contrast [completed: 2026-05-16]
- [ ] Create 3-4 Canva templates for sharing charts as social images
- [ ] Set up donation page: Open Collective or Ko-fi
- [ ] Set up email list: Buttondown (free <100 subs) or Substack
- [ ] Set up project board via GitHub Projects
- [x] Set up analytics: Plausible (£7/month) or Umami (self-hosted, free) [completed: 2026-05-16 — privacy-respecting analytics integrated]
- [ ] Set up project email (hello@wealthlens.uk)
- [ ] Apply for GitHub Sponsors
- [ ] Create media kit: one-pager PDF about the project
- [ ] Create "Data Sources & Licences" page for the website
- [ ] Create contributors page on website
- [x] Build simple landing page (GitHub Pages, Astro, or Hugo) [completed: 2026-05-15 — Vue frontend deployed to GitHub Pages]
- [x] Write README with mission, screenshot, "How to contribute", tech stack, licence [completed: 2026-05-16]
- [x] Write CONTRIBUTING.md with setup instructions and task list [completed: 2026-05-15]
- [x] Create GitHub Issues for first 10 tasks (labelled "good first issue", "help wanted") [completed: 2026-05-15]

## Build: Data Pipelines

- [x] Build `fetch_ons_wealth.py` data pipeline [completed: 2026-05-15]
- [x] Build `fetch_hmrc_stats.py` data pipeline [completed: 2026-05-14]
- [x] Build `fetch_wid_data.py` data pipeline [completed: 2026-05-14]
- [ ] Build reliable spreadsheet parsers for high-value XLSX/ODS wealth releases
- [ ] Set up DWP Stat-Xplore API access (free registration + key)
- [ ] Set up Companies House API key (free, 600 req/5min)
- [x] Ingest Bank of England IADB series via parameterised CSV URLs [completed: 2026-05-16 — fetch_boe_rates.py]
- [ ] Ingest ONS Beta API datasets (JSON, rate limit 120 req/10s)
- [ ] Ingest HMRC tax receipts and NICs annual bulletin CSV
- [x] Ingest ONS housing affordability XLSX [completed: 2026-05-14 — fetch_ons_housing.py]
- [ ] Ingest Land Registry Price Paid Data CSV (~5GB)
- [x] Set up Nomis API for GDHI data (no auth required) [completed: 2026-05-16 — fetch_ons_gdhi.py]
- [ ] Build pdfplumber parser for HMRC Personal Wealth Statistics PDF tables
- [ ] Ingest High Pay Centre CEO pay data from PDF (manual data entry)
- [x] Build `chart_to_social.py` — auto-generate platform-sized images from chart data [completed: 2026-05-15]
- [x] Set up GitHub Action: `weekly-data-update.yml` [completed: 2026-05-16]
- [x] Set up GitHub Action: `deploy.yml` (auto-deploy on push) [completed: 2026-05-15]
- [ ] Build research automation: `summarise_research.py` (Claude API)
- [x] Build research automation: `extract_action_items.py` [completed: 2026-05-15]

## Build: WP Pathway Explorer

- [ ] Build weekend prototype: "Postcode -> Pathway Snapshot" Vue 3 + FastAPI app
- [ ] Create three FastAPI endpoints: `/lookup/{postcode}`, `/providers`, `/programmes`
- [ ] Hand-curate JSON for 19 London providers' contextual-offer policies
- [ ] Create static JSON for bursary data
- [ ] Deploy prototype on Fly.io or Railway
- [ ] Demo prototype to WP team
- [ ] Write one-page brief mapping tool to OfS EORR Risks 1, 2, 4, 7, 12
- [ ] Write costed three-month plan with named deliverables
- [ ] File DPIA with Information Governance team
- [ ] Request named WP team sponsor
- [ ] Propose WP postcode-to-university data tool to Middlesex University WP team

## Build: Tools

- [ ] Build openpoverty-uk Python API wrapping DWP HBAI, ONS FRS, IMD, JRF data
- [ ] Scrape and publish a UK Companies House dataset with a story on GitHub
- [ ] Scrape and publish a Hansard dataset with a story on GitHub
- [ ] Build one D3/Observable interactive visualisation

## Outreach: Emails to Send

- [ ] Email Tax Justice UK (info@taxjustice.uk) with prototype link [UNBLOCKED — v0.1 is live]
- [ ] Contact Patriotic Millionaires UK via website contact form [UNBLOCKED — v0.1 is live]
- [ ] Email The Equality Trust (info@equalitytrust.org.uk) [UNBLOCKED — v0.1 is live]
- [ ] DM Gary Stevenson (@garyseconomics) on X with prototype link [UNBLOCKED — v0.1 is live]
- [x] Email mySociety (whofundsthem@mysociety.org) to join volunteer cohort [completed: 2026-05-14]
- [x] Email Democracy Club (hello@democracyclub.org.uk) [completed: 2026-05-14]
- [ ] Email Common Wealth (info@common-wealth.org) with proposal [after building CH/LR tool]
- [ ] Email Arun Advani at CenTax (a.advani.1@warwick.ac.uk) [after publishing original analysis]
- [ ] Email Max Lawson at Oxfam (max.lawson@oxfam.org) [after building widget]
- [ ] Soft-launch email to John Burn-Murdoch (FT) with chart URLs [after v0.1]
- [ ] Email Charles Arthur (The Overspill) with first post
- [ ] Pitch Data Elixir (Lon Riesberg) with technical post
- [ ] Pitch Python Weekly (Rahul Chaudhary) with technical post + repo
- [ ] Email info@theodi.org for guest blog interest
- [ ] Email Myf Nixon at mySociety about practitioner blog post

## Outreach: Volunteering

- [ ] Sign up to Democracy Club volunteer alerts
- [ ] Sign up to Full Fact's volunteer mailing list
- [ ] Make first PR to mySociety FixMyStreet/Alaveteli (issues tagged "Suitable for Volunteers")
- [ ] Open a PR on TJN's `swift_codes_scraper` repo (modern Python rewrite)
- [ ] Engage one issue on Democracy Club's `UK-Polling-Stations`
- [ ] Open a PR on mySociety's `local-intelligence-hub`
- [ ] Contribute to one Bellingcat Volunteer Community investigation
- [ ] Contribute to OpenSAFELY / Bennett Institute open-source project
- [ ] Contribute to Alan Turing Way book sprints
- [ ] Subscribe to DataKind UK newsletter (for when volunteer apps reopen)

## Outreach: Events and Speaking

- [ ] Attend LSE III Inequalities Seminar Series (Tuesdays during term)
- [ ] Attend UCL IIPP Forum 16-17 June 2026
- [ ] Show up at Newspeak House civic-tech sessions in London
- [ ] Attend Resolution Foundation events at 2 Queen Anne's Gate
- [ ] Investigate attending The Conduit events in London
- [ ] Attend Campaign Lab bi-weekly hack nights
- [ ] Attend Journalism Technology London Meetup
- [ ] Submit MozFest 2026 CFP under digital rights / economic power tracks
- [ ] Submit AIES 2026 abstract (deadline 14 May) for Global Inequalities track
- [ ] Pitch PyData London CFP
- [ ] Submit Hacks/Hackers London talk (DM @HacksHackersLDN on X)
- [ ] Pitch ODI Friday Lecture for autumn slot
- [ ] Pitch Papers We Love London for SGAI paper read-through
- [ ] Apply to TEDxLondon (tedxlondon.com/speaker-applications)
- [ ] Pitch The Conduit: "How engineers can turn inequality data into public action"
- [ ] Submit RightsCon 2027 CFP (opens 1 August 2026)
- [ ] Get UKGovCamp ticket when registration opens (~October 2026)
- [ ] Register for NICAR 2027 (opens ~October 2026)

## Outreach: Podcast Pitches

- [ ] Pitch Tech Won't Save Us (Paris Marx on Bluesky @parismarx)
- [ ] Pitch The Bunker (podmasters.co.uk; 200-word pitch)
- [ ] Pitch ODI podcast (info@theodi.org)
- [ ] Pitch Trashfuture (DM @raaleh or @inthesedeserts on social)
- [ ] Pitch Intelligence Squared (podcasts@intelligencesquared.com)
- [ ] Pitch Novara's Downstream (DM @AaronBastani)
- [ ] Pitch 80,000 Hours (podcast@80000hours.org; 150-word hook + 3 topics)

## Outreach: Grants and Funding

- [ ] Apply to JRRT Larger Grants — September 2026 round (outline by 24 August)
- [ ] Apply to SSI Fellowship — apps open August 2026, close ~6 October 2026
- [ ] Apply to Mozilla Foundation Fellowship — next cycle opens early 2027
- [ ] Apply to Bellingcat Tech Fellowship (tech@bellingcat.com)
- [ ] Apply for Bethnal Green Ventures Autumn 2026 cohort (~May 2026 window)
- [ ] Apply for UnLtd Starting Up Award (500-8,000, rolling)
- [ ] Submit EOI to Esmee Fairbairn, Friends Provident, Barrow Cadbury, Trust for London
- [ ] Apply for internal HEIF + APP investment line + innovation/seedcorn fund (Middlesex)
- [ ] Apply to Comic Relief Tech for Good (with charity partner)
- [ ] Apply to Paul Hamlyn Ideas and Pioneers Fund (via partner org)
- [ ] Contact Trust for London — book a call with grants manager before EOI
- [ ] Track Alan Turing Institute Open Source AI Fellowship 2027 cycle

## FOI Requests to File

- [ ] HMRC top 0.01% effective tax rates by income decile
- [ ] Non-dom counts and tax paid by gross income band
- [ ] Trust ownership of UK property at LA level
- [ ] ATED dwellings by region
- [ ] SDLT by buyer category (corporate / foreign individual / trust)
- [ ] HMRC High Net Worth Unit caseload aggregates
- [ ] Subnational income percentiles by region and London borough

## Content: Social Media and Writing

- [x] Create Twitter/X account with bio and pinned manifesto thread (5-7 tweets) [completed: 2026-05-14]
- [x] Create Bluesky account [completed: 2026-05-14]
- [ ] Update LinkedIn headline and About section per rebranding playbook
- [ ] Add WealthLens to LinkedIn experience
- [ ] Update LinkedIn Featured section (WealthLens, Springer pub, WP post, Taskdeck)
- [ ] Add skills to LinkedIn: Data Visualisation, Open Data, Economic Research, Widening Participation
- [ ] Update Instagram bio gradually
- [ ] Build a private X List of 30-50 accounts (10 big, 20 mid, 20 peers)
- [ ] Join ukgovernmentdigital.slack.com
- [ ] Request access to Bureau Local Slack via TBIJ
- [ ] Write first blog post: "Why I'm building WealthLens UK" (LinkedIn article + Dev.to)
- [ ] Write blog post: "What my experience building trading systems taught me about wealth inequality"
- [ ] Write technical blog post on WealthLens methodology
- [ ] Post LinkedIn announcement using founding document copy
- [ ] Post Instagram launch post
- [ ] Post call for volunteers with specific roles listed

## Content: Writing for the Curriculum

- [ ] Write 500-word summary of r > g argument and the Acemoglu-Robinson critique [Week 1]
- [ ] Produce one-page UK inequality fact-sheet [Week 2]
- [ ] List Atkinson's 15 proposals and assess each [Week 3-4]
- [ ] Write 500-word piece on whether UK exhibits homoploutia [Week 4]
- [ ] Write balanced 1,000-word essay on Wilkinson-Pickett causal claims [Week 6]
- [ ] Write 1,500-word "Best Case Against a UK Wealth Tax" essay + rebuttal [Week 9]
- [ ] Produce timeline of UK wealth-related tax reforms 1965-2026 [Week 8]
- [ ] Write 3,000-word synthesis: "How the UK became as unequal as it is" [Week 12]
- [ ] Write 2,000-word piece: "Why top 1% income share is contested" [Week 17]
- [ ] Write 1,500-word piece: "Will AI reduce or amplify UK wealth inequality?" [Week 23]
- [ ] Produce comparative table of Swiss, Norwegian, Spanish, French, and proposed UK wealth-tax regimes [Week 24]

## Content: Data Analysis

- [ ] Replicate a UK Lorenz curve from FRS or WAS data in Python/R [Week 13]
- [ ] Pull UK top 1% income share time series from WID [Week 16]
- [ ] Produce UK top 1% income share chart 1918-2024 [Week 16]
- [ ] Derive WTC 260bn and 80bn revenue figures from model assumptions [Week 8]

## Career: Job Applications and Education

- [ ] Apply to mySociety SocietyWorks Developer role by 31 May 2026
- [ ] Apply to GDS Senior Developer and HMRC/DWP/MoJ DDaT roles via Civil Service Jobs
- [ ] Apply to NHS England Band 7 digital roles
- [ ] Apply to UCL ARC RSE (autumn round, September-November)
- [ ] Apply to Alan Turing REG
- [ ] Apply to Monzo / Wise / GoCardless / Cleo
- [ ] Apply to Mozilla UK remote roles
- [ ] Apply to Wellcome Trust engineering roles
- [ ] Begin LeetCode and system-design preparation for FAANG/fintech
- [ ] Consider Georgia Tech OMSCS Spring 2027 (applications August-September 2026)
- [ ] Consider AFSEE fellowship for LSE Inequalities (January 2027 deadline)
- [ ] Submit Chevening 2027/28 application by 7 October 2026
- [ ] Submit one freelance data-journalism pitch per month to openDemocracy / The Ferret / Tortoise
- [ ] File FOI requests via WhatDoTheyKnow and document methodology publicly

## Legal and Governance

- [ ] Research domain availability: wealthlens.uk, wealthlensuk.org
- [ ] Choose licence: MIT or AGPL-3.0 (for dashboard code)
- [ ] Incorporate WealthLens UK as CIC Limited by Shares at month 3-4 (~£130)
- [ ] Create data-licences.md documenting licence for each data source
- [ ] Create privacy policy for website
- [ ] Conduct full page-by-page licence audit for every think-tank dataset

## Finance

- [ ] Open a Cash ISA; start saving surplus monthly
- [ ] Build £5,000 emergency fund within 3-4 months of new role

## Community and People

- [ ] Create people/contributors.md listing all contributors
- [ ] Create people/onboarding.md for new volunteers
- [ ] Create people/roles.md defining available roles
- [ ] Create people/thank-yous.md recognition log
- [ ] Create Discord server (delay until prototype exists): #general, #engineering, #data-research, #design, #content, #introductions
- [x] Write "About" page copy for future website [completed: 2026-05-16 — AboutView.vue on frontend]

## Personal Brand

- [ ] Create/update Linktree with all links
- [ ] Repurpose personal Instagram to promote inequality/data mission (gradual transition)
- [ ] Verify Bluesky handle via personal domain
- [ ] Set up Ghost blog on personal domain (or Substack mirror)
- [ ] Apply for FRSA via thersa.org
- [ ] Add openpoverty-uk to Civic Tech Field Guide directory [after building]

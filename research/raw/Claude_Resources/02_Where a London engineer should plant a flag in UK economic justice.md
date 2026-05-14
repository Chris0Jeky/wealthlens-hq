# Where a London engineer should plant a flag in UK economic justice

**Start with mySociety, Common Wealth, CenTax, Tax Justice Network and Equality Trust — these five sit at the intersection of high tech leverage, real receptiveness to volunteers, and direct relevance to wealth inequality.** The wider ecosystem is large (40+ orgs), but it is held together by a small funder pool (JRCT, JRF, Friends Provident, Nuffield, Trust for London) and a recurring cast of campaigners; embedding well means picking two or three nodes and building real artefacts. The UK has no formal "Code for Britain" or PIT-UK fellowship — mySociety is the de facto Code for America equivalent, and the genuine grant routes for an engineer building tools sit at the Joseph Rowntree Reform Trust (political/transparency tools), Software Sustainability Institute (research software), Mozilla Foundation (independent track) and JRF's Emerging Futures programme. The single biggest engineering gap in the UK ecosystem is a clean, open, reproducible wealth-distribution and tax-reform calculator on top of HMRC/ONS/Companies House — almost every campaigning org would use it, and nobody currently owns it.

The political window is unusually wide. Reeves's November 2025 Budget introduced a High Value Council Tax Surcharge on >£2m properties, capped IHT business/agricultural relief, raised dividend and property-income rates, and froze IHT thresholds to 2031 — but explicitly stopped short of a wealth tax. A 51-MP Labour rebellion has formed around Richard Burgon's EDM 64316, Patriotic Millionaires UK and Tax Justice UK are pushing the "Ten Tax Reforms to Raise £50bn" agenda, and Gary Stevenson's YouTube channel (~1.4m subscribers) has made wealth inequality genuinely mainstream. The Autumn Budget 2026 is the next major fiscal moment; the HVCTS implementation consultation is live now; a Spending Review 2027 is in train. Data tools shipped before October 2026 will land.

This report maps the field, ranks the engineering opportunities, and gives specific next steps.

## How the ecosystem fits together

Five clusters do most of the work, with heavy overlap of staff, funders and joint reports.

**Campaign and policy.** Tax Justice UK (TJUK), Patriotic Millionaires UK (PMUK) and the Equality Trust form the visible "tax the rich" front, coordinated tightly and increasingly co-publishing with **NEF**, **IPPR's Centre for Economic Justice**, and the **TUC**. The Tax Justice Network (TJN) is the international research engine behind the Financial Secrecy Index and State of Tax Justice — UK-headquartered but globally focused. Positive Money sits adjacent on monetary/banking reform; Common Wealth on ownership; Oxfam GB's inequality team produces the annual Davos report.

**Research / think tanks.** Resolution Foundation, IFS and IPPR are the heavyweights inside Treasury's orbit — note that **Torsten Bell** (former Resolution Foundation CEO) is now Parliamentary Secretary to HMT and **Dan Tomlinson** (ex-Resolution) is Exchequer Secretary, making Resolution Foundation alumni unusually influential on the current Budget cycle. The new **CenTax** (Centre for the Analysis of Taxation, co-directed by Arun Advani at Warwick and Andy Summers at LSE) is the most policy-impactful new entrant, having directly shaped the 2024–25 non-dom, CGT and IHT reforms. Demos, Fabian Society and Progressive Economy Forum sit further from Treasury but each has a distinct role (deliberation tech, Labour Party constitutional link, heterodox network).

**Academia.** LSE International Inequalities Institute (now joined by the **Stone Centre at STICERD**, $5m Stone Foundation gift, 2024); INET Oxford (Doyne Farmer's Complexity Economics group is the most engineer-friendly research outfit in UK academia); Warwick CAGE (£7.1m ESRC funding for 2025–29); UCL IIPP (Mazzucato — strong on mission/public-value framing, weak on data engineering).

**Civic tech.** mySociety, Democracy Club, Full Fact, the Open Data Institute and DataKind UK — collectively the highest engineering leverage in the ecosystem, but only a subset are directly aligned with wealth inequality work.

**Funder web.** Joseph Rowntree Charitable Trust (JRCT) funds TJUK, Equality Trust, NEF, Positive Money, mySociety, Full Fact, Democracy Club. Friends Provident funds NEF, Positive Money, Equality Trust. Nuffield funds Resolution Foundation, IFS, Full Fact. Trust for London funds Equality Trust, IPPR. **JRCT is the single most connective funder; the new £50–100m JRF Emerging Futures programme (led by Sophia Parker) is the largest new pot in this space.**

## Tier 1: where engineering leverage is highest

These ten organisations get the deepest treatment because they are where a London software engineer's time most plausibly converts into impact.

### mySociety — the anchor of UK civic tech

The UK's flagship civic-tech charity runs TheyWorkForYou, WhatDoTheyKnow, FixMyStreet, WriteToThem, and — crucially for this brief — **WhoFundsThem**, the 2025 project annotating MPs' financial interests with donor context, second jobs, gifts, foreign trips and "highlighted" interests in oil/gas, gambling, and authoritarian-funded trips. Total group income £2.6m (2024/25), with growing commercial revenue from SocietyWorks (council contracts for FixMyStreet Pro) offsetting a 33% drop in restricted grants. Historic funders include Luminate, JRCT, Nesta, MacArthur, Google.org and Porticus.

**Engineering surface.** 403 public repos at github.com/mysociety. Stack is Python (Django) for new builds, Perl (Catalyst) for legacy FixMyStreet/TWFY backend, Ruby on Rails for Alaveteli (the FOI engine), PHP for the TWFY web app. Active issues, CONTRIBUTING.md files, Docker dev environments. `local-intelligence-hub` and `parlparse` are the most directly relevant for inequality-related civic data work. Datasets are openly published at data.mysociety.org including MapIt boundaries, MPs' financial interests, election donations, and climate scorecards.

**Hiring now.** A **Developer at SocietyWorks** role is open, £42–52k, fully remote, Python with willingness to learn Perl, deadline **31 May 2026** (mysociety.workable.com/jobs/5771726). This is the single best paid match in the ecosystem.

**People.** Louise Crow (CEO, ex-Head of Dev, long-time Alaveteli lead), **Alex Parsons (`ajparsons`)** — Senior Researcher and the data lead behind WhoFundsThem, Struan Donald (`struan`), Matthew Somerville, Myf Nixon. Bluesky: @mysociety.org.

**Entry routes.** Beyond the open job: pick a labelled issue on `theyworkforyou` or `local-intelligence-hub` and submit a PR; email **whofundsthem@mysociety.org** to join the volunteer cohort that scrutinises register-of-interests entries each round — direct economic-justice work, low commitment threshold.

### Common Wealth — most data-mature of the campaigning think tanks

Founded 2019 by Mathew Lawrence (ex-IPPR), Common Wealth ships genuinely interactive data products. **"Who Owns Britain?"** (September 2025) maps ownership of utilities and essentials; the Right to Buy market-value calculator (August 2025) and the Toxic Bonds database (Sophie Flinders) are sectoral leaders. The team includes Chris Hayes (Chief Economist, ex-OECD), Sophie Flinders, Eleanor Shearer (Oxford MPhil, "technology for public good"), Bella Smith (Digital Officer). The website was designed and built by Sophie Monk.

**The gap.** No public GitHub organisation. Dashboards appear built on Flourish/D3 by hand; nothing is open-source. They publicly say "we are not currently hiring." This is the strongest "build with them, not at them" target — propose extending the Who Owns Britain? data layer to additional sectors, automating Companies House/Land Registry scraping, opening an API, or modernising the visualisation stack. Mat Lawrence is active and approachable on X (**@DantonsHead**); pitch through info@common-wealth.org.

### Tax Justice Network — the most engineer-ready research org

TJN has what no other UK economic-justice campaign org has: an **active GitHub organisation** (github.com/Tax-Justice-Network) and a **named Senior Developer on staff** — Martin Kopeček (`SmallhillCZ`), based in Prague. Research Fellow **Alison Schultz** (`TackleTaxHavens`) publishes Stata replication code. They maintain the Financial Secrecy Index (v8.0, June 2025), Corporate Tax Haven Index, State of Tax Justice annual report, the Illicit Financial Flows Vulnerability Tracker, and the Tax Justice Policy Tracker. The "millionaire migration myth" report (November 2025) and the post-Trump "US 'R' Us or Tax Sovereignty?" piece are recent flagship outputs.

**Entry routes.** Their `swift_codes_scraper` repo has been untouched since 2022 — a modern Python rewrite would be an immediate, useful PR. The indices require annual data refreshes that are crying out for proper ETL pipelines (currently Stata-heavy and partly delivered through external visualisation partner Thibi). Contacts: Alex Cobham (@alexcobham, CEO, Oxford-based, very responsive on Twitter); Mark Bou Mansour (Head of Comms, @MarkBouMansour); Naomi Fowler (Creative Strategist / Taxcast producer, naomi@taxjustice.net). Pitch a small useful PR before asking for a chat.

### Equality Trust — highest "want a volunteer right now" signal

Six staff, £558k income (2024), founded by Kate Pickett and Richard Wilkinson. Funded by JRCT (core), Barrow Cadbury, Trust for London (£29,875 restricted London SED), Friends Provident, Health Foundation, plus individual donors. Their volunteer page says explicitly: *"as a very small charity we welcome support from people willing to offer their time and skills."* They already use pro-bono SaaS donations (Slack, Google for Non-Profits, Canva).

**The Obscene Wealth Simulator** is their flagship interactive tool — ripe for modernisation. They convene the Inequalities Alliance, Equal Pay Alliance and the #1forEquality SED (Socio-Economic Duty) campaign — none of which has a serious tracker tool. Co-Executive Directors **Jo Wittams** and **Priya Sahni-Nicholas**; the canonical pathway is emailing Jo Wittams via the volunteer page (equalitytrust.org.uk/volunteer-us). Quickest realistic win in the entire ecosystem.

### Democracy Club — small, modern, engineer-friendly

The only comprehensive UK candidate and polling-station database, run by an ~11-person CIC that became **financially independent of charitable grants in 2024**, sustained by Electoral Commission and Welsh Government contracts. Modern Python/Django stack (uv, Ruff, CircleCI, AWS). 117 open issues on `UK-Polling-Stations` and 227 on `yournextrepresentative`, several explicitly labelled "needs help." Slack is open: email **hello@democracyclub.org.uk** and ask Sym Roe (CTO, co-founder; @symroe.bsky.social) which issue to start on. Less directly tied to wealth/tax than mySociety, but the electoral data underpins economic-justice journalism — and the contributor pathway is the smoothest.

### CenTax — the wealth-tax research engine that needs engineers most

CenTax (Centre for the Analysis of Taxation, centax.org.uk) is a small joint Warwick/LSE outfit co-directed by **Arun Advani** (a.advani.1@warwick.ac.uk; arunadvani.com) and **Andy Summers** (@Summers_AD, LSE Law). They work directly with HMRC microdata and have produced the foundational technical research behind the 2024–25 non-dom abolition, the CGT changes, the IHT business/agricultural relief cap, and the partnership NICs reform — all of which appeared in Reeves's budgets. The "Tax Reforms for UK Growth" coalition report (November 2025) co-signed with IPPR, NEF, Adam Smith Institute, JRF, Bright Blue and Tax Policy Associates is the most striking cross-spectrum tax-reform document of the last decade.

**The gap.** CenTax publishes "Data for the charts" downloads alongside PDF reports, but code is not openly published. Their work would benefit enormously from a clean, public, reproducible tax-reform simulator — currently the closest open-source UK option is PolicyEngine UK (worth tracking separately). Pitch Summers (London-based) with a concrete distributional-analysis tool tied to a specific Budget moment.

### Tax Justice UK — the campaign org most likely to use a calculator

TJUK runs the visible "Tax our Wealth" campaign with PMUK. Faiza Shaheen took over as Executive Director in July 2025. Funders: JRCT (£90k 2021–24, +£33k 2024–25), Luminate ($110k 2022), Thirty Percy (£400k core, 2024–28), Gower Street, Funding for Social Change. No technologists on staff. Their supporter base has grown 16k → 54k, almost certainly outgrowing their current low-code tooling. Visible gaps: a **wealth tax revenue calculator** (currently just a "£460m a week" stat), an MP scorecard on tax votes, a constituency-level revenue map, a polling data viz. Outreach via Faiza Shaheen (@faizashaheen) or Jake Atkinson (Campaigns & Movement Manager). Best pitch: a concrete deliverable tied to the Autumn Budget 2026 moment.

### Patriotic Millionaires UK — high media moments, no tech team

Network of ~80 wealthy UK individuals (Gary Stevenson, Stephen Kinsella, Dale Vince, Brian Eno, Julia Davies). Coordinates closely with TJUK. No technologists. **Suzanne Bold** (Head of Advocacy; ex-YouGov, ex-House of Commons) and **Lindsay Storie** (Head of Community) are the relevant contacts. The site is editorial; an interactive "what could £X wealth tax fund in your constituency?" microsite tied to Davos 2027 or Autumn Budget 2026 would land. Member contributions plus likely philanthropic backing; not a registered charity, so funding isn't itemised publicly.

### Oxfam GB inequality team — Davos pipeline is in spreadsheets

The annual Davos report ("Takers Not Makers" 2025; "Inequality Inc." 2024) is built largely in Excel by ~3–6 economists each January, drawing on Forbes Real-Time Billionaires, UBS Global Wealth, World Bank PIP, WID, and academic sources. **No public code repository** exists for the analysis. Methodology PDFs are published but not reproducible. **Max Lawson** (Head of Inequality Policy, max.lawson@oxfam.org, @maxlawsontin) is famously responsive — pitch a reproducible-data pipeline (R/Python/Quarto) or an interactive billionaire-wealth dashboard for Davos 2027. Anna Marriott (UK lead), Susana Ruiz (tax policy lead), Quentin Parrinello (tax adviser, also at EU Tax Observatory) round out the team.

### INET Oxford Complexity Economics — the academic anchor

Doyne Farmer's Complexity Economics programme at INET Oxford (Oxford Martin School) is the only UK academic centre with a serious public GitHub presence (github.com/INET-Complexity, github.com/ox-inet-resilience), a real culture of open agent-based modelling, and active collaboration with non-economists (physicists, CS, mathematicians). Active repos include `housing-model` (UK housing ABM with the Bank of England), `firesale_stresstest`, the Economic Simulation Library, and `sbi4abm` (Bayesian inference for ABMs). Current major project: macroeconomic ABM for the UK's Seventh Carbon Budget in partnership with **DESNZ**, including distributional impacts of decarbonisation — exactly the climate/wealth intersection the user cares about. Approach **Pete Barbrook-Johnson**, **Joel Dyer** or **Arnau Quera-Bofarull** with a PR or tooling proposal.

## Tier 2: solid moderate-depth coverage of the rest

**38 Degrees** has a real in-house tech team and a bespoke "Campaigns by You" petition/email/MP-targeting platform — but no public GitHub and no formal volunteer engineering programme. ~2m supporter list, 95.7% small-donor funded. CEO Matthew McGregor; Campaigns Director Robin Priestley. Best route is monitoring home.38degrees.org.uk/careers and emailing emailtheteam@38degrees.org.uk with scoped contributions.

**Positive Money** is research-led with no engineers. £951k income (2024–25), 93% from trusts/foundations: European Climate Foundation, Friends Provident, JRCT, Partners for a New Economy, Paul Hamlyn, Polden Puckham. **Paul Delaney** (Co-ED UK), **Vicky Van Eyck** (ED Europe), **Simon Youel** (Head of Policy, press contact). Tech-readiness low; data-viz on BoE collateral framework / fossil-fuel finance is the natural pitch.

**New Economics Foundation (NEF)** — UK's oldest progressive economics think tank (founded 1986), ~43 staff in London, ~£3m+ from Oak Foundation, National Lottery Community Fund, European Climate Foundation, Lloyds Bank Foundation, Friends Provident, JRF, OSF, plus many others (A-grade transparency). New CEO **Danny Sriskandarajah** (joined January 2025 from Oxfam GB); former CEO **Miatta Fahnbulleh** is now Labour MP for Peckham and a junior minister. No tech team. Talent flows are interesting: former Chief Economist **Alfie Stirling** moved IPPR → NEF → JRF (now Chief Economist at JRF). Realistic engagement is via researcher collaborations on specific modelling work, not volunteer engineering.

**Rethinking Economics** is a student-led international network (Charity 1158972) with ~10 paid staff; the rest is volunteer. **Most welcoming volunteer culture in the ecosystem** — *"writing a blog, recording a podcast, hosting an event… or anything else"*. Director Laurence Jones-Williams; Associate Director **Janet Gunter** is the warmest first contact (she co-founded The Restart Project, so already pro-tech-volunteer). Concrete needs: a directory tool for 120+ local groups; improvements to the Rethinking Econ 101 platform; a curriculum-Health-Check survey tool. Email info@rethinkeconomics.org.

**Resolution Foundation** sits inside Treasury's orbit — alumni Bell and Tomlinson are now Treasury ministers. CEO **Ruth Curtice** (joined November 2024, ex-HMT Director of Fiscal Policy). Key wealth/inequality contacts: James Smith (Chief Economist), Simon Pittaway (wealth inequality, joined Feb 2023), Adam Corlett (tax/welfare), Nye Cominetti (labour market). Funding: Resolution Trust (Sir Clive Cowdery's family vehicle), Nuffield, JRF, FSB, Trust for London, ESRC. No dedicated data-science team — researchers use Stata/R, website built by Wholegrain Digital. The **Economy 2030 Inquiry** (joint with LSE CEP, £1.8m Nuffield grant) ended Dec 2023; the new **Resolution Ventures WorkerTech Fund** (£6.7m at first close, 2025) is the most engineer-relevant programme. Roles advertised via BeApplied; paid Research Associate is the realistic non-economist entry.

**IPPR** is the centre-left heavyweight, especially close to the current Labour government. Executive Director **Harry Quilter-Pinner** (permanent from January 2025, @harry_qp); previous ED **Carys Roberts** is now in the No. 10 Policy Unit. The **IPPR Centre for Economic Justice** is led by **Dr George Dibb** (@GeorgeDibb), currently on secondment to DESNZ until May 2026; in his absence Carsten Jung (Senior Economist, AI/macro), Henry Parkes, Shreya Nanda and Pranesh Narayanan carry the brief. Recent CEJ outputs: "A Wealth of Difference" (non-dom), "Pulling Down the Ladder" (Proportional Property Tax). No public GitHub. Funders include JRF, JRCT, Trust for London, Lankelly Chase, Open Society, European Climate Foundation.

**Institute for Fiscal Studies (IFS)** is research-only, explicitly not advocacy. **Helen Miller** became Director in July 2025 (succeeding Paul Johnson); she has publicly argued for a one-off wealth tax, CGT/dividend alignment with income tax, and taxing the wealthy more. The flagship **TAXBEN** microsimulation (running since 1983) is **not open source** — a striking contrast with the US Tax-Calculator (PSLmodels/Tax-Calculator on GitHub). The Deaton Review of Inequalities culminated in the 2025 book *Challenging Inequalities*. Funding: ESRC core + Nuffield (huge) + FCDO TaxDev + government departments. ~£15m income. No engineer roles — they hire economists who happen to use Stata/R/Python. Tom Waters maintains TAXBEN; Arun Advani is a key associate fellow on wealth taxation.

**Demos** is the most engineer-friendly UK think tank in capability terms, thanks to **CASM** (Centre for the Analysis of Social Media, joint with Sussex's TAG Laboratory) and Method52 (NLP platform). CEO **Polly Curtis** (ex-Guardian, HuffPost, Tortoise). Hannah Perry leads Demos Digital. Merged with Engage Britain (2023, Hands Family Trust). The only UK think tank actively using Pol.is for citizen deliberation. Less wealth-focused than the others, but the digital/data culture is genuinely different.

**Fabian Society** is the Labour-affiliated membership think tank (~7,000 members, 24 local societies, Young Fabians under-31s). General Secretary **Joe Dromey** (from January 2025). Tech footprint negligible. Most accessible entry to Labour-aligned policy networks; not a meaningful engineering target.

**Progressive Economy Forum (PEF)** is a council network of heterodox economists rather than a staff org — Patrick Allen (Chair), Ann Pettifor, James Meadway, Robert Skidelsky, Stephany Griffith-Jones, Josh Ryan-Collins, Danny Dorling, Kate Pickett, Daniela Gabor, Faiza Shaheen, Howard Reed. Council members run their own modelling projects; this is the closest thing the UK has to an open heterodox-economics laboratory. Pitch via individual council members (Howard Reed in particular does open-style modelling on minimum wage and distributional policy).

**LSE International Inequalities Institute** is the prestige UK home for inequality research; cross-disciplinary, hosts AFSEE (Atlantic Fellows for Social and Economic Equity, funded by $64m from Atlantic Philanthropies; 2026–27 applications closed January 2026). Director Francisco Ferreira; key contacts include **Mike Savage** (wealth, elites), **Aaron Reeves** (the most engineer-compatible — has an active personal GitHub at asreeves.github.io; co-author with Sam Friedman of *Born to Rule*, 2024), **Sam Friedman**, **Xavier Jaravel**, **Facundo Alvaredo** (WID co-maintainer). The **Stone Centre at STICERD** ($5m Stone Foundation gift, 2024) is the new wealth-focused unit. Most welcoming touchpoint: the **fortnightly Inequalities Seminar Series** on Tuesdays during term.

**Oxford Inequality & Prosperity Programme** no longer exists as a standalone unit; it folded into INET Oxford's **Economics, Inequality & Opportunity programme**, now led by **Zachary Parolin** (since October 2025) after Brian Nolan's retirement.

**Warwick CAGE** won £7.1m ESRC funding in November 2024 for the 2025–29 phase (CAGE III). Director **Mirko Draca**; Research Director Bishnupriya Gupta; **Impact Director Arun Advani** (the cross-institutional node linking CAGE, LSE CenTax and IFS). **Tom Crossley** (ex-IFS) is at Warwick on consumption/savings/microsimulation. The annual CAGE Summer School (July) is undergraduate-focused but teaches data-science skills (OCR, GIS, LLMs for economic data). Coventry-based, less ideal for a Londoner.

**UCL IIPP** is Mariana Mazzucato's centre. CBE in 2025; *The Common Good Economy* out June 2026; appointed Whitechapel Gallery's first Economist-in-Residence (2026–2029); launched the Global Council for a Common Good Economy with the Spanish DPM (April 2026). Deputy Directors **Rainer Kattel** and **David Eaves** (digital state capacity — the natural home for a technologist). Funders: Laudes Foundation, Rockefeller, Hewlett, Baillie Gifford. No real GitHub presence; the most policy/practitioner-oriented of the four centres, least technical. Engagement via **MOIN** (Mission-Oriented Innovation Network, ~85 public-sector member agencies) requires your employer to join, not you as an individual. Annual **UCL IIPP Forum 16–17 June 2026 in London** is open and free.

**Full Fact** has a stable engineering team (51–100 staff), recent hires Adam Garscadden (frontend, January 2025) and Nina Menezes (web, July 2025). Head of AI **Andrew Dudfield** (ex-ONS) is the technical lead. Main AI factchecking engine is commercial/closed; public GitHub (github.com/FullFact) has 31 mostly utility repos. Less direct economic-justice fit than mySociety, but stable engineering culture and occasional hiring. Funders: Nuffield, JRCT, Google AI, Meta (third-party factcheck programme), ~2,000 monthly individual donors.

**Open Data Institute (ODI)** is membership-and-consultancy-based; **be careful of the name collision** with ODI Global (the Overseas Development Institute, also London). 438 active repos at github.com/theodi including `csvlint.rb` (canonical CSV validator), `octopub`, the new `ndl-core-data-pipeline` for the National Data Library, and `solid-mcp` (Tim Berners-Lee's Solid + MCP, January 2026). Not a volunteer-friendly organisation; better as a credentialing/training route. The spinoff **Connected by Data** (Jeni Tennison) is more civil-society-power-focused.

**DataKind UK** matches volunteer data scientists with charities via DataDive weekends, DataCorps (multi-month) and Light Touch Support. Past projects with JRF, Global Witness (corporate corruption), Citizens Advice, Trussell Trust, St Mungo's — strong inequality fit. **But volunteer applications are currently paused** due to capacity constraints — sign up to the newsletter at datakind.org.uk/volunteer for when they reopen. CEO **Kye Smith**; previous CEO **Giselle Cory** is now at JRF (useful link).

**Joseph Rowntree Foundation (JRF)** is more interesting as a funder than as an employer. **Sophia Parker** leads the **Emerging Futures** programme — £50–100m of additional unrestricted grants over 5–10 years from 2025, including a strand on "hidden wiring (governance & tax regimes)" and one on "wealth, power & funding systems." **Lightning Reach** (a financial-support portal) is JRF's exemplar social-investment exit (£100k equity, 2023). JRF and the **Joseph Rowntree Charitable Trust** (JRCT) are separate organisations — JRCT is the political campaigning grant-maker, JRF is the operational charity. Alfie Stirling is Chief Economist at JRF since 2024.

## Public voices and where they intersect

**Gary Stevenson (@garyseconomics)** runs the largest popular wealth-inequality channel in the UK — ~1.4m YouTube subscribers, wealtheconomics.org as the content hub, Patreon as the funding/community channel. He has explicitly stated he wants to build political lobbying infrastructure and has been approached by the Labour Growth Group. **Concrete tech needs are real**: data viz on UK wealth distribution, scraping HMRC/ONS releases, modelling 2% wealth-tax scenarios, web infrastructure. No formal volunteer programme — Patreon is the entry channel. Active member of Patriotic Millionaires UK and Millionaires for Humanity.

**Grace Blakeley (@graceblakeley)** — Tribune staff writer, podcast *A World to Win*, 2024 book *Vulture Capitalism*. Patreon supports the podcast. Speaks regularly at Compass/PEF/Green New Deal Rising/The World Transformed events.

**Mariana Mazzucato (@MazzucatoM)** — see UCL IIPP above. Institutional engagement only.

**Danny Dorling** — Halford Mackinder Prof of Geography, Oxford; *Shattered Nation* (2023), *Seven Children* (2024), *Peak Injustice* (2024), *The Next Crisis* (Verso, 2025). All work open-access at dannydorling.org. Council member, Progressive Economy Forum. Co-founded **Worldmapper.org** (2006) which continues to take technical contributors.

**Kate Pickett (@ProfKEPickett) & Richard Wilkinson (@ProfRGWilkinson)** — founders of Equality Trust; *The Spirit Level at 15* (2024 update introduced two new indices). Pickett's *The Good Society* — Bodley Head, 5 February 2026. Engagement via Equality Trust's local-group affiliate model.

**Ann Pettifor (@AnnPettifor)** — Director of PRIME, Council member of PEF, NEF fellow; led Jubilee 2000; co-author of the original 2008 Green New Deal. PEF–Compass Conference 30 May 2026.

**Brett Christophers** — Uppsala academic; *Our Lives in Their Portfolios* (2023), *The Price Is Wrong* (Verso, 2024, ongoing tour). Less active on social media; writes for the NYRB. His asset-manager-capitalism work is highly relevant for engineers who can scrape and structure private-equity / BlackRock / Brookfield / KKR holdings data.

## Political map: who is moving on wealth tax

The Labour government under Starmer/Reeves has stopped short of a wealth tax but has implemented a striking number of adjacent reforms in the November 2025 Budget. The Treasury-side cast as of May 2026:

**Treasury ministers:** Rachel Reeves (Chancellor); James Murray (Chief Secretary, promoted September 2025, attends Cabinet); Dan Tomlinson (Exchequer Secretary, ex-Resolution Foundation); **Torsten Bell** (Parliamentary Secretary to HMT, ex-Resolution Foundation CEO — widely reported as a key architect of the Autumn 2025 Budget); Spencer Livermore (Financial Secretary, Lords); Emma Reynolds (Economic Secretary). Darren Jones moved from Chief Secretary to the Treasury to Chief Secretary to the PM/CDL in September 2025.

**Backbench wealth-tax coalition.** Richard Burgon leads the formal parliamentary push — EDM 64124 (July 2025) and EDM 64316 (October 2025, 51+ signatures by November 2025), plus the 80,000-signature petition delivered to No. 10. The core cohort: Jon Trickett, John McDonnell, Diane Abbott, Zarah Sultana, Clive Lewis, Nadia Whittome, Andy McDonald, Rachael Maskell, Bell Ribeiro-Addy, Ian Lavery, Kim Johnson, Ian Byrne, Kate Osborne, Imran Hussain, Grahame Morris, Rebecca Long Bailey, Apsana Begum, Cat Smith, Brian Leishman, plus Plaid Cymru (Ann Davies, Ben Lake, Liz Saville Roberts, Llinos Medi) and Green (Carla Denyer). Stella Creasy votes consistently against welfare cuts and has a long record on financial regulation.

**Lords.** **Lord (Prem) Sikka** is the most prolific wealth-tax voice in the Lords — Labour peer, emeritus professor of accounting, co-founded Tax Justice Network, regular contributor at Left Foot Forward, detailed budget critiques November 2025 and March 2026. **Baroness Margaret Hodge** is UK Anti-Corruption Champion (appointed December 2024). **Baroness Natalie Bennett** (Green) speaks frequently. **Lord Neil Kinnock** publicly backed a 2% wealth tax on >£10m assets in July 2025.

**Relevant APPGs.** APPG on Inclusive Growth (chair: **Liam Byrne MP**, also Business & Trade Select Committee Chair; research partner Centre for Progressive Policy). APPG on Anti-Corruption & Responsible Tax (chair: **Phil Brickell MP**, ex-NatWest/Barclays anti-bribery; secretariat now Foreign Policy Centre; funded by Joffe Trust and Montpelier Foundation). APPG on Poverty and Inequality (re-formed November 2024, JRF historically provides secretariat). There is no standalone APPG on Wealth Inequality.

## Policy calendar — where engineering work has most impact

| Window | Event | Why it matters for tools |
|---|---|---|
| Now (live) | HVCTS reliefs/exemptions consultation | New surcharge on >£2m properties from April 2028 — distributional modelling on Land Registry data needed |
| Summer 2026 | HMRC consultations on direct-tax "recklessness" criminal offence, information-gathering powers, uncertain tax treatment, close-company reporting, ISA reform | Live technical submissions windows |
| Summer 2026 | OBR Fiscal Risks & Sustainability Report | Sets framing for autumn |
| June 2026 | UCL IIPP Forum (16–17 June, London); Mazzucato's *The Common Good Economy* UK release | Agenda-setting moment |
| Autumn 2026 | **Autumn Budget 2026 (Reeves)** | Main fiscal event — wealth tax pressure expected to intensify; HVCTS implementation; further IHT reform speculation |
| April 2027 | New property-income / savings tax rates take effect | Distributional analysis opportunity |
| Late 2027 | Spending Review 2027 | Second multi-year envelope |
| April 2028 | HVCTS goes live | Major property-data implementation moment |

The single most valuable artefact a London engineer could ship for the Autumn Budget 2026 window: an open, reproducible, distributional **wealth-tax/property-tax/CGT scenario simulator** using HMRC SPI + WAS + Land Registry data, with a constituency-level revenue map. TJUK, PMUK, Equality Trust, NEF and Oxfam would all use it; CenTax and Resolution Foundation researchers would validate it; mySociety would surface it through TheyWorkForYou.

## International peers and what to copy

**ProPublica** (github.com/propublica) is the gold standard — the Nonprofit Explorer turned IRS Form 990 data into an API the IRS doesn't offer. UK parallel: wrap Companies House + Charity Commission + Land Registry into a properly queryable Charity/Corporate Explorer with a UBO graph. **World Inequality Lab** (github.com/WIDworld) maintains `wid-world` (pipeline), `wid-r-tool`, `wid-stata-tool`, `wid-bulk-downloader`, and crucially **`gpinter`** (generalised Pareto interpolation) — directly applicable to reconstructing fine-grained UK distributions from HMRC's coarse public tables. **EPI's State of Working America Data Library** is a replicable template for a "State of Working Britain" combining ASHE, HMRC Personal Incomes Table 3.1a, and FRS. **Inequality.org / IPS** shows the power of consistent editorial framing — the UK equivalent (Equality Trust) is tech-light by comparison and has obvious room to grow. **Oxfam's Davos pipeline** is in spreadsheets — exactly the gap a UK engineer could close. Adjacent tools worth knowing: **OpenCorporates** (220m+ companies, free for journalists/NGOs as Permitted Users), **OCCRP Aleph** (400m+ entities including leaks), **Open Ownership** (BODS data standard), and **ICIJ's Offshore Leaks Database**.

## UK public datasets worth building on

The richest underused data for economic-justice tools:

**Companies House** — free REST + Streaming API, daily bulk CSV/JSON, daily PSC snapshots. The single most valuable UK dataset for UBO and corporate transparency work. **HM Land Registry Price Paid Data** — free, monthly, full UK transactions since 1995. **Overseas Entities Register** — open bulk download. **Electoral Commission donations & loans** — free CSV, quarterly party + monthly individual, data from July 2017. **HMRC Survey of Personal Incomes** — published tables plus anonymised PUT microdata via UK Data Archive (2-year lag). **ONS Wealth & Assets Survey** — biennial, Round 8 (2020–22) **but accreditation suspended June 2025 by OSR** due to response-rate quality issues; flag this in any tool built on it. **HMRC personal wealth/"identified wealth" stats** cover only ~30% of UK adults — *cannot* be used to estimate total UK personal wealth on their own; pair with WAS or WID. **TheyWorkForYou API** (£20/month commercial, free for charity/non-profit; ParlParse XML covering Hansard from 1918). **UK Parliament Members API** — for cross-referencing Register of Members' Interests with Companies House officers. **Stat-Xplore (DWP)** — live OAuth API with benefit caseloads by LSOA/MSOA. **OBR forecast XLSX** — twice yearly, full models for fiscal-impact simulators. **Cabinet Office transparency data** — ministers' meetings/hospitality, quarterly. **Contracts Finder + Find a Tender** — OCDS-format JSON for public procurement.

The composite tool that would change the most conversations: a graph linking Electoral Commission donations → Companies House officers/PSCs → Land Registry overseas entities → ministers' meetings logs. That is exactly the kind of thing **JRRT's Larger Grants** programme exists to fund.

## Fellowships, grants and programmes worth applying to

**Don't waste cycles on.** PIT-UK as a formal fellowship body does not exist — PIT-UN is US-only, run out of New America. ODI fellowships are largely unpaid. Brookings/EPI have no UK programmes. Ada Lovelace doesn't run an external fellowship. There is no "Code for Britain" — mySociety is the de facto equivalent.

**Do apply to.**

**Joseph Rowntree Reform Trust (JRRT) Larger Grants** are the single best fit for an engineer building wealth/political-money transparency tools. **Non-charitable funder** — funds the explicitly political/campaign work that charities can't. Priorities directly aligned: "tighten rules around political giving and improve transparency on how money is given and spent in politics", scrutiny of lobbying, electoral integrity. £10k–£300k. 2026 deadlines: final apps 10am Mon 18 May 2026; outline proposals 24 August 2026 → final 1 September → decisions 2 October; outline proposals 2 November → final 9 November → decisions 11 December. The September round is the realistic target.

**Software Sustainability Institute (SSI) Fellowships.** £4k flexible budget over 15 months for community-building activities; ~20 fellows + up to 3 international. Applications for the 2027 cohort open August 2026, close ~6 October 2026. Strong network in UK research software engineering.

**Mozilla Foundation Fellowships.** Two tracks: Embedded (~$100k with host org) and Independent ($125k). 12-month. Next cycle opens early 2027. Themes include data democratisation, AI accountability, climate justice.

**JRF Emerging Futures / Social Investment Pilot.** Invitation-only, but Sophia Parker is the named contact for "wealth, power and funding systems." JRF have previously funded Open Innovations to build the "Poverty in the North" data hub — that pattern (delivery partner + funded by JRF) is realistic for a London engineer once you have a built artefact to point to.

**Trust for London** — £10.2m grants 2025, max ~£150k, 1–3 years, funds organisations not individuals; book a call with a grants manager before EOI. **City Bridge Foundation** — £100m+ p.a., the largest London funder. **Esmée Fairbairn** — *A Fairer Future* aim relevant; 62% of 2025 grants went to organisations new to Esmée; ~5% of EOIs awarded.

**UKRI Future Leaders Fellowship Round 11** (2026 cycle): EOI ~10 February 2026, funder deadline 16 June 2026 — host-institution-sponsored, 4+3 years, all-discipline including cross-sector.

**Bellingcat Tech Fellowship** — small (~€1,000/month, 3 months, remote) but tool must be open source on Bellingcat's GitHub. Apply tech@bellingcat.com.

**European AI Fund** and **Civitates** (Mercator/OSF/Luminate pooled funds) — UK NGOs eligible for digital democracy and disinformation work.

**Newspeak House** in Bethnal Green — the closest London community to a tech-and-politics fellowship.

**Alan Turing Institute Open Source AI Fellowship** ran for 2026 with applications closed August 2025 — worth tracking 2027 cycle (up to £85k salary, 12 months, embedded in DSIT's i.AI).

## Tiered recommendations — where to invest first

**Do this week.** Apply to the **mySociety SocietyWorks Developer** role by 31 May 2026 if a paid role is plausible. In parallel, email **whofundsthem@mysociety.org** for the volunteer cohort, and **Jo Wittams at Equality Trust** offering scoped skills. Subscribe to JRF Emerging Futures, DataKind UK, and Resolution Foundation newsletters. Join the Democracy Club Slack via hello@democracyclub.org.uk. Subscribe to Gary Stevenson's Patreon to track community needs.

**Do this month.** Pick **one substantive artefact** and start it publicly on GitHub — the best candidate is the wealth-tax revenue calculator (HMRC SPI Table 3.1a + WAS Round 8 + WID + `gpinter` for distributional reconstruction) tied to the Autumn Budget 2026 moment. Publish as open source from day one. Open a small useful PR on TJN's `swift_codes_scraper` (or replace it with a maintained equivalent); open a PR on mySociety's `local-intelligence-hub`; engage one issue on Democracy Club's `UK-Polling-Stations`. Attend the LSE III Inequalities Seminar Series (Tuesdays) and CenTax events.

**Do this quarter.** Email Mat Lawrence (Common Wealth) and Max Lawson (Oxfam) with a specific proposal anchored to your built artefact. Pitch Andy Summers (CenTax) on extending the calculator with HMRC microdata. Attend UCL IIPP Forum 16–17 June 2026. Apply to JRRT Larger Grants — September 2026 round (outline by 24 August). Start preparing an SSI Fellowship application for the October 2026 deadline.

**Build a six-month thesis.** Pick **one** of three positioning strategies:

1. **The transparency engineer** — wealth/power graph linking donations, PSCs, Land Registry, ministers' meetings. Funded by JRRT. Anchored at mySociety. Allies: Tax Justice Network, Tax Justice UK, Patriotic Millionaires UK.

2. **The distribution engineer** — open reproducible wealth-and-tax-reform simulator. Funded by SSI + JRF Emerging Futures. Anchored at CenTax or Common Wealth. Allies: Resolution Foundation, IFS researchers, Equality Trust.

3. **The narrative engineer** — high-quality interactive data products supporting popular voices. Funded by Mozilla Fellowship (Independent track). Anchored with Gary Stevenson's "Gary's Economics" infrastructure or Oxfam's Davos pipeline. Allies: Patriotic Millionaires UK, Tax Justice UK, Grace Blakeley's *A World to Win*.

## What's actually new

Three things have shifted in 2024–26 that should change how a UK engineer approaches this space.

First, **the policy window is open in a way it wasn't in 2020**. Reeves's Budgets have implemented half the wealth-tax-adjacent agenda (non-dom abolition, CGT alignment moves, IHT relief caps, HVCTS) and the Labour rebellion plus Patriotic Millionaires plus Stevenson have made the politics easier, not harder. Tools shipped before the Autumn Budget 2026 will land.

Second, **the funder landscape has expanded sharply**. JRF's £50–100m Emerging Futures programme, the Stone Centre at LSE STICERD ($5m), CenTax's growing footprint, the Resolution Foundation alumni now inside Treasury — there is more money and more academic capacity targeted at this space than at any point since the Wealth Tax Commission in 2020.

Third, **the engineering gap is now the binding constraint, not the funding gap or the policy gap**. Almost every organisation in this report has clear visible tech needs and no in-house engineering capacity. Tax Justice UK has 54k supporters but no calculator. Common Wealth ships interactive dashboards but has no public GitHub. Oxfam's Davos pipeline is in spreadsheets. CenTax's data are publishable but unpublished. The single best move a London software engineer can make is to publish one excellent open-source artefact on top of HMRC/Companies House/Electoral Commission data and let the rest of the ecosystem find them. They will.
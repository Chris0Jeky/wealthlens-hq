# WealthLens UK — Founding Document

## Table of Contents

1. Mission & Messaging Framework
2. The Public Announcement — What to Post and Where
3. Volunteer Roles & Task Board
4. Infrastructure Checklist
5. Public-Facing Website — Structure & Copy
6. The "Why This Matters to You Personally" Messaging Playbook
7. Donation & Funding Strategy
8. Contributor Recognition & Community
9. Social Media Accounts & Content Ops
10. Legal & Practical Considerations
11. Week 1 Execution Plan

---

## 1. Mission & Messaging Framework

### The Mission (one sentence)
WealthLens UK makes the data behind wealth inequality visible, interactive, and impossible to ignore — so that everyone can see the system clearly and push for change.

### The Longer Version (for website, about pages, grant applications)
The UK has some of the best data on wealth inequality in the world. The ONS Wealth and Assets Survey, HMRC tax statistics, and the World Inequality Database contain detailed evidence of how wealth has concentrated over decades. But almost nobody can see it. The data is buried in spreadsheets, locked in PDFs, and written for experts.

WealthLens UK is an open-source project that turns this data into interactive, shareable, beautifully designed tools that anyone can understand — a student in Ilford, a nurse in Manchester, a first-time voter in Cardiff. We believe that when people can see the data, they make better decisions, ask harder questions, and demand fairer systems.

We are not a political party or a campaign. We are a data transparency project. We let the numbers speak.

### Core Principles
- **Open source, always.** All code, data pipelines, and methodologies are public on GitHub.
- **Data first, opinion second.** We present verified public data with sources. Our visualisations are designed to inform, not manipulate.
- **Accessible by default.** Every tool works on mobile, meets WCAG accessibility standards, and uses plain language.
- **Independent.** We are not affiliated with any political party. We collaborate with research organisations, charities, and campaigners across the spectrum who share our commitment to data transparency.

### The Messaging That Reframes Inequality as Personal

This is critical. Most people tune out when they hear "wealth inequality" because it sounds abstract and political. Your messaging needs to make it personal. Here are the reframes:

**"People ask how to get rich. The answer starts with understanding why it's gotten harder."**
Most people's financial frustration (can't buy a house, wages don't stretch, savings earn nothing) has structural causes. WealthLens makes those causes visible.

**"You can't fix what you can't see."**
The data exists. It's just hidden in government spreadsheets. We're making it visible.

**"This isn't left vs right. This is seeing the numbers clearly."**
Wealth concentration is a measurable phenomenon, not an opinion. Our tools don't tell you what to think — they show you what's happening.

**"Inequality doesn't just hurt the poor. It slows down everyone."**
When spending power concentrates at the top, demand falls, businesses struggle, and the economy stagnates. This is Gary Stevenson's core argument, backed by Piketty, Mian & Sufi, and IMF research.

**"The biggest factor standing between you and your goals isn't effort — it's the system you're operating in."**
People work harder than ever and feel like they're falling behind. That's not a personal failure. It's a structural shift. The data shows it clearly.

---

## 2. The Public Announcement — What to Post and Where

### LinkedIn Post (your personal account)

Post this as text only (no external links in the body — put links in first comment):

---

I've spent my career building software systems — trading platforms, developer tools, enterprise infrastructure.

Today I'm starting something different.

I'm building WealthLens UK — an open-source project that makes wealth inequality data visible to everyone. The UK has incredible data on how wealth has concentrated over the past 30 years. But it's buried in government spreadsheets that nobody reads.

I'm turning it into interactive, shareable tools that anyone can understand.

Why? Because I grew up in a family that couldn't afford things other families took for granted. I now work in widening participation, helping young people from underrepresented backgrounds access higher education. And I've spent enough time inside financial systems to understand how they concentrate wealth at the top.

The data exists. The problem is visibility. That's an engineering problem. And I'm an engineer.

This is bigger than one person. If you want to help, there's always something to do:

→ Software engineers (Python, TypeScript, Vue, data viz)
→ Data analysts and researchers
→ Designers and UX people
→ Content creators and social media
→ Writers and editors
→ Strategists and organisers
→ People who can connect us with relevant organisations
→ Anyone who cares and has a skill to offer

No commitment required. Even a few hours matters.

Drop a comment or DM me if you want in. More details coming soon.

---

### Instagram Post

Use a clean, bold graphic (white text on dark background, or a striking data chart from your first prototype) with the caption:

---

I'm building something.

WealthLens UK — an open-source project making wealth inequality data visible to everyone.

The UK has some of the best inequality data in the world. Almost nobody can see it because it's trapped in government spreadsheets.

I'm an engineer. I'm fixing that.

If you want to help — any skill, any amount of time — DM me or comment below. Software, design, content, strategy, connections, anything. Let's go.

Link in bio.

---

### Twitter/X Thread (pin this)

Tweet 1:
I'm starting something. 🧵

WealthLens UK — an open-source project making UK wealth inequality data visible, interactive, and impossible to ignore.

The data exists. It's just buried. I'm an engineer. I'm digging it out.

Tweet 2:
The ONS publishes incredible data on wealth distribution. HMRC publishes capital gains and inheritance stats. The World Inequality Database has decades of UK data.

Almost nobody can access any of it unless they're an economist.

That's a design problem. And it has an engineering solution.

Tweet 3:
I grew up without privilege. I now work in widening participation, helping underrepresented kids access university. I've also built trading systems.

I've seen both sides. The system is visible if you know where to look. I want to make it visible to everyone.

Tweet 4:
This is open source. Everything on GitHub. No political affiliation. Just data, presented clearly.

If you want to help — engineering, design, data, content, strategy, connections — reply or DM me.

Every contribution matters. Every hour counts.

[GitHub link]

Tweet 5:
Following and supporting the work of @garyseconomics @TaxJusticeUK @PatMillsUK @TheEqualityTrst @reabornes

If you work at any of these organisations and want to collaborate, my DMs are open.

Let's make the data impossible to ignore. 📊

---

## 3. Volunteer Roles & Task Board

### Roles People Can Fill

Create a simple public task board (GitHub Projects, Notion, or Trello — I recommend GitHub Projects since the code is there too). Organise by role:

**Engineering**
- Data pipeline: scripts to pull, clean, and update ONS/HMRC/WID data
- Backend API: FastAPI endpoints serving processed data as JSON
- Frontend: Vue 3 components for interactive charts (D3.js, ECharts, or Recharts)
- Infrastructure: Docker, CI/CD, deployment (Railway, Vercel, or Cloudflare Pages)
- Testing: unit tests, integration tests, accessibility testing
- Mobile responsiveness and performance optimisation

**Data & Research**
- Identify and catalogue all relevant public datasets
- Write data dictionaries and methodology notes
- Fact-check all visualisations against primary sources
- Research what statistics campaigners cite most frequently
- Monitor ONS/HMRC release calendars for new data

**Design & UX**
- Design system: colours, typography, chart styles, responsive layouts
- Individual chart designs that work on mobile and social media
- Social media card templates (for sharing charts as images)
- Logo and basic brand identity
- Accessibility audit

**Content & Communications**
- Write plain-language explanations for each visualisation
- Draft social media posts for each new chart/tool release
- Write blog posts explaining methodology and findings
- Newsletter (monthly or fortnightly)
- Community management (responding to comments, DMs, issues)

**Strategy & Partnerships**
- Research potential partner organisations
- Draft outreach emails to think tanks and charities
- Identify speaking opportunities and events
- Grant research and funding applications
- Legal advice (charity structure, data licensing)

**Anyone**
- Share content on social media
- Provide feedback on visualisations (is this clear? what's confusing?)
- Suggest data stories or visualisations you'd want to see
- Translate content for non-English-speaking communities
- Tell friends

### How to Manage Volunteers (Keep It Simple)

Do NOT build complex infrastructure before you have people. Start with:

1. A GitHub repo with a clear CONTRIBUTING.md
2. A Discord server or WhatsApp group (Discord is better for project organisation)
3. A pinned "Start Here" message in the Discord with: mission, current priorities, how to pick up a task
4. Weekly 30-minute standup (optional, async-friendly) — post a brief update in Discord every Monday

Graduate to more formal tools only when you have 5+ active contributors.

---

## 4. Infrastructure Checklist

### Immediate (Day 1-7)

- [ ] GitHub repo: github.com/Chris0Jeky/wealthlens-uk (or a new GitHub org: github.com/WealthLensUK)
- [ ] README with: mission statement, screenshot of prototype, "How to contribute", tech stack, license (MIT or AGPL-3.0)
- [ ] CONTRIBUTING.md with setup instructions and task list
- [ ] Discord server with channels: #general, #engineering, #data-research, #design, #content, #introductions
- [ ] Linktree updated with all links
- [ ] Twitter/X account (personal, not project — build personal brand first)
- [ ] Bluesky account

### Short Term (Week 2-4)

- [ ] Simple landing page: one-page site explaining the mission with "Get Involved" section (can be a GitHub Pages site or a simple Astro/Hugo static site)
- [ ] Email list: use Buttondown (free up to 100 subscribers, ethical, indie) or Substack (free, built-in discovery) for a newsletter
- [ ] Project board: GitHub Projects (free, integrated with issues)
- [ ] Social media templates: create 3-4 Canva templates for sharing charts as images

### Medium Term (Month 2-3)

- [ ] Donation page: Open Collective (designed for open-source projects, transparent finances, no charity registration needed initially) or Ko-fi (simpler, lower fees)
- [ ] Proper website: wealthlens.uk or wealthlensuk.org (check domain availability)
- [ ] Analytics: Plausible (privacy-respecting, £7/month) or Umami (self-hosted, free)
- [ ] Contributors page on website
- [ ] Media kit: one-pager PDF about the project for press/organisations

---

## 5. Public-Facing Website — Structure & Copy

### Page Structure

**Homepage**
- Hero: one striking visualisation (e.g., wealth share of top 1% vs bottom 50% over 30 years) with the line: "The data exists. Now you can see it."
- One-paragraph mission statement
- 3 featured visualisations (most impactful charts)
- "Get Involved" call to action
- Logos/links of organisations using or supporting the data (add as they come)

**Explore the Data**
- Interactive dashboard: filterable by time period, wealth type, region, age group
- Each chart has: title, plain-language description, source link, methodology note, share buttons, embed code
- Download buttons for underlying data (CSV)

**About**
- The mission (longer version from Section 1)
- Your personal story (2 paragraphs — why you're building this)
- Core principles
- How this project is funded (transparency section)

**Get Involved**
- Roles needed (from Section 3)
- Link to GitHub
- Link to Discord
- "I want to help but I'm not technical" section — sharing, feedback, spreading the word
- Contact email

**Contributors**
- List of everyone who has contributed, with their role and link to their profile (GitHub, LinkedIn, or personal site)
- "We believe in recognising every contribution. If you've helped, you're listed."

**Blog / Updates**
- Project updates, new data releases, methodology posts
- Can live on Substack/Buttondown and embed on the main site

**Resources**
- Reading list: books, papers, and reports on UK wealth inequality
- Links to partner organisations
- "If you're a journalist or researcher, here's how to use our data and tools"

---

## 6. The "Why This Matters to You Personally" Messaging Playbook

This section is your cheat sheet for social media, conversations, and outreach. Every message should connect inequality to something the listener cares about personally.

### For young people (18-30):
"You're not imagining it. Buying a house IS harder than it was for your parents. The data shows exactly why — and who benefited while it got harder."

### For parents:
"Your kids will likely earn less in real terms than you did at their age. This isn't because they're lazy. The data shows a structural shift that's been building for decades."

### For entrepreneurs and self-employed:
"You're competing against inherited wealth that compounds tax-free at 5-8% per year. Understanding the system you're operating in isn't pessimism — it's strategy."

### For people who think this is "politics of envy":
"This isn't about envying the rich. It's about understanding why the economy isn't growing for everyone. The IMF, OECD, and Bank of England have all published research showing that extreme inequality slows growth. This is economic pragmatism, not ideology."

### For people who say "just work harder":
"The UK has record employment, record hours worked, and falling real wages. If hard work alone determined outcomes, we'd be the richest generation in history. Something else is going on. The data shows what."

### For the "what can I even do?" response:
"Step one is seeing clearly. Step two is sharing what you see. Step three is demanding that elected officials respond to what the data shows. We're building the tools for step one."

---

## 7. Donation & Funding Strategy

### Phase 1: No Money Needed (Now)
You're a solo engineer with free hosting options (Vercel, Railway free tier, GitHub Pages, Cloudflare Pages). Don't ask for money until you have something to show. Premature fundraising kills credibility.

### Phase 2: Cover Costs (Month 2-3)
Once you have a live project with some traction, set up:
- **Open Collective** (opencollective.com): designed for open-source projects. Transparent budget — everyone sees what comes in and what goes out. No charity registration needed. Open Collective Europe can act as fiscal host. Fees: 5-10% depending on fiscal host.
- **Ko-fi** (ko-fi.com): simpler, lower barrier. People can "buy you a coffee" (one-time) or subscribe monthly. 0% platform fee on donations (payment processor fees still apply).
- **GitHub Sponsors**: if enabled, people can sponsor your GitHub profile directly. 0% fees — GitHub absorbs them. Requires application but approval is usually fast.

Use funds for: domain name (~£10/year), analytics (£7/month), design tools, data hosting if needed.

### Phase 3: Grant Funding (Month 6+)
Once you have a live project, contributors, and some organisational endorsement:
- **Nesta Challenges**: periodic open calls for tech-for-good projects
- **National Lottery Community Fund**: supports projects that reduce inequality
- **Paul Hamlyn Foundation**: funds social justice initiatives
- **Esmée Fairbairn Foundation**: funds social change
- **Open Society Foundations**: George Soros's foundation explicitly funds transparency and inequality projects
- **Omidyar Network**: funds civic tech
- **Shuttleworth Foundation**: provides fellowships for open-source social impact projects (up to $250k/year)
- **UnLtd**: UK's foundation for social entrepreneurs — provides awards of £500-£15,000 plus mentoring for early-stage social ventures

### What to Say About Money
On the website and in all communications:
"WealthLens UK is a volunteer-led, open-source project. All donations go directly to hosting, data, and tools. Our finances are fully transparent on Open Collective. We don't pay ourselves — we do this because we believe the public deserves to see the data."

This transparency is both ethically right and strategically powerful. It neutralises any "grifter" accusations before they start.

---

## 8. Contributor Recognition & Community

### The Contributors Page
Every person who contributes — code, design, research, a useful suggestion, even sharing a post that led to a new contributor — gets listed on the Contributors page with:
- Name (or handle, if they prefer anonymity)
- Role/contribution
- Link to their profile (optional)
- Date of first contribution

This matters more than you think. People contribute to open source for recognition, learning, and community. Making recognition visible and generous is how you retain volunteers.

### Contributor Tiers (lightweight, not gamified)
- **Builders**: wrote code, designed visuals, or created content that's in production
- **Researchers**: identified data sources, fact-checked visualisations, or wrote methodology notes
- **Amplifiers**: shared content, connected us with organisations, or brought in new contributors
- **Advisors**: provided strategic guidance, domain expertise, or organisational connections

### Community Health
- Welcome every new Discord member personally (a 2-line message is enough)
- Thank every GitHub PR and issue, even if you can't merge it
- Post a monthly "State of WealthLens" update in Discord and newsletter: what was built, what's next, who contributed
- Never let a volunteer contribution sit unacknowledged for more than 48 hours
- Be honest about capacity: "We're a small volunteer team and responses may take a few days" is better than ghosting

---

## 9. Social Media Accounts & Content Operations

### Account Strategy
For now, run everything from your personal accounts. The project doesn't need its own social media until you have a team member dedicated to running it. Reasons:
- Personal accounts get more reach than brand accounts (algorithms favour people over organisations)
- Your personal story IS the brand story right now
- Managing multiple accounts solo leads to burnout and inconsistency

### When to Create a WealthLens Account
When you have either: (a) a dedicated volunteer social media manager, or (b) 1,000+ followers on your personal account talking about WealthLens. Then create @WealthLensUK on Twitter and Instagram, and have the volunteer run it while you continue your personal brand.

### Content Calendar Template (weekly)

| Day | Platform | Content Type | Example |
|-----|----------|-------------|---------|
| Mon | LinkedIn | Build update + data insight | "This week I visualised 20 years of ONS wealth data. Here's what I found..." + chart image |
| Tue | Twitter | Single chart + one-line insight | Image of chart + "Since 2010, the wealth of the top 1% grew by £X while median wages grew by £Y. Source: ONS." |
| Wed | Instagram Story | Behind-the-scenes | Screenshot of code, data cleaning, or a Slack/Discord convo with a contributor |
| Thu | Twitter | Engagement — reply to inequality discussions, quote-tweet Gary/Tax Justice UK with your data | Quote-tweet + "Here's what the data actually shows..." |
| Fri | LinkedIn | Widening participation story OR volunteer spotlight | "Met a 17-year-old this week who..." OR "Welcome to [name], our newest contributor who's building..." |
| Sat | Instagram | Polished visualisation as feed post | Beautiful chart + educational caption |
| Sun | Off | Rest | Seriously. Sustainable pace matters. |

### Newsletter (Buttondown or Substack)
- Frequency: fortnightly or monthly (start monthly — you can always increase)
- Format: 3 sections — (1) What we built this fortnight, (2) One data insight explained in plain language, (3) How to get involved
- Name suggestion: "The Wealth Report" or "WealthLens Dispatch"
- Keep it short: 500-800 words max. Respect people's inboxes.

---

## 10. Legal & Practical Considerations

### You Don't Need to Register Anything Yet
In the UK, you can operate as an unincorporated voluntary group indefinitely, as long as you're not holding significant funds or employing people. Don't let legal structure slow you down.

### When You'd Need to Formalise
- **Receiving over ~£5,000/year in donations**: consider registering as a CIO (Charitable Incorporated Organisation) with the Charity Commission. Income thresholds for mandatory registration are £5,000/year.
- **Employing someone**: you'd need a legal entity (CIO, CIC, or Ltd company)
- **Applying for grants**: most funders require a legal entity. A CIC (Community Interest Company) is faster to set up than a charity and still signals social purpose.
- **Data licensing**: all the data you're using (ONS, HMRC, WID) is published under the Open Government Licence or Creative Commons. You're fine to use, transform, and republish with attribution. Add a "Data Sources & Licences" page to the website listing every source and its licence.

### CIC vs Charity vs Unincorporated
- **Unincorporated group**: no registration, no protection, no admin. Fine for now.
- **CIC (Community Interest Company)**: £27 to register, takes 2-4 weeks. Gives you a legal entity, asset lock (assets must serve community purpose), and credibility for grants. Cannot claim Gift Aid on donations.
- **CIO (Charitable Incorporated Organisation)**: free to register but takes 2-6 months. Charity status, Gift Aid eligibility, but more governance requirements (trustees, annual accounts, Charity Commission reporting).
- **Recommendation**: stay unincorporated for months 1-3. If you get traction and want to apply for grants, register a CIC (fast, cheap, sufficient). Consider CIO later if the scale justifies it.

### Protecting Yourself
- Use a project email (e.g., hello@wealthlens.uk) for all public communications, not your personal email
- Don't publish your home address anywhere (this matters once you have any public profile)
- Be rigorous about data accuracy: every chart must cite its source. One wrong number undermines everything.
- If you receive media inquiries, respond thoughtfully and stick to data — don't get drawn into political speculation. "The data shows X. We believe the public should be able to see this." is always a safe answer.

---

## 11. Week 1 Execution Plan

### Day 1 (Today)
**Morning:**
- [ ] Create GitHub repo (wealthlens-uk)
- [ ] Write README with mission statement, tech stack, and "How to Contribute"
- [ ] Pull first dataset (ONS Wealth and Assets Survey) into Python notebook
- [ ] Create 2-3 initial charts
- [ ] Push to GitHub

**Afternoon:**
- [ ] Update LinkedIn (headline, About, Featured section)
- [ ] Post LinkedIn announcement (Section 2 copy)
- [ ] Create/update Twitter with bio and pinned thread
- [ ] Update Instagram bio
- [ ] Send emails to Tax Justice UK, Patriotic Millionaires UK, Equality Trust
- [ ] DM Gary Stevenson on Twitter

**Evening:**
- [ ] Create Discord server with basic channels
- [ ] Create Linktree with all links
- [ ] Order The Trading Game

### Day 2-3
- [ ] Respond to any LinkedIn/Twitter engagement
- [ ] Continue building data pipeline and charts
- [ ] Deploy v0.1 prototype (even if rough — Vercel or Railway free tier)
- [ ] Post Instagram story showing behind-the-scenes of building
- [ ] Follow and engage with key accounts: @garyseconomics, @TaxJusticeUK, @PatMillsUK, @TheEqualityTrst, @reabornes, @ipabornes, @NEabornes, @CommonWealthUK

### Day 4-5
- [ ] Write CONTRIBUTING.md with clear setup instructions
- [ ] Create GitHub Issues for first 10 tasks (labelled "good first issue", "help wanted")
- [ ] Write first blog post: "Why I'm building WealthLens UK" (publish on LinkedIn as article + Dev.to + personal blog if you have one)
- [ ] Post second LinkedIn update with a specific chart and data insight

### Day 6-7
- [ ] Write the "About" page copy for future website
- [ ] Research domain availability (wealthlens.uk, wealthlensuk.org, fairshare.uk)
- [ ] Set up Buttondown or Substack for newsletter
- [ ] Review any responses to emails/DMs and follow up
- [ ] Plan next week's content

### End of Week 1 Success Criteria
- [ ] Live GitHub repo with README, CONTRIBUTING.md, and initial data/charts
- [ ] Deployed prototype accessible via URL (even if rough)
- [ ] LinkedIn post published with 10+ genuine engagements
- [ ] At least 2 of 4 outreach emails sent
- [ ] Discord server created and link shared with anyone who expressed interest
- [ ] At least 1 person besides you has shown interest in contributing

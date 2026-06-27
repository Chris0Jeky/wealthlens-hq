# WealthLens UK — Claude Design Brief

> Paste this entire document into Claude Design as your opening prompt.
> It establishes the design system, then requests specific deliverables.
> After the initial generation, iterate per-section using inline comments on the canvas.

---

## PART 1: DESIGN SYSTEM BRIEF

### Who We Are

**WealthLens UK** is an open-source data transparency project that makes UK wealth inequality visible, interactive, and impossible to ignore. We turn buried government spreadsheets (ONS, HMRC, WID) into source-backed, accessible, shareable public tools — charts, dashboards, and data pages that anyone can use, embed, and verify.

We are not a political campaign, not a charity fundraiser, not a news outlet. We are an engineering project that makes public evidence legible.

**Founder:** Chris — a London-based software engineer (First Class BSc Computer Science, published researcher at Springer, former DevSecOps at GE Digital) who works in Widening Participation outreach. The personal angle: inequality isn't abstract when you've lived the gap between opportunity and postcode.

**Target audience (in priority order):**
1. Journalists and researchers looking for ready-made, cited, embeddable UK inequality charts
2. Campaign organisations (Tax Justice UK, Equality Trust, Patriotic Millionaires UK) that need public-facing evidence
3. Educators who need accessible material on wealth, housing, and opportunity
4. Engaged citizens who want to understand the system they live in
5. Potential contributors / open-source developers

### Product Personality

The design should feel like: **a Bloomberg terminal built for citizens** — rigorous, authoritative, information-dense where needed, but clean and welcoming rather than intimidating. Think: the seriousness of the Financial Times data journalism + the accessibility of Our World in Data + the visual clarity of the ONS Census interactive maps.

**Emotional targets:**
- First impression: "This is serious. This is real."
- After 10 seconds: "This is beautiful. I want to explore."
- After 1 minute: "I can't unsee this. I need to share this."
- After 5 minutes: "I trust this. I can use this in my work."

**Personality adjectives (must hit ALL):** Authoritative. Clean. Accessible. Striking. Trustworthy. Modern. Data-dense but not cluttered. Serious but not cold. Personal but not sentimental.

### The Data Domains (5 pillars)

Every design element should accommodate these five content areas:

1. **Wealth** — Who owns what in the UK. Top 10% own 57% of all wealth. Household wealth is ~£17 trillion (~7x GDP).
2. **Housing** — The affordability crisis. Median house price to median earnings ratio. Regional divergence. Generational lockout.
3. **Tax** — Where the money comes from and doesn't. Capital gains: 92% of gains go to the top 1%. Inheritance tax: only 4-5% of estates pay it. Wealth taxes raise ~3% of GDP despite wealth being 7x GDP.
4. **Inheritance** — Intergenerational wealth transfer and its concentration.
5. **Income & Opportunity** — The gap between earnings and capital gains. Regional GDHI (Kensington & Chelsea / Hammersmith & Fulham £79,500 vs UK average £24,800). Educational inequality as the first valve in the wealth funnel.

### Voice & Tone (reflected in all copy)

- Confident but not arrogant
- Data-driven and accessible — lead with the finding, never the topic
- Personal where it connects (housing, wages, opportunity) — not sentimental
- Non-partisan: "This isn't left vs right. This is seeing the numbers clearly."
- Never use: "disrupting inequality," "democratising X," "AI for good," "data will save us," "empowering," "scaling impact"
- DO use: "You can't fix what you can't see." / "We let the numbers speak." / "Source-backed. Open-source. Impossible to ignore."

---

## PART 2: VISUAL DESIGN SYSTEM

### CRITICAL: Override Default Claude Aesthetic

Do NOT use Claude's default warm/editorial aesthetic. Specifically avoid:
- Cream or off-white backgrounds (#F4F1EA and similar warm tones)
- Serif display typography (no Georgia, Fraunces, Playfair Display)
- Terracotta, amber, or warm accent colors
- Italic word-accents in headlines
- Soft, rounded, "cozy" feeling

This is a data transparency platform, not a lifestyle magazine.

### Color Palette

**Philosophy:** High contrast. WCAG AA minimum everywhere (4.5:1 for text, 3:1 for UI elements). The palette must feel institutional and trustworthy — like a government data service designed by someone who actually cares about aesthetics.

**Primary palette:**
- **Background:** Pure white (#FFFFFF) for content areas, with a very subtle cool gray (#F8F9FA) for section breaks and cards
- **Text:** Near-black (#1A1A2E) for body, true dark (#0D0D0D) for headlines
- **Primary accent (The WealthLens Blue):** A deep, authoritative navy-teal — something between the FT's dark salmon authority and the ONS's institutional blue. Think: #1B4965 or #0B3D59 — dark enough to anchor, distinctive enough to own
- **Secondary accent (The Signal Red):** A clear, non-aggressive red for highlighting inequality data points and critical findings. Something like #C1292E or #D64045 — serious, not alarming
- **Tertiary accent:** A muted gold/amber (#D4A843 or #C9A227) used sparingly for awards, highlights, and "key finding" badges — adding warmth without softness
- **Success/positive:** A restrained teal-green (#2A9D8F) for positive trends

**Data visualization palette (categorical):**
Use an Okabe-Ito inspired palette for categorical data — specifically designed for colorblind accessibility:
- #0072B2 (blue), #D55E00 (vermillion), #009E73 (green), #CC79A7 (pink), #F0E442 (yellow), #56B4E9 (sky blue), #E69F00 (orange)

**Data visualization palette (sequential):**
Use Viridis-family for continuous data — perceptually uniform and colorblind-safe.

**Data visualization palette (diverging):**
Use a blue-to-red diverging scale for inequality comparisons, with a neutral midpoint.

### Typography

**Display / Headlines:** Inter, Source Sans Pro, or IBM Plex Sans — clean, modern, geometric sans-serif. Bold weights (700-800) for headlines. LARGE sizes for hero statistics (think 72-96px for a single number like "£17 trillion").

**Body:** The same family at regular weight (400), or pair with a humanist sans-serif like Source Sans Pro. 16-18px base size. 1.6 line height for readability.

**Data / Numbers:** Use tabular (monospaced) number figures. Consider JetBrains Mono or IBM Plex Mono for data tables and chart annotations — gives a "source code of the economy" feel.

**Hierarchy:**
- H1: 48-64px, bold, near-black — used for page titles and hero stats
- H2: 32-40px, semibold — section headers
- H3: 24-28px, medium — card titles, chart titles
- Body: 16-18px, regular
- Caption/Source: 12-14px, regular, muted gray (#666666)
- Data callout: 72-96px, bold, primary accent color — for hero statistics

### Spacing & Layout

- 8px base grid
- Max content width: 1200px (wide enough for side-by-side charts)
- Generous whitespace between sections (64-96px)
- Cards with subtle shadows (0 1px 3px rgba(0,0,0,0.08)) and 8px border-radius
- No heavy borders — use whitespace and subtle background shifts to separate sections

### Iconography

Minimal, functional line icons. Consistent 24px stroke width. No emoji, no playful illustrations. Consider Lucide icons or Heroicons (outline style) — open source, clean, scalable.

### Photography & Imagery

No stock photos of sad people or generic "community" images. Instead:
- Data visualizations ARE the imagery
- Abstract geometric patterns derived from actual data (e.g., a waffle chart pattern as a background texture)
- Screenshots of the actual tools
- Maps and geographic visualizations

---

## PART 3: DELIVERABLES

### DELIVERABLE 1: Landing Page (wealthlens.org)

**Structure — follows a Problem → Evidence → Action narrative arc:**

**Section 1 — Hero (above the fold)**
- A single, devastating statistic rendered HUGE — e.g., "The top 10% of UK households own 57% of all wealth."
- Below it, a smaller contextual line: "UK household wealth is £17 trillion — 7x GDP. The data exists. It's just buried."
- A prominent CTA button: "Explore the data" (links to dashboard/charts)
- A secondary link: "View the source" (links to GitHub)
- Background: a subtle, animated data visualization — perhaps a slowly shifting area chart or particle system representing wealth distribution, rendered in the primary palette. Not distracting — atmospheric.
- Navigation: clean top bar with: Logo | Explore | About | Methodology | Contribute

**Section 2 — The Five Pillars (scrolling cards)**
- Five horizontally-scrollable or grid-arranged cards, one per data domain:
  1. Wealth — "Who owns what" — mini sparkline showing top 10% share over time
  2. Housing — "The affordability crisis" — mini chart of price-to-earnings ratio
  3. Tax — "Where the money comes from" — mini pie/donut of tax composition
  4. Inheritance — "The generational transfer" — mini bar chart
  5. Income & Opportunity — "The gap" — mini regional comparison
- Each card has: a one-line finding, a mini chart, and a "See the full picture →" link
- Card design: white background, subtle shadow, hover state that lifts slightly

**Section 3 — Credibility bar**
- A horizontal strip showing: "Data from: ONS | HMRC | WID | Land Registry | DWP" with their logos or wordmarks in muted gray
- Below: "Every chart cites its source. Every dataset is downloadable. Every pipeline is open source."

**Section 4 — How It Works (3 steps)**
- "1. We collect public data" — icon of database/download
- "2. We make it visible" — icon of chart/eye
- "3. You share the evidence" — icon of share/embed
- Clean, minimal, three-column layout

**Section 5 — Featured chart**
- An embedded interactive chart (the best one — likely the WID wealth shares chart or housing affordability)
- Full interactivity right on the landing page
- Source citation visible
- "Embed this chart" and "Download data" buttons visible

**Section 6 — The Mission**
- Short, punchy copy: "WealthLens UK makes the data behind wealth inequality visible, interactive, and impossible to ignore — so that everyone can see the system clearly and push for better decisions."
- Below: "Built by Chris — a software engineer and widening participation practitioner who believes you can't fix what you can't see."
- A "Read more about the project →" link

**Section 7 — Call to Action (footer CTA)**
- "The data is public. The tools are open source. The evidence should be impossible to ignore."
- Three buttons: "Explore the data" | "Contribute on GitHub" | "Follow on Bluesky"

**Footer:**
- Logo | Open Source (MIT) | GitHub | Twitter/X | Bluesky | Contact
- "Every statistic on this site links to its primary source."

### DELIVERABLE 2: Dashboard Overview Page

**The main /explore or /dashboard page — a gallery of all available chart pages.**

- Hero area: "Explore UK Inequality Data" with a search/filter bar
- Filter pills: All | Wealth | Housing | Tax | Inheritance | Income & Opportunity
- Grid of chart page cards (responsive: 3 columns desktop, 2 tablet, 1 mobile):
  - Each card shows:
    - Chart title (e.g., "Share of Net Personal Wealth — UK, 1820–2023")
    - A static preview thumbnail of the chart
    - Data source badge (e.g., "WID" or "ONS")
    - Last updated date
    - One-line key finding in bold
    - Tags/pills for the data domain
- Hover state: card lifts, thumbnail animates to show a hint of interactivity
- Sort options: "Most recent" | "Most viewed" | "By domain"

### DELIVERABLE 3: Individual Chart Page Template

**The most important page — this is what gets shared, embedded, and cited.**

Inspired by Our World in Data's article pages and the Fed DFA explorer:

**Layout:**
- Clean, focused, single-column (max 800px) with the chart spanning full width
- Title: large, clear, plain-language (e.g., "Who owns wealth in the UK?")
- Subtitle: the key finding in one sentence (e.g., "The top 10% have held over 50% of all net personal wealth for at least two centuries.")
- The interactive chart: full-width, responsive, with:
  - Hover tooltips showing exact values
  - Direct labels on the chart (not just a legend)
  - Annotation callouts for key moments (e.g., "Post-WWII compression" or "Thatcher era")
  - A visible source citation bar below the chart: "Source: World Inequality Database (wid.world) · CC-BY · Accessed 2026-05-14"
- Below the chart, a share/embed toolbar:
  - Copy link | Embed (iframe code) | Download PNG | Download SVG | Download CSV | Share to X | Share to Bluesky | Share to LinkedIn
- Methodology section: collapsible, plain-English explanation of what the data measures, what it omits, and what assumptions sit underneath
- "Related charts" section: 2-3 card links to related chart pages
- Navigation breadcrumb: Home > Explore > Wealth > This Chart

### DELIVERABLE 4: Logo & Brand Mark

**Requirements:**
- Works at 16px (favicon), 32px, 64px, and full size
- Works in full color, single color (dark on light), and inverted (light on dark)
- Must be distinctive at small sizes in a browser tab
- Should NOT look like a generic "charity logo" or "tech startup logo"

**Direction:**
The logo should evoke: a lens (the act of seeing clearly) + data (charts, distributions, structure) + the UK (subtle, not a flag).

**Concepts to explore:**
1. A stylized lens or eye shape with a wealth distribution curve (area chart silhouette) visible through it — "seeing the data clearly"
2. A geometric mark that abstractly represents concentration — many small shapes converging into fewer, larger ones (the wealth funnel)
3. A clean wordmark "WealthLens" where the "L" in Lens subtly forms a chart axis, or where the dot of the "i" (if we style it "Wealthlens") is a data point
4. A magnifying glass or lens with a bar chart or distribution curve inside it

**Typographic logo:** "WealthLens" or "WEALTHLENS" in the primary sans-serif, with "UK" in a smaller, muted style. The wordmark should work standalone.

**Color:** The primary navy-teal accent color. Single-color versions in black and white.

**Generate multiple concepts (at least 3-4 variations) so we can compare.**

### DELIVERABLE 5: Social Media Templates

**For announcing charts on LinkedIn, X/Twitter, and Bluesky:**

**LinkedIn carousel template (most important — highest engagement format):**
- Slide 1 (hook): A single large statistic on a branded background. E.g., "92% of capital gains go to the top 1%." WealthLens logo in corner.
- Slide 2-4 (evidence): The chart(s), with annotations and source citations. Clean white background, the chart takes up 80% of the space.
- Slide 5 (CTA): "See the full interactive chart and download the data at wealthlens.org/charts/cgt-concentration" + GitHub star prompt + follow prompt.

**X/Bluesky image template:**
- 1200x675px (2:1 ratio for X/Bluesky cards)
- The chart as the hero image, with a branded header bar containing the WealthLens logo and a one-line finding
- Source citation visible in the image itself
- URL visible at bottom

**OG image template (for link previews):**
- 1200x630px
- When someone shares a WealthLens chart page URL, this is what previews
- Shows: the chart title, a static version of the chart, the WealthLens logo, and "wealthlens.org"

### DELIVERABLE 6: About / Mission Page

- Hero: "Making inequality data visible, interactive, and impossible to ignore."
- The theory of change, visualized:
  - A flowing diagram: Public Data → Collection & Processing → Interactive Charts → Journalists, educators, citizens reuse → Better evidence circulates → Better decisions
- About Chris section: photo placeholder, short bio, the personal angle (WP work, the engineering positioning)
- Values as design elements (not just a list):
  - "Data first, opinion second" — with an icon
  - "Open source always" — with GitHub link
  - "Accessible by default" — with WCAG badge
  - "Independent and non-partisan" — with a neutral icon
- Collaborators / aligned organisations section: logos of Tax Justice UK, Equality Trust, IFS, Resolution Foundation, ONS (as aspirational/aligned, not claiming partnership)
- CTA: "Contribute" and "Get in touch"

### DELIVERABLE 7: Methodology / Trust Page

- Hero: "Every number has a source. Every source has a link."
- Explanation of the data pipeline: fetch → process → chart → cite
- Interactive table of all data sources (searchable/filterable):
  - Source name, publisher, format, licence, update frequency, geographic coverage, notes
- Explanation of chart standards: WCAG AA, mobile-responsive, downloadable, embeddable
- Link to GitHub for full reproducibility

### DELIVERABLE 8: Contributor / Get Involved Page

- Hero: "This is open source. You can help."
- Three paths:
  1. "Use the data" — Embed charts, cite in articles, use in teaching
  2. "Improve the tools" — Contribute code, file bugs, suggest datasets (link to GitHub)
  3. "Spread the evidence" — Share charts, follow on social, join the mailing list
- Good-first-issues callout (pulled from GitHub)
- Tech stack summary: Python, FastAPI, Vue 3, TypeScript, D3.js, TailwindCSS

### DELIVERABLE 9: Mobile Responsive Variants

Show how the following look on mobile (375px width):
- Landing page hero
- Chart page (chart must remain interactive and readable)
- Dashboard gallery (single-column cards)
- Navigation (hamburger menu)

### DELIVERABLE 10: Dark Mode Variant

Design a dark mode for the entire system:
- Background: #0D1117 (GitHub dark) or similar cool dark
- Cards: #161B22
- Text: #E6EDF3
- Accent colors adjusted for dark backgrounds (lighter variants)
- Charts: dark background with light gridlines, bright data colors
- The dark mode should feel like a Bloomberg terminal — information-dense, focused, professional

---

## PART 4: DESIGN CONSTRAINTS & ANTI-PATTERNS

### Do
- Use generous whitespace to let data breathe
- Make source citations visible and prominent on every chart
- Use direct labeling on charts (labels on the data, not just a legend)
- Design for sharing — every chart page should look good when screenshotted
- Use real data in mockups where possible (the actual statistics from Part 1)
- Make interactive elements obviously interactive (hover states, cursor changes)
- Use the monospace font for data/numbers to give a "source code of the economy" feel

### Do Not
- Do not use stock photography of any kind
- Do not use generic gradient backgrounds
- Do not use rounded, playful UI elements (no pill-shaped everything)
- Do not use emoji in the UI
- Do not use "tech startup" visual language (no floating 3D shapes, no glassmorphism, no neon gradients)
- Do not make it look like a charity donation page
- Do not use political imagery, party colors, or partisan visual language
- Do not sacrifice data density for aesthetics — the data IS the aesthetic
- Do not hide source citations in tooltips or expandable sections — they should be visible by default
- Do not use loading spinners where static content could work
- Do not use carousel auto-play

### Inspirations to Reference

- **Our World in Data** (ourworldindata.org) — chart page layout, one-question-per-view, direct labeling, methodology notes
- **US Federal Reserve DFA Dashboard** (federalreserve.gov/releases/z1/dataviz/dfa/) — wealth distribution by percentile, clean institutional feel
- **ONS Census Maps** (ons.gov.uk/census/maps) — interactive, embeddable, deep-linkable, open source
- **Financial Times Data Journalism** — authority, typography, use of red as a signal color
- **"Wealth, Shown to Scale"** (github.com/mkorostoff/1-pixel-wealth) — the viral scroller that made wealth concentration visceral
- **The Pudding** (pudding.cool) — data storytelling that makes you FEEL the numbers
- **PolicyEngine** (policyengine.org) — reform simulator, quintile visualizations

---

## PART 5: TECHNICAL CONTEXT (for handoff to Claude Code)

The final implementation will use:
- **Frontend:** Vue 3 + TypeScript, Pinia (state), TailwindCSS (styling), D3.js or ECharts (charts), Vite (build)
- **Backend:** Python 3.11+, FastAPI, Pydantic, SQLite (dev) / PostgreSQL (prod)
- **Deploy:** GitHub Pages or Cloudflare Pages initially, then containerized

Design with TailwindCSS utility classes in mind. Component structure should map naturally to Vue single-file components. Use CSS custom properties for the color tokens so they can be swapped for dark mode.

When you export the handoff bundle to Claude Code, the design tokens, component hierarchy, and layout specs should translate directly into Tailwind config and Vue components.

---

Please generate all deliverables as a cohesive design system. Start with the landing page (Deliverable 1) and the logo concepts (Deliverable 4), then the chart page template (Deliverable 3) — these three set the visual identity that everything else follows.

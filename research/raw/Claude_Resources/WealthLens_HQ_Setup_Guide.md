# WealthLens HQ — Master Repo Setup Guide

## What This Is

A single repository that serves as your command centre for everything: the WealthLens UK mission, your career strategy, research outputs, task management, automation, and the actual software projects. Designed to work with Claude Code, Claude Desktop, and Cowork as your AI-assisted operating system.

---

## Step 1: Create the Repo

```bash
mkdir wealthlens-hq
cd wealthlens-hq
git init
```

---

## Step 2: The Folder Structure

```
wealthlens-hq/
│
├── CLAUDE.md                          # Instructions for AI agents (see below)
├── README.md                          # Overview of the entire repo
├── .gitignore
│
├── identity/                          # Who you are — for AI context
│   ├── about-me.md                    # Your story, background, values, outlook
│   ├── cv.pdf                         # Latest CV
│   ├── cv-notes.md                    # What to emphasise, what to downplay, framing
│   ├── skills.md                      # Technical skills, soft skills, learning goals
│   ├── passions.md                    # What drives you, what you care about
│   ├── portfolio.md                   # Links to all projects, publications, talks
│   └── principles.md                  # Personal operating principles and values
│
├── vision/                            # The big picture
│   ├── mission.md                     # WealthLens UK mission statement
│   ├── theory-of-change.md            # How visibility → understanding → action → policy
│   ├── horizon.md                     # Where this could go in 1, 3, 5 years
│   ├── north-stars.md                 # Key metrics and milestones that matter
│   └── inspiration.md                 # People, projects, and ideas that inspire this work
│
├── strategy/                          # Plans and playbooks
│   ├── career-strategy.md             # Your overall career plan (from our sessions)
│   ├── branding-playbook.md           # LinkedIn, Twitter, Instagram, Bluesky strategy
│   ├── outreach-strategy.md           # How to approach organisations and individuals
│   ├── content-strategy.md            # What to post, where, when, how often
│   ├── volunteer-strategy.md          # How to recruit, onboard, retain contributors
│   ├── funding-strategy.md            # Donations, grants, fiscal sponsorship
│   ├── partnership-strategy.md        # Orgs to partner with, how to approach them
│   └── growth-strategy.md             # How to grow audience, contributors, impact
│
├── research/                          # All research outputs
│   ├── raw/                           # Raw LLM research outputs (dump them here)
│   │   ├── 01-cv-analysis.md
│   │   ├── 02-career-strategy.md
│   │   ├── 03-strength-building.md
│   │   ├── 04-high-roi-investments.md
│   │   ├── 05-wealthlens-data-landscape.md
│   │   ├── 06-uk-justice-ecosystem.md
│   │   ├── 07-content-brand-strategy.md
│   │   ├── 08-widening-participation-tech.md
│   │   ├── 09-career-paths-civic-tech.md
│   │   ├── 10-reading-curriculum.md
│   │   └── ...
│   ├── synthesised/                   # Distilled key takeaways from each research
│   │   └── key-insights.md            # The 20% that drives 80% of action
│   ├── data-sources/                  # Catalogue of all data sources identified
│   │   └── data-source-registry.md    # Name, URL, format, update frequency, licence
│   └── reading-list/                  # Books, papers, podcasts, courses to consume
│       ├── queue.md                   # What to read next, prioritised
│       ├── completed.md               # What you've read, with key takeaways
│       └── notes/                     # Notes on individual books/papers
│
├── tasks/                             # Everything that needs doing
│   ├── inbox.md                       # Unsorted ideas, thoughts, tasks (dump here first)
│   ├── active-sprint.md               # This week's focus (5-7 tasks max)
│   ├── backlog.md                     # Prioritised list of everything else
│   ├── done.md                        # Completed tasks (move here for motivation)
│   │
│   ├── outreach/                      # People and orgs to contact
│   │   ├── emails-to-send.md          # Drafted emails ready to send
│   │   ├── emails-sent.md             # Sent emails with date and status
│   │   ├── follow-ups-needed.md       # Who to follow up with and when
│   │   └── contacts.md                # Key people, their roles, how to reach them
│   │
│   ├── social-media/                  # Social media tasks
│   │   ├── accounts-to-follow.md      # Strategic follows on X, Bluesky, LinkedIn
│   │   ├── posts-drafted.md           # Ready-to-publish posts
│   │   ├── posts-published.md         # Archive of what went out
│   │   ├── engagement-targets.md      # Accounts to regularly engage with
│   │   └── content-calendar.md        # Weekly content plan
│   │
│   └── learning/                      # Courses, certifications, skills to build
│       ├── in-progress.md             # What you're currently studying
│       ├── planned.md                 # What's next
│       └── completed.md               # What you've finished
│
├── projects/                          # Actual software and creative projects
│   ├── wealthlens-dashboard/          # Git submodule or subfolder for the main app
│   │   ├── README.md
│   │   ├── CONTRIBUTING.md
│   │   ├── backend/                   # FastAPI, data pipelines
│   │   ├── frontend/                  # Vue 3, D3.js, charts
│   │   ├── data/                      # Raw and processed datasets
│   │   ├── notebooks/                 # Jupyter notebooks for data exploration
│   │   └── docs/                      # Technical docs, architecture decisions
│   │
│   ├── landing-page/                  # Public-facing website for WealthLens UK
│   │   └── ...                        # Astro, Hugo, or simple HTML/CSS
│   │
│   ├── newsletter/                    # Newsletter content and templates
│   │   ├── issues/                    # Drafted and published issues
│   │   └── templates/                 # Reusable templates
│   │
│   └── social-media-assets/           # Templates, charts, graphics for sharing
│       ├── templates/                 # Canva or Figma templates
│       ├── charts/                    # Exported chart images for social media
│       └── brand/                     # Logo, colours, fonts, style guide
│
├── automation/                        # Scripts and workflows
│   ├── data-pipelines/                # Scripts to pull and update data from ONS, HMRC, etc
│   │   ├── fetch_ons_wealth.py
│   │   ├── fetch_wid_data.py
│   │   ├── fetch_hmrc_stats.py
│   │   └── update_all.sh
│   │
│   ├── social-media/                  # Automation for social posting
│   │   └── chart_to_social.py         # Generate social media images from chart data
│   │
│   ├── analysis/                      # Scripts for analysing research docs with Claude
│   │   ├── summarise_research.py      # Feed research docs to Claude API, get summaries
│   │   └── extract_action_items.py    # Pull action items from research outputs
│   │
│   └── workflows/                     # GitHub Actions or cron jobs
│       ├── weekly-data-update.yml     # Auto-fetch latest data weekly
│       └── deploy.yml                 # Auto-deploy dashboard on push
│
├── people/                            # Contributor and community management
│   ├── contributors.md                # List of all contributors and their roles
│   ├── onboarding.md                  # How new volunteers get started
│   ├── roles.md                       # What roles exist and what each involves
│   └── thank-yous.md                  # Recognition log
│
├── legal/                             # Legal and governance docs
│   ├── data-licences.md               # Licence for each data source used
│   ├── project-licence.md             # The repo's open-source licence
│   ├── cic-notes.md                   # Notes on eventual CIC registration
│   └── privacy-policy.md              # For the website
│
├── meetings/                          # Notes from any meetings or calls
│   └── YYYY-MM-DD-topic.md
│
└── journal/                           # Personal reflections and learning log
    └── YYYY-MM-DD.md                  # What you did, learned, felt, decided
```

---

## Step 3: The CLAUDE.md File

This is the most important file in the repo. It tells Claude Code, Claude Desktop, and any AI agent who you are, what you're doing, and how to help. Place it in the repo root.

```markdown
# CLAUDE.md — Instructions for AI Agents

## Who Is Cristian Tcaci

Cristian is a London-based software engineer and the founder of WealthLens UK,
an open-source project making UK wealth inequality data visible to the public.

### Background
- BSc Computer Science, First Class Honours, Middlesex University (2025)
- Published lead author: "Navigating the N-Person Prisoners' Dilemma" — Springer, SGAI-AI 2025
- 15-month software engineering internship at GE Digital (DevSecOps, AWS, Jenkins, CI/CD)
- Near-co-founder of a quant/options trading platform startup
- Built Taskdeck: a 4,000-commit local-first developer tool (.NET 8, Vue 3, LLM integration)
- Works at Middlesex University in Widening Participation outreach
- See identity/ folder for full details

### Technical Skills
- Primary: C#/.NET 8, Python, TypeScript, JavaScript
- Backend: FastAPI, Node.js/Express, .NET, REST APIs
- Frontend: Vue 3, Pinia, TailwindCSS, D3.js
- Data: Pandas, scikit-learn, SQLite, PostgreSQL, MongoDB
- Infrastructure: Docker, AWS, Jenkins, CI/CD, Git, Linux
- AI/LLM: OpenAI API, Gemini API, multi-provider abstraction, intent classification

### Mission
Build open-source tools that make UK wealth inequality data accessible, interactive,
and impossible to ignore. Collaborate with organisations like Tax Justice UK,
Patriotic Millionaires UK, and the Equality Trust.

### Values
- Data first, opinion second
- Open source always
- Accessible by default
- Independent and non-partisan

## How to Help Cristian

### When working on WealthLens code (projects/wealthlens-dashboard/)
- Use Python (FastAPI) for backend, Vue 3 + TypeScript for frontend
- All data must cite its source with URL and access date
- Charts must be mobile-responsive and accessible (WCAG AA minimum)
- Write clear docstrings and comments — volunteers will read this code
- Prefer D3.js or ECharts for interactive visualisations
- All data pipelines should be reproducible (scripts in automation/data-pipelines/)

### When working on content (tasks/social-media/, strategy/)
- Voice: confident but not arrogant, data-driven, accessible, personal
- Never partisan — present data, not political opinions
- Connect inequality to personal experience (housing, wages, opportunity)
- Reference the messaging playbook in strategy/branding-playbook.md

### When working on tasks and planning
- Check tasks/active-sprint.md for current priorities
- New ideas go in tasks/inbox.md for later triage
- Completed tasks move to tasks/done.md with date
- Always check if a task connects to an existing strategy doc before creating new ones

### When working on outreach
- Check tasks/outreach/contacts.md for existing relationships
- Never send an email without checking tasks/outreach/emails-sent.md for prior contact
- Tone: professional, specific, offering value (not asking for favours)
- Always include a link to something you've already built

### When organising research
- Raw LLM outputs go in research/raw/ numbered sequentially
- After processing, key insights go in research/synthesised/key-insights.md
- Action items extracted from research go in tasks/inbox.md

### When making decisions
- Refer to vision/north-stars.md for what success looks like
- Refer to identity/principles.md for values-based decision making
- When in doubt, optimise for: (1) shipping something real, (2) making it visible,
  (3) connecting with the right people — in that order

### File Conventions
- Markdown for all docs
- Dates in YYYY-MM-DD format
- Task format: "- [ ] Task description (@owner if assigned) [due: YYYY-MM-DD]"
- When updating any strategy doc, add a "Last updated: YYYY-MM-DD" line at the top
```

---

## Step 4: Bootstrap Prompt for Claude Code / Cowork

Use this prompt in a Claude Code or Cowork session to get Claude to help you
set up and organise the repo from your existing research outputs:

```
I have a master repo at ~/wealthlens-hq that serves as my command centre for
WealthLens UK (an open-source project making UK wealth inequality data visible)
and my broader career and mission.

Read CLAUDE.md for full context on who I am and what I'm building.

I have a folder of research outputs at research/raw/ that contain extensive
analysis from previous Claude sessions covering:
- CV analysis and career strategy
- High-leverage career playbook (quant, dev-tooling, AI infrastructure)
- High-ROI certifications, courses, and actions
- Rebranding and personal brand strategy
- WealthLens UK founding document (mission, volunteer roles, infrastructure, legal)
- Future research prompts for additional sessions

I need you to:

1. Read through all files in research/raw/ and identity/
2. Create research/synthesised/key-insights.md — extract the top 30-50 actionable
   insights across all research, grouped by category (career, technical, outreach,
   content, learning, mission)
3. Populate tasks/inbox.md with every concrete action item mentioned across all
   research outputs — every email to send, every account to follow, every cert to
   pursue, every tool to build, every post to write
4. Create an initial tasks/active-sprint.md with the 7 highest-priority tasks
   for this week based on urgency and impact
5. Populate tasks/outreach/contacts.md with every person and organisation mentioned
   across the research — name, role, platform, contact method, status (not contacted /
   contacted / responded / collaborating)
6. Populate tasks/social-media/accounts-to-follow.md with every Twitter, LinkedIn,
   and Bluesky account mentioned as worth following
7. Populate tasks/outreach/emails-to-send.md with the draft emails from the research
   (Tax Justice UK, Patriotic Millionaires, Equality Trust, Gary Stevenson)
8. Create research/data-sources/data-source-registry.md listing every data source
   mentioned (ONS, HMRC, WID, etc.) with URL, format, and licence
9. Create research/reading-list/queue.md with every book, paper, course, and
   resource mentioned, prioritised by the research recommendations
10. Populate tasks/social-media/content-calendar.md with a 2-week content plan
    based on the content strategy in the research

After completing this, give me a summary of:
- Total action items extracted
- Top 5 things I should do today
- Any gaps or contradictions you noticed across the research
- Suggestions for additional structure or files the repo needs
```

---

## Step 5: Ongoing Workflows

### Daily (5 minutes)
- Check tasks/active-sprint.md — what's the one thing to move forward today?
- Check tasks/outreach/follow-ups-needed.md — anyone to follow up with?
- Add any new thoughts to tasks/inbox.md or journal/

### Weekly (30 minutes, Sunday evening)
- Review tasks/active-sprint.md — move completed items to tasks/done.md
- Pull next items from tasks/backlog.md into tasks/active-sprint.md
- Review tasks/social-media/content-calendar.md — plan next week's posts
- Write a brief journal/ entry: what happened, what I learned, what's next

### Monthly (1 hour)
- Review strategy/ docs — are they still accurate? Update as needed
- Review tasks/outreach/contacts.md — who haven't I followed up with?
- Review vision/north-stars.md — am I moving toward the metrics that matter?
- Run automation/analysis/summarise_research.py on any new research outputs
- Update research/reading-list/completed.md with what you've read

### When Adding New Research
1. Save raw output to research/raw/NN-topic.md
2. Ask Claude Code to extract action items → tasks/inbox.md
3. Ask Claude Code to extract key insights → research/synthesised/key-insights.md
4. Ask Claude Code to extract any new contacts → tasks/outreach/contacts.md
5. Ask Claude Code to extract any new data sources → research/data-sources/

### When a New Volunteer Joins
1. Add them to people/contributors.md
2. Point them to projects/wealthlens-dashboard/CONTRIBUTING.md
3. Assign them a specific task from the GitHub Issues board
4. Welcome them in Discord
5. Add a thank-you to people/thank-yous.md

---

## Step 6: Automation Ideas (Build These Over Time)

### Data Pipeline Automation
- Cron job or GitHub Action that runs weekly: pulls latest ONS, HMRC, WID data,
  processes it, commits to the data/ folder, triggers a dashboard rebuild
- Script: fetch_ons_wealth.py — downloads Wealth and Assets Survey tables
- Script: fetch_hmrc_stats.py — downloads capital gains, inheritance tax stats
- Script: fetch_wid_data.py — pulls World Inequality Database UK series

### Research Processing Automation
- Script: summarise_research.py — takes a markdown file in research/raw/,
  sends it to Claude API with a prompt to extract action items, key insights,
  contacts, and data sources, writes outputs to the appropriate folders
- Script: extract_action_items.py — lighter version, just pulls tasks

### Social Media Automation
- Script: chart_to_social.py — takes a chart image + caption text,
  generates properly sized images for Twitter (1200x675), Instagram (1080x1350),
  LinkedIn (1200x627) with consistent branding
- GitHub Action: when a new chart is committed to projects/social-media-assets/charts/,
  auto-generate social-sized versions

### Content Generation Support
- Template: newsletter_template.md — fill in sections, export to Buttondown/Substack
- Template: linkedin_post_template.md — with prompts for each section
- Template: twitter_thread_template.md — with character count guidance

---

## Step 7: Connector and Tool Recommendations

### For Claude Code / Desktop
- Connect to GitHub (for repo management)
- Connect to Google Drive (if storing research docs there)

### For the Dashboard Project
- Vercel or Cloudflare Pages (free hosting, auto-deploy from GitHub)
- Railway (free tier for FastAPI backend if needed)
- Plausible Analytics (privacy-respecting, £7/month)

### For Community
- Discord (free, good for project organisation)
- GitHub Discussions (alternative if you want everything in GitHub)

### For Content
- Buttondown (free newsletter up to 100 subs) or Substack (free, built-in discovery)
- Canva (social media templates — you already have it connected)
- Buffer or Typefully (schedule social media posts — both have free tiers)

### For Task Management (if you outgrow markdown files)
- GitHub Projects (free, integrated with Issues — best if contributors use GitHub)
- Linear (excellent UX, free for small teams — overkill for now but great later)
- Notion (flexible but can become a time sink — avoid unless you already use it)

---

## How This Repo Grows

### Month 1: Foundation
The repo is mostly strategy docs, research, tasks, and the first prototype
of the dashboard. You're the only contributor. The structure is simple.

### Month 3: First Contributors
Add CONTRIBUTING.md to root, expand people/ folder, create GitHub Issues
from tasks/backlog.md. The projects/ subfolder becomes the most active area.

### Month 6: Possible Split
If the dashboard project grows significantly, consider splitting it into
its own repo (github.com/WealthLensUK/dashboard) and keeping wealthlens-hq
as the private strategy/ops repo. The public-facing code lives separately
from your personal career strategy and outreach tracking.

### Month 12: Organisation
If WealthLens becomes a registered CIC or charity, the repo structure
naturally maps to organisational functions: strategy/ becomes board docs,
people/ becomes team management, legal/ becomes governance, and projects/
contains all the public-facing work.

The structure is designed to grow with you. Start simple, add complexity
only when you feel the friction of not having it.

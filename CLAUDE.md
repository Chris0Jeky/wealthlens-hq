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
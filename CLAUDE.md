# CLAUDE.md

This file provides guidance to Claude Code when working in the WealthLens HQ repository.

## Who Is Cristian Tcaci

Cristian is a London-based software engineer and the founder of WealthLens UK, an open-source project making UK wealth inequality data visible to the public.

### Background

- BSc Computer Science, First Class Honours, Middlesex University (2025)
- Published lead author: "Navigating the N-Person Prisoners' Dilemma" - Springer, SGAI-AI 2025
- 15-month software engineering internship at GE Digital (DevSecOps, AWS, Jenkins, CI/CD)
- Near-co-founder of a quant/options trading platform startup
- Built Taskdeck: a 4,000-commit local-first developer tool (.NET 8, Vue 3, LLM integration)
- Works at Middlesex University in Widening Participation outreach
- See `identity/` for fuller context

### Technical Skills

- Primary: C#/.NET 8, Python, TypeScript, JavaScript
- Backend: FastAPI, Node.js/Express, .NET, REST APIs
- Frontend: Vue 3, Pinia, TailwindCSS, D3.js
- Data: Pandas, scikit-learn, SQLite, PostgreSQL, MongoDB
- Infrastructure: Docker, AWS, Jenkins, CI/CD, Git, Linux
- AI/LLM: OpenAI API, Gemini API, multi-provider abstraction, intent classification

## Mission

Build open-source tools that make UK wealth inequality data accessible, interactive, and impossible to ignore. Collaborate with organisations like Tax Justice UK, Patriotic Millionaires UK, and the Equality Trust.

## Values

- Data first, opinion second
- Open source always
- Accessible by default
- Independent and non-partisan

## Repository Role

WealthLens HQ is the command-centre repo for strategy, research, tasks, outreach, community, automation, and planned software projects.

The main planned product is `projects/wealthlens-dashboard/`, with:

- Python and FastAPI for backend/API work
- Vue 3, TypeScript, Pinia, TailwindCSS, D3.js or ECharts for frontend and visualisation
- Reproducible data pipelines in `automation/data-pipelines/`
- Source citations for every dataset, including URL and access date
- Mobile-responsive charts that meet WCAG AA minimum
- Clear docstrings and comments because volunteers will read the code

## Important Paths

- `tasks/active-sprint.md` - current priorities
- `tasks/inbox.md` - new ideas and untriaged work
- `tasks/done.md` - completed work with dates
- `research/raw/` - raw and consolidated research inputs
- `research/synthesised/key-insights.md` - distilled research conclusions
- `research/data-sources/data-source-registry.md` - data source catalogue
- `strategy/branding-playbook.md` - tone, platform, and public voice guidance
- `vision/north-stars.md` - success metrics and milestones
- `identity/principles.md` - values-based decision guidance

## Research Handling

Raw source documents from Claude, Codex, and other assistants may remain in provider-specific folders under `research/raw/`. When research is consolidated by topic, keep the original raw files intact and add the merged output as a clearly named Markdown file in `research/raw/` or a distilled note in `research/synthesised/`.

Action items extracted from research should go into `tasks/inbox.md`. Key insights should go into `research/synthesised/key-insights.md`.

## Content Voice

- Confident but not arrogant
- Data-driven and accessible
- Personal where useful, especially around housing, wages, opportunity, and widening participation
- Non-partisan: present data, not party-political opinions
- Avoid making claims that are not backed by sources

## Outreach Rules

- Check `tasks/outreach/contacts.md` before contacting anyone
- Check `tasks/outreach/emails-sent.md` for prior contact history
- Tone should be professional, specific, and value-offering
- Include a link to something already built whenever possible

## File Conventions

- Markdown for docs
- Dates in `YYYY-MM-DD`
- Task format: `- [ ] Task description (@owner if assigned) [due: YYYY-MM-DD]`
- Strategy docs must include `Last updated: YYYY-MM-DD` near the top
- Keep data source records explicit: source name, URL, access date, format, licence, update pattern, and notes

## Decision Framework

When prioritising, optimise for:

1. Shipping something real
2. Making it visible
3. Connecting with the right people

In practice, prefer a small number of source-backed, shareable chart pages over a large generic dashboard.

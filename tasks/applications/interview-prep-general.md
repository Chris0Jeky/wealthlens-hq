# Interview Preparation -- General Guide

Last updated: 2026-05-31

## The honest situation

Chris has been using AI extensively for coding over the past few years. This has:

**Strengthened:**
- High-level architecture and system design thinking
- Orchestration of complex multi-agent workflows
- Code review and quality assessment
- Understanding of what good code looks like
- Ability to specify and direct technical work precisely
- Security awareness (led a 150-finding audit)
- Testing strategy and framework design

**Weakened:**
- Writing code from scratch without assistance (speed, syntax recall)
- Typing out boilerplate and standard patterns from memory
- Recalling exact API signatures and stdlib functions
- The "muscle memory" of daily unassisted coding

**Strategy:** This is not a fatal problem. It is a preparation gap that can be closed with 2-3 weeks of focused daily practice before interviews. The knowledge is there; the fluency needs rebuilding.

---

## Preparation plan (start immediately, intensify when interview is confirmed)

### Phase 1: Daily coding fluency (start now, 30-60 min/day)

The goal is NOT to learn new things. It is to rebuild fluency with things you already understand.

#### Python fundamentals (no AI, no autocomplete)

- [ ] Open a plain text editor (not VS Code with Copilot). Use Notepad++ or VS Code with all AI extensions disabled.
- [ ] Write small programs daily WITHOUT any AI assistance:
  - Day 1-3: File I/O, CSV parsing, JSON manipulation, dict/list comprehensions
  - Day 4-6: HTTP requests with `requests`, parsing HTML with BeautifulSoup, simple web scraping
  - Day 7-9: SQLite/PostgreSQL queries with raw SQL and with SQLAlchemy
  - Day 10-12: FastAPI routes: GET/POST/PUT/DELETE, path params, query params, request bodies, Pydantic models
  - Day 13-15: Testing with pytest: fixtures, parametrize, mocking, asserting exceptions
  - Day 16-18: Pandas basics: read_csv, filtering, groupby, merge, pivot
  - Day 19-21: String manipulation, regex, datetime handling, error handling patterns
- [ ] Time yourself. The goal is not perfection but speed recovery.
- [ ] After writing, run the code. Fix bugs WITHOUT AI. This is where the real learning happens.

#### Web fundamentals (HTML/CSS/JS)

- [ ] Build a simple page from scratch: a form that submits data, a table that displays it
- [ ] Write CSS without Tailwind: flexbox layout, responsive media queries, basic styling
- [ ] Write vanilla JavaScript: DOM manipulation, fetch API, event listeners
- [ ] These are likely to come up in a take-home or pairing session

#### Perl exposure (if mySociety invites you)

- [ ] Do the first 10 exercises on exercism.org/tracks/perl5
- [ ] Read "Learn Perl in about 2 hours 30 minutes" (minimalist guide)
- [ ] Read through one FixMyStreet Perl file (e.g., a controller) and annotate what each block does
- [ ] You do NOT need to be proficient. You need to show you can read and reason about Perl code.

### Phase 2: Mock technical exercises (when interview is confirmed)

#### Likely exercise formats for UK civic tech roles

1. **Take-home exercise (most likely for mySociety)**
   - Typically: "Build a small web app that does X" in 3-4 hours
   - They evaluate: code quality, testing, documentation, git history, pragmatism
   - Practice: build a small FastAPI app that reads from a database and serves HTML
   - AI policy: UNCLEAR. Some orgs allow AI tools, some don't. Ask when they send the exercise.

2. **Pair programming (possible)**
   - You share screen and work on a problem with an interviewer
   - They evaluate: communication, problem-solving approach, how you handle getting stuck
   - This is the highest-risk format if coding fluency is rusty
   - Practice: have a friend watch you code a small problem while you narrate your thinking
   - KEY INSIGHT: they care more about your thought process than perfect syntax. Talk through what you're doing.

3. **Code review exercise (possible)**
   - They show you a piece of code and ask you to review it
   - This plays to your strengths (you review a lot of code already)
   - Practice: review open PRs on FixMyStreet or Alaveteli

4. **System design / architecture discussion (possible)**
   - "How would you build X?" or "How would you improve Y?"
   - This plays to your strengths
   - Practice: be ready to discuss WealthLens architecture decisions

### Phase 3: Soft skills and mission alignment

#### Communication prep

- [ ] Prepare 2-minute versions of each STAR story (see application-specific files)
- [ ] Practice explaining a technical decision to a non-technical person (e.g., "why did you choose FastAPI over Django?")
- [ ] Prepare a 30-second pitch for WealthLens that a council worker would understand
- [ ] Practice answering "tell me about yourself" in under 90 seconds

#### Mission alignment prep

- [ ] Use FixMyStreet to report a real problem in your area
- [ ] Make a WhatDoTheyKnow FOI request about something you genuinely want to know
- [ ] Read 3-5 mySociety blog posts about technical decisions or civic impact
- [ ] Be ready to discuss: "How does removing barriers to democratic participation connect to what you do with WealthLens?"

---

## Common interview questions for UK civic tech developer roles

### Technical

1. "Walk me through how you'd build a feature for FixMyStreet that lets users track the status of their report."
2. "You inherit a Perl codebase you've never seen. Walk me through your first day."
3. "How would you write a test for an API endpoint that depends on an external service?"
4. "Describe a time you found and fixed a security vulnerability."
5. "How do you approach database schema changes in a production system?"
6. "What's the difference between unit tests, integration tests, and end-to-end tests? When would you use each?"
7. "How would you debug a performance issue on a busy web service?"
8. "Tell me about your experience with Linux servers and deployment."

### Behavioural / values

9. "Why mySociety? Why civic tech?"
10. "Describe a time you had to context-switch between multiple projects."
11. "Tell me about a time you translated something technical for a non-technical audience."
12. "How do you prioritise when you have too much to do?"
13. "Describe a time you disagreed with a technical decision. What happened?"
14. "How do you stay motivated working remotely?"
15. "What's your biggest weakness?" (Be honest. "I've been relying on AI tools and I'm actively rebuilding my unassisted coding speed" is a surprisingly strong answer if framed as self-awareness + action.)

### Role-specific

16. "How would you approach learning Perl?"
17. "What does good client support look like to you?"
18. "How do you balance feature development with maintenance and bug fixes?"
19. "Tell me about your experience with on-call or incident response."
20. "How do you write documentation that's actually useful?"

---

## The AI coding question -- how to handle it

If asked about AI tools in the interview (increasingly likely in 2026):

**DO say:**
- "I use AI tools as part of my workflow. I find them most valuable for boilerplate generation, test scaffolding, and exploring unfamiliar codebases."
- "I always review and understand generated code before committing. My security hardening sprint found vulnerabilities that AI tools had introduced."
- "I've found that AI makes me more productive at architecture and review, which is where I add the most value."
- "I'm conscious about maintaining my core coding skills and I practice writing code without assistance."

**DO NOT say:**
- "I use AI for everything" (implies you can't code without it)
- "AI writes most of my code" (red flag for any employer)
- Nothing at all (avoidance looks suspicious in 2026)

**Frame it as:** AI is one tool in your toolkit, like an IDE or a linter. You use it where it helps, you verify what it produces, and you maintain the judgment to know when it's wrong. The 150-finding security audit you led is proof that you don't blindly accept AI output.

---

## Resources

- mySociety GitHub: github.com/mysociety
- FixMyStreet codebase: github.com/mysociety/fixmystreet
- Alaveteli (WhatDoTheyKnow): github.com/mysociety/alaveteli
- TheyWorkForYou: github.com/mysociety/theyworkforyou
- mySociety blog: mysociety.org/blog
- Exercism Perl track: exercism.org/tracks/perl5
- Python practice: exercism.org/tracks/python

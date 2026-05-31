# CV Changes for mySociety Application

**Goal:** Anonymize + reframe for civic tech / Python developer role.
**Action:** Apply these changes to your LaTeX source, compile to PDF, upload.

---

## 1. Header — Anonymize

**Before:**
```
Cristian Tcaci
Software Engineer – Backend / Platform
London, UK | Jeky.tck@gmail.com | +44 7588 221922
linkedin.com/in/cristian-tcaci | github.com/Chris0Jeky | portfolio
```

**After:**
```
C.T.
Software Engineer – Python / Web
London, UK
```

Remove ALL contact info. The application form captures your real details separately.

---

## 2. Profile — Reframe for civic tech + Python

**Before:**
> Early-career software engineer focused on backend and platform work, with
> hands-on experience across enterprise CI/CD security, product development,
> and published research. At GE Digital, integrated automated scanning into
> ~72 AWS pipelines using Bash and Groovy; currently building local-first
> developer tooling and contract software solutions using C#, Java, Python,
> and TypeScript.

**After:**
> Early-career software engineer focused on Python, web development, and
> public-interest data. Built and deployed an open-source civic technology
> platform with a FastAPI backend, ten reproducible data pipelines, and a
> policy microsimulation engine (670+ tests). At GE Digital, integrated
> automated scanning into ~72 AWS CI/CD pipelines and maintained a legacy
> Smallworld/Magik codebase on the job. Published lead-author research in
> Springer proceedings.

---

## 3. Experience — Add WealthLens entry (near the top)

Insert this as the **second entry** (after DeliveraSoft or before it — your call on ordering):

```
Open-Source Civic Technology Project — Founder & Lead Developer
2025 – Present | London, UK

• Built a FastAPI backend serving data endpoints with security headers,
  rate limiting, GZip compression, and CSV download; deployed via GitHub
  Actions.
• Created ten reproducible data pipelines using Pandas to process ONS,
  HMRC, and WID public datasets with full source citations.
• Developed a policy microsimulation engine with 670+ passing tests,
  interval arithmetic, and provenance tracking.
• Frontend: Vue 3, TypeScript, TailwindCSS — 1,100+ tests, dark mode,
  WCAG AA accessibility compliance.
```

**Note:** I've kept the description generic (no project name) to stay
within the anonymization spirit. If you're comfortable with it being
identifiable via the description, you could add the name.

---

## 4. Experience — GE Digital: highlight the Magik/Perl angle

The existing GE Digital section is already strong. Consider making the
Smallworld/Magik bullet slightly more prominent since it directly maps to
their "willingness to learn Perl" requirement:

**Tweak the Magik bullet to:**
> Learned and maintained a legacy Smallworld/Magik codebase on the job
> (a language not previously encountered): fixed bugs, improved database
> interactions, added MUnit tests, and documented the system for onboarding.

The word "learned" at the start signals adaptability.

---

## 5. Selected Projects — Reframe fintech, consider trimming

**"Collaborative Fintech Strategy Platform"** — reframe slightly:
> Co-developing a data-driven strategy platform with a configurable engine
> parameterised from database-defined settings. Python, FastAPI, React,
> TypeScript.

(Removes "fintech" and "options" — frames it as systems/data work.)

**If you need space** for the new WealthLens experience entry, drop
**EduHub** (least relevant to this role) or condense the Leadership &
Service section.

---

## 6. Skills — Reorder for Python prominence

**Before:**
```
Languages: C#, Java, Python, TypeScript, JavaScript, Bash, Groovy, SQL
Backend / Platform: .NET, FastAPI, Node.js / Express, REST APIs, Jenkins,
  Docker, AWS, CI/CD, Git, Linux
Databases / Data: SQLite, PostgreSQL, MongoDB, Pandas, scikit-learn
Also: Smallworld/Magik, MUnit, testing, developer tools, secure automation,
  basic Kubernetes familiarity
```

**After:**
```
Languages: Python, JavaScript, TypeScript, SQL, Bash, Groovy, C#, Java
Backend / Web: FastAPI, Node.js / Express, REST APIs, Vue 3, React,
  HTML/CSS, TailwindCSS
Infrastructure: Docker, AWS, Jenkins, GitHub Actions, CI/CD, Git, Linux
Databases / Data: PostgreSQL, MySQL, SQLite, MongoDB, Pandas, scikit-learn
Testing: pytest, Vitest, Playwright E2E, Hypothesis, MUnit
Also: Smallworld/Magik, D3.js, secure automation, OpenTelemetry
```

Key changes:
- Python first in languages
- Added Vue 3, React, HTML/CSS, TailwindCSS (they want "clean, maintainable HTML, CSS, and JavaScript")
- PostgreSQL and MySQL before SQLite (they use PostgreSQL/MySQL)
- Dedicated testing line (they want "write and maintain test suites")
- GitHub Actions added (they'll care about CI/CD)
- Infrastructure as its own line (they mention "linux servers, load balancers, caches")

---

## 7. Publication — No changes needed

The publication section is already strong and directly relevant (shows
research communication ability). Keep as-is.

---

## 8. Leadership & Service — Condense if space is tight

If you need room for the new WealthLens entry, merge the two Middlesex
entries into one:

```
Middlesex University — Student Voice Leader & Ambassador
Nov 2024 – Jul 2025 | London, UK

• Gathered and presented student feedback to faculty boards; represented
  the university at information sessions and open days.
```

---

## Final checklist before compiling

- [ ] Name replaced with C.T.
- [ ] Email, phone, LinkedIn, GitHub, portfolio ALL removed
- [ ] Profile rewritten for Python / civic tech
- [ ] WealthLens experience entry added
- [ ] GE Digital Magik bullet tweaked
- [ ] Skills reordered (Python first, testing line added)
- [ ] Fits on 2 pages
- [ ] Spell-check
- [ ] Export to PDF

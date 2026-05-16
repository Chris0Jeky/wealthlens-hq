/* WealthLens UK — Landing page interactive bits
   Red / cream / ink black newsprint aesthetic. */

const LANDING_TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "palette": "frontpage",
  "headlineIndex": 0,
  "flowAnimate": true
}/*EDITMODE-END*/;

/* ============================================================ */
/* Hero headlines — second-order consequences, not just facts.  */
/* The point isn't "this is happening." It's "this is what it   */
/* costs you, in years, in family, in life."                    */
/* ============================================================ */
const HEADLINES = [
  {
    label: 'Cascade',
    title: ['Everything in your life is ', { it: 'ten years late' }, '.'],
    sub: <>Your parents bought a house at 24. Had you at 27. You'll be lucky to buy at 36 — if at all. So the family waits. The retirement waits. And in that twelve‑year gap, roughly <strong>£180,000 of your wages becomes someone else's mortgage</strong>. <span className="red">The clock didn't break. It was moved.</span></>,
    src: 'Source: UK Finance first‑time buyer age · ONS House Price Index · IFS 2024'
  },
  {
    label: 'Rent',
    title: ['You\'ll pay for ', { it: 'three houses' }, '. You\'ll own none.'],
    sub: <>Forty years of renting in a UK city ≈ <strong>£540,000</strong> in today's money. That's three average UK homes. It doesn't disappear — it becomes someone else's pension, someone else's holiday villa, someone else's child's deposit. <span className="red">Renting isn't a service. It's a transfer.</span></>,
    src: 'Source: ONS Private Rental Market 2024 · HM Land Registry'
  },
  {
    label: 'Wages',
    title: ['Your job pays what it did in ', { it: '2008' }, '. Life doesn\'t.'],
    sub: <>Real wages haven't grown in 16 years — Britain is the <strong>only G7 economy</strong> where this happened. Rent didn't sit still. Childcare didn't. Energy didn't. <span className="red">You're not bad with money. The maths was rewritten while you weren't looking.</span></>,
    src: 'Source: ONS AWE deflated by CPIH · IFS Living Standards 2024'
  },
  {
    label: 'Inheritance',
    title: ['By 2040, Britain will be ', { it: 'inherited' }, ', not earned.'],
    sub: <>£100 billion a year transferred through estates — and rising. If your parents own, you're set. If they don't, you're not, no matter the hours. <strong>Only 4–5% of estates pay any tax</strong> — the threshold hasn't moved since 2009. <span className="red">"Hard work pays" used to be a promise. It's a lottery ticket.</span></>,
    src: 'Source: HMRC IHT statistics · Resolution Foundation 2024'
  },
  {
    label: 'Tax',
    title: ['Britain taxes the ', { it: 'alarm clock' }, '. Not the inheritance.'],
    sub: <>Wages from work: up to <strong>47%</strong>. Capital gains: 10–28%. Inheritance under £325k: <strong>0%</strong>. The system charges you most for the one thing you actually control — your time. <span className="red">Effort is taxed. Luck is not.</span></>,
    src: 'Source: HMRC · IFS Tax Analysis 2024'
  },
];

/* ============================================================ */
/* Gut-feeling test — lead with the felt experience, then       */
/* deliver the number as a punch, then the second-order cost.   */
/* ============================================================ */
const GUT_CARDS = [
  {
    n: '01',
    q: 'Everyone I know is renting at thirty‑five.',
    stat: ['36 years.'],
    body: 'Median age of a UK first‑time buyer in 2024 — up from 24 in 1981. Twelve extra years renting before you start to own anything. Twelve years of saving for a deposit while the deposit keeps moving. Roughly £180,000 paid to someone else.',
    src: 'Source: UK Finance · ONS Housing Survey'
  },
  {
    n: '02',
    q: 'I work full‑time. I still can\'t save.',
    stat: ['16 years', { pct: ' flat.' }],
    body: 'Real UK wages have not grown since 2008 — the only G7 economy where this is true. Your salary buys what your older sister\'s did. Your rent does not. Your weekly shop does not. The deposit does not.',
    src: 'Source: ONS AWE, CPIH‑deflated · IFS Living Standards'
  },
  {
    n: '03',
    q: 'Money seems to be taxed less than work.',
    stat: [{ pct: '10%' }, ' vs ', { pct: '47%' }, '.'],
    body: 'Top capital‑gains rate vs top income‑tax rate. Inheriting £325,000 is taxed at 0%. Earning that same £325,000 is taxed at roughly £130,000. Britain prices effort higher than luck — by design.',
    src: 'Source: HMRC · Warwick Wealth Tax Commission 2020'
  },
  {
    n: '04',
    q: 'Half my pay goes on rent before I\'ve eaten.',
    stat: [{ pct: '41%' }, ' on rent.'],
    body: 'Pre‑tax income paid in rent by London renters aged 25–34. The WHO calls anything over 30% "housing stress." It\'s also the deposit you\'re not saving, the pension you\'re not topping up, the year off you\'ll never take, the family you keep postponing.',
    src: 'Source: ONS Private Rental Market 2024'
  },
  {
    n: '05',
    q: 'My future depends on whether my parents own a house.',
    stat: [{ pct: '£100bn' }, ' a year.'],
    body: 'Forecast annual inheritance transfer in the UK by 2040. Only 4–5% of estates pay any tax — the threshold hasn\'t moved since 2009. Britain is quietly becoming a hereditary economy. Whose parents you have decides whose life you get.',
    src: 'Source: HMRC IHT · Resolution Foundation 2024'
  },
  {
    n: '06',
    q: 'London might as well be a different country.',
    stat: [{ pct: '£79.5k' }, ' vs ', { pct: '£14.2k' }, '.'],
    body: 'Gross disposable income per head, Westminster vs Blackpool. Same currency. Same passport. Same NHS, in theory. Your postcode at 18 forecasts your retirement at 67 better than your A‑levels do.',
    src: 'Source: ONS Regional GDHI 2023'
  },
  {
    n: '07',
    q: 'I\'ll still be paying rent when I retire.',
    stat: ['1 in 3', { pct: ' renters at 70.' }],
    body: 'Projected share of UK pensioners in private rentals by 2040 — roughly triple today\'s. Renting in your seventies, when your wages are gone but your landlord is not. The state pension does not stretch to a London tenancy.',
    src: 'Source: Resolution Foundation Housing Outlook 2024'
  },
  {
    n: '08',
    q: 'My kids will live with us until they\'re thirty.',
    stat: [{ pct: '4.9 million' }, ' adults.'],
    body: 'UK adults aged 20–34 still living with parents — up 55% since 2000. Not because anyone is closer. Because the next flat costs three times what the spare room costs (£0), and the family they wanted gets paused with it.',
    src: 'Source: ONS Young Adults Living With Parents 2024'
  },
];

/* ============================================================ */
/* Hero wealth-flow visualisation                                */
/* "100 PEOPLE  →  £100 OF WEALTH." Sankey ribbons make the      */
/* split legible at first glance, before any reading happens.    */
/* ============================================================ */
const FLOW_GROUPS = [
  { p: 10, m: 57, colorVar: '--wl-red',       name: 'Top 10%',    perPerson: '£5.70 each',  hover: '10 households take more than 9 in 10 combined.' },
  { p: 40, m: 37, colorVar: '--wl-ink',       name: 'Middle 40%', perPerson: '£0.93 each',  hover: 'The squeezed middle. Owns a chunk — usually one house, leveraged.' },
  { p: 50, m: 6,  colorVar: '--wl-ink-faint', name: 'Bottom 50%', perPerson: '£0.12 each',  hover: '50 households share less than one household at the top.' },
];

function setupWealthFlow() {
  const stage = document.getElementById('lensStage');
  if (!stage) return;

  const W = 480, H = 600;
  const top = 110, bot = 540, barH = bot - top;
  const peopleX = 132, peopleW = 16;
  const moneyX = 332,  moneyW = 16;

  let pY = top, mY = top;
  const parts = [];

  // Headers
  parts.push(`
    <text x="${peopleX + peopleW/2}" y="56" text-anchor="middle" class="flow-h">100 PEOPLE</text>
    <text x="${peopleX + peopleW/2}" y="76" text-anchor="middle" class="flow-sub">UK households, sorted by wealth</text>
    <text x="${moneyX + moneyW/2}" y="56" text-anchor="middle" class="flow-h">£100 OF WEALTH</text>
    <text x="${moneyX + moneyW/2}" y="76" text-anchor="middle" class="flow-sub">every pound the UK owns</text>
  `);

  // Bracket markers (top and bottom)
  parts.push(`
    <line x1="${peopleX - 6}" y1="${top}" x2="${peopleX + peopleW + 6}" y2="${top}" stroke="var(--wl-ink)" stroke-width="1"/>
    <line x1="${peopleX - 6}" y1="${bot}" x2="${peopleX + peopleW + 6}" y2="${bot}" stroke="var(--wl-ink)" stroke-width="1"/>
    <line x1="${moneyX - 6}"  y1="${top}" x2="${moneyX + moneyW + 6}"  y2="${top}" stroke="var(--wl-ink)" stroke-width="1"/>
    <line x1="${moneyX - 6}"  y1="${bot}" x2="${moneyX + moneyW + 6}"  y2="${bot}" stroke="var(--wl-ink)" stroke-width="1"/>
  `);

  FLOW_GROUPS.forEach((g, i) => {
    const pY0 = pY, pY1 = pY + barH * g.p / 100;
    const mY0 = mY, mY1 = mY + barH * g.m / 100;
    const color = `var(${g.colorVar})`;

    // People bar segment
    parts.push(`<rect class="flow-bar" x="${peopleX}" y="${pY0}" width="${peopleW}" height="${pY1 - pY0}" fill="${color}"/>`);
    // Money bar segment
    parts.push(`<rect class="flow-bar" x="${moneyX}" y="${mY0}" width="${moneyW}" height="${mY1 - mY0}" fill="${color}"/>`);

    // Sankey ribbon (cubic bezier)
    const x0 = peopleX + peopleW, x1 = moneyX;
    const cx0 = x0 + (x1 - x0) * 0.55;
    const cx1 = x0 + (x1 - x0) * 0.45;
    const ribbon = `M ${x0} ${pY0}
                    C ${cx0} ${pY0}, ${cx1} ${mY0}, ${x1} ${mY0}
                    L ${x1} ${mY1}
                    C ${cx1} ${mY1}, ${cx0} ${pY1}, ${x0} ${pY1} Z`;
    parts.push(`<path class="flow-ribbon flow-ribbon-${i}" d="${ribbon}" fill="${color}" fill-opacity="${i === 0 ? 0.55 : i === 1 ? 0.32 : 0.18}"/>`);

    // Inline labels — left of people, right of money
    const pMidY = (pY0 + pY1) / 2;
    const mMidY = (mY0 + mY1) / 2;

    // PEOPLE side label
    parts.push(`
      <text x="${peopleX - 16}" y="${pMidY - 4}" text-anchor="end" class="flow-pcount" fill="${color}">${g.p}</text>
      <text x="${peopleX - 16}" y="${pMidY + 12}" text-anchor="end" class="flow-plabel">people</text>
    `);

    // MONEY side label
    parts.push(`
      <text x="${moneyX + moneyW + 16}" y="${mMidY - 4}" text-anchor="start" class="flow-mvalue" fill="${color}">£${g.m}</text>
      <text x="${moneyX + moneyW + 16}" y="${mMidY + 12}" text-anchor="start" class="flow-mlabel">${g.name}</text>
      <text x="${moneyX + moneyW + 16}" y="${mMidY + 26}" text-anchor="start" class="flow-mfine">${g.perPerson}</text>
    `);

    pY = pY1; mY = mY1;
  });

  // Footer — the punch line
  parts.push(`
    <line x1="40" y1="${H - 60}" x2="${W - 40}" y2="${H - 60}" stroke="var(--wl-rule)" stroke-width="1"/>
    <text x="${W / 2}" y="${H - 38}" text-anchor="middle" class="flow-punch">
      <tspan class="flow-punch-red">10 households</tspan>
      <tspan>own more than the other</tspan>
      <tspan class="flow-punch-bold"> 90</tspan>
      <tspan>combined.</tspan>
    </text>
    <text x="${W / 2}" y="${H - 16}" text-anchor="middle" class="flow-src">Source: ONS Wealth &amp; Assets Survey · WID UK · 2023</text>
  `);

  stage.innerHTML = `
    <svg viewBox="0 0 ${W} ${H}" class="flow-svg" preserveAspectRatio="xMidYMid meet" aria-label="Of every £100 of UK wealth, £57 goes to the top 10 households, £6 to the bottom 50.">
      ${parts.join('\n')}
    </svg>
    <div class="flow-corner-tag">
      <span class="dot"></span> If Britain were 100 households
    </div>
  `;

  // After mount, animate ribbons in by clip-path
  requestAnimationFrame(() => {
    const ribbons = stage.querySelectorAll('.flow-ribbon');
    ribbons.forEach((r, i) => {
      r.style.transformOrigin = 'left center';
      r.style.transform = 'scaleX(0)';
      r.style.transition = `transform 0.9s cubic-bezier(0.22, 0.7, 0.18, 1) ${0.15 + i * 0.18}s`;
      setTimeout(() => { r.style.transform = 'scaleX(1)'; }, 50);
    });
  });
}

/* ============================================================ */
/* Gut-feeling cards                                             */
/* ============================================================ */
function renderStatSegments(segs) {
  return segs.map(s => {
    if (typeof s === 'string') return s;
    if (s.pct) return `<span class="pct">${s.pct}</span>`;
    return '';
  }).join('');
}

function paintGutCards() {
  const root = document.getElementById('gutGrid');
  if (!root) return;
  root.innerHTML = GUT_CARDS.map(c => `
    <div class="gut-card" data-n="${c.n}" role="button" tabindex="0">
      <span class="num">${c.n}</span>
      <p class="gut-q">${c.q}</p>
      <div class="gut-answer">
        <div class="stat">${renderStatSegments(c.stat)}</div>
        <p>${c.body}</p>
        <div class="src">${c.src}</div>
      </div>
      <span class="gut-hint">↓ Tap to see the number</span>
    </div>
  `).join('');
  root.querySelectorAll('.gut-card').forEach(card => {
    card.addEventListener('click', () => card.classList.toggle('revealed'));
    card.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        card.classList.toggle('revealed');
      }
    });
  });
}

/* ============================================================ */
/* Pillar sparklines                                             */
/* ============================================================ */
const PILLARS = [
  {
    n: '01', name: 'Wealth',
    find: 'The <b>top 10%</b> own <b>57%</b> of everything — same as 1910, before the welfare state existed.',
    series: [42, 44, 47, 51, 53, 55, 56, 57], red: true
  },
  {
    n: '02', name: 'Housing',
    find: 'A house now costs <b>8.6×</b> average earnings. Your parents paid 3×. Same job. Same house.',
    series: [3.2, 3.5, 4.1, 4.8, 5.6, 6.9, 7.8, 8.6], red: true
  },
  {
    n: '03', name: 'Tax',
    find: '<b>92%</b> of capital gains flow to the top 1% — taxed lower than your salary.',
    donut: [92, 8]
  },
  {
    n: '04', name: 'Inheritance',
    find: 'Only <b>4–5%</b> of estates pay any tax. The threshold hasn\'t moved since 2009 — the year of the iPhone 3GS.',
    bars: [5, 95]
  },
  {
    n: '05', name: 'Place',
    find: 'Westminster: <b>£79.5k</b> per head. Blackpool: <b>£14.2k</b>. Same country. Same NHS, in theory.',
    columns: [{ v: 79.5, label: 'WSM' }, { v: 24.8, label: 'UK' }, { v: 14.2, label: 'BLA' }]
  },
];

function buildPillarCard(p) {
  let chart = '';
  if (p.series) {
    const W = 220, H = 60, pad = 4;
    const max = Math.max(...p.series);
    const xs = p.series.map((_, i) => pad + (i * (W - pad * 2)) / (p.series.length - 1));
    const ys = p.series.map(v => H - pad - ((v / max) * (H - pad * 2 - 6)));
    const d = xs.map((x, i) => `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${ys[i].toFixed(1)}`).join(' ');
    const color = p.red ? 'var(--wl-red)' : 'var(--wl-ink)';
    chart = `<svg class="pillar-chart" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none">
      <path d="${d}" stroke="${color}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
      <circle cx="${xs[xs.length - 1]}" cy="${ys[ys.length - 1]}" r="3.5" fill="${color}"/>
    </svg>`;
  } else if (p.donut) {
    const [a, b] = p.donut;
    const total = a + b, C = 2 * Math.PI * 22;
    const aLen = (a / total) * C;
    chart = `<svg class="pillar-chart" viewBox="0 0 220 60">
      <g transform="translate(30 30)">
        <circle r="22" cx="0" cy="0" fill="none" stroke="var(--wl-rule)" stroke-width="8"/>
        <circle r="22" cx="0" cy="0" fill="none" stroke="var(--wl-red)" stroke-width="8"
          stroke-dasharray="${aLen} ${C - aLen}" transform="rotate(-90)"/>
      </g>
      <text x="68" y="34" font-family="IBM Plex Mono" font-size="16" font-weight="600" fill="var(--wl-red)">${a}%</text>
      <text x="68" y="50" font-family="IBM Plex Mono" font-size="9" fill="var(--wl-ink-muted)">to top 1%</text>
    </svg>`;
  } else if (p.bars) {
    const [yes, no] = p.bars;
    chart = `<svg class="pillar-chart" viewBox="0 0 220 60">
      <rect x="0" y="22" width="${(yes / 100) * 220}" height="14" fill="var(--wl-red)"/>
      <rect x="${(yes / 100) * 220 + 2}" y="22" width="${(no / 100) * 220 - 2}" height="14" fill="var(--wl-rule)"/>
      <text x="0" y="16" font-family="IBM Plex Mono" font-size="9" fill="var(--wl-ink-muted)" letter-spacing="1">PAY IHT  ·  DON'T</text>
      <text x="0" y="52" font-family="IBM Plex Mono" font-size="11" font-weight="600" fill="var(--wl-red)">${yes}%</text>
      <text x="${(yes / 100) * 220 + 10}" y="52" font-family="IBM Plex Mono" font-size="11" fill="var(--wl-ink-muted)">${no}%</text>
    </svg>`;
  } else if (p.columns) {
    const maxV = Math.max(...p.columns.map(c => c.v));
    let bars = '';
    p.columns.forEach((c, i) => {
      const x = 18 + i * 70;
      const h = (c.v / maxV) * 40;
      const y = 50 - h;
      const fill = i === 0 ? 'var(--wl-red)' : 'var(--wl-ink)';
      bars += `<rect x="${x}" y="${y}" width="40" height="${h}" fill="${fill}"/>
        <text x="${x + 20}" y="58" text-anchor="middle" font-family="IBM Plex Mono" font-size="9" fill="var(--wl-ink-muted)">${c.label}</text>
        <text x="${x + 20}" y="${y - 4}" text-anchor="middle" font-family="IBM Plex Mono" font-size="10" font-weight="600" fill="${fill}">£${c.v}k</text>`;
    });
    chart = `<svg class="pillar-chart" viewBox="0 0 220 60">${bars}</svg>`;
  }

  return `
    <div class="pillar" role="link" tabindex="0">
      <div style="display:flex; align-items:center; justify-content:space-between;">
        <span class="pillar-num">${p.n}</span>
        <span class="pillar-link">→</span>
      </div>
      <div class="pillar-name">${p.name}</div>
      <div class="pillar-find">${p.find}</div>
      ${chart}
    </div>
  `;
}

function paintPillars() {
  const root = document.getElementById('pillarsGrid');
  if (!root) return;
  root.innerHTML = PILLARS.map(buildPillarCard).join('');
}

/* ============================================================ */
/* Featured chart                                                */
/* ============================================================ */
const WEALTH_SHARES = [
  [1820, 60, 86,  13, 1],
  [1840, 61, 87,  12, 1],
  [1860, 62, 88,  11, 1],
  [1880, 63, 89,  10, 1],
  [1900, 64, 90,   9, 1],
  [1910, 65, 90,   9, 1],
  [1920, 60, 85,  13, 2],
  [1930, 55, 81,  16, 3],
  [1940, 48, 75,  21, 4],
  [1950, 40, 70,  25, 5],
  [1960, 32, 63,  31, 6],
  [1970, 26, 56,  37, 7],
  [1980, 21, 50,  42, 8],
  [1985, 19, 49,  43, 8],
  [1990, 20, 50,  42, 8],
  [1995, 21, 52,  41, 7],
  [2000, 23, 54,  40, 6],
  [2005, 25, 56,  38, 6],
  [2010, 26, 58,  37, 5],
  [2015, 27, 58,  37, 5],
  [2020, 28, 57,  37, 6],
  [2023, 28, 57,  37, 6],
];

function drawFeatured(range) {
  const svg = document.getElementById('featuredChart');
  if (!svg) return;
  const W = 920, H = 420;
  const padL = 64, padR = 200, padT = 36, padB = 52;
  const minYear = range === 200 ? 1820 : range === 100 ? 1925 : range === 50 ? 1975 : 2000;
  const data = WEALTH_SHARES.filter(d => d[0] >= minYear);
  const xMin = data[0][0], xMax = data[data.length - 1][0];

  const x = y => padL + ((y - xMin) / (xMax - xMin)) * (W - padL - padR);
  const yScale = v => padT + (1 - v / 100) * (H - padT - padB);

  // gridlines
  const yTicks = [0, 25, 50, 75, 100];
  const grid = yTicks.map(t => `
    <line x1="${padL}" x2="${W - padR}" y1="${yScale(t)}" y2="${yScale(t)}"
      stroke="var(--wl-rule)" stroke-width="1"/>
    <text x="${padL - 10}" y="${yScale(t) + 4}" text-anchor="end"
      font-family="IBM Plex Mono" font-size="11" fill="var(--wl-ink-muted)">${t}%</text>
  `).join('');

  // x ticks
  const n = Math.min(7, data.length);
  const xTicks = Array.from({ length: n }, (_, i) => data[Math.round(i * (data.length - 1) / (n - 1))][0]);
  const xAxis = xTicks.map(t => `
    <line x1="${x(t)}" x2="${x(t)}" y1="${H - padB}" y2="${H - padB + 5}"
      stroke="var(--wl-ink)" stroke-width="1"/>
    <text x="${x(t)}" y="${H - padB + 22}" text-anchor="middle"
      font-family="IBM Plex Mono" font-size="11" fill="var(--wl-ink-muted)">${t}</text>
  `).join('');

  // Highlight the 50% line as the "50/50 floor"
  const fifty = `<line x1="${padL}" x2="${W - padR}" y1="${yScale(50)}" y2="${yScale(50)}"
    stroke="var(--wl-ink)" stroke-width="1" stroke-dasharray="4 4"/>
  <text x="${W - padR - 6}" y="${yScale(50) - 4}" text-anchor="end"
    font-family="IBM Plex Mono" font-size="10" fill="var(--wl-ink-muted)"
    letter-spacing="1">50% LINE · TOP 10% NEVER BELOW</text>`;

  // Eras shaded
  const eras = [
    { from: minYear, to: 1945, label: 'Aristocratic era' },
    { from: 1945, to: 1980, label: 'Post-war compression' },
    { from: 1980, to: xMax, label: 'Re-concentration' },
  ].filter(e => e.from < xMax && e.to > minYear);
  const eraBands = eras.map((e, i) => {
    const from = Math.max(e.from, minYear);
    const x0 = x(from), x1 = x(Math.min(e.to, xMax));
    if (x1 - x0 < 30) return '';
    return `
      <rect x="${x0}" y="${padT}" width="${x1 - x0}" height="${H - padT - padB}"
        fill="${i % 2 === 0 ? 'transparent' : 'var(--wl-paper-deep)'}" opacity="0.4"/>
      <text x="${(x0 + x1) / 2}" y="${padT + 14}" text-anchor="middle"
        font-family="IBM Plex Mono" font-size="9" fill="var(--wl-ink-muted)"
        letter-spacing="1.4" text-transform="uppercase">${e.label.toUpperCase()}</text>
    `;
  }).join('');

  // Series: Top 10% is the hero in red, Top 1% in ink, others muted
  const series = [
    { idx: 2, color: 'var(--wl-red)',      label: 'Top 10%',     w: 3.5, dim: false },
    { idx: 1, color: 'var(--wl-ink)',      label: 'Top 1%',      w: 2,   dim: false },
    { idx: 3, color: 'var(--wl-ink-faint)', label: 'Middle 40%', w: 1.2, dim: true },
    { idx: 4, color: 'var(--wl-ink-faint)', label: 'Bottom 50%', w: 1.2, dim: true },
  ];

  function path(idx) {
    return data.map((d, i) => `${i === 0 ? 'M' : 'L'} ${x(d[0]).toFixed(1)} ${yScale(d[idx]).toFixed(1)}`).join(' ');
  }

  // Draw dim series first, then ink, then red on top
  const drawOrder = [...series].sort((a, b) => (a.dim === b.dim ? 0 : a.dim ? -1 : 1));
  const paths = drawOrder.map(s => `
    <path d="${path(s.idx)}" stroke="${s.color}" stroke-width="${s.w}" fill="none"
      stroke-linejoin="round" stroke-linecap="round"
      ${s.dim ? 'stroke-dasharray="3 2" opacity="0.7"' : ''}/>
  `).join('');

  // Right-side direct labels
  const last = data[data.length - 1];
  const labels = series.map(s => `
    <g transform="translate(${W - padR + 14} ${yScale(last[s.idx])})">
      <line x1="-8" x2="0" y1="0" y2="0" stroke="${s.color}" stroke-width="${s.w}"/>
      <text x="8" y="4" font-family="IBM Plex Sans" font-size="13" font-weight="600" fill="${s.color}">${s.label}</text>
      <text x="8" y="20" font-family="IBM Plex Mono" font-size="11" fill="var(--wl-ink-muted)">${last[s.idx]}% · ${last[0]}</text>
    </g>
  `).join('');

  svg.innerHTML = `
    <defs><clipPath id="clipChart"><rect x="${padL}" y="${padT}" width="${W - padL - padR}" height="${H - padT - padB}"/></clipPath></defs>
    ${eraBands}
    ${grid}
    ${xAxis}
    ${fifty}
    <g clip-path="url(#clipChart)">${paths}</g>
    ${labels}
    <text x="${padL}" y="22" font-family="IBM Plex Mono" font-size="10"
      fill="var(--wl-ink-muted)" letter-spacing="2">SHARE OF NET PERSONAL WEALTH (%) · ${xMin}–${xMax}</text>
    <line x1="${padL}" x2="${padL}" y1="${padT}" y2="${H - padB}" stroke="var(--wl-ink)" stroke-width="1"/>
    <line x1="${padL}" x2="${W - padR}" y1="${H - padB}" y2="${H - padB}" stroke="var(--wl-ink)" stroke-width="1"/>
  `;
}

function setupRangeButtons() {
  const buttons = document.querySelectorAll('.range');
  buttons.forEach(btn => {
    btn.addEventListener('click', () => {
      buttons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      drawFeatured(parseInt(btn.dataset.range, 10));
    });
  });
}

/* ============================================================ */
/* Hero copy swap                                                */
/* ============================================================ */
function paintHero(idx) {
  const h = HEADLINES[idx] || HEADLINES[0];
  const elH = document.getElementById('heroHeadline');
  const elS = document.getElementById('heroSub');
  const elSrc = document.getElementById('heroSources');
  if (!elH) return;

  let html = '';
  h.title.forEach(seg => {
    if (typeof seg === 'string') html += seg;
    else if (seg.it) html += `<em>${seg.it}</em>`;
    else if (seg.u)  html += `<span class="underline">${seg.u}</span>`;
  });
  elH.innerHTML = html;

  const sub = document.createElement('div');
  ReactDOM.createRoot(sub).render(h.sub);
  elS.innerHTML = sub.innerHTML;
  if (elSrc) elSrc.textContent = h.src;
}

/* ============================================================ */
/* Tweaks panel                                                  */
/* ============================================================ */
const { useEffect } = React;

function applyPalette(p) {
  if (p === 'frontpage') document.documentElement.removeAttribute('data-theme');
  else document.documentElement.setAttribute('data-theme', p);
}

function LandingTweaks() {
  const [t, setTweak] = useTweaks(LANDING_TWEAK_DEFAULTS);

  useEffect(() => { applyPalette(t.palette); }, [t.palette]);
  useEffect(() => { paintHero(t.headlineIndex); }, [t.headlineIndex]);
  useEffect(() => {
    const stage = document.getElementById('lensStage');
    if (!stage) return;
    stage.classList.toggle('flow-animate-off', !t.flowAnimate);
  }, [t.flowAnimate]);

  return (
    <TweaksPanel title="Tweaks">
      <TweakSection label="Palette">
        <TweakRadio
          label="Theme"
          value={t.palette}
          onChange={v => setTweak('palette', v)}
          options={[
            { value: 'frontpage', label: 'Front Page' },
            { value: 'dark', label: 'Late Edition' },
            { value: 'stark', label: 'Stark' },
          ]}
        />
      </TweakSection>
      <TweakSection label="Hero headline">
        <TweakSelect
          label="Lead story"
          value={t.headlineIndex}
          onChange={v => setTweak('headlineIndex', parseInt(v, 10))}
          options={HEADLINES.map((h, i) => ({
            value: i,
            label: `${i + 1}. ${h.label}`
          }))}
        />
      </TweakSection>
      <TweakSection label="Motion">
        <TweakToggle
          label="Animate the flow on load"
          value={t.flowAnimate}
          onChange={v => setTweak('flowAnimate', v)}
        />
      </TweakSection>
    </TweaksPanel>
  );
}

/* ============================================================ */
/* Live rent ticker — the country-wide £ paid to private        */
/* landlords since you opened this page.                         */
/* Private rental sector revenue ≈ £85bn/yr ≈ £2,695/sec.        */
/* ============================================================ */
function startRentTicker() {
  const el = document.getElementById('rentTicker');
  const elTime = document.getElementById('rentTickerTime');
  if (!el) return;
  const RATE_PER_MS = 85_000_000_000 / (365.25 * 24 * 60 * 60 * 1000); // £/ms
  const start = Date.now();
  function tick() {
    const elapsed = Date.now() - start;
    const paid = Math.floor(elapsed * RATE_PER_MS);
    el.textContent = '£' + paid.toLocaleString('en-GB');
    if (elTime) {
      const secs = Math.floor(elapsed / 1000);
      const mm = String(Math.floor(secs / 60)).padStart(2, '0');
      const ss = String(secs % 60).padStart(2, '0');
      elTime.textContent = `${mm}:${ss}`;
    }
  }
  tick();
  // setInterval (not rAF) so the ticker keeps running when the iframe
  // is off-screen inside the design canvas. Every 100ms is plenty to feel live.
  setInterval(tick, 100);
}

/* ============================================================ */
/* Init                                                          */
/* ============================================================ */
function initLanding() {
  setupWealthFlow();
  paintGutCards();
  paintPillars();
  drawFeatured(100);
  setupRangeButtons();
  startRentTicker();

  const root = document.getElementById('tweaks-root');
  if (root && window.TweaksPanel) {
    ReactDOM.createRoot(root).render(<LandingTweaks />);
  }
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initLanding);
} else {
  initLanding();
}

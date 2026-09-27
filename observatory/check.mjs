// Verifies the vendored Pulseboard SDK v3 artifact (Pulseboard#105) against observatory.lock.json.
// Run from the repository root: node observatory/check.mjs
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
const root = new URL('../', import.meta.url);
// The build derives the adapter's `?v=` URL version from these same bytes (#604).
const versioner = new URL('projects/wealthlens-dashboard/frontend/scripts/observatory-version.mjs', root);
const { observatoryDigest, readObservatoryVersion, OBSERVATORY_VERSION_LENGTH } = await import(versioner.href);
const lock = JSON.parse(readFileSync(new URL('observatory.lock.json', root), 'utf8'));
// The SDK version comes from the lock, so an automatic SDK update that rewrites the lock needs no edit here.
const SDK_VERSION = lock.sdk;
assert.match(SDK_VERSION, /^\d+\.\d+\.\d+$/, 'The lock must record the SDK version');
const SDK_VERSION_RE = SDK_VERSION.replaceAll('.', '\\.');
const COLLECTOR = 'https://pulseboard-observatory.commit-atlas.workers.dev';
const ORIGIN = 'https://chris0jeky.github.io';
const targets = Object.entries(lock.installs ?? {});
assert.ok(targets.length > 0, 'The lock records no installed artifact');

/** A minimal element: enough for the SDK's placeholder release and DOM-ready wait. */
function element(tag) {
  const attrs = new Map();
  return { tagName: tag, style: {}, children: [], attrs,
    setAttribute(k, v) { attrs.set(k, String(v)); }, removeAttribute(k) { attrs.delete(k); },
    hasAttribute(k) { return attrs.has(k); }, getAttribute(k) { return attrs.get(k) ?? null; },
    append(...nodes) { this.children.push(...nodes); }, addEventListener() {} };
}

/** A fake window. Every network, timer and storage touch is recorded so the check can assert on it. */
function runtime({ origin, readyState }) {
  const calls = [];
  const listeners = new Map();
  const placeholder = element('div');
  placeholder.style.minHeight = '2.5rem';
  const body = element('body');
  const storage = () => ({ getItem() { calls.push('storage'); return null; }, setItem() { calls.push('storage'); }, removeItem() {} });
  const document = { readyState, body, visibilityState: 'visible', referrer: '',
    querySelector: sel => (sel === '[data-pulseboard-bar]' ? placeholder : null),
    createElement: element,
    addEventListener(type, fn) { listeners.set(type, fn); } };
  const url = new URL('/wealthlens-hq/', origin);
  const context = { document, location: { origin: url.origin, protocol: url.protocol, href: url.href, pathname: url.pathname, search: '' },
    navigator: {}, localStorage: storage(), sessionStorage: storage(),
    fetch() { calls.push('fetch'); return new Promise(() => {}); },
    setTimeout() { calls.push('timer'); return 0; }, clearTimeout() {},
    addEventListener() {}, matchMedia: () => ({ matches: false }), innerWidth: 1280 };
  return { context, calls, listeners, placeholder };
}

for (const [target, owned] of targets) {
  assert.equal(owned.project, 'wealthlens');
  // Read as text and normalise: a CRLF checkout must not silently change the digest the lock pins.
  const code = readFileSync(new URL(target, root), 'utf8').replaceAll('\r\n', '\n');
  assert.equal(createHash('sha256').update(code).digest('hex'), owned.sha256, 'Artifact bytes differ from the lock');
  assert.equal(observatoryDigest(code), owned.sha256, 'Build-time digest rule diverged from the lock rule');
  assert.equal(readObservatoryVersion(fileURLToPath(new URL(target, root))), owned.sha256.slice(0, OBSERVATORY_VERSION_LENGTH),
    'The adapter URL version must be the locked digest prefix');

  const header = code.split('\n').slice(0, 3).join('\n');
  assert.match(header, new RegExp('pulseboard-sdk ' + SDK_VERSION_RE + ' for wealthlens\\b'), `Header must name pulseboard-sdk ${SDK_VERSION} for wealthlens`);
  const bodyHash = /sha256 of the body below: ([0-9a-f]{64})/.exec(header)?.[1];
  const body = code.slice(code.indexOf('*/\n') + 3);
  assert.equal(createHash('sha256').update(body).digest('hex'), bodyHash, 'The artifact was edited after generation');
  const config = JSON.parse(/\nconst config = (\{.*\});\n/.exec(code)?.[1] ?? 'null');
  assert.equal(config?.id, 'wealthlens');
  assert.equal(config.origin, ORIGIN);
  assert.equal(config.collector, COLLECTOR);
  assert.deepEqual(config.project.routes, ['home']);
  assert.doesNotMatch(code, /MAX_BYTES|MAX_BATCH/, 'Server constants must not ship in the browser artifact');

  // On the registered origin, before DOMContentLoaded: the API exists and nothing has been sent or stored.
  const live = runtime({ origin: ORIGIN, readyState: 'loading' });
  vm.runInNewContext(code, live.context);
  const api = live.context.Pulseboard;
  assert.equal(api?.version, SDK_VERSION);
  assert.deepEqual(Object.keys(api), ['version', 'route', 'count', 'track', 'consent']);
  assert.equal(live.calls.includes('fetch'), false, 'No network call before mount');
  assert.equal(live.listeners.has('DOMContentLoaded'), true, 'Mount waits for the DOM');
  assert.equal(live.placeholder.hasAttribute('hidden'), false, 'The reserved bar space is untouched before mount');

  // On any other origin (local preview, CI, forks) the SDK is inert: no request, no storage, placeholder released.
  const local = runtime({ origin: 'http://127.0.0.1:4173', readyState: 'complete' });
  vm.runInNewContext(code, local.context);
  assert.equal(local.context.Pulseboard.version, SDK_VERSION);
  assert.equal(local.context.Pulseboard.track('page.view', {}), false);
  assert.deepEqual(local.calls, [], 'An inert SDK makes no network, timer or storage call');
  assert.equal(local.placeholder.hasAttribute('hidden'), true, 'An inert SDK releases the reserved bar space');
  assert.equal(local.placeholder.style.minHeight, '0');
}
console.log('Pulseboard SDK ' + SDK_VERSION + ': lock hash, header, collector origin, URL version, pre-mount silence and inert fallback passed. Full host CI remains required.');

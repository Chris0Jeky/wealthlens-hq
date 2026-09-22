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
// The lock is keyed by target since Pulseboard #15; the original single-entry shape still reads.
const installs = lock.installs ?? { [lock.target]: { project: lock.project, sha256: lock.sha256 } };
const targets = Object.entries(installs);
assert.ok(targets.length > 0, 'The lock records no installed artifact');
for (const [target, owned] of targets) {
  // Read as bytes: a CRLF checkout must not silently change the digest the lock pins.
  const code = readFileSync(new URL(target, root), 'utf8').replaceAll('\r\n', '\n');
  assert.equal(createHash('sha256').update(code).digest('hex'), owned.sha256);
  assert.equal(observatoryDigest(code), owned.sha256, 'Build-time digest rule diverged from the lock rule');
  assert.equal(readObservatoryVersion(fileURLToPath(new URL(target, root))), owned.sha256.slice(0, OBSERVATORY_VERSION_LENGTH),
    'The adapter URL version must be the locked digest prefix');
  assert.ok(code.includes('"endpoint":""'), 'Activation requires a separate reviewed change');
  const context = { document: { readyState: 'complete' }, fetch() { throw new Error('Unexpected network'); }, setTimeout() { throw new Error('Unexpected timer'); } };
  vm.runInNewContext(code, context);
  assert.equal(context.PulseboardUsage, null);
}
console.log('Observer hash, URL version and inactive runtime passed. Full host CI remains required.');

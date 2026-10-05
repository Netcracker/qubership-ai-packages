import assert from 'node:assert/strict';
import { test } from 'node:test';
import { ensureBytes } from './stream.mjs';

test('planned assertion made through the module', async (t) => {
  t.plan(1);
  await Promise.resolve();
  assert.strictEqual(ensureBytes(0), 0);
});

test('planned assertion made through t.assert', async (t) => {
  t.plan(1);
  await Promise.resolve();
  t.assert.strictEqual(ensureBytes(0), 0);
});

test('planned assertion behind a missing await', async (t) => {
  t.plan(1);
  // The assertion runs after a timer that nothing awaits, so the test has ended by then.
  new Promise((resolve) => setTimeout(resolve, 10)).then(() => t.assert.strictEqual(ensureBytes(0), 0));
});

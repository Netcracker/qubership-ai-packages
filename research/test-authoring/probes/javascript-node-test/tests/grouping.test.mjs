import assert from 'node:assert/strict';
import { test } from 'node:test';
import { ensureBytes } from './stream.mjs';

test('two assertions on one result', () => {
  const result = ensureBytes(-1);
  assert.strictEqual(result, 0, 'first');
  assert.ok(result > 0, 'second');
});

test('one deepStrictEqual over the fields', () => {
  const result = { count: ensureBytes(-1), sign: Math.sign(ensureBytes(-1)) };
  assert.deepStrictEqual(result, { count: 0, sign: 0 });
});

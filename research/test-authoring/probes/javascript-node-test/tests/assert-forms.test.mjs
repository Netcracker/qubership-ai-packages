import assert from 'node:assert/strict';
import { test } from 'node:test';
import { ensureBytes } from './stream.mjs';

test('strictEqual', () => {
  assert.strictEqual(ensureBytes(-1), 0);
});

test('strictEqual with a message', () => {
  assert.strictEqual(ensureBytes(-1), 0, 'ensureBytes(-1)');
});

test('strictEqual with the operands swapped', () => {
  assert.strictEqual(0, ensureBytes(-1));
});

test('deepStrictEqual', () => {
  assert.deepStrictEqual({ count: ensureBytes(-1), unit: 'B' }, { count: 0, unit: 'B' });
});

test('ok', () => {
  assert.ok(ensureBytes(-1) === 0);
});

test('ok with a message', () => {
  assert.ok(ensureBytes(-1) === 0, 'ensureBytes(-1) must return 0');
});

test('fail', () => {
  assert.fail();
});

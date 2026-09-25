import assert from 'node:assert/strict';
import { test } from 'node:test';
import { ensureBytes } from './stream.mjs';

test('throws with another error type', () => {
  // ensureBytes(-1) returns a number, and reading a property of undefined throws a TypeError.
  assert.throws(() => ensureBytes(-1).unit.name, RangeError);
});

test('throws when nothing is thrown', () => {
  assert.throws(() => ensureBytes(-1), RangeError);
});

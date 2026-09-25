import assert from 'node:assert/strict';
import { test } from 'node:test';
import { ensureBytes } from './stream.mjs';

test.each([-1, -2])('ensureBytes(%i) is refused', (n) => {
  assert.strictEqual(ensureBytes(n), 0);
});

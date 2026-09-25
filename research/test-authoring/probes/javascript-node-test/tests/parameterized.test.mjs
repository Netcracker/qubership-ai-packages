import assert from 'node:assert/strict';
import { describe, test } from 'node:test';
import { ensureBytes } from './stream.mjs';

describe('ensureBytes', () => {
  for (const n of [-1, -2]) {
    test(`ensureBytes(${n}) is refused`, () => {
      assert.strictEqual(ensureBytes(n), 0);
    });
  }
});

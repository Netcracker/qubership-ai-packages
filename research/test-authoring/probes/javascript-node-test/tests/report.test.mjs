import assert from 'node:assert/strict';
import { describe, it } from 'node:test';
import { ensureBytes } from './stream.mjs';

describe('ensureBytes', () => {
  describe('with a negative count', () => {
    it('returns zero', () => {
      assert.strictEqual(ensureBytes(-1), 0);
    });
  });
  it('passes a positive count through', () => {
    assert.strictEqual(ensureBytes(1), 1);
  });
});

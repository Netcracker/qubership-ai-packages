import assert from 'node:assert/strict';
import { test } from 'node:test';
import { ensureBytes } from './stream.mjs';

test('calls an assertion that does not exist', () => {
  assert.noSuchCall(ensureBytes(-1), 0);
});

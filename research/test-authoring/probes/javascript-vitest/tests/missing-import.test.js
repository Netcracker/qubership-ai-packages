import { expect, noSuchExport, test } from 'vitest';
import { ensureBytes } from '../src/stream.js';

test('an export this release does not have', () => {
  noSuchExport();
  expect(ensureBytes(-1)).toBe(0);
});

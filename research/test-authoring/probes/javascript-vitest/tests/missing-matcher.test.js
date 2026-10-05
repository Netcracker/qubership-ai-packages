import { expect, test } from 'vitest';
import { ensureBytes } from '../src/stream.js';

test('a matcher this release does not have', () => {
  expect(ensureBytes(-1)).toBeNoSuchMatcher(0);
});

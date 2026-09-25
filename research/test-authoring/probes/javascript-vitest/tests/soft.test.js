import { expect, test } from 'vitest';
import { ensureBytes } from '../src/stream.js';

test('bare expect calls', () => {
  const result = ensureBytes(-1);
  expect(result, 'first').toBe(0);
  expect(result, 'second').toBeGreaterThan(0);
});

test('expect.soft calls', () => {
  const result = ensureBytes(-1);
  expect.soft(result, 'first').toBe(0);
  expect.soft(result, 'second').toBeGreaterThan(0);
});

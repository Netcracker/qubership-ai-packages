import { expect, test } from 'vitest';
import { ensureBytes } from '../src/stream.js';

// A promise that never settles stands for work that finishes after the test has returned: the callback, and the
// assertion in it, never run while the test is being counted.
function never(value) {
  return new Promise(() => {}).then(() => value);
}

test('forgotten await with expect.assertions', async () => {
  expect.assertions(1);
  never(ensureBytes(-1)).then((result) => expect(result).toBe(0));
});

test('forgotten await with expect.hasAssertions', async () => {
  expect.hasAssertions();
  never(ensureBytes(-1)).then((result) => expect(result).toBe(0));
});

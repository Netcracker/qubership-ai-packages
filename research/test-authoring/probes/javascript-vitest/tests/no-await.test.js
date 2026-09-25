import { expect, test } from 'vitest';
import { ensureBytes } from '../src/stream.js';

// The same forgotten await as in assertions.test.js, with nothing that counts the assertions.
function never(value) {
  return new Promise(() => {}).then(() => value);
}

test('forgotten await', async () => {
  never(ensureBytes(-1)).then((result) => expect(result).toBe(0));
});

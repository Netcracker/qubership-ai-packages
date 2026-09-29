const { ensureBytes } = require('./stream');

expect.extend({
  toBeRefusedCount(received) {
    return {
      pass: received === 0,
      message: () => `ensureBytes returned ${received} for a negative count instead of 0`,
    };
  },
});

test('a second argument to expect', () => {
  expect(ensureBytes(-1), 'ensureBytes(-1)').toBe(0);
});

test('a custom matcher from expect.extend', () => {
  expect(ensureBytes(-1)).toBeRefusedCount();
});

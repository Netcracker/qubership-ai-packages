const { ensureBytes } = require('./stream');

test('expect.soft', () => {
  expect.soft(ensureBytes(-1)).toBe(0);
  expect.soft(ensureBytes(-2)).toBe(0);
});

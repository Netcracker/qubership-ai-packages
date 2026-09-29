const { ensureBytes } = require('./stream');

test.eachh([[-1]])('ensureBytes(%d) is refused', (n) => {
  expect(ensureBytes(n)).toBe(0);
});

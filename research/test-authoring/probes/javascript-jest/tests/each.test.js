const { ensureBytes } = require('./stream');

describe('ensureBytes', () => {
  test.each([[-1], [-2]])('ensureBytes(%d) is refused', (n) => {
    expect(ensureBytes(n)).toBe(0);
  });

  test.each([['minus one', -1, { n: -1 }, { n: -1 }]])('%s: %p %j %o, case %#', (name, n) => {
    expect(ensureBytes(n)).toBe(0);
  });

  test.each([{ name: 'minus one', value: { path: -1 } }])('$name via $value.path', ({ value }) => {
    expect(ensureBytes(value.path)).toBe(0);
  });

  test.each([[-1], [-1]])('duplicate %d', (n) => {
    expect(ensureBytes(n)).toBe(0);
  });
});

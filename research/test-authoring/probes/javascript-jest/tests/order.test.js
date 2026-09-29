const { ensureBytes } = require('./stream');

describe('ensureBytes', () => {
  for (const n of [-1, -2, -3, -4, -5, -6]) {
    test(`case ${n}`, () => {
      expect(ensureBytes(n)).toBe(n);
    });
  }
});

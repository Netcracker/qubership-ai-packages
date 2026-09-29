const { ensureBytes } = require('./stream');

describe('ensureBytes', () => {
  describe('with a negative count', () => {
    it('returns zero', () => {
      expect(ensureBytes(-1)).toBe(0);
    });
  });
});

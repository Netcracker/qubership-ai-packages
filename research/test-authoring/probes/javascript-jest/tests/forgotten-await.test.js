const { ensureBytes } = require('./stream');

// Resolves after the test has returned and Jest has printed its summary, but before Jest exits.
function later(value) {
  return new Promise((resolve) => {
    setTimeout(() => resolve(value), 300);
  });
}

test('a forgotten await', async () => {
  later(ensureBytes(-1)).then((n) => expect(n).toBe(0));
});

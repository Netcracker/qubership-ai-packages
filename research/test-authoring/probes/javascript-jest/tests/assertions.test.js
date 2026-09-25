const { ensureBytes } = require('./stream');

// Never settles, so the assertion chained on it without await does not run, during the test or after it.
function never() {
  return new Promise(() => {});
}

test('a forgotten await under expect.assertions', async () => {
  expect.assertions(1);
  never().then(() => expect(ensureBytes(-1)).toBe(0));
});

test('a forgotten await under expect.hasAssertions', async () => {
  expect.hasAssertions();
  never().then(() => expect(ensureBytes(-1)).toBe(0));
});

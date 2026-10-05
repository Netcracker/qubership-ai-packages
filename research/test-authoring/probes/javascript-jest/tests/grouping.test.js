const { ensureBytes } = require('./stream');

test('two assertions on one result', () => {
  const result = { count: ensureBytes(-1), unit: 'byte' };
  expect(result.count).toBe(0);
  expect(result.unit).toBe('bytes');
});

test('the whole object with toEqual', () => {
  const result = { count: ensureBytes(-1), unit: 'byte' };
  expect(result).toEqual({ count: 0, unit: 'bytes' });
});

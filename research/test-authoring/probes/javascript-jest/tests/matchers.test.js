const { ensureBytes } = require('./stream');

test('toBe', () => {
  expect(ensureBytes(-1)).toBe(0);
});

test('toEqual', () => {
  expect({ a: 1, b: 2 }).toEqual({ a: 1, b: 3 });
});

test('boolean toBe(true)', () => {
  expect(ensureBytes(-1) === 0).toBe(true);
});

test('boolean toBeTruthy', () => {
  expect(ensureBytes(-1) === 0).toBeTruthy();
});

test('toThrow, another type thrown', () => {
  expect(() => {
    throw new TypeError('boom');
  }).toThrow(RangeError);
});

test('toThrow, nothing thrown', () => {
  expect(() => ensureBytes(-1)).toThrow(RangeError);
});

test('swapped operands', () => {
  expect(0).toBe(ensureBytes(-1));
});

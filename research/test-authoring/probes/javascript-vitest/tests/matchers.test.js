import { expect, test } from 'vitest';
import { ensureBytes } from '../src/stream.js';

test('toBe', () => {
  expect(ensureBytes(-1)).toBe(0);
});

test('toBe with a message', () => {
  expect(ensureBytes(-1), 'ensureBytes(-1)').toBe(0);
});

test('toBe with the operands reversed', () => {
  expect(0).toBe(ensureBytes(-1));
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

test('toThrow with another error type', () => {
  expect(() => {
    throw new TypeError('count must not be negative: -1');
  }).toThrow(RangeError);
});

test('toThrow when nothing is thrown', () => {
  expect(() => ensureBytes(-1)).toThrow(RangeError);
});

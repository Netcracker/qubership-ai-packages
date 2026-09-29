import { afterAll, expect, test } from 'vitest';

// Every test records its name; the hook fails on purpose so the report shows the order the tests ran in.
const order = [];

afterAll(() => {
  expect(order).toEqual([]);
});

test('one', () => order.push('one'));
test('two', () => order.push('two'));
test('three', () => order.push('three'));
test('four', () => order.push('four'));
test('five', () => order.push('five'));

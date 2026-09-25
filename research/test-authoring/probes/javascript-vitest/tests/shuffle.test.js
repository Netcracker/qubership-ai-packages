import { expect, test } from 'vitest';

// Every test passes, so a run with a random seed prints the same report whatever order it picks.
test('one', () => expect(1).toBe(1));
test('two', () => expect(2).toBe(2));
test('three', () => expect(3).toBe(3));

import { describe, expect, test } from 'vitest';
import { ensureBytes } from '../src/stream.js';

// One table per placeholder, so the report shows what each one formats on its own.
describe('ensureBytes', () => {
  test.each([[-1], [-2]])('ensureBytes(%d) is refused', (n) => {
    expect(ensureBytes(n)).toBe(0);
  });

  test.each([['minus one', -1]])('placeholder s: %s', (_name, n) => {
    expect(ensureBytes(n)).toBe(0);
  });

  test.each([[{ count: -1 }]])('placeholder p: %p', ({ count }) => {
    expect(ensureBytes(count)).toBe(0);
  });

  test.each([[{ count: -1 }]])('placeholder j: %j', ({ count }) => {
    expect(ensureBytes(count)).toBe(0);
  });

  test.each([[{ count: -1 }]])('placeholder o: %o', ({ count }) => {
    expect(ensureBytes(count)).toBe(0);
  });

  test.each([[-1], [-2]])('placeholder #: case %#', (n) => {
    expect(ensureBytes(n)).toBe(0);
  });

  test.each([{ name: 'minus one', value: { count: -1 } }])('$name with count $value.count', ({ value }) => {
    expect(ensureBytes(value.count)).toBe(0);
  });

  test.for([[-1], [-2]])('test.for: ensureBytes(%d) is refused', ([n]) => {
    expect(ensureBytes(n)).toBe(0);
  });
});

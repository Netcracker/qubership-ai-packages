import { describe, expect, it } from 'vitest';
import { ensureBytes } from '../src/stream.js';

describe('ensureBytes', () => {
  it('refuses a negative count', () => {
    expect(ensureBytes(-1)).toBe(0);
  });
});

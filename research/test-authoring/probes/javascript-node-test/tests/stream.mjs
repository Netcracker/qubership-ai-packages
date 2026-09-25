// The function under test in every probe. It returns its argument instead of refusing a negative count.
export function ensureBytes(count) {
  return count;
}

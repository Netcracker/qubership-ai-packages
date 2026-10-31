```ts
export const DEFAULT_TIMEOUT_SECONDS = 30;

/**
 * Largest entry size {@link EntryCache.put} accepts: 1 MiB (1048576 bytes).
 */
export const MAX_ENTRY_BYTES = 1 << 20;

/**
 * Signals an entry larger than {@link MAX_ENTRY_BYTES}.
 *
 * @remarks
 * Match it with `instanceof` or by its `code`, `"ENTRY_TOO_LARGE"`.
 */
export class EntryTooLargeError extends Error {
  readonly code = "ENTRY_TOO_LARGE";
}

/**
 * Holds byte entries in memory under string keys.
 *
 * @remarks
 * The cache stores each array by reference and does not copy it, so a caller that changes an array
 * after storing it changes the cached entry. It has no limit on the number of entries and removes
 * one only through {@link EntryCache.evict}.
 */
export class EntryCache {
  retries = 3;

  readonly #name: string;
  readonly #entries = new Map<string, Uint8Array>();
  #evictedBytes = 0;
  #lastEvictionMs: number | undefined;

  constructor(name: string) {
    this.#name = name;
  }

  get name(): string {
    return this.#name;
  }

  /**
   * Stores an entry under a key, replacing any entry already there.
   *
   * @throws {@link EntryTooLargeError} when `value` is longer than {@link MAX_ENTRY_BYTES}. The cache is left unchanged.
   */
  put(key: string, value: Uint8Array): void {
    if (value.byteLength > MAX_ENTRY_BYTES) {
      throw new EntryTooLargeError(`entry ${key} is ${value.byteLength} bytes, limit ${MAX_ENTRY_BYTES}`);
    }
    this.#entries.set(key, value);
  }

  /**
   * Removes the entry stored under a key.
   *
   * @remarks
   * A key with no entry is ignored and does not change {@link EntryCache.msSinceLastEviction}.
   */
  evict(key: string): void {
    const removed = this.#entries.get(key);
    if (removed !== undefined) {
      this.#entries.delete(key);
      this.#evictedBytes += removed.byteLength;
      this.#lastEvictionMs = Date.now();
    }
  }

  /**
   * Returns the milliseconds since {@link EntryCache.evict} last removed an entry, or `undefined` if it never has.
   *
   * @remarks
   * The interval is measured on the system clock, so a clock adjustment changes it.
   */
  msSinceLastEviction(): number | undefined {
    return this.#lastEvictionMs === undefined ? undefined : Date.now() - this.#lastEvictionMs;
  }

  /**
   * Fetches the entry for a key, stores it, and returns it.
   *
   * @remarks
   * `fetchValue` runs on every call, including when the key already has an entry, and the fetched
   * value replaces that entry.
   *
   * @returns the array that was stored, not a copy
   * @throws Rejects with the error `fetchValue` rejects with, or with {@link EntryTooLargeError} when the
   * fetched value is longer than {@link MAX_ENTRY_BYTES}. The cache is left unchanged in both cases.
   */
  async load(key: string, fetchValue: (key: string) => Promise<Uint8Array>): Promise<Uint8Array> {
    const value = await fetchValue(key);
    this.put(key, value);
    return value;
  }
}
```

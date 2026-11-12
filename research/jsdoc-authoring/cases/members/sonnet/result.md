```ts
export const DEFAULT_TIMEOUT_SECONDS = 30;

/** Largest value, in bytes, that an {@link EntryCache} accepts: 1 MiB (1048576 bytes). */
export const MAX_ENTRY_BYTES = 1 << 20;

/**
 * Reports a value larger than {@link MAX_ENTRY_BYTES}.
 *
 * @remarks
 * Match it with `instanceof` or by its `code` property.
 */
export class EntryTooLargeError extends Error {
  readonly code = "ENTRY_TOO_LARGE";
}

/**
 * Holds byte values in memory under string keys.
 *
 * @remarks
 * An entry stays until {@link EntryCache.evict} removes it. The cache never evicts on its own.
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
   * Stores a value under a key, replacing any entry already stored there.
   *
   * @remarks
   * The cache keeps `value` itself, not a copy, so the caller must not modify the array afterward.
   *
   * @throws {@link EntryTooLargeError} if `value` is longer than {@link MAX_ENTRY_BYTES}. The cache is left unchanged.
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
   * A key with no entry is ignored, and {@link EntryCache.msSinceLastEviction} does not count that call.
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
   * Returns the milliseconds elapsed, by `Date.now`, since an entry was last evicted.
   *
   * @returns `undefined` if no entry has been evicted yet.
   */
  msSinceLastEviction(): number | undefined {
    return this.#lastEvictionMs === undefined ? undefined : Date.now() - this.#lastEvictionMs;
  }

  /**
   * Fetches a value with `fetchValue`, stores it under `key`, and returns it.
   *
   * @remarks
   * `fetchValue` runs on every call, even when `key` already has an entry, and the fetched value replaces that entry.
   * The returned array is the one the cache stores, not a copy.
   *
   * @throws The promise rejects with the error `fetchValue` rejects with, or with {@link EntryTooLargeError} if the
   * fetched value is longer than {@link MAX_ENTRY_BYTES}. In both cases the cache is left unchanged.
   */
  async load(key: string, fetchValue: (key: string) => Promise<Uint8Array>): Promise<Uint8Array> {
    const value = await fetchValue(key);
    this.put(key, value);
    return value;
  }
}
```

```ts
export const DEFAULT_TIMEOUT_SECONDS = 30;

/**
 * Largest value an {@link EntryCache} accepts for one entry, in bytes.
 *
 * @remarks
 * The limit is 1 MiB (1048576 bytes) and applies to each value's `byteLength`. Keys do not count toward it.
 */
export const MAX_ENTRY_BYTES = 1 << 20;

/**
 * Thrown when a value is larger than {@link MAX_ENTRY_BYTES}.
 */
export class EntryTooLargeError extends Error {
  readonly code = "ENTRY_TOO_LARGE";
}

/**
 * In-memory cache of byte arrays keyed by string.
 *
 * @remarks
 * Each value is at most {@link MAX_ENTRY_BYTES} bytes. An entry stays until {@link EntryCache.evict} removes it.
 * The cache limits the size of each value, but not the number of entries or their total size.
 */
export class EntryCache {
  /** @defaultValue 3 */
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
   * Stores `value` under `key` and replaces any value already stored there.
   *
   * @remarks
   * The cache keeps a reference to `value`, not a copy. If the caller later changes the array, the cached entry
   * changes too.
   *
   * @throws {@link EntryTooLargeError} synchronously when `value` is larger than {@link MAX_ENTRY_BYTES}. The cache
   * is left unchanged.
   */
  put(key: string, value: Uint8Array): void {
    if (value.byteLength > MAX_ENTRY_BYTES) {
      throw new EntryTooLargeError(`entry ${key} is ${value.byteLength} bytes, limit ${MAX_ENTRY_BYTES}`);
    }
    this.#entries.set(key, value);
  }

  /**
   * Removes the entry stored under `key`.
   *
   * @remarks
   * If `key` has no entry, the call does nothing and does not reset {@link EntryCache.msSinceLastEviction}.
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
   * Returns the milliseconds elapsed since {@link EntryCache.evict} last removed an entry, or `undefined` if it has
   * never removed one.
   *
   * @remarks
   * The time comes from the system clock, so the result can be negative after the clock is set back.
   */
  msSinceLastEviction(): number | undefined {
    return this.#lastEvictionMs === undefined ? undefined : Date.now() - this.#lastEvictionMs;
  }

  /**
   * Calls `fetchValue` for `key`, stores the result under `key`, and resolves to that result.
   *
   * @remarks
   * `fetchValue` runs on every call, even when `key` already has an entry. If calls for the same key overlap, each
   * one calls `fetchValue`, and the value from the call that settles last stays stored. The cache keeps the array
   * the promise resolves to, not a copy, as {@link EntryCache.put} does.
   *
   * Every failure arrives as a rejection, and the cache is left unchanged. If `fetchValue` throws or rejects, the
   * promise rejects with that error.
   *
   * @throws {@link EntryTooLargeError} as a rejection when the fetched value is larger than {@link MAX_ENTRY_BYTES}.
   */
  async load(key: string, fetchValue: (key: string) => Promise<Uint8Array>): Promise<Uint8Array> {
    const value = await fetchValue(key);
    this.put(key, value);
    return value;
  }
}
```

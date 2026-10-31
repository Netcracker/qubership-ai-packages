```ts
export const DEFAULT_TIMEOUT_SECONDS = 30;

/** Largest value {@link EntryCache.put} accepts, in bytes: 1 MiB (1048576 bytes). */
export const MAX_ENTRY_BYTES = 1 << 20;

/**
 * Thrown when a value stored in an {@link EntryCache} is larger than {@link MAX_ENTRY_BYTES}.
 *
 * @remarks
 * Its `name` is `"Error"`, so match it with `instanceof` or by {@link EntryTooLargeError.code}.
 */
export class EntryTooLargeError extends Error {
  readonly code = "ENTRY_TOO_LARGE";
}

/**
 * Stores byte values in memory under string keys.
 *
 * @remarks
 * An entry stays until {@link EntryCache.evict} removes it or a later store under the same key
 * replaces it. The cache has no capacity limit and no expiry.
 *
 * The cache stores each value by reference, without copying it. Mutating the array after
 * {@link EntryCache.put} or {@link EntryCache.load} changes the stored entry.
 */
export class EntryCache {
  /**
   * Retry count that callers can read and set on the cache.
   *
   * @remarks
   * No method of this class reads it, and {@link EntryCache.load} calls `fetchValue` once.
   *
   * @defaultValue 3
   */
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
   * Stores `value` under `key`, replacing any existing entry.
   *
   * @throws {@link EntryTooLargeError}
   * Thrown when `value` is larger than {@link MAX_ENTRY_BYTES}. The existing entry for `key`
   * stays in place.
   */
  put(key: string, value: Uint8Array): void {
    if (value.byteLength > MAX_ENTRY_BYTES) {
      throw new EntryTooLargeError(`entry ${key} is ${value.byteLength} bytes, limit ${MAX_ENTRY_BYTES}`);
    }
    this.#entries.set(key, value);
  }

  /**
   * Removes the entry for `key`, if there is one.
   *
   * @remarks
   * A key with no entry leaves the cache unchanged and does not count as an eviction for
   * {@link EntryCache.msSinceLastEviction}.
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
   * Returns the milliseconds since {@link EntryCache.evict} last removed an entry, or `undefined`
   * if it has never removed one.
   *
   * @remarks
   * The time comes from `Date.now()`, so a wall-clock adjustment can make the result negative.
   */
  msSinceLastEviction(): number | undefined {
    return this.#lastEvictionMs === undefined ? undefined : Date.now() - this.#lastEvictionMs;
  }

  /**
   * Fetches the value for `key` with `fetchValue`, stores it under `key`, and returns it.
   *
   * @remarks
   * Every call invokes `fetchValue` once, even when `key` already has an entry. When the fetch
   * fails, the existing entry for `key` stays in place.
   *
   * @throws {@link EntryTooLargeError}
   * The promise rejects with this error when the fetched value is larger than
   * {@link MAX_ENTRY_BYTES}. A rejection from `fetchValue` is passed to the caller unchanged.
   */
  async load(key: string, fetchValue: (key: string) => Promise<Uint8Array>): Promise<Uint8Array> {
    const value = await fetchValue(key);
    this.put(key, value);
    return value;
  }
}
```

```ts
export const DEFAULT_TIMEOUT_SECONDS = 30;

/**
 * Largest value an {@link EntryCache} stores, in bytes: 1 MiB (1048576 bytes).
 */
export const MAX_ENTRY_BYTES = 1 << 20;

/**
 * Thrown when a value is larger than {@link MAX_ENTRY_BYTES}.
 */
export class EntryTooLargeError extends Error {
  readonly code = "ENTRY_TOO_LARGE";
}

/**
 * Holds byte values in memory under string keys.
 *
 * @remarks
 * Each value is at most {@link MAX_ENTRY_BYTES} bytes long. The number of entries and their total size are
 * unbounded, and an entry stays until {@link EntryCache.evict} removes it.
 *
 * The cache keeps the arrays it is given and returns them without copying. A caller that mutates one of
 * them changes the cached entry.
 */
export class EntryCache {
  /**
   * Number of retries.
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
   * @throws {@link EntryTooLargeError} if `value` is larger than {@link MAX_ENTRY_BYTES}. The cache is left
   * unchanged.
   */
  put(key: string, value: Uint8Array): void {
    if (value.byteLength > MAX_ENTRY_BYTES) {
      throw new EntryTooLargeError(`entry ${key} is ${value.byteLength} bytes, limit ${MAX_ENTRY_BYTES}`);
    }
    this.#entries.set(key, value);
  }

  /**
   * Removes the entry for `key`, if there is one.
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
   * Returns the milliseconds elapsed since {@link EntryCache.evict} last removed an entry, or `undefined` if
   * it never has.
   *
   * @remarks
   * The time is read from the system clock (`Date.now()`). If the clock is adjusted, the result can jump or
   * become negative.
   */
  msSinceLastEviction(): number | undefined {
    return this.#lastEvictionMs === undefined ? undefined : Date.now() - this.#lastEvictionMs;
  }

  /**
   * Fetches the value for `key` with `fetchValue`, stores it, and returns it.
   *
   * @remarks
   * `fetchValue` runs on every call, even when `key` already has an entry.
   *
   * Every failure arrives as a rejection, never as a synchronous throw. A rejection from `fetchValue`
   * passes through unchanged. A fetched value larger than {@link MAX_ENTRY_BYTES} rejects with
   * {@link EntryTooLargeError}. In both cases the cache is left unchanged.
   */
  async load(key: string, fetchValue: (key: string) => Promise<Uint8Array>): Promise<Uint8Array> {
    const value = await fetchValue(key);
    this.put(key, value);
    return value;
  }
}
```

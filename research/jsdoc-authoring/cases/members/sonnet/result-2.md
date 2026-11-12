```ts
export const DEFAULT_TIMEOUT_SECONDS = 30;

/**
 * Largest value {@link EntryCache.put} accepts, in bytes: 1 MiB (1048576 bytes).
 */
export const MAX_ENTRY_BYTES = 1 << 20;

/**
 * Reports a value larger than {@link MAX_ENTRY_BYTES}.
 *
 * @remarks
 * Match it with `instanceof` or by its `code`, which is `"ENTRY_TOO_LARGE"`.
 */
export class EntryTooLargeError extends Error {
  readonly code = "ENTRY_TOO_LARGE";
}

/**
 * Holds byte values in memory, keyed by string.
 *
 * @remarks
 * Entries leave the cache only through {@link EntryCache.evict}. Nothing expires, and nothing is
 * removed on its own.
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
   * Stores a value under a key, replacing any earlier value for that key.
   *
   * @remarks
   * The cache keeps the array itself, not a copy, so a caller that modifies it afterward changes
   * the stored entry.
   *
   * @param value - at most {@link MAX_ENTRY_BYTES} bytes long
   * @throws {@link EntryTooLargeError} if the value is longer than that. The throw is synchronous,
   * and the cache is left unchanged.
   */
  put(key: string, value: Uint8Array): void {
    if (value.byteLength > MAX_ENTRY_BYTES) {
      throw new EntryTooLargeError(`entry ${key} is ${value.byteLength} bytes, limit ${MAX_ENTRY_BYTES}`);
    }
    this.#entries.set(key, value);
  }

  /**
   * Removes the entry for a key.
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
   * Returns the milliseconds elapsed since {@link EntryCache.evict} last removed an entry, or
   * `undefined` if it has not removed one yet.
   *
   * @remarks
   * The time comes from `Date.now()`, so a change to the system clock changes the result.
   */
  msSinceLastEviction(): number | undefined {
    return this.#lastEvictionMs === undefined ? undefined : Date.now() - this.#lastEvictionMs;
  }

  /**
   * Fetches the value for a key, stores it, and returns it.
   *
   * @remarks
   * The cache is never read here: `fetchValue` runs on every call, even when the key already has
   * an entry, and its result replaces that entry. The stored value is the returned array itself,
   * as with {@link EntryCache.put}.
   *
   * @param fetchValue - called once per call, with `key`
   * @returns the value `fetchValue` produced
   * @throws Rejects with whatever `fetchValue` rejects with, or with {@link EntryTooLargeError} if
   * the value is longer than {@link MAX_ENTRY_BYTES}. In both cases the cache is left unchanged.
   */
  async load(key: string, fetchValue: (key: string) => Promise<Uint8Array>): Promise<Uint8Array> {
    const value = await fetchValue(key);
    this.put(key, value);
    return value;
  }
}
```

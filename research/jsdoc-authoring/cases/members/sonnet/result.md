```ts
export const DEFAULT_TIMEOUT_SECONDS = 30;

/**
 * Largest value {@link EntryCache.put} accepts, in bytes. This is 1 MiB (1048576 bytes).
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
 * Holds byte-array entries in memory, by string key.
 *
 * @remarks
 * Each entry is limited to {@link MAX_ENTRY_BYTES}. The cache has no limit on its total size and removes an entry only
 * when {@link EntryCache.evict} is called for it or {@link EntryCache.put} replaces it.
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
   * Stores a value under a key, replacing any existing entry for that key.
   *
   * @remarks
   * The cache keeps the array itself, not a copy, so changing the array afterward changes the entry.
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
   * Removes the entry for a key. A key with no entry is ignored.
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
   * Returns the milliseconds since the last {@link EntryCache.evict} call that removed an entry.
   *
   * @remarks
   * Returns `undefined` if no call has removed an entry yet.
   */
  msSinceLastEviction(): number | undefined {
    return this.#lastEvictionMs === undefined ? undefined : Date.now() - this.#lastEvictionMs;
  }

  /**
   * Fetches the value for a key with `fetchValue`, stores it under that key, and returns it.
   *
   * @remarks
   * `fetchValue` is called on every invocation, including when the key already has an entry, and the fetched value
   * replaces that entry. The returned array is the one the cache stores.
   *
   * @throws Every failure arrives as a rejection. The promise rejects with whatever `fetchValue` rejects with, or with
   * {@link EntryTooLargeError} if the fetched value is longer than {@link MAX_ENTRY_BYTES}. In both cases the cache is
   * left unchanged.
   */
  async load(key: string, fetchValue: (key: string) => Promise<Uint8Array>): Promise<Uint8Array> {
    const value = await fetchValue(key);
    this.put(key, value);
    return value;
  }
}
```

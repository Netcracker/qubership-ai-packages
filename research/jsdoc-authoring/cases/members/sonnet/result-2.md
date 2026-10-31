```ts
/**
 * Largest entry value {@link EntryCache.put} accepts, in bytes: 1 MiB (1048576 bytes).
 */
export const MAX_ENTRY_BYTES = 1 << 20;

export const DEFAULT_TIMEOUT_SECONDS = 30;

/**
 * Reports an entry value larger than {@link MAX_ENTRY_BYTES}.
 */
export class EntryTooLargeError extends Error {
  readonly code = "ENTRY_TOO_LARGE";
}

/**
 * Holds byte-array entries in memory under string keys.
 *
 * @remarks
 * An entry leaves the cache only through {@link EntryCache.evict}. The cache bounds the size of each
 * entry, not the number of entries or their total size.
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
   * Stores a value under a key, replacing any entry already there.
   *
   * @remarks
   * The cache keeps a reference to `value` and does not copy it, so the caller must not modify the array
   * afterward.
   *
   * @throws {@link EntryTooLargeError} when `value` is larger than {@link MAX_ENTRY_BYTES}. The cache is
   * left unchanged, and an entry already stored under `key` stays.
   */
  put(key: string, value: Uint8Array): void {
    if (value.byteLength > MAX_ENTRY_BYTES) {
      throw new EntryTooLargeError(`entry ${key} is ${value.byteLength} bytes, limit ${MAX_ENTRY_BYTES}`);
    }
    this.#entries.set(key, value);
  }

  /**
   * Removes the entry stored under a key. Does nothing when there is none.
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
   * Returns the milliseconds elapsed since {@link EntryCache.evict} last removed an entry.
   *
   * @returns `undefined` until an eviction has removed an entry. An `evict` call for a missing key does
   * not count.
   */
  msSinceLastEviction(): number | undefined {
    return this.#lastEvictionMs === undefined ? undefined : Date.now() - this.#lastEvictionMs;
  }

  /**
   * Fetches the value for a key with `fetchValue`, stores it, and returns it.
   *
   * @remarks
   * `fetchValue` is called on every invocation, even when an entry is already stored under `key`; the
   * fetched value then replaces that entry.
   *
   * @throws Rejects with the error from `fetchValue`, or with {@link EntryTooLargeError} when the fetched
   * value is larger than {@link MAX_ENTRY_BYTES}. Nothing is stored in either case.
   */
  async load(key: string, fetchValue: (key: string) => Promise<Uint8Array>): Promise<Uint8Array> {
    const value = await fetchValue(key);
    this.put(key, value);
    return value;
  }
}
```

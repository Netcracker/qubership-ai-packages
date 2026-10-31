```ts
/** Timeout, in seconds. */
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
 * Holds byte values by string key, each at most {@link MAX_ENTRY_BYTES} long.
 *
 * @remarks
 * An entry stays until {@link EntryCache.evict} removes it or a later `put` replaces it.
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
   * Stores a value under a key, replacing any existing entry.
   *
   * @remarks
   * The cache keeps the array itself, not a copy, so a later change to `value` changes the entry.
   *
   * @throws EntryTooLargeError if `value` is longer than {@link MAX_ENTRY_BYTES}. The cache is left unchanged.
   */
  put(key: string, value: Uint8Array): void {
    if (value.byteLength > MAX_ENTRY_BYTES) {
      throw new EntryTooLargeError(`entry ${key} is ${value.byteLength} bytes, limit ${MAX_ENTRY_BYTES}`);
    }
    this.#entries.set(key, value);
  }

  /**
   * Removes the entry for a key. A key with no entry is ignored.
   *
   * @remarks
   * Only a removal updates {@link EntryCache.msSinceLastEviction}.
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
   * @returns `undefined` if no entry has been removed yet.
   */
  msSinceLastEviction(): number | undefined {
    return this.#lastEvictionMs === undefined ? undefined : Date.now() - this.#lastEvictionMs;
  }

  /**
   * Fetches a value with `fetchValue`, stores it under the key, and returns it.
   *
   * @remarks
   * `fetchValue` runs on every call, even when the key already has an entry, and its result replaces that entry.
   * The returned array is the one the cache holds.
   *
   * @throws EntryTooLargeError as a rejection if the fetched value is longer than {@link MAX_ENTRY_BYTES}.
   * A rejection from `fetchValue` is passed on unchanged. In both cases the cache is left unchanged.
   */
  async load(key: string, fetchValue: (key: string) => Promise<Uint8Array>): Promise<Uint8Array> {
    const value = await fetchValue(key);
    this.put(key, value);
    return value;
  }
}
```

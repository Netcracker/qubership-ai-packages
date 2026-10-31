```ts
export const DEFAULT_TIMEOUT_SECONDS = 30;

/** Largest value {@link EntryCache.put} accepts, in bytes: 1 MiB (1048576 bytes). */
export const MAX_ENTRY_BYTES = 1 << 20;

/** Thrown when a value is longer than {@link MAX_ENTRY_BYTES}. */
export class EntryTooLargeError extends Error {
  readonly code = "ENTRY_TOO_LARGE";
}

/** An in-memory cache of byte arrays keyed by string, each at most {@link MAX_ENTRY_BYTES} long. */
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
   * Stores `value` under `key`, replacing any value already stored there.
   *
   * @remarks
   * The cache keeps `value` itself, not a copy, so a later change to the array changes the cached entry.
   *
   * @throws {@link EntryTooLargeError} when `value` is longer than {@link MAX_ENTRY_BYTES}. The existing entry
   * for `key`, if any, is kept.
   */
  put(key: string, value: Uint8Array): void {
    if (value.byteLength > MAX_ENTRY_BYTES) {
      throw new EntryTooLargeError(`entry ${key} is ${value.byteLength} bytes, limit ${MAX_ENTRY_BYTES}`);
    }
    this.#entries.set(key, value);
  }

  /** Removes the entry for `key`. An unknown key is ignored. */
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
   * The time base is the system clock, so setting the clock back can make the result negative.
   */
  msSinceLastEviction(): number | undefined {
    return this.#lastEvictionMs === undefined ? undefined : Date.now() - this.#lastEvictionMs;
  }

  /**
   * Fetches the value for `key` with `fetchValue`, stores it as {@link EntryCache.put} does, and returns it.
   *
   * @remarks
   * `fetchValue` runs on every call, whether or not `key` is already cached. A rejection from `fetchValue`
   * passes through unchanged and leaves the cache as it was.
   *
   * @throws {@link EntryTooLargeError} as a rejection, when the fetched value is longer than
   * {@link MAX_ENTRY_BYTES}. The fetched value is not stored.
   */
  async load(key: string, fetchValue: (key: string) => Promise<Uint8Array>): Promise<Uint8Array> {
    const value = await fetchValue(key);
    this.put(key, value);
    return value;
  }
}
```

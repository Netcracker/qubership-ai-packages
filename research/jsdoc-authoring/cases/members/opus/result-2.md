```ts
/** @packageDocumentation
 * In-memory cache of byte values keyed by string. Start with {@link EntryCache}.
 */

export const DEFAULT_TIMEOUT_SECONDS = 30;

/**
 * Largest value {@link EntryCache.put} accepts, in bytes: 1 MiB (1048576 bytes).
 *
 * @remarks
 * The limit applies to each value's `byteLength` on its own. Keys do not count toward it, and
 * nothing limits the total size of a cache.
 */
export const MAX_ENTRY_BYTES = 1 << 20;

/**
 * Thrown when a value is larger than {@link MAX_ENTRY_BYTES}.
 *
 * @remarks
 * Callers can match it with `instanceof` or by its `code`.
 */
export class EntryTooLargeError extends Error {
  readonly code = "ENTRY_TOO_LARGE";
}

/**
 * In-memory map from string keys to byte values, each at most {@link MAX_ENTRY_BYTES} long.
 *
 * @remarks
 * An entry stays in the cache until {@link EntryCache.evict} removes it or a later write replaces
 * it. Nothing removes entries automatically, and the cache has no total size limit.
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
   * Stores `value` under `key` and replaces any entry already stored there.
   *
   * @remarks
   * The cache keeps a reference to `value` and does not copy it, so later changes to the array
   * show up in the cached entry. A value of exactly {@link MAX_ENTRY_BYTES} bytes is accepted.
   *
   * @throws {@link EntryTooLargeError} synchronously, when `value` is larger than
   * {@link MAX_ENTRY_BYTES}. The cache is left unchanged, including any entry already under `key`.
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
   * Evicting a key that has no entry does nothing, and it does not reset
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
   * Returns the number of milliseconds since {@link EntryCache.evict} last removed an entry, or
   * `undefined` if it has never removed one.
   *
   * @remarks
   * The time comes from the system clock (`Date.now()`), so the result can be negative after the
   * clock is set back.
   */
  msSinceLastEviction(): number | undefined {
    return this.#lastEvictionMs === undefined ? undefined : Date.now() - this.#lastEvictionMs;
  }

  /**
   * Fetches the value for `key`, stores it as {@link EntryCache.put} does, and returns it.
   *
   * @remarks
   * `fetchValue` is called exactly once per call, even when `key` already has an entry, and the
   * fetched value replaces that entry.
   *
   * @throws Every failure arrives as a rejection. When `fetchValue` rejects, the promise rejects
   * with the same error. When the fetched value is too large, it rejects with
   * {@link EntryTooLargeError}. In both cases the cache is left unchanged.
   */
  async load(key: string, fetchValue: (key: string) => Promise<Uint8Array>): Promise<Uint8Array> {
    const value = await fetchValue(key);
    this.put(key, value);
    return value;
  }
}
```

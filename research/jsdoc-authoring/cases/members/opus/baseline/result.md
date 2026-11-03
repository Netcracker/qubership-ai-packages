```ts
/**
 * Largest value {@link EntryCache.put} accepts, in bytes: 1 MiB (1048576 bytes).
 *
 * @remarks
 * This limit bounds each value on its own. Keys and the total size of a cache have no limit.
 */
export const MAX_ENTRY_BYTES = 1 << 20;

/**
 * Thrown when a value is larger than {@link MAX_ENTRY_BYTES}.
 *
 * @remarks
 * Callers can match the error with `instanceof` or by its `code`, `"ENTRY_TOO_LARGE"`.
 */
export class EntryTooLargeError extends Error {
  readonly code = "ENTRY_TOO_LARGE";
}

/**
 * In-memory cache that stores byte values under string keys.
 *
 * @remarks
 * An entry stays in the cache until {@link EntryCache.evict} removes it. The cache never evicts entries on its own.
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
   * Stores `value` under `key` and replaces any value already stored there.
   *
   * @remarks
   * The cache keeps a reference to `value` and does not copy it. If the caller changes the array later, the cached
   * entry changes too.
   *
   * @throws {@link EntryTooLargeError} synchronously when `value.byteLength` is greater than {@link MAX_ENTRY_BYTES}.
   * When that happens, the entry already stored under `key` stays as it was.
   */
  put(key: string, value: Uint8Array): void {
    if (value.byteLength > MAX_ENTRY_BYTES) {
      throw new EntryTooLargeError(`entry ${key} is ${value.byteLength} bytes, limit ${MAX_ENTRY_BYTES}`);
    }
    this.#entries.set(key, value);
  }

  /**
   * Removes the entry stored under `key`. If `key` has no entry, nothing changes.
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
   * Returns the milliseconds since {@link EntryCache.evict} last removed an entry, or `undefined` if it has never
   * removed one.
   *
   * @remarks
   * The time comes from `Date.now()`. If the system clock changes, the result shifts and can be negative.
   */
  msSinceLastEviction(): number | undefined {
    return this.#lastEvictionMs === undefined ? undefined : Date.now() - this.#lastEvictionMs;
  }

  /**
   * Fetches the value for `key` with `fetchValue`, stores it as {@link EntryCache.put} does, and resolves with it.
   *
   * @remarks
   * Each call runs `fetchValue` exactly once, even when `key` already has an entry. A failed fetch is not retried.
   * The promise resolves with the same array the cache stores.
   *
   * @throws Every failure arrives as a rejection. If `fetchValue` fails, the promise rejects with its error and the
   * cache stays unchanged. If the fetched value is larger than {@link MAX_ENTRY_BYTES}, the promise rejects with
   * {@link EntryTooLargeError} and nothing is stored.
   */
  async load(key: string, fetchValue: (key: string) => Promise<Uint8Array>): Promise<Uint8Array> {
    const value = await fetchValue(key);
    this.put(key, value);
    return value;
  }
}
```

The module below is new in this change, in a published TypeScript library (`@example/cache`, TypeScript 5, ES
modules). The project's other exported classes carry TSDoc comments, and the build runs no lint rule that demands one.

Write the doc comments and inline comments this module needs, and none that it does not. Give back the whole module
with your comments in it, in one `ts` block, and nothing else.

```ts
export const DEFAULT_TIMEOUT_SECONDS = 30;

export const MAX_ENTRY_BYTES = 1 << 20;

export class EntryTooLargeError extends Error {
  readonly code = "ENTRY_TOO_LARGE";
}

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

  put(key: string, value: Uint8Array): void {
    if (value.byteLength > MAX_ENTRY_BYTES) {
      throw new EntryTooLargeError(`entry ${key} is ${value.byteLength} bytes, limit ${MAX_ENTRY_BYTES}`);
    }
    this.#entries.set(key, value);
  }

  evict(key: string): void {
    const removed = this.#entries.get(key);
    if (removed !== undefined) {
      this.#entries.delete(key);
      this.#evictedBytes += removed.byteLength;
      this.#lastEvictionMs = Date.now();
    }
  }

  msSinceLastEviction(): number | undefined {
    return this.#lastEvictionMs === undefined ? undefined : Date.now() - this.#lastEvictionMs;
  }

  async load(key: string, fetchValue: (key: string) => Promise<Uint8Array>): Promise<Uint8Array> {
    const value = await fetchValue(key);
    this.put(key, value);
    return value;
  }
}
```

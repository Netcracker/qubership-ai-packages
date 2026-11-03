```ts
import { describe, expect, it } from "vitest";
import { EntryCache, EntryTooLargeError, MAX_ENTRY_BYTES } from "./cache.js";
import { ALL_EVENTS, HANDLED } from "./events.js";

describe("EntryCache", () => {
  it("returns the value put under a key", () => {
    const cache = new EntryCache("c");
    cache.put("k", Uint8Array.of(1, 2));
    expect(cache.get("k")).toEqual(Uint8Array.of(1, 2));
  });

  it("rejects a value over the limit", () => {
    const cache = new EntryCache("c");
    expect(() => cache.put("k", new Uint8Array(MAX_ENTRY_BYTES + 1))).toThrow(EntryTooLargeError);
  });

  /**
   * Each eviction adds only the evicted value's length to `evictedBytes`.
   *
   * @remarks
   * `evict` used to add the key's length as well, so the total came out too large and nothing threw (issue #57).
   */
  it("counts only the value in evictedBytes", () => {
    const cache = new EntryCache("c");
    cache.put("a-long-key", new Uint8Array(3));
    cache.evict("a-long-key");
    expect(cache.evictedBytes).toBe(3);
  });

  it("has a handler for every event", () => {
    const missing = ALL_EVENTS.filter((e) => !HANDLED.has(e));
    expect(missing).toEqual([]);
  });
});
```

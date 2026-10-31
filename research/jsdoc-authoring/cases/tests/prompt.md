The test file below is new in this change, in a TypeScript library (`@example/cache`, TypeScript 5, Vitest). It tests
`EntryCache`, whose `evict` adds the evicted value's length to a running total and whose `put` throws
`EntryTooLargeError` for a value over `MAX_ENTRY_BYTES`. `ALL_EVENTS` lists every cache event; `HANDLED` is the set of
events the dispatcher has a handler for.

`counts only the value in evictedBytes` is the regression test for issue #57: `evict` used to add the key's length to
the total as well as the value's, so the total came out too large. Nothing threw.

Write the doc comments and inline comments this file needs, and none that it does not. Give back the whole file with
your comments in it, in one `ts` block, and nothing else.

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

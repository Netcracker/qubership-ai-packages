# Case: a new public class, `jsdoc-authoring`

The input is one new file (TypeScript 5, a published package) holding a cache class with a getter, a private field, two
constants, a sentinel, and a failure. The task asks for the comments the class needs and none that it does not. The case
is the negative control for the getter, field, and size-constant rules of 1.3.0, and checks that the facts a caller
needs still appear.

## Skill parts

- `SKILL.md`: §2 (the getter sentence), §4 (Property, field, and constant), §6 (`@throws`, `@deprecated`), §7, §8
- `english-developer-style` (`agent-packages/english-us-developer-style`), at the working copy, in both arms

## Checks

Every check reads a result that keeps each declaration of the input; a result that drops one fails the case, whatever
its comments, because a comment that is absent with its declaration has not been left out.

1. **The getter gets no comment:** `get name()`, whose name and type are its contract.
2. **The private field gets no comment:** `readonly #name: string`.
3. **The small constant carries one form.** `DEFAULT_TIMEOUT_SECONDS = 30`: no `30 seconds (30 …)` pair. No comment at
   all also passes.
4. **The shifted constant carries both forms**, on the constant or in the failure it bounds: `MAX_ENTRY_BYTES = 1 << 20`
   as `1 MiB (1048576 bytes)`.
5. **The sentinel is stated:** `msSinceLastEviction()` returning `undefined` before the first eviction.
6. **The failure is stated:** `@throws EntryTooLargeError` on `put`.
7. **`load` says its failures arrive as rejections** (§6, `@throws`): the package is published, and its `.d.ts` reads
   `load(…): Promise<Uint8Array>` with `async` gone. **No `@defaultValue` on a constant** (§4). `@defaultValue 3` on the
   exported `retries` property is allowed: declaration emit drops its initializer.

## Results

Runs of 2026-10-31, graded by reading; both models at the default effort, two runs each. The baseline ran on
`a51171b` (`<model>/baseline/`), the new arm on the skill tree in `<model>/skill-tree`.

| Arm | Declarations kept | Getter (1) | Small constant (3) | Rejection on `load` (7) |
| --- | --- | --- | --- | --- |
| Baseline | Opus r1 fails: `DEFAULT_TIMEOUT_SECONDS` is gone | passes | passes | passes |
| 1.3.0 | passes | passes | passes | passes |

Checks 2 and 4 to 6 passed in every run, and no run put `@defaultValue` on a constant. Opus r1 and r2 of 1.3.0 put
`@defaultValue 3` on the mutable `retries`, which check 7 allows. Sonnet baseline r2 commented the timeout `Timeout, in
seconds.`, one form, which passes check 3.

An earlier 1.3.0 tree told the skill that an `async` function needs no rejection sentence, and check 7 then asked for
none; three of its runs dropped the sentence, and its Sonnet r1 dropped `DEFAULT_TIMEOUT_SECONDS`. Review of the pull
request pointed out that declaration emit drops `async`, so a reader of this published package's `.d.ts` cannot tell
the two kinds of function apart. The rule now keys on whether the reader sees `async`, and the 1.3.0 row is the run of
that tree.

# Case: a new public class, `javadoc-authoring`

The input is one new file (Java 17, a published library whose other public classes carry no `@since`) holding a cache
class with a getter, a private field, two constants, a sentinel, and a failure. The task asks for the comments the class
needs and none that it does not. The case is the negative control for the getter, field, and size-constant rules of
1.3.0, and checks that the facts a caller needs still appear.

## Skill parts

- `SKILL.md`: §2 (the getter sentence), §3, §4 (Field and constant; Method), §6 (`@since`), §7, §8
- `english-developer-style` (`agent-packages/english-us-developer-style`), at the working copy, in both arms

## Checks

1. **The getter gets no comment:** `getName()`, whose name and type are its contract.
2. **The private field gets no comment:** `private final String name`.
3. **The small constant carries one form.** `DEFAULT_TIMEOUT_SECONDS = 30`: no `30 seconds (30 …)` pair. No comment at
   all also passes.
4. **The shifted constant carries both forms**, on the constant or in the failure it bounds: `MAX_ENTRY_BYTES = 1 << 20`
   as `1 MiB (1048576 bytes)`.
5. **The sentinel is stated:** `nanosSinceLastEviction()` empty before the first eviction (`lastEvictionNanos == 0`).
6. **The failure is stated:** `@throws IllegalArgumentException` on `put`.
7. **No `@since`** (§6): the project tags none.

## Results

Runs of 2026-10-31, graded by reading; both models at the default effort, two runs each. The baseline ran on
`a51171b` (`<model>/baseline/`), the new arm on the skill tree in `<model>/skill-tree`.

| Arm | Getter (1) | Small constant (3) | Language (7) |
| --- | --- | --- | --- |
| Baseline | Opus r2 fails: `Returns the name this cache was created with.`, and a comment on the constructor | passes | passes |
| 1.3.0 | passes | passes | passes |

Checks 2 and 4 to 7 passed in every run of both arms; `@since` appeared in none, so the input does not reach the
narrowed `@since` rule.

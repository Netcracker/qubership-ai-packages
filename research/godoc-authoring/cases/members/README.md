# Case: a new public class, `godoc-authoring`

The input is one new file (Go 1.22, a published module whose linters demand no comment on an exported name) holding a
cache class with a getter, a private field, two constants, a sentinel, and a failure. The task asks for the comments the
class needs and none that it does not. The case is the negative control for the getter, field, and size-constant rules
of 1.3.0, and checks that the facts a caller needs still appear.

## Skill parts

- `SKILL.md`: §2 (the getter sentence), §4 (Type; Method that implements an interface; Field, constant, and variable),
  §6 (Errors), §7, §8
- `english-developer-style` (`agent-packages/english-us-developer-style`), at the working copy, in both arms

## Checks

1. **The getter gets no comment:** `Name()`, whose name and type are its contract.
2. **The private field gets no comment:** the `name string` field.
3. **The small constant carries one form.** `DefaultTimeoutSeconds = 30`: no `30 seconds (30 …)` pair. No comment at all
   also passes.
4. **The shifted constant carries both forms**, on the constant or in the failure it bounds: `maxEntryBytes = 1 << 20`
   as `1 MiB (1048576 bytes)`.
5. **The sentinel is stated:** `SinceLastEviction()` returning `false` before the first eviction.
6. **The failure is stated:** the error from `Put` wrapping `ErrTooLarge`, matched with `errors.Is`.
7. **No `implements` line on the unexported `oldestFirst`** (§4), and **the type comment says the zero value is not
   ready to use** (`Put` panics on its nil map).

## Results

Runs of 2026-10-31, graded by reading; both models at the default effort, two runs each. The baseline ran on
`a51171b` (`<model>/baseline/`), the new arm on the skill tree in `<model>/skill-tree`.

| Arm | Getter (1) | Small constant (3) | Language (7) |
| --- | --- | --- | --- |
| Baseline | Opus r1, r2 fail: `Name returns the name passed to [New].` | passes | passes |
| 1.3.0 draft | passes | passes | Sonnet r1, r2 fail: no word on the zero value |
| 1.3.0 | passes | passes | passes |

Checks 2 and 4 to 6 passed in every run. No run wrote an `implements` line, in either arm. A draft of 1.3.0 made the
"ready to use" clause depend on the package having no constructor, and Sonnet then dropped the true sentence that the
zero value is not ready; 1.3.0 keeps the sentence as it was. The draft runs are not committed.

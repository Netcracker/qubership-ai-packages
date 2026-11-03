# Case: a new public class, `rustdoc-authoring`

The input is one new file (Rust 2021, a crate on crates.io with `#![warn(missing_docs)]`) holding a cache class with a
getter, a private field, two constants, a sentinel, and a failure. The task asks for the comments the class needs and
none that it does not. The case is the negative control for the getter, field, and size-constant rules of 1.3.0, and
checks that the facts a caller needs still appear.

## Skill parts

- `SKILL.md`: §2 (the accessor sentence, `# Examples`), §4 (Field, constant, and static; the work list, Panics), §6 (the
  sections table), §7, §8, §9 (the accessor example)
- `english-developer-style` (`agent-packages/english-us-developer-style`), at the working copy, in both arms

## Checks

1. **The getter gets one line, the one `missing_docs` asks for:** `name()`, whose name and type are its contract.
2. **The private field gets no comment:** the `name: String` field.
3. **The small constant carries one form.** `DEFAULT_TIMEOUT_SECS: u64 = 30`: no `30 seconds (30 …)` pair. No comment at
   all also passes.
4. **The shifted constant carries both forms**, on the constant or in the failure it bounds: `MAX_ENTRY_BYTES: usize = 1
   << 20` as `1 MiB (1048576 bytes)`.
5. **The sentinel is stated:** `since_last_eviction()` returning `None` before the first eviction.
6. **The failure is stated:** `# Panics` on `put`, which a caller causes with a long value.
7. **No `# Examples` section** (§6): no item here has a use its signature does not show. The getter gets the one line
   `missing_docs` asks for (check 1).

## Results

Runs of 2026-10-31, graded by reading; both models at the default effort, two runs each. The baseline ran on
`a51171b` (`<model>/baseline/`), the new arm on the skill tree in `<model>/skill-tree`.

| Arm | Getter (1) | Small constant (3) | Language (7) |
| --- | --- | --- | --- |
| Baseline | passes | passes | passes |
| 1.3.0 | passes | passes | passes |

Every check passed in every run of both arms: the baseline already wrote one line on `name()` and no `# Examples`. The
case shows the 1.3.0 text does not drop the `# Panics` section a caller can trigger.

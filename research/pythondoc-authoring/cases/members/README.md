# Case: a new public class, `pythondoc-authoring`

The input is one new file (Python 3.12, a published library with Google-style docstrings) holding a cache class with a
getter, a private field, two constants, a sentinel, and a failure. The task asks for the comments the class needs and
none that it does not. The case is the negative control for the getter, field, and size-constant rules of 1.3.0, and
checks that the facts a caller needs still appear.

## Skill parts

- `SKILL.md`: §2 (the property sentence), §4 (Generator, coroutine, and context manager; Attribute, property, and
  constant), §7, §8
- `english-developer-style` (`agent-packages/english-us-developer-style`), at the working copy, in both arms

## Checks

1. **The getter gets no docstring:** the `name` property, whose name and type are its contract.
2. **The private field gets no docstring:** `self._name`.
3. **The small constant carries one form.** `DEFAULT_TIMEOUT_SECONDS = 30`: no `30 seconds (30 …)` pair. No docstring at
   all also passes.
4. **The shifted constant carries both forms**, on the constant or in the failure it bounds: `_MAX_ENTRY_BYTES = 1 <<
   20` as `1 MiB (1048576 bytes)`.
5. **The sentinel is stated:** `seconds_since_last_eviction()` returning `None` before the first eviction.
6. **The failure is stated:** `Raises: EntryTooLargeError` on `put`.
7. **No single-pass, closing, or held-resource note on `keys()`** (§4, Generator), a generator over a sorted copy of the
   keys. A sentence that the cache may change while the iterator runs is a fact of its contract and passes.

## Results

Runs of 2026-10-31, graded by reading; both models at the default effort, two runs each. The baseline ran on
`a51171b` (`<model>/baseline/`), the new arm on the skill tree in `<model>/skill-tree`.

| Arm | Getter (1) | Small constant (3) | Language (7) |
| --- | --- | --- | --- |
| Baseline | passes | passes | 4 of 4 fail: `The iterator is single-pass.`, `Single-pass: a second iteration yields nothing.` |
| 1.3.0 | passes | passes | passes |

Checks 2 and 4 to 6 passed in every run of both arms. Every 1.3.0 run still says when the keys are copied, as the reason
the cache may change during iteration.

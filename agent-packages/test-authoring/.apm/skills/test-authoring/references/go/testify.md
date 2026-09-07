# testify

Which call prints the operands, where the message goes, and which package continues after a failure. The engine, the
subtest names, and the shuffle flag are `testing.md`'s. The rules that use this file are in `SKILL.md` §7.

## Which assertion prints the operands

| Call | Message on failure |
| --- | --- |
| `assert.Equal(t, 0, ensureBytes(-1))` | `Not equal:` then `expected: 0` and `actual  : -1` |
| `assert.Equal(t, 0, ensureBytes(-1), "ensureBytes(%d)", -1)` | the same, then `Messages:` and `ensureBytes(-1)` |
| `assert.Equal(t, "Hello world", "Hello, world")` | both strings, then a `--- Expected` / `+++ Actual` diff |
| `assert.Equal(t, P{1, 2}, P{1, 3})` | both structs, then a field-level diff |
| `assert.True(t, ensureBytes(-1) == 0)` | `Should be true` |
| `assert.True(t, ensureBytes(-1) == 0, "ensureBytes(-1) must refuse")` | `Should be true` then `Messages:` and `ensureBytes(-1) must refuse` |
| `assert.ErrorIs(t, err, ErrNegativeCount)` | `Target error should be in err chain:` then `expected: "negative"` and `in chain: "other"` |
| `assert.EqualError(t, err, "negative")` | `Error message not equal:` then both strings |
| `assert.NoError(t, err)` | `Received unexpected error:` then the error text |

Every failure also prints `Error Trace:` with the file and line and `Test:` with the test name. `assert.True` prints
`Should be true` and no values, so it is for a function that returns a boolean; a comparison goes into `Equal`,
`Len`, `Contains`, `ErrorIs`, or `ErrorAs`, which print what they compared.

- **Operand order is `(expected, actual)`**, the reverse of the standard library's `got, want`, and the labels
  `expected:` and `actual:` follow it. A swapped pair prints the bug as the expectation.
- **The message is the last argument**, a format string and its arguments, printed after the values under
  `Messages:`. It carries the function and the input (`"ensureBytes(%d)", n`), since the case name may not spell it.
- **`assert.ErrorIs`** compares error semantics; `assert.EqualError` pins the message string and is a change detector
  for wording.

## Keep going, or stop

`assert` marks the test failed and continues, so one run reports every mismatch; `require` stops at the first
failure and is for the point after which continuing is meaningless, such as a `nil` the next line dereferences.
`assert.NoError` alone is the shape §5 rejects where the contract defines a result; follow it with an assertion on
that result. It stands alone only where completing is the contract (the repair of §5's row *Passes only because
nothing threw*), and the test's name then says what no longer fails.

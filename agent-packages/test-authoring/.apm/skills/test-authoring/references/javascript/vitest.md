# Vitest

What the runner prints, which matcher carries the values, and how a case is named. Vitest is both the engine and the
`expect` library, so one file covers both roles. The rules that use it are in `SKILL.md` §7 and §8.

## What the runner prints

The runner prints the `describe` path and the `it` or `test` string as `describe > test` above each failure, then the
matcher's message, then a code frame. So the `describe` string carries the unit and the shared condition, the `it`
string carries the scenario and the outcome (`it('rejects with AbortError when the signal fires mid-flight')`, not
`it('handles abort')`, and never `it('works')`), and the message never says where. A test that holds a case with its
controls in one check (`SKILL.md` §7) is named by the rule they establish.

## Which matcher prints the operands

| Call | Message on failure |
| --- | --- |
| `expect(ensureBytes(-1)).toBe(0)` | `AssertionError: expected -1 to be +0 // Object.is equality` then a `- Expected` / `+ Received` diff of the two values |
| `expect(ensureBytes(-1), 'ensureBytes(-1)').toBe(0)` | `AssertionError: ensureBytes(-1): expected -1 to be +0 // Object.is equality` then the diff |
| `expect({ a: 1, b: 2 }).toEqual({ a: 1, b: 3 })` | `expected { a: 1, b: 2 } to deeply equal { a: 1, b: 3 }` then a line diff |
| `expect(ensureBytes(-1) === 0).toBe(true)` | `expected false to be true // Object.is equality` |
| `expect(ensureBytes(-1) === 0).toBeTruthy()` | `expected false to be truthy` |
| `expect(fn).toThrow(RangeError)` when a `TypeError` is thrown | `expected error to be instance of RangeError` then the received error with its message |

A boolean inside `expect()` prints `false to be true` and no values. Put the value inside `expect()` and the
expectation in the matcher, and keep `toBe(true)` for a function that returns a boolean.

- **The actual value goes inside `expect()`**, the expected value in the matcher.
- **`expect(actual, message)` takes a message as the second argument**, printed as a prefix of the first line; it
  carries the function and the input, not the values.
- **`expect(fn).toThrow(RangeError)`** prints the expected class; match a message only on the part the behavior
  defines.

## Parameterized cases

`test.each([[-1], [-2]])('ensureBytes(%d) is refused', n => …)` formats the title with `%s`, `%d`, `%p`, `%j`, `%o`, and
`%#` (the index, which is a location on its own); with an array of objects, `$name` and `$value.path` interpolate
fields. `test.for` takes the same placeholders and passes the row as one argument. The formatted title is the test's
name in the report, so the title carries the condition and the message adds nothing the title already says. Cases that
share a setup (`SKILL.md` §7) and assert the same way may be the rows of one `test.each`, or separate `test` calls on
one helper. The main skill (§7) and the file's neighbors (§9) choose between them, and a short setup is repeated in each
case. Where the outcomes differ in kind, one throwing and one returning, a row field such as `shouldThrow` that selects
the assertion is the condition that decides whether an assertion runs, which §6 rules out. Such cases are separate
`test` calls on one helper that builds the setup from the varying value. Many cases of each kind are one `test.each` for
each kind.

## Grouping assertions

`expect.soft(actual).toBe(expected)` records the failure and continues, and the test reports every soft failure as
its own block; a chain of bare `expect` calls stops at the first. Use `expect.soft` for several assertions on the
fields of one result.

An `async` test that forgets to `await` passes with no assertion run; `expect.assertions(n)` or
`expect.hasAssertions()` turns that into a failure.

## Order and flakiness

`sequence.shuffle` in the config (or `--sequence.shuffle`) randomizes the order and prints the seed;
`--sequence.seed=<num>` replays it. `vi.mock` of a module the repository does not own is the shape §6 rejects; wrap
the module and fake the wrapper.

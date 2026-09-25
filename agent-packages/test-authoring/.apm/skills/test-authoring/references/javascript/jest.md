# Jest

What the runner prints, which matcher carries the values, and how a case is named. Jest is both the engine and the
`expect` library, so one file covers both roles. The rules that use it are in `SKILL.md` §7 and §8.

## What the runner prints

The runner prints the `describe` path and the `it` or `test` string as `describe › test` above each failure, then the
matcher's message, then a code frame. So the `describe` string carries the unit and the shared condition, the `it`
string carries the scenario and the outcome (`it('rejects with AbortError when the signal fires mid-flight')`, not
`it('handles abort')`, and never `it('works')`), and the message never says where. A test that holds a case with its
controls in one check (`SKILL.md` §7) is named by the rule they establish.

## Which matcher prints the operands

| Call | Message on failure |
| --- | --- |
| `expect(ensureBytes(-1)).toBe(0)` | `expect(received).toBe(expected) // Object.is equality` then `Expected: 0` and `Received: -1` |
| `expect({ a: 1, b: 2 }).toEqual({ a: 1, b: 3 })` | `expect(received).toEqual(expected) // deep equality` then a `- Expected` / `+ Received` line diff |
| `expect(ensureBytes(-1) === 0).toBe(true)` | `Expected: true` and `Received: false` |
| `expect(ensureBytes(-1) === 0).toBeTruthy()` | `Received: false` and nothing else |
| `expect(fn).toThrow(RangeError)` when a `TypeError` is thrown | `Expected constructor: RangeError`, `Received constructor: TypeError`, `Received message: "boom"` |
| `expect(fn).toThrow(RangeError)` when nothing is thrown | `Expected constructor: RangeError` then `Received function did not throw` |

A boolean inside `expect()` prints `true` and `false`, and `toBeTruthy()` prints the received value alone. Put the
value inside `expect()` and the expectation in the matcher, and keep `toBe(true)` for a function that returns a
boolean.

- **The actual value goes inside `expect()`**, the expected value in the matcher.
- **`expect` takes no message.** Add context by naming the case, or with a custom matcher through `expect.extend`.
- **`expect(fn).toThrow(RangeError)`** prints the expected class; match a message only on the part the behavior
  defines.

## Parameterized cases

`test.each([[-1], [-2]])('ensureBytes(%d) is refused', n => …)` formats the title with `%s`, `%d`, `%p`, `%j`, `%o`, and
`%#` (the index, which is a location on its own); with an array of objects, `$name` and `$value.path` interpolate
fields. The formatted title is the test's name in the report, so the title carries the condition and the message adds
nothing the title already says. Cases that share a setup (`SKILL.md` §7) and assert the same way may be the rows of one
`test.each`, or separate `test` calls on one helper. The main skill (§7) and the file's neighbors (§9) choose between
them, and a short setup is repeated in each case. Where the outcomes differ in kind, one throwing and one returning, a
row field such as `shouldThrow` that selects the assertion is the condition that decides whether an assertion runs,
which §6 rules out. Such cases are separate `test` calls on one helper that builds the setup from the varying value.
Many cases of each kind are one `test.each` for each kind.

## Grouping assertions

Jest stops at the first failing assertion; several assertions on the fields of one result either compare the whole
object with `toEqual` or move into separate cases. Several expectations on the result of one act, the errors of one
validated batch, are one `toEqual` of the whole list reduced to the fields the behavior defines, the record and the
error code without the message, sorted where the behavior defines no order, so that one run shows every mismatch (§7).

An `async` test that forgets to `await` passes with no assertion run; `expect.assertions(n)` or
`expect.hasAssertions()` turns that into a failure.

## Order and flakiness

`--randomize` shuffles the tests within each file and prints the seed; `--seed=<num>` replays it. `jest.mock` of a
module the repository does not own is the shape §6 rejects; wrap the module and fake the wrapper.

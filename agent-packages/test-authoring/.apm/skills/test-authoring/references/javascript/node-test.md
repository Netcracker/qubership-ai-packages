# `node:test` with `node:assert/strict`

What the runner prints, which assertion carries the values, and how a case is named. The runner and the assertion
module ship with Node, so one file covers both roles. The rules that use it are in `SKILL.md` §7 and §8.

## What the runner prints

The runner prints the `describe` path and the `it` or `test` string as `parent > child` above each failure, then the
assertion's message, then `test at m.test.mjs:5:3`. So the `describe` string carries the unit and the shared
condition, the `it` string carries the scenario and the outcome (`it('rejects with AbortError when the signal fires
mid-flight')`, not `it('handles abort')`, and never `it('works')`), and the message never says where.

## Which assertion prints the operands

| Call | Message |
| --- | --- |
| `assert.strictEqual(ensureBytes(-1), 0)` | `Expected values to be strictly equal:` then `-1 !== 0` |
| `assert.strictEqual(ensureBytes(-1), 0, "ensureBytes(-1)")` | `ensureBytes(-1)` then `-1 !== 0` |
| `assert.deepStrictEqual(a, b)` | `Expected values to be strictly deep-equal:` then a `+ actual - expected` line diff |
| `assert.ok(ensureBytes(-1) === 0)` | `The expression evaluated to a falsy value:` then the source expression |
| `assert.ok(ensureBytes(-1) === 0, "msg")` | `msg`, with `actual: false, expected: true` and no expression text |
| `assert.throws(fn, RangeError)` when a `TypeError` is thrown | `The error is expected to be an instance of "RangeError". Received "TypeError"` |
| `assert.fail()` | `Failed` |

A message on `strictEqual` replaces only the header and keeps the `-1 !== 0` line; a message on `ok` replaces the
expression text, so the values are gone. Use `strictEqual`, `deepStrictEqual`, and `throws`; keep `ok` for a boolean
result. The operand order is `(actual, expected)`, and the message is the last argument.

## Parameterized cases

There is no `test.each`. A loop over a table that calls `test(name, …)` once per row gives each case its own name in
the report; build the name from the condition (`` `ensureBytes(${n}) is refused` ``), not from the index.

## Grouping assertions

`node:assert` stops at the first failing assertion. Several assertions on the fields of one result either compare the
whole object with `deepStrictEqual` or move into separate cases.

`t.plan(n)` on the test context fails the test when fewer than `n` assertions ran by the time it ended, which is
how an `async` test that forgot an `await` is caught. The plan counts only assertions made through `t.assert`
(`t.assert.strictEqual(…)`); an imported `assert.strictEqual` is not counted, so a test that plans one assertion and
makes it through the module fails with `plan expected 1 assertions but received 0` even when the assertion ran.

## Order and flakiness

`node --test --test-randomize` runs the tests in random order and `--test-random-seed=<seed>` replays it. A
`mock.module` of a module the repository does not own is the shape §6 rejects; wrap the module and fake the wrapper.

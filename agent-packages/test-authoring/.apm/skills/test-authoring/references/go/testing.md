# Go `testing`

What `go test` prints, the shape of a failure line, and how a subtest is named. The standard library has no
assertion, so this file covers both the engine and the failure message; `testify.md` is for a project that uses
that library on top. The rules that use it are in `SKILL.md` §7 and §8.

## What the runner prints

```text
--- FAIL: TestEnsureBytes (0.00s)
    --- FAIL: TestEnsureBytes/negative_count_is_refused (0.00s)
        m_test.go:7: ensureBytes(-1) = -1, want 0
```

The runner prints the function, the subtest, and `file:line:` before every message. So the message never says where,
and the function name plus the subtest name carry the unit and the scenario. `t.Fail()` with no message prints the
name and nothing else; `t.Fatal("mismatch")` prints the literal and no values.

## The failure line

There is no assertion in the standard library; the message is the whole report, and its shape is fixed by the Go
wiki: the function, its input, got, then want.

```go
if got := ensureBytes(-1); got != 0 {
    t.Errorf("ensureBytes(-1) = %d, want 0", got)
}
```

- **Got before want.** `%v = %v, want %v`. A swapped pair prints the bug as the expectation.
- **Identify the function and the input.** `ensureBytes(-1) = -1, want 0` beats `wrong result: -1`.
- **Compare whole values with a diff where the value is the behavior.** `cmp.Diff(want, got)` from `go-cmp` returns a
  diff labeled `(-want +got)`; print it as `t.Errorf("ensureBytes() mismatch (-want +got):\n%s", diff)`.
- **Assert error semantics.** `errors.Is(err, ErrNegativeCount)` or `errors.As`, not `err.Error() == "…"`.

## Subtests and table-driven tests

`t.Run(name, func(t *testing.T) {…})` prints the name after a slash, with spaces turned into underscores:
`TestEnsureBytes/negative_count_is_refused`. Name each table case by its condition, never by its ordinal
(`case_3` is a location), and keep the names unique, since two identical names are disambiguated by a suffix. The
message inside the loop identifies the input (`ensureBytes(%d)`), because the case name may not spell it.

## Keep going, or stop

`t.Error` and `t.Errorf` mark the test failed and continue, so one run reports every mismatch; `t.Fatal` and
`t.Fatalf` stop the test, and are for the point after which continuing is meaningless (a `nil` the next line
dereferences).

## Order and flakiness

`go test -shuffle=on` randomizes the order of top-level tests and prints the seed; `-shuffle=<seed>` replays it.
`t.Parallel()` runs subtests concurrently and surfaces shared state as a race; `-race` reports the data race itself.
Fix an order dependence by removing the package-level state, not by dropping `-shuffle`.

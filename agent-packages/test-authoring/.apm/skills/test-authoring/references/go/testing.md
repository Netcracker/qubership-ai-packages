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

The runner prints the function, the subtest, and `file:line:` before every message. So the message never says where, and
the function name plus the subtest name carry the unit and the scenario. `t.Fail()` with no message prints the name and
nothing else; `t.Fatal("mismatch")` prints the literal and no values. A test that holds a case with its controls in one
check (`SKILL.md` §7) is named by the rule they establish.

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
`TestEnsureBytes/negative_count_is_refused`. Name each table case by its condition, never by its ordinal (`case_3` is a
location), and keep the names unique, since two identical names are disambiguated by a suffix. The message inside the
loop identifies the input (`ensureBytes(%d)`), because the case name may not spell it. Cases that share a setup
(`SKILL.md` §7) and assert the same way may be rows of the table, each run through `t.Run` so that it has its own name
and result, or separate functions on one helper marked with `t.Helper()`. The main skill (§7) and the file's neighbors
(§9) choose between them, and a short setup is repeated in each case. `t.Error` against `t.Fatal` inside the subtest
decides whether that case continues, not whether the next row runs. Rows assert the same way where the loop makes the
same comparisons for every row. A table with `want` and `wantErr error` columns whose loop compares both,
`errors.Is(err, tt.wantErr)` and `got != tt.want`, is one table. So is the table the `gotests` generator writes: a
`wantErr bool` column, `(err != nil) != tt.wantErr` compared for every row with a `return` on a mismatch, and `got`
compared with `tt.want` for every row. That table is the idiom of the ecosystem, and a new row whose input the contract
accepts joins it (§9): the row requires no error and compares `got` with `want`, the comparisons §5 to §7 ask for there.
A new row that expects an error does not join it, because the table is ill-suited to such a row in two ways. A `bool`
establishes only that some error came back, which is §5's row *An assertion weakened until it passes*. An error row
compares `got` with a zero `want`, which asserts more than the contract where the contract leaves the result undefined
on an error. The new error case is a test of its own, or a table of its own where there are several, beside the old one.
The old table keeps its rows and its assertions unless the task is to rewrite them. Where the setup is too long to
repeat, the old loop and the new test share it through a helper that both call, which is the one change §9 allows in a
twin. A new table avoids both weaknesses. It carries `wantErr error` and compares with `errors.Is`. Where the contract
leaves the result undefined on an error, the accepting rows and the rejecting rows are two tables, each with its own
loop, and only the accepting loop compares `got`. A row field that chooses between two blocks of assertions is the
condition that decides whether an assertion runs, which §6 rules out. Such cases are separate test functions, or
separate `t.Run` blocks written out under one parent, that call one helper marked with `t.Helper()`. Many cases of each
kind are one table for each kind.

## Keep going, or stop

`t.Error` and `t.Errorf` mark the test failed and continue, so one run reports every mismatch; `t.Fatal` and
`t.Fatalf` stop the test, and are for the point after which continuing is meaningless (a `nil` the next line
dereferences).

## Order and flakiness

`go test -shuffle=on` randomizes the order of top-level tests and prints the seed; `-shuffle=<seed>` replays it.
`t.Parallel()` runs subtests concurrently and surfaces shared state as a race; `-race` reports the data race itself.
Fix an order dependence by removing the package-level state, not by dropping `-shuffle`.

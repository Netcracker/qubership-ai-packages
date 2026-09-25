# Rust `cargo test` and the assertion macros

What `cargo test` prints and which macro carries the values. The harness and the macros ship together, so one file
covers both roles. The rules that use it are in `SKILL.md` §7 and §8.

## What the runner prints

```text
---- tests::assert_eq_prints_both stdout ----
thread 'tests::assert_eq_prints_both' panicked at src/lib.rs:5:42:
assertion `left == right` failed
  left: -1
 right: 0
```

The module path and the test name are printed before the panic, with the file and line. So the module carries the unit,
the test name carries the scenario and the outcome, and the message never says where. A test that holds a case with its
controls in one check (`SKILL.md` §7) is named by the rule they establish.

## Which macro prints the operands

| Call | Panic message |
| --- | --- |
| `assert_eq!(ensure_bytes(-1), 0)` | `assertion \`left == right\` failed` then `left: -1` and `right: 0` |
| `assert_eq!(ensure_bytes(-1), 0, "ensure_bytes({})", -1)` | `assertion \`left == right\` failed: ensure_bytes(-1)` then both values |
| `assert!(ensure_bytes(-1) == 0)` | `assertion failed: ensure_bytes(-1) == 0` |
| `assert!(ensure_bytes(-1) == 0, "ensure_bytes(-1)")` | `ensure_bytes(-1)` and nothing else |
| `panic!()` | `explicit panic` |
| `#[should_panic(expected = "negative")]` when the panic says `boom` | `panic message: "boom"` then `expected substring: "negative"` |

`assert_eq!` and `assert_ne!` print both operands in `Debug` form; `assert!` prints the expression text and no
values, and **a message on `assert!` replaces the expression text**, so a message there has to carry the values
itself. Use `assert_eq!` for a comparison and keep `assert!` for a boolean result. There is no prescribed operand
order; `left` and `right` are labeled as written.

## Parameterized cases

The engine has no parameterized test. A loop over cases inside one `#[test]` reports the first failure only, and each
call in the loop is a case of its own (§7's bullet *One behavior per test*), so the cases after the first failure are
not reported. Separate `#[test]` functions, a macro that expands to one `#[test]` per case, or the `rstest` crate's
`#[case]` give each case its own name in the report, which is the shape §7 asks for. A crate without `rstest` often
keeps such a loop anyway. It is a check that stops at the first mismatch, which §9 lists among the shapes a new test
does not take. Where the file already has one, the new case is a `#[test]` function of its own, or a row of the file's
macro where it has one, and the loop stays as it is unless the task is to rewrite it. The pull request names §7. Name an
`rstest` case by its condition, `#[case::minus_one(-1)]`, since the default name is an index. Cases that share a setup
(`SKILL.md` §7) and assert the same way may be the `#[case]` rows of one `rstest` function, or separate `#[test]`
functions that call one helper which builds the setup from the varying value. The main skill (§7) and the file's
neighbors (§9) choose between them, and a short setup is repeated in each case. An `Err` and an `Ok` that one
`assert_eq!` compares assert the same way and stay rows. Where the cases need different assertions, one panicking under
`#[should_panic]` and one returning a value, they are separate functions on that helper. Many cases of each kind are one
`rstest` function for each kind.

## Grouping assertions

Each `assert_eq!` panics on failure, so a test with several assertions on one result stops at the first. Where the
fields are independent, compare the whole value with one `assert_eq!` on a `Debug`-printable struct, which prints the
full diff of both sides, or split the test. Several expectations on the result of one act, the errors of one validated
batch, are one `assert_eq!` of the whole list reduced to the fields the behavior defines, the record and the error code
without the message, sorted where the behavior defines no order, so that one run shows every mismatch (§7).

## Errors

For a `Result`, match the variant: `assert!(matches!(r, Err(Error::NegativeCount(_))))`, or
`assert_eq!(r.unwrap_err(), Error::NegativeCount(-1))` where the error type is `PartialEq`. For a panic,
`#[should_panic(expected = "…")]` matches a substring of the message; keep the substring to the part the behavior
defines.

## Order and flakiness

libtest runs tests on several threads by default, so a shared-state dependence usually shows as flakiness without any
extra tool; `--test-threads=1` hides it and is not a fix. Remove the shared `static` or the file both tests write.

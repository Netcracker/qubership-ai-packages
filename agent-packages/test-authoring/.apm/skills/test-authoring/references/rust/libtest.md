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

The harness has no parameterized test. A loop over cases inside one `#[test]` reports the first failure only, and the
message must then identify the case: `assert_eq!(ensure_bytes(n), 0, "ensure_bytes({n})")`. A macro that expands to one
`#[test]` per case, or the `rstest` crate's `#[case]`, gives each case its own name in the report, which is the shape §7
asks for. Name an `rstest` case by its condition, `#[case::minus_one(-1)]`, since the default name is an index. Cases
that share a setup (`SKILL.md` §7) and assert the same way are the `#[case]` rows of one `rstest` function, or separate
`#[test]` functions that call one helper which builds the setup from the varying value. An `Err` and an `Ok` that one
`assert_eq!` compares assert the same way and stay rows. Where the cases need different assertions, one panicking under
`#[should_panic]` and one returning a value, they are separate functions on that helper. Many cases of each kind are one
`rstest` function for each kind.

## Grouping assertions

Each `assert_eq!` panics on failure, so a test with several assertions on one result stops at the first. Where the
fields are independent, compare the whole value with one `assert_eq!` on a `Debug`-printable struct, which prints the
full diff of both sides, or split the test.

## Errors

For a `Result`, match the variant: `assert!(matches!(r, Err(Error::NegativeCount(_))))`, or
`assert_eq!(r.unwrap_err(), Error::NegativeCount(-1))` where the error type is `PartialEq`. For a panic,
`#[should_panic(expected = "…")]` matches a substring of the message; keep the substring to the part the behavior
defines.

## Order and flakiness

libtest runs tests on several threads by default, so a shared-state dependence usually shows as flakiness without any
extra tool; `--test-threads=1` hides it and is not a fix. Remove the shared `static` or the file both tests write.

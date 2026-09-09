# Mutation tools

What each tool calls its verdicts, and how `SKILL.md` §1 reads them: *no coverage* is a missing test, a mutant that
does not compile is no information, and *survived* on a line the change touched is a candidate gap the writer
settles: a missing or weak test where the mutant changes behavior the specification defines, an equivalent mutant
explained in the pull request where it does not, an unresolved one reported as such. The tools name the survivor
differently (*survived*, *lived*, *missed*, and go-mutesting's *failed*), and every name below means the same thing:
no test failed with the mutation applied. Scope every run to the diff.

| Ecosystem | Tool | Verdicts | Scoping and notes |
| --- | --- | --- | --- |
| JVM | PIT (`pitest`) | `KILLED`, `SURVIVED`, `NO_COVERAGE`, `TIMED_OUT`, `NON_VIABLE` | Incremental analysis re-runs only mutants whose class or killing test changed; `targetClasses` narrows the run |
| Python | `mutmut run` | killed, survived, suspicious, timeout | Re-tests by default only the functions whose source changed |
| Go | `gremlins` | killed, lived, not covered, timed out, not viable | Re-runs `go test` per mutant; pass the changed packages |
| Go | `go-mutesting` | passed (the mutant was killed), failed (it survived), skipped | The words are inverted against every other tool; read *failed* as *survived* |
| Rust | `cargo mutants` | caught, missed, unviable, timeout | `--file` or `--in-diff` scopes to the changed code; *unviable* is a mutant that did not compile |
| JavaScript | Stryker | `Killed`, `Survived`, `NoCoverage`, `Timeout`, `CompileError` | `--mutate` takes the changed files; a compile error is no information |

Write the killing test through the unit's interface, not against the mutant: a test that asserts the
exact line the mutant changed is a change detector (§5) that the next refactoring breaks.

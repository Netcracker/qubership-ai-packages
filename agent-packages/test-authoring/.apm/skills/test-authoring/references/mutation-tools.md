# Mutation tools

What each tool calls its verdicts, and how `SKILL.md` §1 reads them: *no coverage* is a missing test, a mutant that
does not compile is no information, and *survived* on a line the change touched is a candidate gap the writer
settles: a missing or weak test where the mutant changes behavior the specification defines, an equivalent mutant
explained in the pull request where it does not, an unresolved one reported as such. The tools name the survivor
differently (*survived*, *lived*, *missed*, *escaped*, and go-mutesting's *failed*), and every name below means the
same thing: no test failed with the mutation applied. Scope every run to the diff.

| Ecosystem | Tool | Verdicts | Scoping and notes |
| --- | --- | --- | --- |
| JVM | PIT (`pitest`) | `KILLED`, `SURVIVED`, `NO_COVERAGE`, `TIMED_OUT`, `NON_VIABLE` | Incremental analysis re-runs only mutants whose class or killing test changed; `targetClasses` narrows the run |
| Python | `mutmut run` | killed, survived, suspicious, timeout | Re-tests by default only the functions whose source changed |
| Go | `gremlins` | killed, lived, not covered, timed out, not viable, skipped | `--diff <ref>` reports the mutants outside the change *skipped*, and can skip changed lines too; *killed* includes mutants that did not compile, and *not covered* includes mutants in code the tests run (below) |
| Go | `go-mutesting` | passed (the mutant was killed), failed (it survived), skipped | No diff mode: pass the changed files. `--match` with an anchored regex of the changed functions' names narrows the run, but mutates only function declarations, so leave it out where the change touches a package-level `const` or `var`. The words are inverted against every other tool; read *failed* as *survived*. The built-in runner reports a mutant that did not compile as *passed* (below) |
| Go | `mutago` | killed, escaped, not covered, skipped, errored | `--git-diff-lines --git-diff-base <ref>` keeps the mutants on lines changed since the merge base with `<ref>`, uncommitted changes included and untracked files left out. *skipped* includes mutants that did not compile, and under a `go.work` workspace *not covered* includes mutants in code the tests run (below) |
| Rust | `cargo mutants` | caught, missed, unviable, timeout | `--file` or `--in-diff` scopes to the changed code; *unviable* is a mutant that did not compile |
| JavaScript | Stryker | `Killed`, `Survived`, `NoCoverage`, `Timeout`, `CompileError` | `--mutate` takes the changed files; a compile error is no information |

In Go, `go test` exits 1 when the package does not build, as it does when a test fails, and prints
`FAIL <package> [build failed]` or `FAIL <package> [setup failed]`. gremlins reads exit 1 as *killed* and only exit 2
as *not viable*. go-mutesting's built-in runner, and the `test-mutated-package.sh` script it ships, read exit 1 as
*passed*. With the defaults of these two tools, a mutant that does not compile is counted as killed. gremlins has no
option that changes this. For go-mutesting, pass `--exec` a copy of `test-mutated-package.sh` that exits 2
(*skipped*) when the `go test` output contains `[build failed]` or `[setup failed]`. Keep the copy's other steps: with
`--exec`, go-mutesting leaves it to the script to put the mutant in place, run `go test`, and restore the file.

mutago's built-in runner reports a mutant *skipped* when the `go test` output contains `[build failed]` or
`[setup failed]`, and *errored* for a test exit it cannot classify. It reports *not covered* only under `--coverage`.
The runner swaps each mutant in with `go test -overlay`, so the source files stay as they are. mutago exits 0 with
escaped mutants unless `--fail-on-escaped` is set, and then exits 4 when a mutant escapes that the baseline file does
not list. It exits 3 on a tool error, including tests that fail or time out before any mutation.

gremlins matches the coverage profile to source files after deleting every `<module path>/` from the profile's file
names. Where that string occurs again inside a package's path, every mutant in that package is reported *not
covered*. Go coverage blocks do not span the case expressions of a `switch`, so gremlins reports every mutant in a
`case` expression *not covered* and never runs it, although the case runs. Read *not covered* in both as no
information, not as a missing test. gremlins' default mutators swap operators and remove nothing, so a check that the
happy path runs through can leave no survivor although no test feeds it the input it rejects.

gremlins' `--diff` reads each hunk as one block of as many lines as the hunk adds, starting at its first changed line,
so a later change in the same hunk is reported *skipped*; set git's `diff.context` to 0 for the run. It compares the
paths git prints, relative to the repository root, with paths relative to the directory it runs in. A package
argument, or a module below the repository root, then makes every mutant *skipped*, and the run passes with nothing
tested. Run it in the module root with no argument, set `diff.relative` to true where the module is below the
repository root, and check that no changed line has only *skipped* mutants.

In the file passed to go-mutesting's `--config`, set both `skip_without_test` and `skip_with_build_tags` to false; the
shipped `config.yml.dist` sets both to true. `skip_with_build_tags` also skips every file that has no `_test.go` of
the same name, whatever `skip_without_test` is set to. go-mutesting mutates the files in place, so run it on a copy
or a worktree. It writes each mutant with `go/printer`, so a mutant's diff can carry hunks of reformatting beside the
one that holds the mutation; find that hunk, which need not be the first, before deciding whether the mutant is on a
changed line.

Four conditions let a mutago run exit 0 although it ran none of the change's mutants or ignored their escape. A
summary line whose total is 0 for a change to non-test code, or whose mutants are all *not covered*, means the change
was not tested. `skip_without_test` and `skip_with_build_tags` default to true in the code, not only in
`config.yml.dist`, and `skip_without_test` leaves out every file that has no `_test.go` of the same name. Pass
`--config` with both set to false. mutago finds the changed files by matching `+++ b/<path>` in `git diff`, so a git
config that colors the diff or changes its destination prefix (`color.ui=always`, `color.diff=always`,
`diff.noprefix`, `diff.mnemonicPrefix`, `diff.dstPrefix`) leaves no changed line. `diff.relative` does the same when
mutago runs in a subdirectory. Override those keys for its process with `GIT_CONFIG_COUNT`, `GIT_CONFIG_KEY_<n>`, and
`GIT_CONFIG_VALUE_<n>`. It reads `mutago-baseline.json` from its working directory, and an escape listed there does
not fail the run; pass `--baseline` with a path that does not exist. Under a `go.work` workspace, mutago takes the
output of `go list -m`, one line per module, as its module path, and `--coverage` then reports every mutant *not
covered*. Read *not covered* there as no information, not as a missing test. Set `GOWORK=off` and pass the changed
packages or files, since `./...` then fails on a nested module.

Write the killing test through the unit's interface, not against the mutant: a test that asserts the
exact line the mutant changed is a change detector (§5) that the next refactoring breaks.

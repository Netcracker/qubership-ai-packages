# Go mutation tools

Evidence for the Go rows of `references/mutation-tools.md`: what gremlins, go-mutesting, and mutago report for a
mutant that does not compile, and how to tell it from a mutant a test killed.

## Where the facts come from

A mutation pilot on a Go service ran gremlins v0.6.0 and go-mutesting at tag v2.3.1
(`v0.0.0-20251226130216-48d0401f00fb`) and checked each verdict against a hand run of the mutant. The service later
moved its diff-scoped run to mutago v2.10.40, run with Go 1.27.3 and git 2.56 on macOS. Each fact was then read in the
source at those tags:

- gremlins maps the exit code of `go test` in [`getTestFailedStatus`][g-status]: 1 is `KILLED`, 2 is `NOT VIABLE`.
  `unleash` has no flag that replaces the test command.
- go-mutesting's [built-in runner][m-builtin] and its [`test-mutated-package.sh`][m-script] map 1 to `PASS`. With
  `--exec` it [only runs the script][m-exec], with the mutant's paths in the environment.
- mutago turns a `go test` exit of 1 with `[build failed]` or `[setup failed]` in the output into a skip in
  [`classifyGoTestResult`][t-classify], and [records any other exit][t-record] it cannot classify as `ERRORED`. It
  marks a mutant `NOT COVERED` only [under `--coverage`][t-coverage].

`go test` exits 1 on a build failure; the output is in `framework_output.md`.

[g-status]: https://github.com/go-gremlins/gremlins/blob/v0.6.0/internal/engine/executor.go#L257-L266
[m-builtin]: https://github.com/avito-tech/go-mutesting/blob/v2.3.1/cmd/go-mutesting/main.go#L486-L498
[m-script]: https://github.com/avito-tech/go-mutesting/blob/v2.3.1/scripts/exec/test-mutated-package.sh#L46-L59
[m-exec]: https://github.com/avito-tech/go-mutesting/blob/v2.3.1/cmd/go-mutesting/main.go#L518-L552
[t-classify]: https://github.com/quality-gates/mutago/blob/v2.10.40/internal/engine/engine.go#L1731-L1736
[t-record]: https://github.com/quality-gates/mutago/blob/v2.10.40/internal/engine/engine.go#L1841-L1856
[t-coverage]: https://github.com/quality-gates/mutago/blob/v2.10.40/internal/engine/runner.go#L29

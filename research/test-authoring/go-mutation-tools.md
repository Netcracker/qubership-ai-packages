# Go mutation tools

Evidence for the Go rows of `references/mutation-tools.md`: what gremlins, go-mutesting, and mutago report for a
mutant that does not compile, when gremlins and mutago report *not covered* for code the tests run, and how each tool
is scoped to a change.

## Where the facts come from

A mutation pilot on a Go service ran gremlins v0.6.0 and go-mutesting at tag v2.3.1
(`v0.0.0-20251226130216-48d0401f00fb`) and checked each verdict against a hand run of the mutant. The service later
moved its diff-scoped run to mutago v2.10.40, run with Go 1.27.3 and git 2.56 on macOS. Each fact was then read in the
source at those tags:

- gremlins maps the exit code of `go test` in [`getTestFailedStatus`][g-status]: 1 is `KILLED`, 2 is `NOT VIABLE`.
  `unleash` has no flag that replaces the test command. It strips every `<module path>/` from the coverage profile's
  file names in [`removeModuleFromPath`][g-cover] and does not run a mutant it marks `NOT COVERED`
  ([executor.go][g-skip]). Its [default mutators][g-default] are five operator swaps.
- [`cmd/cover`][cover] starts the counter of every case clause after its colon, so no coverage block holds a `case`
  expression.
- gremlins' [`newChanges`][g-diff] turns each hunk of `--diff` into one range of as many lines as the hunk adds, from
  its first change. On a small test repository, a second change in one hunk was reported `SKIPPED` until git's
  `diff.context` was 0, and `--diff` with a package argument, or on a module below the repository root, reported every
  mutant `SKIPPED`. These two were seen on that repository only.
- go-mutesting's [built-in runner][m-builtin] and its [`test-mutated-package.sh`][m-script] map 1 to `PASS`. With
  `--exec` it [only runs the script][m-exec], with the mutant's paths in the environment. It [skips a file with no
  `_test.go` when either skip setting is on][m-skip], mutates only function declarations [under `--match`][m-match],
  and writes the mutant with [`go/printer`][m-printer].
- mutago turns a `go test` exit of 1 with `[build failed]` or `[setup failed]` in the output into a skip in
  [`classifyGoTestResult`][t-classify], and [records any other exit][t-record] it cannot classify as `ERRORED`. It
  marks a mutant `NOT COVERED` only [under `--coverage`][t-coverage].

`go test` exits 1 on a build failure; the output is in `framework_output.md`.

## mutago setup

Each mutago fact in the reference was seen in a run, and then read in the source:

- The built-in runner swaps the mutant in with [`-overlay`][t-overlay]. mutago exits [3 on a tool error and 4 on a
  failed gate][t-exit], and 3 when the tests fail [before any mutation][t-preflight]. The escaped gate
  [counts only escapes missing from the baseline][t-gate], read by default from [`mutago-baseline.json`][t-baseline].
- `skip_without_test` and `skip_with_build_tags` are [true by default in the code][t-defaults], and a file with no
  `_test.go` of the same name is [skipped only under `skip_without_test`][t-skip].
- The changed lines come from [`git diff --unified=0 <merge base>`][t-gitdiff], whose file names are matched with
  `^\+\+\+ b/(.+)$`. A diff with color, or with a destination prefix other than `b/`, matches no file, and the run
  saw 0 mutants and exit 0 under each of those settings.
- The module path is [the whole output of `go list -m`][t-module], which under a `go.work` workspace holds every
  module. With `--coverage`, the run reported every mutant `NOT COVERED` although `go test -coverprofile` covered the
  lines, and exited 0 under `--fail-on-escaped`. `GOWORK=off` restored the verdicts, and a `./...` target then failed
  on the nested modules.

[g-status]: https://github.com/go-gremlins/gremlins/blob/v0.6.0/internal/engine/executor.go#L257-L266
[g-cover]: https://github.com/go-gremlins/gremlins/blob/v0.6.0/internal/coverage/coverage.go#L202-L207
[g-skip]: https://github.com/go-gremlins/gremlins/blob/v0.6.0/internal/engine/executor.go#L171-L175
[g-default]: https://github.com/go-gremlins/gremlins/blob/v0.6.0/internal/configuration/mutantenabled.go#L23-L35
[g-diff]: https://github.com/go-gremlins/gremlins/blob/v0.6.0/internal/diff/diff.go#L34-L51
[cover]: https://github.com/golang/go/blob/go1.27.3/src/cmd/cover/cover.go#L463-L466
[m-builtin]: https://github.com/avito-tech/go-mutesting/blob/v2.3.1/cmd/go-mutesting/main.go#L486-L498
[m-script]: https://github.com/avito-tech/go-mutesting/blob/v2.3.1/scripts/exec/test-mutated-package.sh#L46-L59
[m-exec]: https://github.com/avito-tech/go-mutesting/blob/v2.3.1/cmd/go-mutesting/main.go#L518-L552
[m-skip]: https://github.com/avito-tech/go-mutesting/blob/v2.3.1/internal/importing/filepath.go#L80-L97
[m-match]: https://github.com/avito-tech/go-mutesting/blob/v2.3.1/cmd/go-mutesting/main.go#L242-L254
[m-printer]: https://github.com/avito-tech/go-mutesting/blob/v2.3.1/cmd/go-mutesting/main.go#L564
[t-classify]: https://github.com/quality-gates/mutago/blob/v2.10.40/internal/engine/engine.go#L1731-L1736
[t-record]: https://github.com/quality-gates/mutago/blob/v2.10.40/internal/engine/engine.go#L1841-L1856
[t-coverage]: https://github.com/quality-gates/mutago/blob/v2.10.40/internal/engine/runner.go#L29
[t-overlay]: https://github.com/quality-gates/mutago/blob/v2.10.40/internal/engine/gotest.go#L120
[t-exit]: https://github.com/quality-gates/mutago/blob/v2.10.40/internal/engine/engine.go#L46-L51
[t-preflight]: https://github.com/quality-gates/mutago/blob/v2.10.40/internal/engine/engine.go#L927-L946
[t-gate]: https://github.com/quality-gates/mutago/blob/v2.10.40/internal/engine/engine.go#L1398-L1412
[t-baseline]: https://github.com/quality-gates/mutago/blob/v2.10.40/internal/models/options.go#L64
[t-defaults]: https://github.com/quality-gates/mutago/blob/v2.10.40/internal/models/options.go#L108-L111
[t-skip]: https://github.com/quality-gates/mutago/blob/v2.10.40/internal/importing/filepath.go#L106-L121
[t-gitdiff]: https://github.com/quality-gates/mutago/blob/v2.10.40/internal/gitdiff/gitdiff.go#L35-L50
[t-module]: https://github.com/quality-gates/mutago/blob/v2.10.40/internal/engine/engine.go#L480-L486

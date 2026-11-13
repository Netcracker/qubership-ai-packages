# Measurement brief

Give this to one subagent at the start of the axes. The orchestrator fills in the placeholders.

> You measure diff coverage and diff mutation coverage for a pull request review. The review input is `<work>/input.md`;
> the change is `git diff <base>...<head>`. Add your own worktree first
> (`git -C <workspace> worktree add <work>/measure-wt <head>`) and run everything there, never in `<workspace>`:
> reviewers read it at the same time. Write only under `<work>/measure/` and `<work>/measure-wt`, and post nothing.
>
> 1. Find the tool. Where the repository's agent rules in `input.md` name one
>    (`run pitestDiff after changing src/main`), use it. For a Gradle build with Java sources, cribro applies when
>    `settings.gradle` or `settings.gradle.kts` names `io.github.cribrodev.cribro`, or when
>    `~/.gradle/cribro/cribro.init.gradle` exists.
>    Load the `cribro` skill for its commands; where it is not installed, run `./gradlew -q cribro` (with
>    `--init-script` for the init script) and follow the guide it prints. With no tool, stop and reply `skipped`.
> 2. Measure against `<base>`, not the tool's default base (for cribro, `-Pcribro.diffBase=<base>`).
> 3. Run the full test suite of each changed module first: a run filtered to some tests reports the lines other tests
>    execute as unexecuted. Where part of the suite needs a service this machine lacks (a database, a container), run
>    the rest. Then run the mutation tool on the same modules, in the background, for at most 30 minutes; where it would
>    take longer, narrow it to the tests that exercise the change (for cribro, `-Pcribro.pitestTargetTests=<classes>`).
>    A mutation run that times out does not discard the coverage report.
> 4. Read the exit status of every run, and check that each report was written by this run: a build that failed leaves
>    the previous report on disk, and nothing in it shows that it is stale. Read the mutation tool's log for tests it
>    dropped (PIT drops a test that fails on its first run).
> 5. Copy the reports into `<work>/measure/`, one file per module and report (for cribro,
>    `build/reports/diff-coverage/test.txt`, `build/reports/pitest-diff/survivors.txt`, and `pit.log`). Where the build
>    fails on the reviewed head, copy its output there too.
> 6. Write `<work>/measure/README.md`. It opens with the outcome of each part (coverage, mutation: ran, timed out,
>    failed, or not run, and why), then lists the files, the commands, the base, and every test the tools did not run
>    (tests in another module or another test task, tests left out for a missing service, tests the mutation tool
>    dropped).
>
> Reply with one line: `ran` (every part ran), `failed` (a part failed or timed out), or `skipped` (no tool), and the
> reason.

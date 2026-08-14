# Axis: tests

Finding prefix: `TEST`.

You are reviewing the **test suite as an asset**, not the code under it. The question is not "is coverage high" but
"if this code broke, would anything notice, and would the failure name the cause".

Your report is an input to every other axis in this review: the places where nothing would notice are where the other
agents should dig. Make that list explicit and specific.

## What counts as a finding

- A behavior that the code promises (in its API, its docs, or its error messages) and no test pins.
- A test that cannot fail: asserts nothing meaningful, asserts the mock, catches everything, or is skipped.
- A defect class the suite is structurally blind to — concurrency, timeouts, partial failure, resource cleanup,
  large inputs, malformed inputs — because there is no harness that could express it.
- A test that will fail for reasons unrelated to the code: wall-clock time, ordering, network, ports, locale,
  file-system layout. Flakiness is a correctness problem in the suite.
- A missing regression test for something the history says already broke (search the changelog and fix commits).
- Tests that lock in the implementation rather than the contract, so any refactor breaks them. This makes the code
  unchangeable and is a real cost, not a style preference.

## What is not a finding

A coverage percentage. Never report one as a defect on its own. Coverage is a way to find untested behavior, not a
target — say which behavior is untested and why it matters.

## Method

1. Run the suite. Record the command, the wall-clock time, and the result in the report. A suite too slow to run on
   every change is a finding in itself.
2. Map the test layout onto the source layout. Which packages, which layers, which failure paths have no tests at all?
   `sb digest` on both trees is usually enough.
3. Measure coverage. See *Measurement setup* below — the project not having it configured is not a reason to skip it.
   Use the number as a pointer, never as a verdict: report the uncovered branches that matter, by name.
4. Probe for surviving mutants in the two or three most important units, not the whole repository. See below for the
   full-tool route and the manual one. Surviving mutants in core logic are the strongest evidence this axis can
   produce — quote each one as the exact edit that no test noticed.
5. Look for the harnesses that should exist and do not: property-based tests where invariants are stated in prose,
   fuzzing for parsers, integration tests against a real peer for protocol code, race detection in CI, deterministic
   clocks and injected schedulers for timeout logic.
6. Read CI: which of these actually runs on a pull request, on which platforms and versions, and what is allowed to
   fail.

## Measurement setup

Assume nothing is configured. Most projects have neither coverage nor mutation testing, and "the project does not
measure this" is the finding, not the end of the work. Set it up in a throwaway copy (see *Working-tree hygiene* in
the ground rules), measure, report the command, and throw the copy away.

**Without touching the project**, these work as-is in most repositories:

| Ecosystem | Coverage |
| --- | --- |
| Maven | `mvn -q org.jacoco:jacoco-maven-plugin:prepare-agent test org.jacoco:jacoco-maven-plugin:report` — no POM change needed |
| Gradle | add the `jacoco` plugin in an init script passed with `--init-script`, not in `build.gradle` |
| Go | `go test ./... -coverprofile=cover.out && go tool cover -func=cover.out` |
| Rust | `cargo llvm-cov --summary-only` |
| Python | `pytest --cov=<pkg> --cov-report=term-missing` |
| Node | `npx c8 <test command>` |

**Mutation testing** usually does need a project edit — PIT needs `pitest-junit5-plugin` declared as a plugin
dependency, which the command line cannot supply. That is exactly what the throwaway copy is for: edit the POM there,
run it scoped, discard.

Scope it or it will run for hours: target the two or three classes or packages that carry the logic, cap the
operators to the default set, and give the whole exercise a wall-clock budget of about fifteen minutes. Say in the
report what you scoped it to — a mutation score for 3% of the codebase is a useful number only if the reader knows it
is 3%.

**When the tooling will not cooperate** — an exotic build, an unavailable dependency, tests that need a live peer —
fall back to the manual probe, which is often better evidence anyway:

1. Pick six to ten specific behaviors that matter (a boundary check, an error branch, a timeout value, an ordering
   guarantee, a cleanup call).
2. In the throwaway copy, break each one deliberately and minimally: invert a comparison, drop a `close()`, return
   early, change a constant, remove a null check.
3. Run the suite after each. Every green run is a surviving mutant, and you can name it precisely: "removing the
   `channel.close()` at `Foo.java:214` leaves the suite green".

That list beats any percentage. Report the manual probe as such, so nobody mistakes it for a full mutation run, and
say how many mutations you tried — six survivors out of six attempts and six out of sixty are very different claims.

## Required section

End the report with **Where the suite is blind** — a ranked list of source areas with no meaningful test, each with
one line on the defect class that would hide there. Other axes read this section first.

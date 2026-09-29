# Axis: build and release engineering

Finding prefix: `BUILD`.

Whether the thing can be built, tested, and shipped reliably by someone who is not the person who set it up.

## Build

- **Cold clone to green build.** Do it: fresh clone, documented command, nothing else. Record what was needed that
  the documentation did not mention — a toolchain version, a credential, a local registry, a running database.
  Anything undocumented is a finding.
- **Reproducibility.** Pinned toolchain version, pinned plugin and action versions, committed lockfile, no dependency
  on wall-clock time or network state. Build twice and compare artifacts where the ecosystem supports it.
- **Speed and incrementality.** Time a clean build and an incremental one. A build slow enough that developers skip
  it is the root cause of the next set of defects.
- **Warnings.** Are compiler warnings visible, and is there a policy? A build with hundreds of warnings has no
  warnings, because nobody reads them.
- **Generated code.** Is it committed, generated, or both? Does regeneration produce a clean tree? Drift between the
  generator's input and the committed output is a finding on its own.

## CI

- What runs on a pull request versus on the default branch versus on a release, and what is allowed to fail.
- The matrix: which language versions, platforms, and dependency versions are actually exercised against the ones the
  project claims to support. A supported combination nobody tests is a finding.
- Required checks: does a green pull request mean the tests ran? A check that is skipped when no files match, and is
  also required, reports green for a change that never ran.
- Flaky-job handling: automatic retries that hide real failures, `continue-on-error` on something that matters.
- Caching that can serve a stale result across a dependency change.
- **Where the configuration comes from.** For every linter, scanner, and quality gate, establish which file CI
  actually applies and where that file lives. Configuration pulled from outside the repository — an organization
  `.github` repository, a reusable workflow, a shared preset — is normal and often good, but it has consequences to
  check: pinned to a moving ref, the rules change with no commit here and a green history can turn red overnight;
  and a contributor running the tool locally may get a different rule set from CI, which turns "it passed on my
  machine" into a recurring argument. Report the divergence and the ref, not the existence of the arrangement.

## Release

- Is the release process documented, and can somebody other than its author run it? Manual steps are findings when
  they are unwritten, not when they are deliberate.
- Versioning: where the version lives, whether it is set in one place, and whether a release is tagged and immutable.
- Publication: which registries, with which credentials, signed or not, with an SBOM or not, and whether a release can
  be reproduced from its tag.
- Changelog generation, and whether the released notes match what actually changed.
- Rollback: can a bad release be yanked or superseded, and is that written down?

## Rules

Findings must name what breaks and for whom. A build detail that never causes a failure is not a finding. Where you
could not run something (no credentials, no network), say so explicitly rather than reporting it as absent.

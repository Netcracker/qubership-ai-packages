# Framework probes

The references under
[`agent-packages/test-authoring/.apm/skills/test-authoring/references/`](../../../agent-packages/test-authoring/.apm/skills/test-authoring/references/)
quote what a framework prints and state how it behaves: which assertion prints the operands, whether a run stops at
the first failure, how a parameterized case is named, when a diff is truncated. Each of those is a fact about one
release of the framework. The probes here run deliberately failing tests against the pinned release, compare the
output with a golden file, and check that every claim the reference makes still holds in that output. When Renovate
bumps a framework and the output changes, the golden comparison fails, the bump does not automerge, and whoever
updates the golden file reads the diff against the claims ledger and edits the reference where it has gone stale.

`framework_output.md` in the parent directory is the hand-measured snapshot the probes replace, one ecosystem at a
time. Nothing under `agent-packages/` is touched by this directory: the probes are research, and the package is what
consumers install.

## Layout

```text
probes/
  run.sh              runs the probes of one or more ecosystems and compares with the golden files
  normalize.py        the normalization every ecosystem's output goes through (paths, durations, temp dirs, pids)
  check-claims.py     verifies every claims.tsv against the golden files and against the reference it cites
  <ecosystem>/        one directory per ecosystem, named <language>-<framework>: python-pytest, go-testing, ...
    probe.sh          the ecosystem's entry point (contract below)
    claims.tsv        the ledger: claim, probe, check, reference quote
    expected/<case>.txt  one golden file per case
    ...               a real dependency manifest and lock file that Renovate updates, and the failing tests
```

## Run locally

```bash
research/test-authoring/probes/run.sh                 # every ecosystem, compare with the golden files
research/test-authoring/probes/run.sh python-pytest   # one ecosystem
research/test-authoring/probes/run.sh --update        # rewrite the golden files
uv run --python 3.12 --no-project python research/test-authoring/probes/check-claims.py
```

`run.sh` exits 1 and prints a unified diff for each case whose output differs from its golden file. The checker
exits 1 and names each claim whose pattern is missing from the golden file, or whose quote is no longer in the
reference. Both need `uv`; each ecosystem needs its own toolchain (`go`, `cargo`, `node`, a JDK), which its
`probe.sh` names in a comment at the top.

## The contract of probe.sh

`run.sh` calls the script with the ecosystem directory as its working directory and one of two commands:

- `probe.sh list` prints the case ids, one per line. An id is `[a-z0-9-]+` and names the behavior probed
  (`assert-forms`, `parametrize`), with a suffix for an environment variant (`diffs-ci`, `diffs-v`).
- `probe.sh run <case>` runs one case and prints its output to stdout, stdout and stderr merged, followed by a last
  line `exit code: N` with the framework's exit status. The script exits non-zero only when the probe itself is
  broken (toolchain missing, unknown case), never because the tests failed: they are meant to.

`run.sh` runs the script under a scrubbed environment: `CI`, `BUILD_NUMBER`, `GITHUB_ACTIONS`, and the other
variables a runner reads to detect CI are unset, colors are off (`NO_COLOR=1`, `TERM=dumb`), the terminal is 80
columns, the locale is `C.UTF-8`. A case about the behavior under CI sets the variable on its own command line, so
that a local run and a CI run produce the same golden file. Where a claim depends on an environment variable, the
probe has both variants, and the ledger cites both.

The output then goes through two normalizations. `normalize.py` replaces the probe directory, the repository root,
`$HOME`, temp directories, durations, clock times, process ids, and `0x` addresses with placeholders and strips
trailing whitespace. Everything the ecosystem alone produces, a header line with version numbers, a random seed, a
platform name, is the `probe.sh`'s to replace, with a placeholder in angle brackets (`pytest-<version>`, `<seed>`).
A version number must not survive into a golden file: a bump that changes no behavior must leave the golden file
untouched.

Cases are pytest invocations, `go test` runs, `cargo test` runs, one file or one filter each. A case is one probe.sh
run so that a failure in one file does not hide the others, and so that a claim can cite a case by its id.

## The ledger

`claims.tsv` is tab-separated with a header row and these columns:

| Column | Content |
| --- | --- |
| `id` | Unique within the ecosystem, `[a-z0-9-]+`; several rows may serve one sentence of the reference |
| `probe` | The case id whose golden file the check runs against |
| `check` | `contains`: the pattern is a literal that must appear in the golden file, with `\n` and `\t` escapes. `regex`: a Python regular expression that must match. `absent`: a regular expression that must not match |
| `pattern` | The literal or the expression |
| `reference` | The file that makes the claim, relative to the skill directory: `references/python/pytest.md`, `SKILL.md` |
| `quote` | A verbatim substring of that file. The checker collapses whitespace on both sides, so a quote may span a wrapped line. Editing the sentence in the reference breaks the row, which is the point |
| `note` | Empty, or `contradicts: ...` where the measurement disagrees with the quote, or `refines: ...` where it adds a condition the reference does not state. The pattern always records the measured behavior; the reference is not edited from here |

The checker prints the `contradicts:` and `refines:` notes as a summary on every run. A contradiction is a finding
for whoever maintains the reference, and it stays in the ledger until the reference changes, at which point the
quote no longer matches and the row is rewritten.

A claim is worth a row when it is a fact about the framework that a release could change: a quoted message, an
operand order, a case name, whether a second failure is reported, whether output is truncated. A rule of judgment
(where to put the comparison, how to name a case) is not.

## Adding an ecosystem

1. Create `probes/<language>-<framework>/` with a manifest and lock that Renovate's manager for that ecosystem
   updates natively (`pyproject.toml` and `uv.lock`, `go.mod` and `go.sum`, `Cargo.toml` and `Cargo.lock`,
   `package.json` and `package-lock.json`, a Gradle version catalog). Pin exact versions. Check
   [`renovate.json`](../../../renovate.json) and the `Netcracker/renovate-config` presets it extends for a
   `packageRules` entry that would skip or group the manifest.
2. Write the failing tests, one file per case, over the same function the reference quotes (`ensure_bytes(-1)`
   returning `-1` instead of `0` in the Python probe).
3. Write `probe.sh` to the contract above, with the ecosystem's own normalization in it.
4. Run `run.sh --update <ecosystem>` and read every golden file: nothing machine-specific, no version numbers.
5. Write `claims.tsv`, one row per claim in the reference, then run `check-claims.py`.
6. Add a job to [`.github/workflows/test-authoring-probes.yml`](../../../.github/workflows/test-authoring-probes.yml)
   that installs the toolchain and runs `run.sh <ecosystem>`, and add the job to the gate's `needs` and its result
   loop.

## After a framework bump

Renovate opens the bump; the probe job fails when the output changed. To land it:

1. Check out the branch and run `run.sh --update <ecosystem>`.
2. Read the diff of the golden files. A changed message or a changed behavior means the reference is stale: edit
   the reference in `agent-packages/`, then rewrite the ledger row's quote and pattern to match. Note a change that
   contradicts a sentence of the reference in the row's `note` until the reference is edited.
3. Run `check-claims.py`; commit the goldens, the ledger, and the reference together.

## CI

`test-authoring-probes.yml` runs on every pull request (a change-detection job skips the probes when neither
`research/test-authoring/probes/`, the skill package, nor the workflow changed), on push to `main`, weekly, and on
demand. One job per ecosystem runs `run.sh` for it; the `claims` job runs the checker; `Test-authoring probes gate`
folds them into one status.

The repository automerges Renovate's non-major bumps once the required checks pass, so **`Test-authoring probes
gate` must be a required status check on `main`** (repository settings, branch protection). Without that, a bump
that changes a framework's output merges with a red probe job and the reference drifts silently. The gate job is
the one to require, not the per-ecosystem jobs: it reports success when the change detection skips the probes, so a
pull request that touches nothing here is not blocked.

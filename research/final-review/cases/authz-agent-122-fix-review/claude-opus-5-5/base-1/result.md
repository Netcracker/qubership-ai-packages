I ran the final-review form over `17b17fc..HEAD`. All three review comments are addressed. Four substantive findings remain: two in the Makefile, one in the docs table, and one in `test/k8s/README.md`. The most important is that the commit title's "let a suite outlast 15 minutes" is still not true, because the Go test timeout in the suite args caps every suite at 10 minutes.

I loaded `english-developer-style` and `test-authoring`. There was no previous report, so there is no table of earlier findings. The change is a Makefile and three Markdown pages, so I used the §2a analogues and say which one under each item. The drift script ran and printed nothing, because it parses no members in Makefile or Markdown.

## Item 1: comments consistent with the code and with each other
**Analogue used:** statements in the Makefile comments and the pages, checked against the code and against each other.

- **`Makefile:99-100`** (the comment above `run-suite`; its body changed, its comment did not): "`helm test` … prints the log only at the end, so the log is streamed while it runs." This is false, and the commit itself shows it. `run-suite` passes no `--logs`, so `helm test` never prints the suite log. Even with `--logs`, the commit message and `helm-templates/authz-test-stand/README.md:61-62` say Helm 4 prints nothing for a Job and Helm 3 fails. A reader would think the streaming is only a convenience, when it is the only way the log ever appears.
- **`Makefile:49-50` and `Makefile:103-104`** tell you to raise the Helm wait "together with `suite.activeDeadlineSeconds`". **`README.md:69-70`** says the same. Both leave out the third limit; see Item 3.
- **`docs/local-integration-tests.md:190`** gives the cause as objects "an older `make e2e` created" and the fix as "then `make e2e`". The same row covers a `make parity-harness` failure. `test/k8s/README.md:47` names `make e2e` or `make parity`, which matches the old Makefile: `git show 8b85515^:Makefile` shows `parity-harness` also used `kubectl apply` in `authz-parity`. Someone hitting this on parity is told the wrong cause and the wrong command to rerun.
- **Checked and consistent:** `suite.yaml:12-13` (the Job is kept after `helm test`) matches the README's `kubectl logs job/…` after `helm test`. The replaced row "runs out of its 10-minute wait" matches `--timeout 10m` at `Makefile:90`.
- No sentence narrates the change ("now", "no longer") outside the commit message.

## Item 2: claimed cases covered
**Analogue used:** each claimed case against the section that handles it, and each command line against the target or CI job that runs it.

| Claimed case | Where it is handled |
| --- | --- |
| Comment 1: a stand set up by an older `make e2e` fails with "invalid ownership metadata"; a note in `docs/local-integration-tests.md` and `test/k8s/README.md` | `docs/local-integration-tests.md:190`; `test/k8s/README.md:47-49` |
| Comment 1: `parity-harness` fails the same way | The docs row (with the wording problem in Item 1); `test/k8s/README.md:47` |
| Comment 2: `--logs` does not print the Job log; use `kubectl logs job/<suite.name>` after `helm test` | `README.md:61-66` |
| Comment 3: a timeout variable per suite, passed to `--timeout` | `Makefile:51-52`, `:107`, `:115`, `:163`. `make -n parity-suite PARITY_SUITE_TIMEOUT=40m` gives `--timeout 40m`; the default gives `15m`. |
| Commit message: Helm 3 fails with "unable to get pod logs for parity-suite" | Confirmed from the Helm v3.15.2 source in the module cache: `pkg/action/release_testing.go` `GetPodLogs` asks for a Pod named after the hook (`h.Name`) whatever its kind, and wraps the error as `unable to get pod logs for %s`. |
| Commit message: Helm 4.3.1 skips the Job and prints nothing | No Helm 4 source here, and no cluster to run it on. This rests on the writer's statement. |

Command lines in the changed files:

| Command and promised outcome | Form that runs | Note |
| --- | --- | --- |
| `helm test authz-test-stand --timeout 15m`, then `kubectl logs job/parity-suite` (README), printing the log | Nearest is `run-suite` in CI on Helm v4.3.1: the same `helm test --timeout`, but run alongside `kubectl logs -f`. Exact form: `none`. | The outcome depends on the Job and its single Pod surviving after `helm test` ends. `suite.yaml:22` sets `hook-delete-policy: before-hook-creation` and `backoffLimit: 0`, so in both Helm 3 and Helm 4 the Job is deleted only before the next run. It is not deleted on success, so the outcome holds. No finding. |
| `make e2e-down`, then `make e2e` (docs row); `make e2e-down` once (`test/k8s/README.md`) | `none`; CI starts from a fresh cluster. | `kind delete cluster` removes every object whatever its ownership, so the outcome follows. No run on an old stand is stated (Item 6). |
| `make e2e-suite` / `make parity-suite` with `*_SUITE_TIMEOUT` raised | `none`; CI runs only the 15m default. | A raised value does not deliver what the commit title promises (Item 3). |

## Item 3: boundaries, partitions, and the negative control
**Analogue used:** the inherited-state partition, and the limits on the suite's run time.

**Inherited state.** The change meets a cluster that the old `kubectl apply` harness set up. It handles this with a documented fix rather than a migration, which is what the review comment allowed. `test-authoring` §3 asks for that fix to be run on the old state. Nothing in the change says that was done, and `make e2e-down` is correct by construction, so this is noted under Item 6, not filed.

**Limits on the suite's run time**, all counted from about the same start:

| Limit | Where it is set | Default |
| --- | --- | --- |
| `-test.timeout` | `suite.args`: `test/k8s/test-stand-values.yaml:54-55`, and the chart default `values.yaml:94-95` (the parity values don't override `args`) | 600s |
| Job `activeDeadlineSeconds` | `values.yaml:99` | 900s |
| `helm test --timeout` | `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT` | 15m |
| CI job `timeout-minutes` (covers image builds, a 10m harness wait, 2×5m installs, and the suite) | `.github/workflows/integration-tests.yaml:120` and `:168` | 30 |

- **Raising the two documented settings has no effect past 10 minutes.** The Go test binary panics at 600s first, so you cannot make a suite outlast 15 minutes by following the Makefile comment or the README. The commit title's claim is therefore false. At the defaults the order is right: the innermost limit fires first and gives the most specific report.
- **CI's 30-minute job limit caps a raised value from outside the Makefile.** After a harness wait of up to 10 minutes and installs of up to 10 minutes, a suite much past 10–15 minutes cannot finish in CI. Nothing documents this pair.
- **Taste:** "no shorter than" / "at least as long as" treats equal values as safe. `helm test`'s clock starts before the Job exists, so at equal values Helm gives up first, and its timeout hides the Job's `DeadlineExceeded`. That only matters once `-test.timeout` has been raised to match.

## Item 3a: level, placement, and the environment
**Analogue used:** where each rule lives, and the gate that runs it.

The settings sit next to the other `E2E_*` variables. The notes sit in the two pages the review comment named. The only gate that runs these targets is the CI kind jobs, which need a cluster, so I ran nothing beyond `make -n`. **Placement gap:** the list of variables you can override at `test/k8s/README.md:65-70` (`KIND_CLUSTER`, …, `E2E_HELM_ARGS`, `E2E_BASE_URL`, `PARITY_AC_BASE_URL`) does not include the two new variables.

## Item 4: names by content, not by position
**Analogue used:** unchanged. `none`. I checked the headings, the new docs row, and the README step; nothing refers to anything by position.

## Item 5: the failure report
**Analogue used:** what each fix tells the reader to look at. `none`. Both notes quote the exact Helm error text, which matches Helm's ownership-validation wording, and the README quotes the Helm 3 error that the v3.15.2 source produces.

## Item 6: what the writer says it verified
The commit message gives specific results for Helm 4.3.1 and Helm 3.22.1 on `--logs`, which suggests a run; the Helm 3 half matches the source. It does not say that:
- the "invalid ownership metadata" failure was reproduced on an old stand, or that `make e2e-down` cleared it;
- a suite was ever run with a raised `*_SUITE_TIMEOUT`.

## Item 7: siblings of the change
**Analogue used:** the places that list or point to these settings.

- `git grep` finds no other `helm test` call with a fixed timeout; `run-suite` has exactly two callers, and both were updated.
- **Missing:** the override list in `test/k8s/README.md` (Item 3a).
- **Taste:** the run notes in `test/parity/README.md` do not mention the old-stand fix. Its teardown section already offers `kubectl … delete namespace authz-parity`, which would be enough for a parity-only stand.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| The comment says `helm test` prints the log at the end; it prints none, and the streaming is the only log output | Substantive | `Makefile:99-100` | Say that `helm test` does not print the Job log, so `run-suite` streams it with `kubectl logs -f`. |
| Raising `*_SUITE_TIMEOUT` and `activeDeadlineSeconds` as told has no effect past the 600s `-test.timeout` in `suite.args`, so the title's "outlast 15 minutes" is false | Substantive | `Makefile:49-50`, `:103-104`; `helm-templates/authz-test-stand/README.md:69-70` | Name all three limits (`-test.timeout` in `suite.args`, `activeDeadlineSeconds`, the Helm timeout) in the comment and the README, or derive one from another. |
| CI's `timeout-minutes: 30` per job caps a raised suite timeout, and nothing documents it | Substantive | `.github/workflows/integration-tests.yaml:120`, `:168`; `Makefile:49-50` | Document the pair next to the variables, or raise both together. |
| The troubleshooting row names only `make e2e` as the cause and gives `make e2e` as the rerun, though it also covers `parity-harness` | Substantive | `docs/local-integration-tests.md:190` | "an older `make e2e` or `make parity`", then rerun the same target. |
| The two new variables are missing from the README's list of overrides | Substantive | `test/k8s/README.md:65-70` | Add `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`, with the limits they must move with. |
| "At least as long as" treats equal values as safe, but Helm's clock starts first | Taste | `Makefile:104`; `README.md:69-70` | Ask for the Helm timeout to be somewhat longer than the Job deadline. |
| The parity README has no old-stand fix | Taste | `test/parity/README.md` | Optionally point to the note in `test/k8s/README.md`. |

The review did not run the suites, did not run the `make e2e-down` fix on an old stand, and did not check Helm 4's `--logs` behavior (there was no cluster or Helm 4 source), and it was not a style pass over the prose.

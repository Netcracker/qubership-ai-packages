I reviewed `5dcb6be..HEAD` (f3b64e0) against the form. All ten review comments got a change, but four findings remain. The most serious is that the new three-minute stop in `run-suite` does not hold when the Job exists but has no Pod: the loop then runs about 33 minutes.

The drift script printed nothing, because the commit touches only a Makefile, Markdown, a Dockerfile and YAML. So I used the "no code" analogues in §2a of the skill, plus the CI workflow and the kubectl v0.35.0 source in the Go module cache. There is no earlier report of this form for this change.

## Item 1: comments consistent with the code and with each other
Analogue used: every statement a changed file makes about the Makefile, CI or other files.

- **`Makefile:104-107` and the commit message.** Both say `kubectl logs` "fails until the Job exists and its container has started, so the loop polls for up to three minutes". When the Job exists but has no Pod, the command does not fail at once:
  - `kubectl logs job/X` resolves the Pod through `GetPodList` (`k8s.io/kubectl@v0.35.0/pkg/polymorphichelpers/helpers.go:61-75`).
  - With no Pod, that function watches for one until `--pod-running-timeout`, which defaults to 20s (`cmd/logs/logs.go:117`).
  - Each attempt therefore takes about 22s, and 90 attempts take about 33 minutes.

  The finding is under item 3.
- **`README.md:59-60`.** The sentence was rewritten to "CI builds them, with the test images and the transfer image, from the component list in `.github/docker-dev-config.json`". No workflow in `.github/workflows` reads that file or calls the shared `docker-build.yaml`; `git grep` finds only the docs page. The release workflow builds from `.qubership/docker.cfg`. "The test images" also covers only pip-stub and parity-suite, while `e2e-images` builds four test images.

  The claim was already there before this commit, but the rewrite states it again and now gives a count. A reader would believe a CI job builds five images on every change.
- `.github/docs-for-publication-task.md:77`: "The component array" no longer gives a count. No other sentence still says "both" or "two" about the component list.
- `helm-templates/authz-test-stand/README.md:62`, `test/k8s/README.md:66-70`, and the new troubleshooting rows agree with the Makefile (`E2E_SUITE_TIMEOUT ?= 15m`, `TEST_STAND_HELM_ARGS`, `activeDeadlineSeconds: 900`). None of the changed lines narrate the change.

## Item 2: claimed cases covered
Claimed cases and their coverage:

| Claim | Covered by |
| --- | --- |
| Reviewer comment 1: Helm 4.3 and later print nothing, earlier releases fail | The text matches the comment. CI runs only v4.3.1, so the earlier-release half has no run; I accepted it from the comment. |
| Reviewer comment 2: suite timeout variables listed | `test/k8s/README.md:69`, and the troubleshooting row at `docs/local-integration-tests.md:196` |
| Reviewer comment 3: `make parity` named in the remedy | `docs/local-integration-tests.md:193` |
| kubectl 1.31 dependency removed | `Makefile:113`: `logs job/` works on any supported kubectl. |
| Suite stops after 3 minutes when the container does not start | The CI jobs `kind-e2e` and `kind-parity` run only the path where it starts. No run of the fault is stated. |
| `E2E_HELM_ARGS` no longer reaches the test stand | `Makefile:93,164`, and CI passes neither variable. |
| Dockerfile user-file merge: sorted order, file names with spaces | **No build exercises it.** `test/parity/suite/testdata/realm/` holds only `README.md`, so every build takes the empty-input path. I ran the pipeline locally with macOS `sort`/`xargs` and jq: an empty directory, `aa.json`, and `b z.json` merged in sorted order. It did not run with the busybox in `alpine:3.22`. |
| SVT Keycloak back on 26.0 | An exact revert of `8b85515` (`git log -p` on the compose file). |

Commands the change documents, and whether anything runs them:

| Command or claim | Promised outcome | Run by | Notes |
| --- | --- | --- | --- |
| "Docker 23.0 or later", "helm 3.14 or later" (`docs/local-integration-tests.md:35,38`) | The targets work on those versions | **none** | CI pins Helm v4.3.1 and uses the Docker on `ubuntu-latest`. The outcome depends on Helm 3's legacy `--wait` against Helm 4's kstatus watcher, and on Helm 3's `helm test` of a Job hook; nothing shows a run on 3.14. The commit subject says "year-old tools", but Helm 3.14 shipped in January 2024 and Docker 23.0 in February 2023. |
| `make parity-suite PARITY_SUITE_TIMEOUT=5h30m` (`docs/local-integration-tests.md:196`) | The long suite no longer fails at 15 minutes | **none** | See item 7: as written, it still fails at 15 minutes. |
| `make e2e-down`, then `make e2e` or `make parity` | Clears the leftover objects | Equivalent to the CI steps on a new cluster | `e2e-down` deletes the whole cluster, so this holds. |

Every hunk maps to a sentence of the commit message, so there are no unclaimed hunks.

## Item 3: boundaries, partitions, and the negative control
**The replaced wait, on two faults:**

- **The usual fault, `ErrImageNeverPull`.** The Pod exists, so each `logs` attempt fails at once. The old target took about 3 minutes and then waited out the 15-minute `helm test` timeout. The new one takes about 3 minutes, then prints the Pod listing. The fix works here.
- **The fault where one attempt waits longest: the Job exists but has no Pod.** This happens when admission refuses the Pod; the previous commit put the namespace under the restricted Pod Security Standard. Each attempt then waits 20s (`--pod-running-timeout`), so the loop takes 90 × (20s + 2s) ≈ 33 minutes.
  - `helm test` gives up at 15 minutes, and the loop keeps going.
  - `kind-e2e` and `kind-parity` have `timeout-minutes: 30`, so CI cancels the job before the message prints.
  - Even when the message does print, `get pods -l job-name=…` shows only "No resources found", not the `FailedCreate` reason.

  This is substantive. The request is to bound the loop by time, for example with `--pod-running-timeout=2s` on the probe or a deadline instead of a count, and to run this fault.

**Limits:** `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` (Makefile, 15m) sit alongside three other limits:
- `suite.activeDeadlineSeconds` (`values.yaml:99`, 900s)
- the CI job's `timeout-minutes: 30`, part of which goes to images, harness and install first
- the 3-minute start loop, which lies inside and does not count

If someone raises `PARITY_SUITE_TIMEOUT` to 20m and leaves the values alone, the 900s deadline fires first and the raise has no effect. The docs ask the reader to raise both by hand; nothing derives one from the other. This limit was introduced in the previous commit; this one documents it.

**Values users already pass:** `E2E_HELM_ARGS` now reaches fewer consumers, which the commit message states as user-visible. `TEST_STAND_HELM_ARGS` is new, so no existing values reach it. Nothing to report.

**State left by an earlier version:** with sorted input, the merged realm, and with it `checksum/realms`, could change once on an existing stand. Today there are no user files, so there is no change. Nothing to report.

## Item 3a: level, placement, and the environment
Analogue used: where each rule lives and which gate checks it. The behaviour lives in a Makefile recipe and a Dockerfile, so there is no in-process level to test at. `helm lint` with `test/k8s/test-stand-values.yaml` passes. CI runs the success path of both suites but neither failure path, and no build runs the user-file merge with any input (item 2).

## Item 4: names by content, not by position
None. The new row and README sentences name variables and targets.

## Item 5: the failure report
Analogue used: what the new failure message tells the reader to look at.
- On a refused Pod, the new message shows an empty Pod listing (item 3). Showing `describe job` or the Job's events would name the cause.
- When `helm test` has already exited, for example because the release is missing, the loop still runs for 3 minutes, `kill` prints "No such process", and the message blames the container. This is taste.

## Item 6: what the writer says it verified
The commit states no run: no run of either fault on the new `run-suite`, no build of the chart-files stage with user files, no run on Helm 3.14 or Docker 23.0, and no SVT run (the revert makes that one moot).

## Item 7: siblings of the change
- `run-suite` has two callers, `e2e-suite` and `parity-suite`, and the change covers both.
- `TEST_STAND_HELM_ARGS` is listed wherever `E2E_HELM_ARGS` is: the Makefile and `test/k8s/README.md`. The docs page lists neither, before or after this commit.
- **Remedy row at `docs/local-integration-tests.md:196`.** The cause it names covers two steps, but its action covers one. `suite.activeDeadlineSeconds` reaches the Job only at `e2e-harness` or `parity-harness`; `test/k8s/README.md:71-74` says the same for the suite's other values. Yet the example runs only `make parity-suite PARITY_SUITE_TIMEOUT=5h30m`, so the Job is still stopped at 900s.
- The `exists and cannot be imported` row now names both targets in its action, so the gap from review comment 3 is closed.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| The start loop takes about 33 minutes, not 3, when the Job exists but has no Pod: 20s `--pod-running-timeout` per attempt × 90. This is longer than `helm test`'s 15 minutes and the CI job's 30. The Makefile comment and commit message say "up to three minutes". | Substantive | `Makefile:104-114` | Bound the loop by time, for example `logs --pod-running-timeout=2s` or a deadline, and run this fault, stating its duration and output. |
| The timeout remedy runs only `parity-suite`, but `activeDeadlineSeconds` applies only after a harness rerun, so the example still fails at 15 minutes. | Substantive | `docs/local-integration-tests.md:196` | Name the harness rerun, or pass the deadline with `TEST_STAND_HELM_ARGS='--set suite.activeDeadlineSeconds=…'`. Better, derive one limit from the other. |
| The minimum versions "Docker 23.0" and "helm 3.14" have no run behind them. CI uses Helm v4.3.1 and current Docker, and the subject's "year-old" does not match the dates. | Substantive | `docs/local-integration-tests.md:35,38`; commit subject | Run the targets on Helm 3.14 and Docker 23.0, or state only the versions CI runs. |
| "CI builds them … from `.github/docker-dev-config.json`": no workflow in the repository reads that file, and "the test images" covers two of four. | Substantive | `README.md:59-60` | Name the job that reads the file, or describe the release build from `.qubership/docker.cfg`. |
| The sorted, NUL-separated user-file merge has never run with input; the users directory holds only `README.md`. | Substantive | `build/authz-agent-transfer/Dockerfile:43-45` | Build the `chart-files` stage once with two user files, one with a space in its name, and state the result. |
| The "did not start" message prints an empty Pod list when admission refuses the Pod, and blames the container when `helm test` itself exited. | Taste | `Makefile:115-118` | Print `describe job` or the Job's events, and check that `helm test` is still running before blaming the container. |

I did not run either suite, a Docker build, Helm 3.x or Docker 23.0, or busybox `sort -z` / `xargs -0 -r` inside `alpine:3.22`. I did not do a style-only pass over the prose.

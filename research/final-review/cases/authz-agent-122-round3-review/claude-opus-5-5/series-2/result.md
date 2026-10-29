# Final review: `5dcb6be..f3b64e0`, one commit: "run the test stand on year-old tools, and stop a suite that never starts"

The commit fixes almost every review comment. The real problem is that the new start window is not three minutes on every fault. When the Pod is never created, each poll can take 22 seconds, so `make e2e-suite` can run about 33 minutes. That is longer than the CI job's 30-minute timeout, so CI would kill the job before the diagnostic prints.

**Inputs.** I read the diff whole, along with the commit message and the review comments in the prompt. No earlier report of this form exists, so there is no table of earlier findings. The drift script ran (`comment-drift.py 5dcb6be HEAD`) and printed nothing: the change is only a Makefile, a Dockerfile, Markdown and YAML, which it does not parse. I filled the form through §2a's analogues, so the "comments" are the Makefile and Dockerfile comments and the statements the pages make. There are no tests, so the "tests" are the CI jobs and runs.

## Item 1: comments consistent with the code and with each other

- **`Makefile:104-105`**: "`kubectl logs` fails until the Job exists and its container has started, so the loop polls for up to three minutes" is false for one fault. The `echo` at `Makefile:115` ("did not start within 3 minutes") has the same problem. Details are under Item 3. **Substantive.**
- The `E2E_HELM_ARGS` comment (`Makefile:46-49`) and `test/k8s/README.md:67-70` both match the recipes in `make -n`.
- The chart README's Helm 4.3 sentence (`helm-templates/authz-test-stand/README.md:62`) matches inline comment 1.
- The new troubleshooting row matches the Makefile: `e2e-down` runs `kind delete cluster`, and `parity` depends on `e2e-cluster`.
- `.github/docs-for-publication-task.md:77` no longer counts the entries.
- `README.md:59-60` is true. "the test images" is broad: the list has two of the four test images (pip-stub and parity-suite). The next paragraph names them, so this is **taste**.
- The Dockerfile header comments still match the stage.
- Nothing in the change describes itself with "now" or "no longer".

## Item 2: claimed cases covered

The analogue: each case the comments or the commit message claim, against the code or run that makes it true.

| Claimed case | Covered by |
| --- | --- |
| kubectl before 1.31: no `--for=create` | `Makefile:111`. The loop on `kubectl logs job/` uses no new kubectl feature. No run on an old kubectl, and none is needed for that. |
| ErrImageNeverPull fails after about 3 min with the Pod listing | Code reading: the Pod exists and `logs` fails at once, so 90 × (under 1 s + 2 s) ≈ 3–4.5 min. No run is stated. |
| `TEST_STAND_HELM_ARGS` reaches only the stand, `E2E_HELM_ARGS` only the product charts | `make -n parity-harness TEST_STAND_HELM_ARGS='--set TAG=x' E2E_HELM_ARGS='--set TAG=y'` passes only `TAG=x` to the stand. |
| Files sorted and passed NUL-separated; a name with a space survives | The repo has no user JSON (only `README.md` under `testdata/realm/`), so CI runs only the empty path. I ran it myself (see Item 6). |
| SVT back on Keycloak 26.0 | `git log -p` shows the line is back to its value before 8b85515, so the PR as a whole no longer touches the file. |
| Docker 23.0, Helm 3.14 or later, Helm 4; kubectl and kind any version | **none.** CI runs only Helm v4.3.1 (`integration-tests.yaml:129,176`). The behavior depends on `helm test` waiting on a Job hook, `upgrade --install --create-namespace --wait`, BuildKit `--output type=local`, `FROM --platform`, and `kubectl logs job/` / `get pods -l job-name=`. All of these predate the stated minimums, and the charts use only `include`, `required`, `fail` and `sha256sum` with draft-07 schemas. So I find no conflict, but no run backs the claim. |
| After `make e2e-down`, `make parity` | `parity: e2e-cluster …`. The older `kubectl apply` harness in parity is confirmed at `8b85515^:Makefile:134`. |
| `make parity-suite PARITY_SUITE_TIMEOUT=5h30m` | Not run. Helm accepts the Go duration, and the row tells the reader to raise `activeDeadlineSeconds` with it. |

**Hunks with no sentence in the commit message** (substantive, small): the `README.md` "CI builds them" rewrite, `.github/docs-for-publication-task.md:77`, and the troubleshooting row that adds `make parity`. They answer review comments, but the commit message does not mention them. The request is one sentence that claims them.

## Item 3: boundaries, partitions, and the negative control

**Mechanism replaced: the wait in `run-suite`.**

- **Missing image, the most common fault:**
  - Old: `kubectl wait --for=create` succeeds, then the loop runs about 3 min, `logs -f` fails, and `wait` holds until `helm test` times out at 15 min.
  - New: about 3–4.5 min, then the message, the Pod listing with `ErrImageNeverPull`, and helm is killed.
  - The fix holds for this fault.
- **The fault where one attempt waits longest: the Job exists but no Pod is ever created.** Examples are an admission rejection (Pod Security, ResourceQuota or LimitRange) or a webhook.
  - On a Job, `kubectl logs` lists the Job's Pods. With none, it watches for up to `--pod-running-timeout`, 20 s by default (`k8s.io/kubectl@v0.29.0/pkg/polymorphichelpers/helpers.go:58-72`, `cmd/logs/logs.go:94`).
  - The loop therefore takes 90 × (20 s + 2 s) ≈ **33 min**.
  - `helm test` gives up at 15 min (the Job's `activeDeadlineSeconds: 900`). The loop does not check whether helm is still running, so it keeps polling.
  - CI's `timeout-minutes: 30` kills the job first, so the diagnostic never prints. Even if it did, `get pods` would print `No resources found`, because the reason is in the Job's events.
  - The old target had the same loop behind a 2-minute wait, so it was no better. But the new comment and message promise 3 minutes, and nothing in the change accepts this case.
  - **Substantive.** Requested fix:
    - pass `--pod-running-timeout=2s` to the polling `logs`, or end the loop on a wall-clock deadline;
    - stop the loop when `kill -0 $helm_pid` fails;
    - print `describe job` (or its events) along with the Pods.
  - Then run that fault, for example with a pod-count ResourceQuota of 0, and report how long it takes and what it prints.
- **Smaller case of the same flaw:** if `helm test` fails at once (say the release is missing), the new target still polls for 3 min and then says the container "did not start". The old target failed after the 2-minute wait. The `kill -0` check above fixes this too.

**Pass-through setting.** `E2E_HELM_ARGS` no longer reaches the stand. Its values now reach only the product charts, and `TEST_STAND_HELM_ARGS` is new, so no value users already pass changes meaning for any consumer. None.

**Limits.**
- The suite timeout default (15m) equals the default `activeDeadlineSeconds` (900). Neither changed here.
- The 3-minute start window only fires before the suite timeout. That holds unless `E2E_SUITE_TIMEOUT` is set under 3 min, in which case helm fails first and the loop then runs on (the same flaw as above).
- The 30-minute CI limit is covered under the fault above.

**State left by an earlier version.** The troubleshooting row covers the harness objects left by the old `kubectl apply` targets. None beyond that.

## Item 3a: level, placement, and the environment

The analogue is the CI jobs. `kind-e2e` and `kind-parity` run every changed target, but only on the happy path, Helm 4.3.1 and an empty user set. The failure paths are not runs CI could reasonably host. The Dockerfile change is checkable offline, and I checked it (Item 6). Placement matches the existing layout. None beyond Items 2 and 6.

## Item 4: names by content, not by position

None. The headings, the variable names and the message ("The runtime-suite container …") all name things by content.

## Item 5: the failure report

The new message prints the Pod listing, which shows `ErrImageNeverPull` and `CreateContainerConfigError`. When no Pod exists it prints nothing useful; the fix is folded into the Item 3 finding.

There is a taste point too: the troubleshooting row "The Job Pod stays `Pending` or reports `ErrImageNeverPull`" (`docs/local-integration-tests.md:192`) could quote the new message "container did not start within 3 minutes", so a reader can search the page for it.

## Item 6: what the writer says it verified

The commit states no runs: no ErrImageNeverPull run with its duration, no Helm 3.14 or Docker 23.0 run, and no multi-file build of the chart-files stage. These are the runs the change still needs.

I built the `chart-files` stage myself, into the scratchpad only:

- **Base against head, repo as it is:** identical output, which is the empty user set.
- **Copy of the build context with two user files** (`a.json`, and `b users.json` with no trailing newline): the build passed, and the users merged in sorted order (`amy`, `bob`, `zed`) with their profiles filled.

## Item 7: siblings of the change

- **`TEST_STAND_HELM_ARGS`:** `git grep` for `E2E_HELM_ARGS` and `SUITE_TIMEOUT` finds only `Makefile`, `test/k8s/README.md` and the new troubleshooting row. Both pages that list overrides now name the new variable and the timeout variables. No CI workflow passes either one.
- **The `run-suite` change:** there are no other users of `--for=create` or `logs -f`, and both suites use the one macro.
- **The remedy row:** its symptom names both harness targets and its action now names both reruns.
- **Counts:** I searched `.github/docs-for-publication-task.md` and `README.md` for "two" and "both". What remains ("the two services", "Besides the two services") is correct.

## Findings

| Finding | Label | File and line | Request |
| --- | --- | --- | --- |
| The start loop is not bounded at 3 min. With no Pod, each `kubectl logs job/` attempt waits 20 s, so the target takes about 33 min, beyond CI's 30-min timeout. The loop also ignores a `helm test` that has already exited, and the message prints `No resources found` | Substantive | `Makefile:104-105`, `111-117` | `--pod-running-timeout=2s` or a wall-clock deadline; stop on `! kill -0 $helm_pid`; print the Job's events. Then run that fault with its duration and output |
| No run on the documented minimum versions (Helm 3.14, Docker 23.0); CI runs only Helm 4.3.1 | Substantive | `docs/local-integration-tests.md:35-42` | One local run of `make e2e` on Helm 3.14 and Docker 23.0, stated in the description, or state only the versions that ran |
| No stated run of the ErrImageNeverPull path or of the multi-file chart-files build | Substantive | commit message | State the runs: the duration and output of the missed `kind load`, and the build with two or more user files |
| Hunks the commit message does not claim: the README "CI builds" rewrite, the publication-task count, the `make parity` remedy | Substantive | `README.md:59-60`, `.github/docs-for-publication-task.md:77`, `docs/local-integration-tests.md:193` | Add one sentence to the commit message that claims them |
| "the test images" covers two of the four test images | Taste | `README.md:59` | "the test stand's images", as in the next paragraph |
| The troubleshooting row does not quote the new failure message | Taste | `docs/local-integration-tests.md:192` | Add "did not start within 3 minutes" to the symptom |

I did not run the kind suites (there is no cluster), did not test Helm 3.x, Docker 23.0 or an old kubectl, and did not review the prose for style.

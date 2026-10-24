# Final review: `5dcb6be..f3b64e0`, one commit

The change has no code members: it touches a Makefile, a Dockerfile, a Compose file, and Markdown. `comment-drift.py 5dcb6be HEAD` ran and printed nothing, because it parses none of these languages. So the form is filled through the §2a analogues: comments are the statements the files make about each other, and tests are the runs and CI jobs. This is the first review of the change, so there is no earlier report to compare against. I loaded `test-authoring` and `english-developer-style` from the given directory.

## Item 1: comments consistent with the code and with each other
Analogue used: statements one file makes about another.

**None.** What I checked:
- **`run-suite` comment, `Makefile:102-109`:** matches the new loop.
- **`E2E_HELM_ARGS` / `TEST_STAND_HELM_ARGS` comment, `Makefile:46-51`:** matches the targets. `make -n … E2E_HELM_ARGS=EH TEST_STAND_HELM_ARGS=TS` puts `TS` only on the two `authz-test-stand` installs and `EH` only on the four product installs.
- **`test/k8s/README.md:66-70`:** matches the Makefile defaults (15m for both suite timeouts).
- **Chart README line 62:** matches review comment 1.
- **`README.md:59-62`:** five components; only the two services are named as published.
- **`.github/docs-for-publication-task.md:77`:** no longer says "two-entry".
- **Dockerfile header comment:** still true.

## Item 2: claimed cases covered
Analogue used: claims in the review comments and the commit message, matched to the section or run that covers each.

| Claim | Covered by |
| --- | --- |
| Comment 1: Helm 4.3+ prints nothing, earlier releases fail | `helm-templates/authz-test-stand/README.md:62`. Holds. |
| Comment 2: timeout variables listed | `test/k8s/README.md:69-70`, `docs/local-integration-tests.md:196`. Holds. |
| Comment 3: `make parity` named in the `exists and cannot be imported` remedy | `docs/local-integration-tests.md:193`. Holds; `parity` creates the cluster and images itself. |
| `kubectl wait --for=create` removed, works on any kubectl | `Makefile:113`. kubectl v0.29.0 source: `logs job/x` goes through `GetFirstPod`, which returns any existing Pod at once, and the log request then fails while the container waits. No older kubectl was run. |
| A container that never starts fails after about 3 minutes with the quoted message | Simulated with stub `kubectl`/`helm`/`sleep`: the message and the Pod listing print, helm is terminated, and make exits with Error 1. No kind run. See F1 for a case where the message is false. |
| `E2E_HELM_ARGS` no longer reaches the stand | `make -n` (above). |
| Sorted, NUL-separated user files | I built the `chart-files` stage from a `git archive` copy in the scratchpad: <ul><li>`a.json`, `b users.json` and `sub dir/c.json` merge in sorted order, with profiles filled in.</li><li>No user files gives output identical to the seed realm.</li><li>A duplicate username still fails the build.</li></ul> |
| SVT back on Keycloak 26.0 | Matches the exact line that `8b85515` replaced. `test/svt` is otherwise unchanged since `8b85515^`. |
| Docker 23.0 / Helm 3.14 floors | **None:** no job runs either. See F2. |

Command lines in the changed files, with what runs the same form:

| Command | What runs it |
| --- | --- |
| `make e2e-down` then `make e2e` / `make parity` | `kind-e2e` and `kind-parity` run the same targets on a fresh cluster. |
| `make parity-suite PARITY_SUITE_TIMEOUT=5h30m` | **None.** See F3. |
| `make test-stand-files` | The CI `chart` job, plus my build above. |

Hunks no sentence of the commit message claims: the `README.md` hunk, the `.github/docs-for-publication-task.md` hunk, and the `make parity` remedy in the troubleshooting row. → F4.

## Item 3: boundaries, partitions, and the negative control
Analogue used: the modes and situations the change claims, the state earlier versions left behind, and the limits on the same work.

- **Values users already pass.** CI and the docs pass neither variable. The Makefile's own example, `--set IMAGE_PULL_POLICY=Never`, is already in both stand values files, so moving it to the product installs only changes nothing for the stand. Nothing to report.
- **Limits on the suite run.** There are five, at these defaults:
  1. The fixed 90-attempt start window in `Makefile:113`.
  2. `helm test --timeout`, set by `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT`.
  3. `suite.activeDeadlineSeconds: 900` in `helm-templates/authz-test-stand/values.yaml:99`, applied at `*-harness` time.
  4. kubectl's `--pod-running-timeout=20s` on each attempt.
  5. The CI `timeout-minutes: 30`.

  Findings:
  - The start window counts attempts, not time. If the Job exists but has no Pod (for example, a quota or an admission webhook refuses the Pod), each attempt blocks for 20 s in `GetFirstPod`'s watch. 90 attempts then take about 33 min, past both the 15m helm timeout and the 30-minute CI limit. → F1.
  - The new troubleshooting row's example raises only the helm timeout. The Job deadline is set at harness time, so it still ends the run at 15 min. → F3.
  - At the defaults, helm's 15m and the Job's 900 s are equal. Helm starts its clock first, so its timeout fires before the Job's `DeadlineExceeded` and hides that report. This predates the change (it came in with `5dcb6be`). Noted in F3.

## Item 3a: level, placement, and the environment
Analogue used: where each rule lives, and whether the repository's gate runs it.

- **Placement:** correct. Each statement sits in its own README or Makefile comment.
- **Gate:** `make lint` needs `npx` and network access, so I did not run it. Line lengths are within the 400 that `MD013` allows.
- **CI job:** the CI matrix has no job on the documented minimum versions (F2).

## Item 4: names by content, not by position
**None.** The new text names variables, targets and messages by content.

## Item 5: the failure report
Analogue used: what a failure tells the reader to look at.

The new failure prints the Pod listing, which shows the reason, for example `ErrImageNeverPull`. When `helm test` itself fails at once, the report is wrong: it says the container did not start, lists "No resources found", and adds `kill: No such process` (F1). The troubleshooting table does not quote the new message text "did not start within 3 minutes" (F5).

## Item 6: what the writer says it verified
The commit states no run: no kind run of the never-start path, no build of the Dockerfile change, and no run on Helm 3.14 or Docker 23.0. The checks above are mine.

## Item 7: siblings of the change
Analogue used: every place that lists the variables or the components, and the twin targets.

- **Variable lists.** Every file naming both `KIND_CLUSTER` and `E2E_NAMESPACE` is `test/k8s/README.md`, which now lists `TEST_STAND_HELM_ARGS` and both timeout variables.
- **Twin targets.** The `e2e` and `parity` twins share `run-suite` and both switched to `TEST_STAND_HELM_ARGS`.
- **Component count.** No remaining "both" or "two" describes the five-component list. The "both" in the values-file comments refers to two config files.
- **SVT Keycloak image.** The other Keycloak pins (chart values, `test/BASELINE.md`) are 26.3.5. That is intended: the SVT stack is the only one the commit reverts.

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| F1 | The start loop ignores helm's exit and counts attempts rather than time. Simulated: when `helm test` fails at once (no release, e.g. `make e2e-suite` before `e2e-harness`), it polls for 3 minutes, then prints "The runtime-suite container did not start within 3 minutes:", "No resources found", and `kill: No such process`. From the kubectl source, a Job with no Pod makes each attempt wait 20 s, about 33 min in total, longer than both helm's and CI's limits. | Substantive | `Makefile:113-118` | Leave the loop when `kill -0 $$helm_pid` fails and let `wait` report helm's status. Bound the loop by elapsed time, or pass `--pod-running-timeout=2s` to the polling `kubectl logs`. |
| F2 | The version floors (Docker 23.0, Helm 3.14, "Helm 4 works too", "kubectl and kind may be any version that supports the cluster") were not checked on any run; CI runs only Helm v4.3.1 and the kind-action defaults. The subject line "run the test stand on year-old tools" claims such a run. "kind … any version that supports the cluster" is circular, since kind creates the cluster. | Substantive | `docs/local-integration-tests.md:35-42` | Run the targets on Helm 3.14 and Docker 23.0 and say so in the description, or document the versions CI runs. |
| F3 | The example `make parity-suite PARITY_SUITE_TIMEOUT=5h30m` alone still fails at 15 min, because `suite.activeDeadlineSeconds` (900) takes effect only at `parity-harness`. At the defaults, helm's equal 15m timeout also fires first and hides the Job's `DeadlineExceeded`. | Substantive | `docs/local-integration-tests.md:196` | Show both halves, e.g. `make parity-harness TEST_STAND_HELM_ARGS='--set suite.activeDeadlineSeconds=19800'` then `make parity-suite PARITY_SUITE_TIMEOUT=5h30m`. Optionally derive the helm timeout from the deadline plus a margin. |
| F4 | The `README.md` and `.github/docs-for-publication-task.md` hunks and the `make parity` remedy are claimed by no sentence of the commit message. | Substantive | `README.md:59`, `.github/docs-for-publication-task.md:77`, `docs/local-integration-tests.md:193` | Add one sentence to the commit message that claims them. |
| F5 | The troubleshooting table does not quote the new failure text, so a search for it finds nothing. | Taste | `docs/local-integration-tests.md:192` | Add "did not start within 3 minutes" to the `ErrImageNeverPull` row. |

This review did not run the kind targets, `make lint`, or the SVT stack; it did not run any older kubectl, Helm 3, or Docker 23. It did not do a style-only pass over the prose.

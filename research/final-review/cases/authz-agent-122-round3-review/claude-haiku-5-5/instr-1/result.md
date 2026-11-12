# Final review: `5dcb6be..HEAD` (commit f3b64e0)

No previous report exists, so the table below maps the review comments, which are the task statement, to their status. The drift script ran and printed nothing, because the diff has no Go or Java members. The change touches a Makefile, a Dockerfile, a shell recipe, Markdown and YAML, so the analogues in §2a do not apply.

## Review comments

| Comment | Status | Evidence |
| --- | --- | --- |
| Helm 4 prints nothing only from 4.3.0 | holds | `helm-templates/authz-test-stand/README.md:61-62` now says 4.3 and later print nothing, and earlier releases fail. CI pins Helm v4.3.1. |
| Timeout variables missing from the lists | holds for the lists, but the example attached to them is wrong | `test/k8s/README.md:69-70` and `docs/local-integration-tests.md:196` name them. See finding 1. |
| After `make e2e-down`, parity needs `make parity` | holds | `docs/local-integration-tests.md:193` names both reruns. The pairing is left implicit (finding 6). |
| `kubectl wait --for=create` needs kubectl 1.31 | holds | `run-suite` (Makefile:110-121) now polls with `kubectl logs` only. No other `wait --for` exists in the repo. |
| 15-minute hold on a suite Pod that never starts | holds for ErrImageNeverPull, reshaped elsewhere | My stub run (below) prints the message and kills helm after 90 attempts. Findings 2 and 3 cover what the loop does not bound. |
| Dockerfile merge order and file names with spaces | holds | `build/authz-agent-transfer/Dockerfile:43-45` sorts NUL-separated. I simulated the merge with jq 1.8.2: sorted order, a name with a space read correctly, concatenated files without newlines, and an empty set. I did not run it in the image. |
| `E2E_HELM_ARGS` reaches the test stand | holds | `Makefile:93` and `:164` now pass `TEST_STAND_HELM_ARGS`. CI passes neither variable, and `test/k8s/test-stand-values.yaml:4-5` sets `TAG: ci`. |
| SVT Keycloak moved without mention | holds | The commit message names it. The line equals the one `b7064c7` introduced (`git show`). |
| "CI builds both" and "two-entry array" | fixed in the files, unclaimed in the commit | Finding 5. |

## 1. Comments consistent with the code and with each other

Findings 1, 2 and 3. The Makefile comment at lines 105-107 says the loop "polls for up to three minutes" and that a container not started by then "will not" start. The first is not what the loop enforces, and the second is false for a slow pull. The docs and `test/k8s/README.md` describe a timeout raise that does not reach the suite's own limits (finding 1).

## 2. Claimed cases covered

Commands the change tells someone to run, with their outcomes:

- `make e2e-down` (`docs/local-integration-tests.md` near line 118) deletes the cluster. Holds.
- `make parity-suite PARITY_SUITE_TIMEOUT=5h30m` (`docs:196`). CI runs `make parity-suite` with no variable (`integration-tests.yaml:197`). The example does not reach its promised outcome (finding 1).
- `helm test authz-test-stand --timeout 15m` (helm README:65) matches the Makefile's `helm ... test authz-test-stand --timeout $(E2E_SUITE_TIMEOUT)` with the same release. Holds.
- `kubectl logs job/parity-suite` (helm README:66) matches the Makefile's `kubectl logs -f`, after the Job exists. Holds on any kubectl.
- The version floors in `docs/local-integration-tests.md:35-38` (Docker 23.0, Helm 3.14) are not backed by a citation or a run. I found no feature in the Makefile or the charts that needs Helm 3.14. Not verified (see the last paragraph).

Hunks read against the commit message:

- Unclaimed: `README.md:59` and `.github/docs-for-publication-task.md:77` (finding 5).
- Claimed only loosely: the suite-timeout sentence in `test/k8s/README.md:67-70` (finding 5).
- All other hunks have a sentence in the commit message.

## 3. Boundaries, partitions, and the negative control

Mechanism replaced: `wait --for=create --timeout=2m` plus the 90-iteration loop, replaced by the loop alone.

- Most frequent old fault (kubectl older than 1.31): the old target printed no streamed log and the run still passed. The new loop streams on any kubectl.
- ErrImageNeverPull: the old target waited out helm's 15-minute timeout. The new one stops at about 3 minutes and prints the Pod listing. The stub run confirms the logic.
- Hung `kubectl logs` (no request timeout by default): the new loop has no time bound at all. The old `wait` was bounded at 2 minutes, but the old loop had the same unbounded attempts, so this is not a regression. The stated bound is still false (finding 2).
- Slow pull longer than 3 minutes: the old target passed the run with an unstreamed log. The new one kills helm at 3 minutes. This is a regression (finding 3).

Limits on the suite work, each with its source:

- `helm test --timeout`: `E2E_SUITE_TIMEOUT`, 15m (Makefile:54).
- Job `activeDeadlineSeconds: 900` (`helm-templates/authz-test-stand/values.yaml:99`). This matches the default helm wait.
- Go `-test.timeout 600s` in the suite args (`values.yaml:95-96`, and `test/k8s/test-stand-values.yaml:55-56` for the runtime suite). The parity stand does not override it. This fires before both 900 s and 15 m, so raising the make variable has no effect beyond 10 minutes (finding 1).
- New 3-minute cutoff on container start (Makefile:113). It is inside the 15-minute helm wait and fires first at the defaults.
- CI `timeout-minutes: 30` (`integration-tests.yaml:120` and `:168`). It encloses the suite only in CI, where no variable is raised.

Setting that reaches a new consumer: `TAG` and `IMAGE_PULL_POLICY` are read by the agent, policy-admin and the stand (`values.yaml`s). `E2E_HELM_ARGS` now reaches only the first two, and `TEST_STAND_HELM_ARGS` is the stand's own control. Holds.

## 3a. Level, placement, and the environment

None. The change adds no test file, and the repo has no test for the Dockerfile merge with user files. `testdata/realm` holds none today, so that path runs nowhere in the repo.

## 4. Names by content, not by position

None found. The new message names the Job, not its position.

## 5. The failure report

None beyond finding 2. The new message prints the Pod listing, which is the last state the loop saw. Its "within 3 minutes" is not enforced.

## 6. What the writer says it verified

No evidence is stated for the replaced wait, the Dockerfile sort, or the docs. Test-authoring §3 owes both durations and both outputs for a replaced mechanism (finding 4). My stub run covers the logic only. Scripts are at `/private/tmp/claude-501/-private-var-folders-hq-dhvxggnd1gv0fpmt8lg8xzkc0000gn-T-tmp-52HnFu3kuY-repo/7f9fc7ca-9237-40d5-853d-cecbc8ae6460/scratchpad/suite.sh` with stubs in its `bin` directory. Results: the ErrImageNeverPull path makes 90 attempts, prints the message, kills helm and exits 1. The success path streams and exits 0.

## 7. Siblings of the change

- `E2E_HELM_ARGS` appears in `Makefile:47-50` and `test/k8s/README.md:67`, and both were updated. No other list names it.
- `TEST_STAND_HELM_ARGS` has no other list.
- `E2E_SUITE_TIMEOUT` appears in `Makefile:54`, `test/k8s/README.md:69` and `docs:196`. `test/parity/README.md` does not list `PARITY_SUITE_TIMEOUT`.
- The `-test.timeout` limit has the same problem in the runtime suite args (`test/k8s/test-stand-values.yaml:55-56`), which no document names (finding 1).
- `find` in `build/` appears once (Dockerfile:43).
- No stale "two" or "both" count remains. "The two services" (`README.md:60`) is correct.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The example `make parity-suite PARITY_SUITE_TIMEOUT=5h30m` does not reach its outcome. The parity Job runs `./parity.test -test.timeout 600s`, so the suite stops at 10 minutes. `activeDeadlineSeconds: 900` also kills the Job at 15 minutes, and `parity-harness` has no values-file variable to raise it. The row's own symptom ("fails after 15 minutes while the Job still runs") does not occur with the defaults. | substantive | `docs/local-integration-tests.md:196`; `test/k8s/README.md:69-70`; `Makefile:52-54`; `helm-templates/authz-test-stand/values.yaml:95-99`; `test/k8s/test-stand-values.yaml:55-56` | Name `-test.timeout` and `suite.activeDeadlineSeconds` as the limits to raise. Say which values file to edit and that `make parity-harness` or `make e2e-harness` must rerun for it to apply. Run the example or remove it. |
| 2 | The loop bounds attempts, not time. It runs 90 times, and each `kubectl logs` has no request timeout by default. "Up to three minutes" is not kept when calls are slow or hang. | substantive | `Makefile:105`, `:113` | Bound the loop by elapsed time and pass `--request-timeout` to the logs call. Otherwise write "90 attempts". |
| 3 | A container still pulling after 3 minutes is now killed. The old target waited on helm, up to 15 minutes, and passed the run with an unstreamed log. "Will not" holds for ErrImageNeverPull but not for a slow pull, and the commit does not accept that trade. | substantive | `Makefile:105-107`, `:113-119` | Keep helm running while the Pod is pulling, up to the deadline. Or name the trade in the commit and the comment, with the window a stand needs. |
| 4 | No run is stated for the replaced wait. Test-authoring §3 owes both durations and both outputs, on the old fault and the new. | substantive | `Makefile:110-121`; commit message | Run on kind with the suite image not loaded, old and new. Run on kubectl older than 1.31. Paste the durations and outputs. |
| 5 | Hunks no sentence claims: the root README sentence on CI builds and the `docs-for-publication-task.md` "component array" line. The suite-timeout sentence in `test/k8s/README.md` is claimed only by the docs sentence. | substantive | `README.md:59`; `.github/docs-for-publication-task.md:77`; `test/k8s/README.md:67-70` | Add a sentence that claims each hunk and cites the check, for example that `docker-dev-config.json` lists five components. Or move the hunks to their own commit. |
| 6 | The row maps no target. "Rerun `make e2e` or `make parity`" works, but the reader must pick the one matching the failed target. | taste | `docs/local-integration-tests.md:193` | Pair them: `make e2e` for `make e2e-harness`, `make parity` for `make parity-harness`. Expect it may be declined. |
| 7 | The ErrImageNeverPull row does not quote the new message "did not start within 3 minutes", so a reader searching for it finds nothing. | taste | `docs/local-integration-tests.md:192` | Optionally quote the message in the symptom column. |

## Not checked

I did not run a cluster, the Dockerfile in Docker, or any Helm or kubectl version. The busybox `sort -z` and `xargs -0` path in `alpine:3.22` is unverified. The Helm 3.14 floor is unverified, since I found no feature that needs it. The reusable `docker-build.yaml` in another repository, which decides what CI publishes, was not read. The drift script printed nothing for this diff. The form did not include a prose pass beyond the sentences it touches.

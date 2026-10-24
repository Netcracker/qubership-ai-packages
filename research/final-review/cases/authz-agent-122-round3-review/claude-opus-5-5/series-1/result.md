# Final review of f3b64e0 (`5dcb6be..HEAD`)

**Verdict: four findings need changes before this commit is final.** Most of the review comments are fixed. The wait loop in `run-suite` still has a fault that blows past both the 3-minute bound and CI's 30 minutes. The documented tool versions have no run behind them. The timeout example does nothing on its own. And the commit message leaves out four of the hunks.

**How the form was applied.** The change has no code that the drift script parses: it is a Makefile, a Dockerfile, Markdown and YAML. I ran `comment-drift.py 5dcb6be HEAD` and it printed nothing, so I used the §2a analogues. Skills loaded: `english-developer-style`. The repository has no docs-page authoring skill. No earlier report of this form exists, so there is no table of earlier findings. The task statement is the review comments plus the commit message.

## Item 1: comments consistent with the code and with each other
*Analogue: every statement a changed file makes about another file or about tool behaviour.*

- **`Makefile:104-105`** says "`kubectl logs` fails until the Job exists and its container has started, so the loop polls for up to three minutes." That holds only when the attempt fails fast.
  - `kubectl logs job/<name>` takes a `--pod-running-timeout` of 20s by default (see `kubectl logs --help`). When the Job exists but has no Pod yet, each attempt can wait those 20s.
  - So the loop can take 90 × (20s + 2s) = 33 minutes, not three. The echo text "did not start within 3 minutes" is then false too. Details under item 3.
- `README.md:59-60` ("CI builds them, with the test images and the transfer image") matches `.github/docker-dev-config.json`. The only test images it lists are pip-stub and parity-suite, which is what line 67 names.
- `.github/docs-for-publication-task.md:77` no longer gives a count. It is consistent.
- `helm-templates/authz-test-stand/README.md:62` gives the Helm 4.3 boundary that comment 1 asked for. It is consistent with the "Helm 4 works too" in `docs/local-integration-tests.md:38`, because the Makefile does not pass `--logs`.
- `test/k8s/README.md:66-70` and the troubleshooting row in `docs/local-integration-tests.md:196` agree on the variables and the 15m default.

## Item 2: claimed cases covered

| Claim | Covered by |
| --- | --- |
| Comment 1: Helm 4.3 boundary | `helm-templates/authz-test-stand/README.md:62`. A text change; no run of 4.0–4.2 or 4.3 is cited. |
| Comment 2: suite timeouts listed | `test/k8s/README.md:69-70`, `docs/local-integration-tests.md:196` |
| Comment 3: parity remedy | `docs/local-integration-tests.md:193` now names `make parity`. `parity` depends on `e2e-cluster` and `e2e-images` (`Makefile:157`), so the remedy is complete. |
| No `--for=create` | `Makefile:112-120`. No kubectl call left needs 1.31. Every other kubectl call is old (`rollout restart`, `delete --wait`, `get --sort-by`). |
| ErrImageNeverPull fails in about 3 minutes | Read from the code: the Pod exists, so each `logs` attempt fails at once, giving about 90 × 2s. No run of this fault is cited. |
| `TEST_STAND_HELM_ARGS` | `Makefile:51,93,164`; `make -n e2e-suite` expands as expected. |
| Sorted, NUL-separated user files | I ran this. In a scratch copy I added `a.json`, `b users.json` and `sub.json`, then built `--target chart-files`. The users merged in sorted order and the file with a space was read whole. A duplicate username fails the build, an empty file merges as zero users, and the empty `users/` directory of the real tree gives output byte-identical to the base build. |
| SVT back to Keycloak 26.0 | `git diff 8b85515^ HEAD -- test/svt` is empty, so the revert is exact. |
| Docker 23.0 and Helm 3.14 or later; kubectl and kind any version (`docs/local-integration-tests.md:35-42`) | **none.** CI runs only `azure/setup-helm` v4.3.1, the latest kubectl from `kind-action`, and the Docker of `ubuntu-latest`. |

**Documented commands checked against what runs:**

- **`make parity-suite PARITY_SUITE_TIMEOUT=5h30m`** (`docs/local-integration-tests.md:196`): **none** runs it.
  - The outcome depends on `suite.activeDeadlineSeconds`, which is 900 in `values.yaml:99`. That value is set at `parity-harness` time.
  - Run as written, the Job is killed at 15 minutes anyway, so the raised timeout has no effect. The row says "together with", but its only example raises one of the two limits.
  - It should show the full form, for example `make parity-harness TEST_STAND_HELM_ARGS='--set suite.activeDeadlineSeconds=19800' parity-suite PARITY_SUITE_TIMEOUT=5h30m`. `TEST_STAND_HELM_ARGS` is now the variable for exactly this.
- **The minimum-version claim** (`docs/local-integration-tests.md:35-42`): the commit subject says "run the test stand on year-old tools", but nothing runs Helm 3.14, Docker 23.0 or any Helm 4.0–4.2.
  - Helm 3.14 is not tied to any feature I found in the chart's templates or the Makefile.
  - Request: a CI matrix entry on Helm v3.14.x (and an older kubectl), or a cited local run. Otherwise, state only the versions CI runs.
- **`make e2e-down` then `make e2e` / `make parity`**: this deletes the cluster, so the left-over objects cannot survive it. This is covered by construction.

**Hunks the commit message does not claim:**
- the `README.md` "CI builds them" rewrite;
- the `.github/docs-for-publication-task.md` count removal;
- the `make parity` remedy in the troubleshooting row;
- the `test/k8s/README.md` override sentence.

Request: one sentence each in the message, for example "README.md and docs-for-publication-task.md no longer count the components; the import-error row sends a parity run to `make parity`."

## Item 3: boundaries, partitions, and the negative control

**Mechanism replaced: the run-suite wait.**

| Fault | Old | New |
| --- | --- | --- |
| ErrImageNeverPull | About 15 min: `logs -f` failed, then it waited out `helm test`. | About 3 min. Prints the message and the Pod listing, then kills helm. **Good.** |
| Job exists, no Pod is ever created | Same loop: 90 × 22s. | Each `kubectl logs job/…` attempt waits the default 20s `--pod-running-timeout`, so up to **33 minutes**. Helm exits at about 15 min when the 900s deadline fails the Job, but the loop does not notice and keeps going. Then it prints "did not start within 3 minutes" and the listing shows `No resources found`, with nothing about the `FailedCreate` events. |
| `helm test` fails at once (release not found, wrong context) | About 2 min (`wait --for=create --timeout=2m`). | About 3 min. Then it prints the misleading "container did not start" message, and `kill` reports "No such process". |

The "no Pod" case is a realistic one for this branch: commit 17b17fc moved the stand to the restricted Pod Security Standard, and a Pod that breaks that policy is rejected at creation. In CI, 33 minutes is past the job's `timeout-minutes: 30`. Nothing in the change accepts this.

Request:
- end the loop when helm has exited (`kill -0 $$helm_pid || break`);
- bound each attempt (`--pod-running-timeout=2s`), or bound the loop by elapsed time;
- add `kubectl get events --field-selector involvedObject.name=<job>` to the failure output;
- a run of the ErrImageNeverPull fault with its duration and output.

**Values users already pass.** The stand and the product charts both read `TAG` and `IMAGE_PULL_POLICY`.
- After the change, `E2E_HELM_ARGS` no longer reaches the stand, and the stand's own values pin `TAG: ci` and `IMAGE_PULL_POLICY: Never`.
- A `--set suite.…` someone used to pass through `E2E_HELM_ARGS` now goes only to the product charts, which ignore it without an error.
- The User-visible line of the commit message states this change, so it is accepted. No finding.

**Limits.**
- `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT` versus `suite.activeDeadlineSeconds`: covered by the finding in item 2.
- The 3-minute start bound versus `helm test`'s timeout: covered by the loop finding above.
- In CI, any suite timeout above about 15 minutes is cut by `timeout-minutes: 30`, which also has to cover the image build, the harness (10m) and the installs (2 × 5m). The new prose is aimed at local runs, so I label this taste: a clause saying that CI's 30 minutes caps the variable.

**Earlier state.** The import-error remedy deletes the cluster, so no earlier state survives it. The Dockerfile change gives byte-identical output on the current tree.

## Item 3a: level, placement, and the environment
*Analogue: where each rule lives, and which gate runs it.*

- The Dockerfile behaviour can be checked in one process, and I checked it with a local `docker build`. No CI gate runs it on a user file whose name has a space, but the testdata directory is empty today. No finding.
- The version floors are something a CI job would have to run, and none does. Covered in item 2.

## Item 4: names by content, not by position
None. The new rows, variables and messages name things by content.

## Item 5: the failure report
*Analogue: what a failure tells the reader.*

The new failure path prints `get pods -l job-name=…`. In the no-Pod case that prints nothing useful (item 3). Otherwise none.

## Item 6: what the writer says it verified
The commit states no run:
- none of the ErrImageNeverPull path;
- none of the minimum tool versions;
- none of the sorted merge with real user files.

I ran the merge myself (item 2). The other two have no evidence.

## Item 7: siblings of the change

- **Other places that use `run-suite`:** only `e2e-suite` and `parity-suite` (`Makefile:124,172`). Both get the fix.
- **`TEST_STAND_HELM_ARGS` (a new member of the overrides set):** the only list of overrides is in `test/k8s/README.md`, and it is there. `docs/local-integration-tests.md` has no overrides table; it names only the timeouts.
- **Old counts:** I searched for "both", "two" and "three" across the changed docs. `README.md:67` "Besides the two services" is still correct.
- **The import-error row:** it names `e2e-harness` and `parity-harness`, and its action now names `make e2e` and `make parity`. Covered.
- **Other paths with the same symptom:** in `test/k8s/README.md:47-49` the same remedy says "before the first run of the test-stand chart" with no target, so it already covers both.

## Findings

| Finding | Label | File:line | Request |
| --- | --- | --- | --- |
| If no Pod is ever created, the start loop can take up to 33 min (20s per attempt). It ignores helm's exit and then reports "did not start within 3 minutes". | Substantive | `Makefile:112-118`, comment `:104-107` | Break when helm has exited, bound each attempt (`--pod-running-timeout`), print the Job's events, and cite a run of the fault. |
| The loop runs about 3 min and prints a misleading cause when `helm test` fails at once. | Substantive | `Makefile:113` | The same `kill -0` check. |
| The example `PARITY_SUITE_TIMEOUT=5h30m` has no effect while `activeDeadlineSeconds` stays at 900 from the harness. | Substantive | `docs/local-integration-tests.md:196` | Show the harness step with `TEST_STAND_HELM_ARGS='--set suite.activeDeadlineSeconds=…'`. |
| Docker 23.0, Helm 3.14 and "any" kubectl/kind are claimed, but CI runs only Helm 4.3.1 and the latest tools. | Substantive | `docs/local-integration-tests.md:35-42`, commit subject | A CI or local run on those versions, or state only what runs. |
| The README, publication-doc, troubleshooting-row and `test/k8s/README` hunks are not in the commit message. | Substantive | commit message | One sentence each. |
| The suite-timeout prose does not say CI's `timeout-minutes: 30` caps it. | Taste | `test/k8s/README.md:69` | An optional clause. |

I did not run the kind suites or any `helm test` (there is no cluster), did not run Helm 3.x, Docker 23 or older kubectl, did not run SVT, and made no style-only pass over the prose.

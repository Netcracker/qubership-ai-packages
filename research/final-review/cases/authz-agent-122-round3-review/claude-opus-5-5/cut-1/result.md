I made no file changes and no commits. This is the final-review report for `5dcb6be..HEAD` (commit `f3b64e0`).

`comment-drift.py 5dcb6be HEAD` ran and printed nothing, because it does not parse Makefile, Markdown, Dockerfile, or YAML. The change has no code members and no tests, so every item below is answered through the §2a analogues ("change with no code"). I loaded `english-developer-style` and `test-authoring` from the given directory. There is no previous report.

## Item 1: comments consistent with the code and with each other
Analogue used: every statement a changed file makes about the Makefile, the chart, CI, or a tool.
- **`Makefile:104-105`** says "the loop polls for up to three minutes". That is false when the Job exists but its Pod is never created. Each `kubectl logs job/<name>` then waits `--pod-running-timeout`, 20s by default per `kubectl logs --help`, for a Pod to appear. That makes 90 × (20s + 2s) ≈ 33 min. The `echo "… did not start within 3 minutes:"` and the commit's "fail after about three minutes" carry the same error. Details are under Item 3.
- The other statements hold:
  - `Makefile:46-49` (`E2E_HELM_ARGS` and `TEST_STAND_HELM_ARGS`) matches the recipes. `make -n` with both variables set shows each value reaching only its own charts.
  - `test/k8s/README.md:66-70` matches the Makefile.
  - The chart README's Helm 4.3 sentence matches review comment 1.
  - The Dockerfile comments at lines 9-17 and 30-36 still hold, including "fails if a user is declared twice".
  - `docs-for-publication-task.md:77` matches `.github/docker-dev-config.json`.
- **`README.md:59-60`** has two smaller problems (taste):
  - "with the test images" reads as all test images, but the component list has only pip-stub and parity-suite, not tenant-manager or the runtime suite.
  - "publishes the two services as" reads as if CI publishes only those two images.

## Item 2: claimed cases covered
| Claim | Where it is covered |
| --- | --- |
| Comment 1: Helm 4.3+ prints nothing; 4.0–4.2 and 3 fail | `helm-templates/authz-test-stand/README.md:62`. The reviewer's versions are used as given. |
| Comment 2: timeout variables listed | `test/k8s/README.md:69-70` and the troubleshooting row at `docs/local-integration-tests.md:196` |
| Comment 3: the row covers `make parity` | `docs/local-integration-tests.md:192` names `make e2e` or `make parity` in both the cause and the action |
| kubectl 1.31 dependency removed | The `--for=create` call is gone, and `git grep -- --for=create` finds no other use |
| Suite that never starts stops after about 3 minutes | Makefile `run-suite`. No run is stated, and it does not hold on the Pod-never-created fault (Item 3). |
| Test-stand Helm args take their own variable | `make -n e2e-harness parity-harness e2e-install TEST_STAND_HELM_ARGS='--set TAG=x' E2E_HELM_ARGS='--set TAG=y'` sends `TAG=x` only to the stand and `TAG=y` only to the product charts |
| Sorted, NUL-separated user files | Run locally with BSD `find`/`sort` and jq 1.8.2, details below. Not run in the Alpine/busybox stage. |
| SVT Keycloak back on 26.0 | The line is byte-identical to the one before `8b85515`, and yamllint passes |
| README "both" and "two-entry array" fixed | `README.md:59-60`, `.github/docs-for-publication-task.md:77` |

For the sorted-files row:
- The repository has no user JSON files today; `testdata/realm/` holds only a `README.md`. So with the repository's data, the old and new pipelines give byte-identical output (`cmp` reports no difference).
- I also tried three files: `b file.json`, one in a subdirectory, and one with no trailing newline. All of them merged, in byte order.

Commands the change documents:
- **Docker 23.0, Helm 3.14, Helm 4, and "kubectl … any version" (`docs/local-integration-tests.md:35-42`): none.**
  - CI pins Helm v4.3.1 (`integration-tests.yaml:72,132,180`) and the kubectl that `kind-action` installs. No job and no stated run uses Helm 3.x or Docker 23.
  - The behaviour that depends on version:
    - `helm test` waiting on a Job hook and being killed by SIGTERM.
    - `upgrade --install --wait` readiness, where Helm 3 uses the legacy waiter and Helm 4 uses kstatus.
    - BuildKit `--output type=local` together with `FROM --platform=$BUILDPLATFORM`.
  - From the chart's template functions (`dig`, `required`, `toYaml`), I see no feature newer than Helm 3.14, but nothing ran it.
  - The title also says "year-old tools", while Helm 3.14 and Docker 23.0 are 2–3 years old.
- **`make parity-suite PARITY_SUITE_TIMEOUT=5h30m`:** none runs it. It has an effect only if `suite.activeDeadlineSeconds` was raised at harness time (Item 3).

Hunks no sentence claims: the commit message does not mention the `README.md` hunk, the `.github/docs-for-publication-task.md` hunk, or the `test/k8s/README.md` override paragraph. They answer review comments, but the commit message never mentions them.

## Item 3: boundaries, partitions, and the negative control
**Old versus new mechanism**, from the Makefile at `5dcb6be` and at `HEAD`:

| Fault | `5dcb6be` | `HEAD` |
| --- | --- | --- |
| ErrImageNeverPull (common; the stand sets `IMAGE_PULL_POLICY: Never`) | about 15 min, prints only helm's timeout | about 3–4 min (90 × (2s + one API call)), prints the message and a Pod listing with the status |
| Job exists, Pod never created (restricted PSS rejects the Pod after a values override, ResourceQuota, missing ServiceAccount) | about 33 min, prints nothing about the cause | about 33 min. helm stops at 15 min and the loop goes on. Then "did not start within 3 minutes" and `No resources found`. CI's `timeout-minutes: 30` fires first. |
| `helm test` fails at once (release not installed, suite disabled) | about 2 min (the old `kubectl wait --for=create` limit) | about 3 min, then a misleading "container did not start" message and `kill: No such process` |

The no-Pod fault comes from 17b17fc's restricted Pod Security Standard (PSS) stand. The `HEAD` loop does not check whether helm has exited.

That is a substantive finding: the second fault is the one where one attempt waits longest, and the change bounds it nowhere. The request:
- Bound each attempt with `--pod-running-timeout=2s`, or use a wall-clock deadline.
- Leave the loop when `kill -0 $helm_pid` fails.
- On timeout, print `kubectl describe job/<name>` or the Job's events, so that `FailedCreate` shows.
- Or state a run of each fault with its duration.

**Limits:**
- `E2E_SUITE_TIMEOUT` or `PARITY_SUITE_TIMEOUT` raised past 900s has no effect unless `suite.activeDeadlineSeconds` is raised too. The Makefile, the test/k8s README, and the troubleshooting row all say so. The row's example leaves out the step that does it: `make parity-harness TEST_STAND_HELM_ARGS='--set suite.activeDeadlineSeconds=…'` (taste).
- CI's 30-minute job limit caps any raised value in CI. No CI job raises it, so there is no finding.

**Pre-existing state and values users already pass:** before 8b85515, `E2E_HELM_ARGS` never reached the stand, so this change restores the old behaviour. `TEST_STAND_HELM_ARGS` has no earlier consumer. Nothing to report.

**SVT:** no partitions. The change reverts a hunk.

## Item 3a: level, placement, and the environment
Analogue used: gates that run offline.
- `helm lint` on the stand with `test-stand-values.yaml`: 0 failures.
- yamllint on the compose file: passes.
- No changed Markdown line passes MD013's limit of 400.
- The `run-suite` failure branch only runs against a cluster, and no CI job exercises it.

## Item 4: names by content, not by position
None. The new headings, messages, and table rows name things by content.

## Item 5: the failure report
Analogue used: what the new failure message tells a reader to look at. On ErrImageNeverPull, the Pod listing shows the reason. On the Pod-never-created fault, it prints only `No resources found` and does not say why. This is part of the first substantive finding. The new message also has no row in the troubleshooting table (taste).

## Item 6: what the writer says it verified
The commit states none of these runs:
- the never-starts path on a cluster
- the targets on Helm 3.14 or Docker 23
- the `chart-files` stage built with the sorted pipeline

## Item 7: siblings of the change
- `run-suite` serves both `e2e-suite` and `parity-suite`. `--for=create` and unquoted `$(find …)` have no other uses in code.
- New member `TEST_STAND_HELM_ARGS`: every file that names `E2E_HELM_ARGS` also names it (the Makefile and `test/k8s/README.md`). `docs/local-integration-tests.md` has no list of overrides.
- Searched for the old size of the component list ("both", "two"): `README.md:67` "Besides the two services" correctly means the services. The two counts the review flagged are fixed.
- Remedy rows:
  - The "cannot be imported" row now names `make e2e` and `make parity` in both the cause and the action.
  - The new timeout row names both targets and both variables.
  - The ErrImageNeverPull row's `make e2e-images` builds the parity image too.
- The target table entries for `e2e-suite` (`test/k8s/README.md:58`, `docs/local-integration-tests.md:109`) still say only "fails if the Job did not complete". They do not mention the 3-minute stop (taste).

## Findings
| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| The start loop is not bounded at 3 min. On a Job whose Pod is never created, each `kubectl logs` waits 20s, so the target runs about 33 min, past CI's 30. It also keeps polling after `helm test` has exited, and the failure output gives no cause. | Substantive | `Makefile:104-119`; commit message "about three minutes" | Use `--pod-running-timeout=2s` or a wall-clock deadline, break when `kill -0 $helm_pid` fails, and print the Job's events. Or state a run of these faults with durations. |
| Helm 3.14, Docker 23.0, Helm 4, and "any kubectl" are claimed, but only Helm 4.3.1 runs, in CI | Substantive | `docs/local-integration-tests.md:35-42` | Run `make e2e` and `make parity` on Helm 3.14 and Docker 23.0 (or add a CI leg), or claim only what has run |
| The commit message does not mention the `README.md`, `docs-for-publication-task.md`, or `test/k8s/README.md` override hunks | Substantive | commit `f3b64e0` | Add one sentence that covers them |
| "with the test images" covers only pip-stub and parity-suite; "publishes the two services" reads as if CI publishes only two | Taste | `README.md:59-60` | Name the two test images |
| The timeout row's example omits the harness step that raises `suite.activeDeadlineSeconds` | Taste | `docs/local-integration-tests.md:196` | Show `TEST_STAND_HELM_ARGS='--set suite.activeDeadlineSeconds=…'` at `parity-harness` |
| The new "did not start within 3 minutes" failure is missing from the troubleshooting table and the `e2e-suite` target rows | Taste | `docs/local-integration-tests.md:109,192`, `test/k8s/README.md:58` | Add the message to the ErrImageNeverPull row's symptom |

Not checked:
- No cluster was available, so the 20s-per-attempt wait comes from kubectl's help text and source, not from a run.
- The `chart-files` stage was not built with Docker, so busybox `sort -z` and `xargs -0 -r` in Alpine were not run.
- markdownlint did not run.
- The prose was not reviewed for style.

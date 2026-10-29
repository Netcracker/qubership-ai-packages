# Final review: `5dcb6be..HEAD`, one commit (f3b64e0)

The commit covers all nine review comments, and I found no regression in the code it changed. Five substantive findings remain:

- **Suite start bound:** the three-minute bound on a suite that never starts holds only when the Job has a Pod.
- **Minimum versions:** none of the stated minimum tool versions was run.
- **Docker install:** the Docker install command on the same page doesn't give the Docker the page now requires.
- **Suite timeout pair:** the new troubleshooting row about the suite timeout gives only half of the fix.
- **README:** "the test images" claims more images than CI builds.

There was no previous report. The drift script printed nothing: the change touches only a Makefile, a Dockerfile, Markdown and YAML, and the script parses none of them. So item 1 uses the no-code version of the form (statements about other files, counts, lists).

## Item 1: comments consistent with the code and with each other

Every changed statement was checked against what it describes:

- **`Makefile:46-49`:** the `E2E_HELM_ARGS` comment matches lines 93, 99-100, 164 and 168-169.
- **`Makefile:104-109`:** the `run-suite` comment says "polls for up to three minutes". That holds only when the Job has a Pod (see item 3).
- **`helm-templates/authz-test-stand/README.md:62`:** the Helm 4.3 split matches inline comment 1.
- **`README.md:59`:** "with the test images" reads as all of them. `.github/docker-dev-config.json` lists `pip-stub` and `parity-suite` but not `tenant-manager` or `authz-runtime-suite`. A reader would expect CI to build the runtime suite image. **Substantive (minor).**
- **`README.md:60`:** "publishes the two services". If the shared `docker-build.yaml` pushes every component it builds, the other three are published too. I could not read that workflow offline. **Taste, unverified.**
- **`.github/docs-for-publication-task.md:77`:** "The component array" is correct.
- **No change narration.** None of the new text says "now", "no longer" or "used to".

## Item 2: claimed cases covered

| Claimed case | What runs it |
| --- | --- |
| Comment 1 (Helm 4.3 split) | The text matches the comment. No run, and none is owed for prose. |
| Comment 2 (suite timeout variables) | `test/k8s/README.md:69-70`; `docs/local-integration-tests.md:196` |
| Comment 3 (`make parity` after `e2e-down`) | `docs/local-integration-tests.md:193`. `e2e-down` deletes the cluster, so both namespaces go. |
| `--for=create` replaced; works on any kubectl | Only CI's kubectl runs it, the version `kind-action` installs. **No run on kubectl < 1.31.** |
| Suite container never starts → fails after ~3 min with the message and the Pod list | **none.** CI runs only the passing case. |
| `TEST_STAND_HELM_ARGS` reaches the stand; `E2E_HELM_ARGS` doesn't | `make -n` shows the right variable on lines 93, 164 and the four product installs. |
| Sorted, NUL-separated user files | **No test in the change.** I built it myself (item 6). |
| SVT back on Keycloak 26.0 | Identical to the file before 8b85515, so it is a revert to a version already run. |
| Docker 23.0 and Helm 3.14 or later; Helm 4 works; kubectl and kind "any version"; "no tool feature newer than these versions" | **none.** CI pins Helm `v4.3.1` (`.github/workflows/integration-tests.yaml:130,178`). |

Notes on the `none` rows:

- **Minimum versions (substantive).** On Helm 3.14 the targets use `helm test` with a hook Job, `upgrade --install --wait` (Helm 3 polls readiness itself, Helm 4 uses the kstatus watcher), and the stand's `--wait` over the Keycloak Deployment. None of that ran on Helm 3, on kubectl < 1.31, or on Docker 23.0. The commit title, "run the test stand on year-old tools", promises exactly those runs. **Request:** a run of `make e2e` and `make parity` on Helm 3.14, kubectl 1.30 and Docker 23.0 (or a Helm 3.14 entry in the kind jobs' matrix), or remove the minimums the change cannot back.
- **Docker install command (substantive).** The page's install snippet, `apt-get install -y docker.io` (`docs/local-integration-tests.md:51-53`), sits right under the new "Docker 23.0 or later, where BuildKit is the default builder" row. `test-stand-files` needs BuildKit for `docker build --output type=local` and for `FROM --platform=$BUILDPLATFORM`.
  - On Debian 12, `docker.io` is 20.10 as far as I recall, which is below 23.0.
  - On Ubuntu, `docker.io` doesn't pull in `docker-buildx`. Without buildx, the CLI falls back to the legacy builder, which rejects `--output`.
  - I recalled these package facts rather than ran them. **Request:** add `docker-buildx` to the snippet (or point to Docker's own repository) and run `make test-stand-files` on that install.
- **Hunks no sentence of the commit message covers (substantive, small).** The `README.md` and `.github/docs-for-publication-task.md` changes answer the last general review comment, but the commit message never mentions them. **Request:** one sentence for them.

## Item 3: boundaries, partitions, and the negative control

The Makefile, Dockerfile, Markdown and YAML have no unit tests, so this item covers the faults, the limits and the values users already pass.

**The common fault, before and after.**
- **ErrImageNeverPull, old:** waited out `helm test --timeout` (15 min).
- **ErrImageNeverPull, new:** the Pod exists, so `kubectl logs job/…` fails at once ("waiting to start"). That gives 90 × (≈0.3 s + 2 s) ≈ 3.5 min, then the message and the Pod list. Improved as claimed.

**A Job with no Pod (substantive).** This happens when Pod creation is rejected: Pod Security admission under the restricted level the previous commit enables, a quota, or a missing ServiceAccount.
- In that state, `kubectl logs job/<name>` resolves the Job through `GetFirstPod`. That function watches for a Pod for up to `--pod-running-timeout`, 20 s by default; the code is at `k8s.io/kubectl@v0.29.0/pkg/polymorphichelpers/helpers.go:41-71`.
- Each attempt therefore takes about 22 s, and the loop takes 90 × 22 s ≈ 33 min. That is past `helm test`'s 15 min and past CI's `timeout-minutes: 30`, so CI kills the job before the message prints.
- The loop also never checks whether `helm_pid` has exited.
- Even when the message does print, `get pods -l job-name=…` shows "No resources found". The reason is in the Job's `FailedCreate` events.

**Request:**
- Pass `--pod-running-timeout=2s` to the probe, or bound the loop by elapsed time.
- End the loop when `helm test` has exited (`kill -0 $$helm_pid`).
- Print the Job's events as well as the Pods.
- Run the fault, for example with a non-compliant `securityContext`.

**Limits on the suite's run time (substantive).**

| Limit | Value | Where it is set |
| --- | --- | --- |
| Start probe | ~3 min, or ~33 min with no Pod (above) | `Makefile:113` |
| `suite.activeDeadlineSeconds` | 900 s | `helm-templates/authz-test-stand/values.yaml:99`; the parity values don't override it |
| `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT` | 15m | `Makefile:54-55` |
| CI job | 30 min | `.github/workflows/integration-tests.yaml:120,168` |

- **The default pair:** helm's clock starts before the Job exists, so at 15m against 900 s helm fires first and hides the Job's `DeadlineExceeded` report. The new row "fails after 15 minutes while the Job still runs" describes a state the defaults hardly reach.
- **The row's example:** `make parity-suite PARITY_SUITE_TIMEOUT=5h30m` raises only the outer limit. The deadline is rendered into the Job at harness time, and since this change it can be set only through `TEST_STAND_HELM_ARGS`, not `E2E_HELM_ARGS`. Neither page says so. A reader who follows the example still has the Job killed at 15 min.
- **Request:**
  - Default the helm timeout above the deadline, by the 3-min start allowance or more.
  - Complete the example with `make parity-harness TEST_STAND_HELM_ARGS='--set suite.activeDeadlineSeconds=19800'`.

**Values users already pass.** This is fine:
- The documented `E2E_HELM_ARGS='--set IMAGE_PULL_POLICY=Never'` no longer reaches the stand. The stand stays `IfNotPresent`, which works with the images loaded through `kind load`.
- A user who set stand values through `E2E_HELM_ARGS` now has them silently ignored. The commit's "User-visible" section says so.

**State an earlier version left behind.** The `exists and cannot be imported` row covers it, and running it needs the old harness objects. That predates this commit.

## Item 3a: level, placement, and the environment

- **Dockerfile:** CI's chart job runs `make test-stand-files` (`integration-tests.yaml:77`), but `testdata/realm/` holds no user `.json` file, so the sort and the NUL handling never run in CI. No smaller test is possible short of a fixture user file.
- **`run-suite`:** this exists only on a cluster. The finding is the fault partition with no run (item 3), not a missing unit test.
- **Markdown:** the new lines stay under the 400-character MD013 limit.

## Item 4: names by content, not by position

none. I checked the new headings, table rows and messages; "the three" at `test/k8s/README.md:64` predates this commit and names its targets.

## Item 5: the failure report

- **The new message.** "The <job> container did not start within 3 minutes:" followed by the Pod list shows the Pod's reason (`ErrImageNeverPull`) when a Pod exists. With no Pod it shows nothing useful (item 3).
- **The troubleshooting table.** Row 192 ("Pending or reports ErrImageNeverPull") doesn't quote the new message, so a grep for it finds nothing. **Taste.**

## Item 6: what the writer says it verified

The commit states no run:
- of the ErrImageNeverPull fault;
- on an older kubectl, Helm 3.14 or Docker 23.0;
- of the Dockerfile with user files.

I checked the Dockerfile myself, which is not the writer's evidence:
- The `chart-files` stage at the base and at HEAD gives identical output with no user files.
- With `a.json`, `sub/m.json` and `z users.json`, the users merge in sorted order and the name with a space works.
- A duplicate username makes the build fail.

## Item 7: siblings of the change

- **`run-suite`:** it has two callers (`e2e-suite`, `parity-suite`), and both get the change. `git grep -- --for=create` and `$(find` now find no matches.
- **`E2E_HELM_ARGS` / `TEST_STAND_HELM_ARGS`:**
  - The Makefile reads them on lines 93, 99-100, 164 and 168-169.
  - `test/k8s/README.md` lists them.
  - `docs/local-integration-tests.md` has no table of overrides; `KIND_CLUSTER` isn't on it either, so that is consistent.
  - CI passes neither.
- **Old counts:** `git grep` for "both", "two-entry", "two images" and "two components" finds no stale count outside agent skills. `README.md:60` "the two services" is a count of services, not of components.
- **Helm-version paths:** the chart README is the only page that mentions `--logs`.
- **The `make e2e`/`make parity` remedy:** both paths are covered.

## Findings

| Finding | Label | File:line | Requested change |
| --- | --- | --- | --- |
| With no Pod (PSA, quota, missing SA), each probe waits `--pod-running-timeout` 20 s: ~33 min instead of 3; the loop ignores helm's exit; the Pod list is empty | Substantive | `Makefile:113-118` | `--pod-running-timeout=2s` or a time bound; stop when `helm_pid` exits; print the Job's events; run the fault |
| Helm 3.14, kubectl < 1.31, Docker 23.0, "no feature newer" were never run; CI pins Helm 4.3.1 | Substantive | `docs/local-integration-tests.md:35-42` | A run or CI matrix entry on those versions, or remove the minimums |
| The page's `apt-get install docker.io` gives no buildx (Ubuntu) or Docker 20.10 (Debian 12), but `test-stand-files` needs BuildKit | Substantive | `docs/local-integration-tests.md:51-53` | Install `docker-buildx` or use Docker's own repository; run `make test-stand-files` on it |
| Helm timeout 15m equals the 900 s deadline and starts earlier, so the Job's report is hidden; the row's example raises only the helm timeout, and the deadline needs `TEST_STAND_HELM_ARGS` at harness time | Substantive | `Makefile:54-55`, `docs/local-integration-tests.md:196`, `test/k8s/README.md:69-70` | Helm timeout above the deadline; complete the example with the `parity-harness` step |
| "with the test images" suggests CI builds the runtime-suite and tenant-manager images | Substantive | `README.md:59` | Name `pip-stub` and `parity-suite` |
| README and docs-for-publication hunks have no sentence in the commit message | Substantive | `README.md:59`, `.github/docs-for-publication-task.md:77` | One sentence in the message |
| "publishes the two services" may understate what the shared workflow pushes | Taste (unverified) | `README.md:60` | Check `docker-build.yaml` |
| The troubleshooting table doesn't quote the new "did not start within 3 minutes" message | Taste | `docs/local-integration-tests.md:192` | Quote it in that row |

I did not run `make e2e` or `make parity` on a cluster, any tool at the stated minimum versions, apt on Debian or Ubuntu, or the shared `docker-build.yaml`, and I did not review the prose for style.

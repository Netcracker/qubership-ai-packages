I reviewed `5dcb6be..f3b64e0` (one commit), using the review comments and the commit message as the task statement. The commit contains no code the drift script parses (it changes a Makefile, a Dockerfile, Markdown and YAML). The script ran and printed nothing, so each item below uses the §2a analogue for files without code. I loaded `test-authoring` and `english-developer-style` from the given path. The change fixes most of the review comments, but the new three-minute stop in `run-suite` does not hold in two cases, and the new tool versions in the docs have never been run.

There is no previous report of this form, so the report has no opening table.

## Item 1: comments consistent with the code and with each other
(Analogue: every comment in a changed file, and every statement it makes about other files.)

- **`Makefile:104-107`** says "`kubectl logs` fails until the Job exists and its container has started, so the loop polls for up to three minutes." That is wrong in one case: the Job exists but has no Pod.
  - `kubectl logs job/<name>` does not fail at once in that case. It finds Pods through the Job's selector, and when there are none it waits for one until `--pod-running-timeout` runs out. The default is 20s (`k8s.io/kubectl@v0.35.0/pkg/polymorphichelpers/helpers.go:61-75`, `cmd/logs/logs.go:117`).
  - So each attempt takes about 20s plus the 2s sleep, and the loop polls for 90 × 22s ≈ 33 minutes, not three. Item 3 has the details.
- The comment above `E2E_HELM_ARGS` (`Makefile:46-49`) matches the recipes: the product charts at lines 99-100 and 168-169, the stand at 93 and 164. `test/k8s/README.md:67-70` says the same.
- The chart README (`helm-templates/authz-test-stand/README.md:61-62`) and the docs table (`docs/local-integration-tests.md:38`) agree. The README is about `helm test --logs`, which no target runs.
- `docs-for-publication-task.md:77` no longer counts the components.
- `README.md:59` says "with the test images". That reads as every test image, but `.github/docker-dev-config.json` lists only pip-stub and parity-suite. `make e2e-images` builds four test images (`Makefile:74-77`), including tenant-manager and authz-runtime-suite. Line 67 of the same README names the two correctly.
- No comment narrates the change.

## Item 2: claimed cases covered
Claimed cases, from the commit message and the comments:

| Claim | Covered by |
| --- | --- |
| `run-suite` works on kubectl before 1.31 | The recipe no longer uses `wait --for=create`. CI runs only a recent kubectl (kind-action v1.15.1). No run on an old kubectl, but it no longer depends on a 1.31 feature. |
| A suite container that never starts makes the target fail after about 3 minutes, with the message and the Pod listing | **none**. No run of `ErrImageNeverPull` is stated. Working it out from kubectl's source: a Pod whose container is waiting returns a log error at once, so this fault does stop after about 3 minutes. Two other faults do not (Item 3). |
| `TEST_STAND_HELM_ARGS` reaches the stand, and `E2E_HELM_ARGS` no longer does | `make -n` shows it. CI passes neither variable. |
| The chart-files stage is deterministic and handles a file name with a space | No CI coverage: `test/parity/suite/testdata/realm/` holds only `README.md`, so the CI builds never reach the sort or the space path. I ran the commit's pipeline (with jq 1.8.2) on `users/b file.json` and `users/sub/a.json`. Both files merged, in sorted order. An empty users directory leaves the realm at 14 users, as before. |
| SVT goes back to Keycloak 26.0 | `git log -p` on the file shows it restores exactly the line `8b85515` replaced. No SVT run is needed for a revert. |
| Helm 4.3 and later print nothing for `helm test --logs`; 4.0–4.2 and Helm 3 fail | This text comes from the review comment and the earlier commit's runs on 4.3.1 and 3.22.1. No run on 4.0–4.2. |
| Docs: Docker 23.0+, Helm 3.14+, "Helm 4 works too", and "`kubectl` and `kind` may be any version that supports the cluster" | **none**. |
| Docs: `make parity-suite PARITY_SUITE_TIMEOUT=5h30m` | **none**. |
| Docs: `make e2e-down`, then `make e2e` or `make parity` | Nothing runs it on an old cluster, but `e2e-down` is `kind delete cluster` (`Makefile:145`), so no state survives it. This covers both paths. |

Findings:
- **The version table has never been run.** Every CI kind job pins Helm `v4.3.1` (`integration-tests.yaml:132`, `:180`) and uses the runner's Docker and kind-action's kubectl. So "Helm 3.14 or later", "Docker 23.0", "Helm 4 works too" (which covers 4.0–4.2) and "any kubectl" each depend on things nothing checks:
  - how `helm test` and `upgrade --wait` treat a Job hook in Helm 3.14;
  - BuildKit's `--output type=local` in Docker 23;
  - how an old kubectl handles `logs job/`.

  The commit title says the stand runs on year-old tools. Helm 3.14 is from January 2024, nearly three years old. I grepped the chart's template functions and found none newer than Helm 3.14 (only `dig`, `Files.Glob`, `sha256sum`, `include` and `required`). That is not a run.
- **The documented timeout example has no effect.** `make parity-suite PARITY_SUITE_TIMEOUT=5h30m`, run as written, still has the Job's `activeDeadlineSeconds: 900` (`values.yaml:99`). That value is set at `parity-harness`, so Kubernetes stops the Job at 15 minutes. Item 3 has the details.
- Every hunk matches a sentence of the commit message.

## Item 3: boundaries, partitions, and the negative control
**The replaced mechanism (`run-suite`).** Old code: `kubectl wait --for=create --timeout=2m && <90-try loop>; logs -f; wait helm`. New code: the loop, then on failure print, kill helm and `exit 1`.

| Fault | Old | New |
| --- | --- | --- |
| `ErrImageNeverPull`: the Pod exists and its container is waiting; each `logs` call fails at once | about 3 min of polling, then waits for helm, about 15 min | about 3 min, prints the message and the Pod listing (as claimed) |
| The Job exists but has no Pod (the API refuses the Pod: a bad override in `TEST_STAND_HELM_ARGS`, a missing ServiceAccount, a quota); each attempt waits 20s | 90 × 22s ≈ 33 min | the same 33 min. Helm's 15m timeout runs out partway through, and the loop does not notice. Then it prints "did not start within 3 minutes", "No resources found", and `kill: … No such process`. |
| `helm test` fails at once, for example `make e2e-suite` without the harness, so the release is not found | 2 min (`wait --for=create`), then the `logs -f` NotFound error, then helm's error | about 3 min, then "The runtime-suite container did not start within 3 minutes:", which misstates the cause |

I ran the second fault at 1/100 scale with stub `kubectl`, `helm` and `sleep` binaries. The output matched the table: helm's timeout error came first, then the "within 3 minutes" message, the `kill` error and `make: *** Error 1`. In CI, the job's `timeout-minutes: 30` kills it first.

- **Substantive.**
  - The three-minute bound counts sleeps, not elapsed time.
  - The loop never checks whether `helm test` is still running.
  - On the second and third faults the target fails later than the commit says, or prints a wrong cause.

  Request: one deadline on the whole loop, last attempt included (for example `--pod-running-timeout=2s` on the probe plus a `$SECONDS` check), and `kill -0 $helm_pid || break` so a helm that has already exited ends the wait. Then a run of the no-Pod fault and the no-release fault, stating how long each took and what it printed.

**Other limits on the suite run:**

| Limit | Where it is set |
| --- | --- |
| The 3-minute start poll | Fixed in `Makefile:113` (90 tries). Each try is bounded by kubectl's 20s default. |
| `helm test --timeout` | `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT`, default 15m (`Makefile:54-55`) |
| `suite.activeDeadlineSeconds` | 900 (`values.yaml:99`), applied at harness time |
| The CI job | 30 min (`integration-tests.yaml:120`, `:168`), which also covers the image, harness (up to 10m) and install (up to 10m) steps. This was already there and nothing in this commit makes it worse. |

- **Substantive:** raising `PARITY_SUITE_TIMEOUT` alone past 900s does nothing, because the Job's deadline fires first. The troubleshooting row's example does exactly that. Request: make the example raise both, for example `make parity-harness TEST_STAND_HELM_ARGS='--set suite.activeDeadlineSeconds=19800'` and then `make parity-suite PARITY_SUITE_TIMEOUT=5h30m`. Better still, work one value out from the other.

**Values users already pass.** `TAG` and `IMAGE_PULL_POLICY` are read by both the stand and the product charts, and they are now kept apart. A value meant for the stand that users passed through `E2E_HELM_ARGS` is now dropped without a warning; the commit's "User-visible" section says so. No finding.

**State left by an earlier build.** No user files exist, so the rendered realm and `checksum/realms` do not change. No finding.

## Item 3a: level, placement, and the environment
(Analogue: where each rule lives and which gate runs it.)

The jq merge can be checked in one process. No test covers it, only the build's own `jq -e` uniqueness checks; my local run stands in for one. That is taste: there is no shell-test harness here to put it next to.

The `run-suite` behavior only shows up against a cluster. The CI kind jobs run only the success path, so no job runs the failure path. That is folded into Item 3.

## Item 4: names by content, not by position
None. I checked the changed lines: the troubleshooting rows, the README paragraphs and the Makefile comments. "Earlier releases" names a version range, not a position.

## Item 5: the failure report
(Analogue: what the target prints when it fails.)

The new message plus `get pods -o wide` is good on `ErrImageNeverPull`. On the two faults in Item 3 it names the wrong cause; that is filed there. The `ErrImageNeverPull` troubleshooting row (`docs/local-integration-tests.md:192`) matches what the Pod listing shows.

## Item 6: what the writer says it verified
The commit states no run of:
- the fault on the new loop;
- an old kubectl, Helm 3.14, Helm 4.0–4.2 or Docker 23;
- the Dockerfile's sort or space handling.

## Item 7: siblings of the change
- **`TEST_STAND_HELM_ARGS` (a new member of the overrides).** I searched for `E2E_HELM_ARGS` together with `KIND_CLUSTER`. Only `test/k8s/README.md` lists the overrides, and it now names the new variable and the suite timeouts. `docs/local-integration-tests.md` mentions the timeouts in a troubleshooting row, as comment 2 asked.
- **The two suite targets.** Both use `run-suite`, so the Item 3 finding applies to both.
- **Component count.** The words "both" and "two" for docker-dev-config components are gone. "The two services" in `README.md:60` and `:67` is correct. The vague "the test images" is filed under Item 1.
- **Troubleshooting rows.**
  - The ownership row now names a step for both `e2e` and `parity`.
  - The new 15-minute row names both targets and both variables.
  - The `ErrImageNeverPull` row's fix, `make e2e-images`, serves both paths.
- **Keycloak 26.3.5 elsewhere.** It remains only in the chart (`values.yaml:21`) and in `test/BASELINE.md:24`, which both describe the stand. Neither is a sibling of the SVT revert.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| The three-minute bound counts sleeps, not elapsed time. A Job with no Pod costs 20s per attempt, so `make e2e-suite`/`parity-suite` take about 33 min and then say "within 3 minutes". | Substantive | `Makefile:113` (and the comment at `:104-107`) | One deadline on the whole loop: a short `--pod-running-timeout` on the probe plus an elapsed-time check. Run the no-Pod fault and state the duration and output. |
| The loop ignores a `helm test` that has already exited. A missing release takes 3 min instead of 2, prints "container did not start", and `kill` errors. | Substantive | `Makefile:113-118` | `kill -0 $helm_pid \|\| break` in the loop, and on that path print helm's failure, not the start message. Run `make e2e-suite` with no harness installed. |
| The version table and "any kubectl" have never been run: CI pins Helm 4.3.1 and recent Docker and kubectl. | Substantive | `docs/local-integration-tests.md:35-42` | A CI or local run on Helm 3.14, a Helm 4.0–4.2 release, Docker 23 and kubectl 1.30 or older. Or state only the versions that ran. |
| `make parity-suite PARITY_SUITE_TIMEOUT=5h30m` alone has no effect: the Job's 900s `activeDeadlineSeconds`, set at harness time, ends it first. | Substantive | `docs/local-integration-tests.md:196` | Make the example raise both (`TEST_STAND_HELM_ARGS='--set suite.activeDeadlineSeconds=…'` at `parity-harness`), or work one value out from the other. |
| "with the test images" reads as every test image, but CI builds only pip-stub and parity-suite. | Substantive | `README.md:59` | Name the two images, as line 67 does. |
| The jq merge has no test of its own; only the build's uniqueness checks and this review's local run cover it. | Taste | `build/authz-agent-transfer/Dockerfile:43-45` | Optional: state the two-file run in the PR description. |

I did not check the English style of the changed text beyond what makes a sentence wrong, did not run any suite, cluster, Docker build or SVT run, and checked the kubectl behavior only against the v0.35.0 source.

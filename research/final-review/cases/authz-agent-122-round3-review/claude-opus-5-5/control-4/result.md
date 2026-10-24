I've finished the review; here is the report.

# Final review: `5dcb6be..f3b64e0`, "test(k8s): run the test stand on year-old tools, and stop a suite that never starts"

**Previous report:** I wasn't given one, so this report has no table of earlier findings.

**Inputs:**
- I read the whole diff (8 files), the commit message, and the six PR comments.
- I loaded `test-authoring` and `english-developer-style` from the given skills directory.
- `comment-drift.py 5dcb6be HEAD` printed nothing. The change touches only the Makefile, a Dockerfile, Markdown, and Compose YAML, none of which the script parses. So item 1 uses the §2a analogue for the pages and a manual read for the Makefile and Dockerfile comments.

## Item 1: comments consistent with the code and with each other

1. **`Makefile:104-105`, "`kubectl logs` fails until the Job exists and its container has started, so the loop polls for up to three minutes."**
   - Three minutes holds only while each `kubectl logs job/…` returns at once.
   - When the Job exists but has no Pod, each call waits `--pod-running-timeout` (20s by default). `kubectl logs --help` says the flag waits "until at least one pod is running", and kubectl's `GetFirstPod` watches until a Pod is added. A Pod can be missing because of a FailedCreate under the restricted Pod Security admission the previous commit added, a ResourceQuota, or a missing ServiceAccount.
   - 90 iterations then take about 90 × 22s ≈ 33 minutes. That is past `helm test`'s 15m and the CI job's 30m.
   - Details are under item 3.
2. **The `E2E_HELM_ARGS`/`TEST_STAND_HELM_ARGS` comment (`Makefile:46-49`)** matches both installs and `test/k8s/README.md:67-69`.
3. **The Dockerfile comment** ("The build fails if a user is declared twice") is still true.
4. **The chart README's Helm 4.3 sentence** agrees with `docs/local-integration-tests.md` ("helm 3.14 or later; Helm 4 works too").
5. **No comment narrates the change.**

## Item 2: claimed cases covered

There are no tests in this repository for Makefile targets. The runs that cover them are CI's `kind-e2e`, `kind-parity` and `chart` jobs (Helm v4.3.1, the `ubuntu-latest` Docker).

| Claimed case (source) | Covered by |
| --- | --- |
| Inline 1: Helm 4.3+ prints nothing; 4.0–4.2 and Helm 3 fail with `unable to get pod logs` | `helm-templates/authz-test-stand/README.md:61-62`, as the reviewer stated it. Nothing in the repository runs `helm test --logs`. |
| Inline 2: `E2E_SUITE_TIMEOUT`/`PARITY_SUITE_TIMEOUT` listed with the overrides, and named in the docs page | `test/k8s/README.md:69-70`; `docs/local-integration-tests.md:196` (troubleshooting row only) |
| Inline 3: the `exists and cannot be imported` remedy names `make parity` | `docs/local-integration-tests.md:193`. `e2e-down` deletes the whole kind cluster, so both namespaces go. |
| General 1: `run-suite` works on kubectl older than 1.31 | `kubectl wait --for=create` is removed (`Makefile:113-114`). Nothing runs an old kubectl: **none**. |
| General 2: a suite Pod that never starts fails after about 3 min | `Makefile:114-119`. No run of this path is stated: **none**. It holds for `ErrImageNeverPull` (a Pod exists, so `logs` fails fast) but not when no Pod exists (item 3). |
| General 3: user files merged in sorted order; a file name with a space survives | `Dockerfile:43-45`. The repository has no user files (`testdata/realm/` holds only `README.md`), so CI's `make test-stand-files` covers only the empty case. I ran the pipeline locally (jq 1.8.2, macOS `sort`) on no files, three files in two directories (one with a space in its name), and an empty file. The output was sorted, the spaced name survived, and the empty case matched the old output. Alpine's BusyBox `sort -z`/`xargs -0 -r` was not run. |
| General 4: `E2E_HELM_ARGS` no longer reaches the stand; `TEST_STAND_HELM_ARGS` does | `Makefile:93,164`. The stand's values files already set `TAG: ci` and `IMAGE_PULL_POLICY: Never`, so the CI behavior is unchanged. |
| General 5: SVT Keycloak back on 26.0 | `docker-compose.yml:3` restores exactly the line from before 8b85515 (`git log -p`), so no SVT run is owed. |
| General 6: the README and the publication-task doc no longer count the components as two | `README.md:59-61`; `.github/docs-for-publication-task.md:77`. A grep for `both/two/three` in both files finds nothing else. |
| Commit message: Docker 23.0 and Helm 3.14 named as the minimum versions | `docs/local-integration-tests.md:35-41`. Only Helm 4.3.1 and the runner's current Docker run: **none** (findings below). |

**Commands the change documents:**

1. **`make parity-suite PARITY_SUITE_TIMEOUT=5h30m`** (`docs/…:196`) promises the suite outlives 15 minutes. No run uses this form: **none**.
   - The outcome depends on `suite.activeDeadlineSeconds` (900 by default), which `make parity-harness` writes into the hook Job. The suite run doesn't change it.
   - Run alone as shown, the command still ends at 15 minutes, because Kubernetes stops the Job at its deadline.
   - In CI, the job's `timeout-minutes: 30` caps the run as well.
2. **The Docker row** says "23.0 or later, where BuildKit is the default builder", and its Check column is `docker info`.
   - The targets need BuildKit for `docker build --output type=local` (`test-stand-files`) and for `COPY --chmod` (all six images).
   - On Docker 23.0, `docker build` uses BuildKit only when the buildx component is installed. Without it, the CLI falls back to the legacy builder, which rejects both.
   - `docker info` doesn't show whether buildx is there; `docker buildx version` does. No CI job runs 23.0: **none**.
3. **The Helm row**, "3.14 or later". Every Helm in CI is v4.3.1: **none**.
   - The outcome depends on how `helm upgrade --install --wait` judges readiness (Helm 3's legacy waiter against Helm 4's kstatus watcher) and on how `helm test` waits on a Job hook.
   - Nothing in the templates needs 3.14: the functions used are `include`, `nindent`, `required`, `fail`, `sha256sum`, `dig` and `.Files.Glob`.
   - The commit title says "run the test stand on year-old tools", but the message reports no such run.

**Every hunk is claimed:** each of the 8 files maps to a sentence of the commit message or to a comment.

## Item 3: boundaries, partitions, and the negative control

**Partitions of the new start check (`Makefile:113-119`):**

1. **A Pod exists but its container is waiting** (`ErrImageNeverPull`). Each `kubectl logs` fails fast, so the loop ends after about 90 × (2s + call time), roughly 3–3.5 minutes. The commit says "about"; the printed message says "within 3 minutes". This works as claimed.
2. **The Job exists and has no Pod** (FailedCreate). Each call waits 20s, so the loop takes about 33 minutes. `helm test` times out at 15m and CI kills the job at 30m before the message prints. Even if it printed, `get pods -l job-name=…` would show "No resources found" and not the Job's FailedCreate event. **Substantive.**
3. **`helm test` exits at once** (for example, `make e2e-suite` before `e2e-harness`: `release: not found`). The loop still runs about 3 minutes. It then prints "The runtime-suite container did not start within 3 minutes:", which is false here. `kill` hits a dead pid. The base waited 2 minutes too, but it didn't print a wrong cause. **Substantive.**
4. **Control:** the normal case, where the Pod starts within the loop, runs in CI `kind-e2e` and `kind-parity`.

**Limits on the same work (one suite run, counted from `make e2e-suite`):**

| Limit | Where it is set | Default |
| --- | --- | --- |
| Start loop | Fixed in `run-suite` (90 iterations) | About 3 min, or about 33 min when no Pod exists |
| `helm test --timeout` | Documented setting `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT` | 15m |
| `activeDeadlineSeconds` | Chart values, applied at harness time; now settable through `TEST_STAND_HELM_ARGS` | 900s |
| CI job | `timeout-minutes: 30` in `integration-tests.yaml` | 30m (the image build, harness and install also run inside it) |

1. **The deadline caps the timeout setting.** Raising the timeout past 15m has no effect unless the harness is rerun with a higher deadline. The documented example raises only the timeout.
2. **CI caps both.** The 30-minute job limit caps both settings; neither page says so.
3. **At the defaults, helm reports first.** The timeout and the deadline are equal, and `helm test` starts before the Job does. So helm's timeout fires before the Job's `DeadlineExceeded`, and the outer report hides the inner one. This predates the commit.

**Values users already pass:** `E2E_HELM_ARGS` now reaches only the product charts, and both have a `values.schema.json` with `additionalProperties: true`. A stand key someone passes there (say `--set suite.activeDeadlineSeconds=…`) is now silently ignored rather than rejected. The PR isn't merged, so no existing user depends on the old route. No finding.

## Item 3a: level, placement, and the environment

These are Makefile and Dockerfile changes, so no in-process test applies.

- CI `chart` runs `make test-stand-files`, which builds the changed Dockerfile stage, but only with zero user files.
- `kind-e2e` and `kind-parity` run the changed `run-suite` on the happy path.

None of the failure paths run anywhere (item 2). No CI job is missing a target it should run. Nothing to report beyond items 2 and 3.

## Item 4: names by content, not by position

None. I checked the new message text, the Makefile comments, the table rows and the commit message. "then the three" in `test/k8s/README.md:64` is unchanged and names the three targets just before it.

## Item 5: the failure report

The new failure prints the Pod listing, which shows `ErrImageNeverPull` or `Pending`. In the no-Pod partition the listing is empty and the cause sits in the Job's events, so the report points at nothing (part of finding 1). The new message `The <job> container did not start within 3 minutes:` appears in no troubleshooting row. The `ErrImageNeverPull` row covers its usual cause without quoting it (taste).

## Item 6: what the writer says it verified

The commit message states no run:
- no `make e2e` or `make parity` with Helm 3.14 or Docker 23.0;
- no run of the not-started path;
- no build of the chart-files stage with user files present.

The title's "run the test stand on year-old tools" reads as if one happened. I ran none of these myself, as the form directs; my local jq run only checks the pipeline's logic.

## Item 7: siblings of the change

1. **Shared code covers both targets.** `run-suite` is shared, so the e2e and parity suites both get the fix.
2. **No other site needs the same fix.** `--for=create` and `$(find …` have no other sites in the repository.
3. **Other places that describe `e2e-suite`/`parity-suite`** say only "fails if the Job did not complete" or "its log is streamed" (`docs/…:109`, `test/k8s/README.md:59`, `test/parity/README.md:41`). They don't mention the new early stop (taste).
4. **The new variable is listed everywhere the others are.** `TEST_STAND_HELM_ARGS` is listed beside `E2E_HELM_ARGS` in the only page that lists overrides (`test/k8s/README.md`); the docs page lists none.
5. **No stale count of the components.** The values comments in `helm-templates/authz-agent/values.yaml:8-9` and `helm-templates/authz-policy-admin/values.yaml:8-9` say "both list", but that counts two config files, not components, so they're correct.
6. **"Test images" overstates the list.** In `README.md:59`, "the test images" covers two of the four test images (`pip-stub`, `parity-suite`). The release paragraph names them precisely (taste).

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | With a Job that has no Pod (FailedCreate, for example under restricted Pod Security admission), each `kubectl logs job/…` waits `--pod-running-timeout` (20s). The loop then takes about 33 min instead of 3, past helm's 15m and CI's 30m, and the Pod listing it prints is empty. The comment's "up to three minutes" is false for this case. | Substantive | `Makefile:104-105`, `113-117` | Pass `--pod-running-timeout=1s` on the polling call, or bound the loop by wall clock. On failure also print `get job` / `get events` for the Job. Run the path once with a Pod that cannot be created. |
| 2 | When `helm test` exits at once (release missing), the loop still waits about 3 min, then prints "container did not start", which is false for that case. | Substantive | `Makefile:113-117` | Leave the loop when `kill -0 $$helm_pid` fails, then `wait` for helm's status and skip the message. |
| 3 | The example `make parity-suite PARITY_SUITE_TIMEOUT=5h30m` has no effect alone: `activeDeadlineSeconds: 900`, set at harness time, ends the Job at 15m, and CI's 30-minute job limit caps both settings. | Substantive | `docs/local-integration-tests.md:196`; `Makefile:52-53` | Show the pair: `make parity-harness TEST_STAND_HELM_ARGS='--set suite.activeDeadlineSeconds=19800'`, then the suite run. Name the CI `timeout-minutes` beside the variables. |
| 4 | The Docker row names 23.0 and checks with `docker info`. On 23.0 without the buildx component, `docker build` falls back to the legacy builder, which rejects `--output type=local` and `COPY --chmod`. No run on 23.0. | Substantive | `docs/local-integration-tests.md:35` | Name the buildx component and check it with `docker buildx version`. Report a run on 23.0, or name the version that ran. |
| 5 | "helm 3.14 or later" has no run behind it; CI runs only v4.3.1. Helm 3's `--wait` and `helm test`-on-Job handling differ from Helm 4's, and the title implies a run the message doesn't report. | Substantive | `docs/local-integration-tests.md:38`; commit title | Run `make e2e` and `make parity` with Helm 3.14 and state it in the message, or name only the versions that ran. |
| 6 | The chart-files merge (sort, NUL, spaces) runs in CI only with zero user files; BusyBox `sort -z`/`xargs -0 -r` in `alpine:3.22` is unrun. | Taste | `build/authz-agent-transfer/Dockerfile:43-45` | One local build with two user files, one with a space in its name, mentioned in the message. |
| 7 | The new message isn't in the troubleshooting table, and the target tables don't mention the early stop. | Taste | `docs/local-integration-tests.md:109,192`; `test/k8s/README.md:59` | Quote the message in the `ErrImageNeverPull` row. |
| 8 | "the test images" reads as all of them, but the list carries two of four. | Taste | `README.md:59` | "the test stand's images", as the release paragraph says. |
| 9 | The new README line is 152 characters where the file wraps at 120 (lint allows 400). | Taste | `helm-templates/authz-test-stand/README.md:62` | Rewrap. |

**Not checked:**
- **Nothing was run on a cluster:** no `make e2e`, `make parity` or kind run (there is no cluster).
- **Not run on the stated versions:** Helm 3.14, Docker 23.0, and BusyBox `sort`/`xargs`.
- **Not run against kubectl:** the 20-second wait in finding 1 comes from kubectl's help text and source, not from a run.
- **No style pass:** I didn't review the prose for style alone.

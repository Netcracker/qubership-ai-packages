# Final review: `58316ca..HEAD` (four commits)

The change moves the kind harnesses onto a new test-stand chart, adds a default route to pip-stub, runs the stand under the restricted Pod Security Standard, and makes the suite wait configurable. I found 15 substantive findings. The most important: raising the two new timeouts can't let a suite outlast 15 minutes, because `-test.timeout 600s` in `suite.args` ends the test binary at 10 minutes.

**Inputs.** There was no task statement, so item 2 takes its claimed cases from the four commit messages and the test comments alone. There is no previous report. `comment-drift.py` exited 0 with no output: it only parses `.java`, `.kt`, `.groovy` and `.scala`, and this change is Go, YAML, Helm templates, a Makefile and Markdown. I read the Go members and comments by hand. The skills loaded were `test-authoring` (with `references/go/testing.md`) and `english-developer-style`.

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:35-36`.** "answers every request whose path has no route of its own, in sequence like any other route" reads as if each path had its own sequence. The code keeps one counter under `*`, shared by every unrouted path. `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` expects `/a, /b, /a` to get 503, 200, 200. A reader of the package comment would expect `/b` to start at 503.
- **`main.go:34-35` and `:122-123`.** Both say the default route answers a request "whose path has no route of its own". They leave out the case this change added: a path whose route has no responses also falls through to the default route (`main.go:236`). The commit message and the first test's comment both state that case.
- **`main.go:37-38`.** "…answers an unrouted request 404, as it did before the default route existed" describes the change rather than the code (taste).
- **`docs/local-integration-tests.md:104`.** The `e2e-harness` row says the install covers "…and the suite Job; waits until they are Ready". That is false: the Job is a `helm.sh/hook: test` and only `helm test` creates it. `test/k8s/README.md` says so ("installing the stand does not start it"), and its own `e2e-harness` row leaves the Job out.
- **`test/parity/README.md:115`.** This unchanged line still says the harness under `test/k8s/parity/` holds "the manifests". The change deleted all of them; the directory now holds `idp-seed/` and three values files.
- **`helm-templates/authz-test-stand/values.yaml:9-11`.** The list of images that take `TAG` is "pip-stub, authz-parity-suite, and tenant-manager". It leaves out the runtime-suite image, which `test/k8s/test-stand-values.yaml` sets as `suite.imageRepository` and which takes `TAG` too.
- **`templates/suite.yaml:12-13`, and step 3 of the chart README.** "keeps it afterwards so its log stays readable" is false on one outcome: when `activeDeadlineSeconds` fires, the Job controller deletes the Pods still running. After that, `kubectl logs job/parity-suite` has no Pod to read. This is filed with the limits finding under item 3.

## Item 2: claimed cases covered

**Commit 9d25da7 (pip-stub).** All tests are in `test/integration/pipstub/main_test.go`.

| Claimed case | Test |
| --- | --- |
| `*` answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths`, case "an unrouted path gets the default answer" |
| A routed path keeps its own answer | same test, case "a routed path keeps its own answer" |
| A route with no responses falls through to the default route | case "a routed path with no responses gets the default answer" |
| …or to 404 when there is no default route | **none**: there is no routed-empty, no-default case (see item 3) |
| A stub not configured with `*` answers 404 as before (control) | case "an unrouted path without a default route is 404" |
| Sequence and clamp | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the request target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| "`/pip-stub/configure` now takes the path `*`" | **none**. Every test writes `routes[defaultRoute]` directly and never calls `handleConfigure`. No test reads the record through `/pip-stub/calls`, so the JSON key `requestUri`, which the claim names, is never asserted. |

**Commit 8b85515 (test-stand chart).**
- **Keycloak, stubs, tenant-manager, Secret, suite hook, the two values files and the make targets:** CI covers these through `kind-e2e` and `kind-parity` (Helm 4.3.1 only), plus `helm lint` on both values files.
- **"restarting when one changes":** no assertion anywhere. I checked by hand with `helm template` on a scratch copy: changing one realm file's content changed `checksum/realms`.
- **"each off by default":** no assertion. By hand, `helm template` with no values renders nothing.
- **"merges the user files … fills in the profile fields", with the duplicate-username and duplicate-id checks:** no test. `test/parity/suite/testdata/realm/` holds only a README, so no build has ever run `profile.jq` or the uniqueness checks on a user. `find users -name '*.json'` is empty, so the `jq` merge runs over the parity realm alone.
- **The release publishes three more images:** this is configuration only. The dev-build config builds them, but nothing checks what the transfer image contains.

**Commit 17b17fc (restricted Pod Security Standard).**
- **"the stand could [now] start in a namespace that enforces the restricted Pod Security Standard":** no test or run. No harness labels its namespace `pod-security.kubernetes.io/enforce=restricted`, so the kind jobs pass whatever the Pod Security admission would decide.
- **The OpenShift SCC claim:** no run (out of scope offline).
- **The rendered security contexts, the `/tmp` emptyDir, the labels and the `app:` selectors:** I checked them by hand with `helm template`. All four Pods have `runAsNonRoot` and the `RuntimeDefault` seccomp profile, and the suite mounts `/tmp` with a 256Mi `sizeLimit`. No render assertion exists (item 3a).

**Commit 5dcb6be (suite timeouts and run notes).**
- **`E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` set the wait:** CI runs only the 15m default. The headline claim, "let a suite outlast 15 minutes", fails (item 3, limits).
- **What Helm 4.3.1 and 3.22.1 do with `helm test --logs`:** no CI job runs either. The commit quotes the output, so a run is implied but not recorded.
- **The `make e2e-down` remedy:** no run from the old state is stated. The commit quotes the error, so the failure was seen; running the remedy itself was not stated.

**Commands in the changed files.**

| Command | Promised outcome | What runs it |
| --- | --- | --- |
| `make test-stand-files` | `files/` generated | the CI `chart` job |
| `make e2e`, `make parity` and their steps | stand up, suite passes | the `kind-e2e` and `kind-parity` jobs |
| Chart README step 1 (`docker create` / `docker cp` / `docker rm`) | `./charts` holds three charts | none |
| Chart README step 2 (`helm upgrade --install … --set TAG=<version>`) | stand installed from published images | none |
| Chart README step 3 (`helm test --timeout 15m`, then `kubectl logs job/parity-suite`) | exit code, then the log | none |
| docs subset recipe (`helm upgrade --reuse-values --set suite.env.RUNTIME_SUITE_RUN=…`, then `make e2e-suite`) | a filtered run | none |
| troubleshooting `make e2e-down`, then `make e2e` | clean install | none |

Where each `none` depends on something:
- **Step 1:** the image is `FROM scratch` with no CMD. `docker create` does not execute `true`, so the command is plausible but was never run.
- **Step 3:** the outcome depends on the suite Pod still existing. On a failure by `activeDeadlineSeconds` it does not; on an exit at `-test.timeout`, or a pass, it does. The Makefile form streams with `logs -f` while the test runs, so it does not show this.
- **Subset recipe:** it depends on `--reuse-values` keeping `TAG` and `BASE_URL` from the last harness install, and on Kubernetes expanding `$(RUNTIME_SUITE_RUN)` in `args`. The regex value contains `$/`, which Kubernetes does not expand. Plausible, never run.

**Hunks no commit sentence claims.**
- `test/k8s/parity/idp-seed/parity-realm.json` gains 318 lines: roles `ROLE_MT_READER` and `ROLE_MT_ADMIN`, clients `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a`, and users `parity-r29-scope`, `parity-r30-scope`, `mt-a` and `mt-a-admin`. The message claims only "a second tenant realm, parity-mt-b". No suite case references any of these.
- `test/svt/common/compose/docker-compose.yml` moves Keycloak from `26.0` to `26.3.5@sha256:…`.
- `test/k8s/authn/REALM-DESCRIPTION.md` changes the issuer to `/auth/realms/…`. This corrects a stale doc, since the old manifest already set `/auth`, but no sentence claims it.

## Item 3: boundaries, partitions, and the negative control

**Go partitions.** The negative control (no `*`, so 404) is present, as are the empty default route, the clamp, and an encoded path. One partition is missing: a routed path with no responses and no default route, which should get 404. This is the exact input that indexed at −1 before the change. The suite reaches that branch only through combinations of other cases.

**Values users already pass.** `E2E_HELM_ARGS` now reaches the test-stand install (`Makefile:90`, `:155`). The keys the test-stand chart shares with the agent and policy-admin charts are `TAG` and `IMAGE_PULL_POLICY`.
- A user who passes `--set TAG=<x>` to test another agent build now also asks for `local/pip-stub:<x>`, `local/tenant-manager:<x>` and `local/authz-runtime-suite:<x>`. `e2e-images` never builds those tags, and with `IMAGE_PULL_POLICY: Never` the result is `ErrImageNeverPull` and a 10-minute `--wait` timeout.
- `--set IMAGE_PULL_POLICY=Always` makes the stand try to pull `local/*` from a registry.

Only the documented example, `IMAGE_PULL_POLICY=Never`, means the same thing in both places.

**Replaced mechanisms.**
- **`e2e-harness` / `parity-harness`.** Before, there was a `rollout status` per part: 2m for each stub and the tenant-manager, 10m for Keycloak. Now one `helm --wait --timeout 10m` covers everything. On a missing stub image (`ErrImageNeverPull`, the fault the troubleshooting table names), the old harness failed at about 2m and named the Deployment; the new one fails at 10m. What Helm 4 prints on that timeout was not shown. No sentence accepts the later failure.
- **`e2e-suite` / `parity-suite`.** Before, a 3m wait for the Pod to be Ready failed with "timed out waiting for the condition on pods/…". Now, on a suite image that can't start:
  - `wait --for=create` succeeds at once;
  - the log poll runs 90 × 2s, about 3 minutes, plus the time of each `kubectl logs` call, which has no `--request-timeout`;
  - `logs -f` fails, and the recipe ignores its exit;
  - the recipe then waits on `helm test` until the 900s `activeDeadlineSeconds` or the 15m `--timeout`, whichever fires first.

  That is about 15 minutes against about 3. The new form prints a Job deadline or timeout message and nothing about the image. No sentence accepts this.

**Limits on the suite run (the claim of 5dcb6be).** Innermost first:

| Limit | Value | Where it is set |
| --- | --- | --- |
| `-test.timeout` | 600s | `suite.args`: chart default `values.yaml`; runtime-suite `test/k8s/test-stand-values.yaml`; parity relies on the chart default |
| `activeDeadlineSeconds` | 900 | `values.yaml:99` |
| `helm test --timeout` | 15m | `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT`, `Makefile:51-52` |
| CI job `timeout-minutes` | 30 | `kind-e2e` and `kind-parity`; covers the image builds, the 10m harness wait, two 5m installs, and the suite |

- Raising `E2E_SUITE_TIMEOUT` and `suite.activeDeadlineSeconds` to 20m, as the `Makefile:49-50` comment and the chart README advise, changes nothing: the test binary panics at 10 minutes. The suite cannot outlast 10 minutes, let alone 15.
- In CI, the 30-minute job limit also fires before a raised suite timeout.
- At the defaults, the worst case is 10 + 5 + 5 + 15 minutes, which is already more than 30 before the image builds, so the job limit can fire before `helm test` reports.
- Once someone raises `-test.timeout` past `activeDeadlineSeconds`, the deadline deletes the running Pod. README step 3's `kubectl logs` then reads nothing, contradicting `suite.yaml:13`.

**Pre-existing state.** The change documents state left by an older `make e2e` (the ownership error, and `make e2e-down`, which removes both namespaces). No run from that state is recorded. An old `runtime-suite` Job created with `kubectl apply` is removed by the `delete job` in `run-suite`, which handles it.

## Item 3a: level, placement, and the environment

- **Go tests:** these are at the smallest level, in-process with `httptest`. They sit beside the existing `TestHandlePIP_*` tests and share `resetState`. That matches what `test-authoring` §3 and §9 ask for.
- **Chart:** the repository has render assertions in `test/scripts/test-chart-render.sh` for the agent and policy-admin charts, including `runAsNonRoot` and `RuntimeDefault`. The new chart has none. Every claim of 17b17fc, plus the checksum restart, the off-by-default parts and the `fail` messages for missing `files/`, can be seen with `helm template` offline. CI runs only `helm lint`, which checks none of them.
- **Restricted PSS:** this can only be checked across the API-server boundary. The kind jobs could check it by labeling the namespace `enforce=restricted`, and they don't.

## Item 4: names by content, not by position

- `helm-templates/authz-test-stand/values.yaml:10-11`: "Keycloak has its own image and pull policy below" could name `idp.image` and `idp.imagePullPolicy` (taste).
- Elsewhere: none. I checked the test names, case names, README step numbers and table rows.

## Item 5: the failure report

None. Every new assertion is a comparison whose `t.Errorf` or `t.Fatalf` prints the operands and the expected values. The case ids are descriptive names, and no message repeats the test's name.

## Item 6: what the writer says it verified

- No commit states a red run on the base commit or a mutation verdict for the three new Go tests.
- 5dcb6be quotes Helm 4.3.1 and 3.22.1 output and the ownership-metadata error, which implies those runs happened, but none is recorded with its command.
- No run of the restricted PSS, the realm-change restart, or `profile.jq` on a user is stated.
- For consistency only: `go test ./pipstub/` passes at HEAD, and `helm lint` passes with both values files on a scratch copy whose `files/` I filled by hand.

## Item 7: siblings of the change

- **`docs/local-integration-tests.md:190`.** The symptom names `make e2e-harness` or `make parity-harness`, but the action says only "then `make e2e`". A parity user needs `make parity`.
- **The set of overrides.** `test/k8s/README.md:66-71` lists `KIND_CLUSTER`, `E2E_NAMESPACE`, `PARITY_NAMESPACE`, `E2E_ARTIFACTS`, `E2E_HELM_ARGS`, `E2E_BASE_URL` and `PARITY_AC_BASE_URL`. It does not name `E2E_SUITE_TIMEOUT` or `PARITY_SUITE_TIMEOUT`, and neither does `docs/local-integration-tests.md`.
- **`kubectl wait --for=create` (`Makefile:108`).** This needs kubectl 1.31 or later. The prerequisites table (`docs/local-integration-tests.md:37`) names no minimum version. With an older kubectl, the `&&` chain skips the poll, `logs -f` fails, and the streamed log is lost; the pass or fail result is unaffected.
- **pip-stub's other users:** `entitlements-mock`, `pip-mock` and the Compose stacks never configure `*`, so the control case covers them. No other site has the defect.

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The suite timeouts can't let a suite outlast 15 minutes: `-test.timeout 600s` fires first, and in CI the 30-minute job limit does too | substantive | `Makefile:47-52`; `values.yaml:91-99`; `test/k8s/test-stand-values.yaml:52-58`; `integration-tests.yaml:120,168` | Derive `-test.timeout` from `activeDeadlineSeconds` (or the reverse) and say so in the Makefile comment and the README; account for the 30-minute job limit |
| 2 | The suite now fails about 12 minutes later on an image or start fault, and prints less (≈15m against 3m) | substantive | `Makefile:105-111` | A deadline on the log wait at the old 3m that also fails the target, or a sentence accepting the later failure, with a run of that fault |
| 3 | One 10m `--wait` replaces the 2m-per-stub waits; a missing stub image fails at 10m | substantive | `Makefile:90,155` | Accept it in a sentence, or keep per-part waits; show a run with a missing stub image |
| 4 | `E2E_HELM_ARGS` now reaches the test stand, where `TAG` and `IMAGE_PULL_POLICY` ask for images nothing builds | substantive | `Makefile:90,155` | A separate `E2E_TEST_STAND_HELM_ARGS`, or keep `E2E_HELM_ARGS` to the product charts |
| 5 | Package doc says "in sequence like any other route"; the sequence is shared across unrouted paths | substantive | `test/integration/pipstub/main.go:35-36` | State that every unrouted path draws from one sequence |
| 6 | The default-route comments omit the routed-but-empty fall-through | substantive | `main.go:34-35,122-123` | Add "or whose route has no responses" |
| 7 | The docs `e2e-harness` row says the install creates the suite Job and waits for it | substantive | `docs/local-integration-tests.md:104` | Drop the suite Job from that row |
| 8 | Stale "the manifests" in the parity README | substantive | `test/parity/README.md:115` | Name what the directory holds now |
| 9 | The `TAG` image list leaves out the runtime-suite image | substantive | `helm-templates/authz-test-stand/values.yaml:9-11` | Add it |
| 10 | No test goes through `handleConfigure` with `*`, or reads `requestUri` through `/pip-stub/calls` | substantive | `main_test.go:225-286` | One test that configures `*` over HTTP and reads the JSON record back |
| 11 | Missing partition: a routed path with no responses and no default route gets 404 | substantive | `main_test.go:232-241` | Add that case |
| 12 | No render assertions for the new chart's claims (PSS contexts, labels, checksum restart, off by default) | substantive | `test/scripts/test-chart-render.sh` | Add test-stand render assertions beside the existing ones |
| 13 | The restricted-PSS claim is never exercised | substantive | `Makefile:90,155` | Label the kind namespaces `pod-security.kubernetes.io/enforce=restricted` before install, or record a run |
| 14 | `profile.jq` and the user-uniqueness checks have never run on any input | substantive | `build/authz-agent-transfer/Dockerfile:39-46`; `profile.jq` | A fixture user (and a duplicate) run through the `chart-files` stage, or a jq-level test |
| 15 | Hunks no commit message claims: the parity-realm additions, the SVT Keycloak bump, and the REALM-DESCRIPTION issuer fix | substantive | `parity-realm.json`; `test/svt/common/compose/docker-compose.yml:3`; `REALM-DESCRIPTION.md` | A sentence for each in a commit message, or move them to their own change |
| 16 | The troubleshooting action names only `make e2e` for a symptom that includes `parity-harness` | substantive | `docs/local-integration-tests.md:190` | "then `make e2e` or `make parity`" |
| 17 | The new suite-timeout variables are missing from the overrides list | substantive | `test/k8s/README.md:66-71` | Add `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` |
| 18 | `kubectl wait --for=create` needs kubectl 1.31 or later; the prerequisites don't say so | substantive | `docs/local-integration-tests.md:37` | State the minimum version |
| 19 | No red run or mutation verdict is stated for the new Go tests | substantive | commit 9d25da7 | State the red run on the base commit |
| 20 | Narration: "as it did before the default route existed" | taste | `main.go:37-38` | Drop the clause |
| 21 | Position reference: "pull policy below" | taste | `values.yaml:10-11` | Name `idp.image` and `idp.imagePullPolicy` |

This review didn't run anything on a cluster, so the Helm 3 and 4 claims, the timeout faults and the PSS admission are argued from the code, not observed. It didn't run Docker or `make test-stand-files`, and it didn't check the prose for style alone.

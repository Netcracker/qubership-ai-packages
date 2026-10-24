# Final review: `58316ca..5dcb6be` (four commits)

There was no task statement, so the claimed cases come from the four commit messages and the comments in the changed files. No earlier report of this form exists, so there is no table of earlier findings.

**Inputs.** `comment-drift.py` exited 0 with no output. It only parses `.java`, `.kt`, `.kts`, `.groovy` and `.scala` files (`EXT`, line 29), and this change has none. I checked the Go comments, the Helm templates, the Makefile, the Dockerfile and the Markdown by hand. I loaded `test-authoring` (with `references/go/testing.md` as the engine reference) and `english-developer-style`. No `godoc-authoring` skill was provided, so I judged the Go comments against item 1 only.

**What I ran.** `go test ./...` in `test/integration/pipstub` passed. I copied the chart to the scratchpad and generated its `files/` with the same `jq` steps as the `chart-files` Dockerfile stage. On that copy:
- `helm lint` (Helm v4.3.0) passed with both values files.
- `helm template` rendered the documented subset override correctly.
- The `checksum/realms` annotation changes when a realm file's content changes.
- `profile.jq` and the duplicate-user check behave as their comments say, on hand-made inputs.

## Item 1: comments consistent with the code and with each other

Two findings.

- **`test/integration/pipstub/main.go:33-38` and `:122-123`.** Both comments say the default route answers "every request whose path has no route of its own". The code at `handlePIP` also sends a path whose route has an empty `Responses` list to the default route (`if !ok || len(route.Responses) == 0`). The commit message and the test comment at `main_test.go:502` both state this. A reader of the package comment would expect such a path to get 404.
- **`main.go:37-38`.** "as it did before the default route existed" describes the change rather than the code, outside a regression test's comment. (The older "behaviour is exactly as before" at line 31-32 is the same pattern, but it predates this change.)

Everything else I checked matches the code:
- `callRecord.RequestURI`
- the `helpers.go` `LoadConfig` comment
- the `testify/Dockerfile` comment
- the `test/k8s/values.yaml` comment
- `_helpers.tpl`, and the comments in `suite.yaml` and `idp.yaml`
- the Makefile comments on `run-suite`, `e2e-harness`, `parity-harness` and `e2e-restart`
- the `docker-release.yaml` header

Contradictions between docs are listed under item 7.

## Item 2: claimed cases covered

| Claimed case (commit) | Covered by |
| --- | --- |
| `*` is the default route for unrouted paths (9d25da7) | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/"an unrouted path gets the default answer"` |
| A routed path keeps its own answer | the same test, `"a routed path keeps its own answer"` |
| A stub not configured with `*` answers 404 | `"an unrouted path without a default route is 404"`, `"…with an empty default route is 404"` |
| A route with no responses falls through to the default route | `"a routed path with no responses gets the default answer"` |
| …**or to 404** (the base commit indexed at -1 here) | **none**: no row has a routed path with empty responses *and* no default route |
| `/pip-stub/configure` takes `*` | **none**: every test writes `routes[defaultRoute]` directly. `handleConfigure` is never called |
| The sequence is shared across paths and clamped | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths`. It would fail if the counter were keyed per path |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| The chart's parts are off by default; Keycloak imports at every start and restarts on a changed realm | **none in the repository** (my scratch render confirms the checksum) |
| pip-stub instances, the tenant-manager emulator, the M2M Secret, and the suite as a `helm test` hook | CI jobs `kind-e2e` and `kind-parity` (`make e2e-harness`, `e2e-suite`, and the parity equivalents) |
| `make test-stand-files` runs the `chart-files` stage | CI job `chart`, step "Generate the test-stand files" |
| The stage fills in profile fields for user files; the build fails on a duplicate user or id | **none**: `testdata/realm/` holds no `*.json`, so the merge runs on an empty set. I ran both by hand and they work |
| The transfer image carries three charts | CI dev build through `docker-dev-config.json`. Nothing checks what the image contains |
| The parity stand gains `parity-mt-b` | No case uses it yet |
| The release publishes three more images | `.qubership/docker.cfg`. The release workflow was not run here |
| The stand starts under the restricted Pod Security Standard (17b17fc) | **none**: no namespace is labelled to enforce it, and `test/scripts/test-chart-render.sh` does not cover this chart |
| Read-only root filesystem except Keycloak; `/tmp` emptyDir for the suite; no `runAsUser`; `app.kubernetes.io/*` labels; selectors keep `app` | **none** as assertions. The CI kind jobs start the Pods, which covers the read-only root filesystem at run time |
| `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` set the wait (5dcb6be) | CI runs only the defaults. See item 3 for why raising them has no effect |
| Helm 4.3.1 skips `--logs` for a Job; Helm 3.22.1 fails | The commit reports these as observations. CI pins Helm v4.3.1 and runs the README's replacement form through `run-suite` |

**Commands the change tells someone to run.**
- `make test-stand-files`: run by the CI `chart` job.
- The Dockerfile header's `docker build … -f build/authz-agent-transfer/Dockerfile .`: run by the dev build, with the same file and context.
- The chart README's `helm test … --timeout 15m` followed by `kubectl logs job/<suite.name>`: run in the same form by `run-suite` on Helm 4.3.1.
- The chart README's `docker create … true` / `docker cp` / `docker rm`: **none**. The image is `FROM scratch`, but `docker create` never runs the command, so the outcome does not depend on it. No finding.
- The chart README's `helm upgrade --install … --set TAG=<version> -f my-test-stand-values.yaml` on a stand outside kind: **none**. The outcome depends on the published `qubership-authz-pip-stub` and `qubership-authz-parity-suite` images existing under that tag. The commit itself says the e2e stand runs on kind only. I'd accept this as unrun, but the description should say so.
- `docs/local-integration-tests.md`'s `helm upgrade --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false`: **none**. Rendered with `helm template` 4.3.0, the values reach the Job env and the `$(RUNTIME_SUITE_RUN)` argument. No finding.
- The troubleshooting remedy `make e2e-down` then `make e2e`: **none** on the inherited state. The remedy deletes the cluster, so its effect is not in doubt. The row itself has a finding under item 7.

**Hunks no sentence claims (a finding):**
- `test/k8s/parity/idp-seed/parity-realm.json` gains 318 lines: roles `ROLE_MT_READER` and `ROLE_MT_ADMIN`, clients `parity-m2m-tenant-a/b/unknown/empty` and `parity-end-user-tenant-a`, users `parity-r29-scope`, `parity-r30-scope`, `mt-a`, `mt-a-admin`, and more. The commit only says the stand "gains a second tenant realm, parity-mt-b". No case in `test/parity` uses them.
- `test/svt/common/compose/docker-compose.yml` moves Keycloak from `26.0` to `26.3.5@sha256:…`.
- `.github/docker-dev-config.json` adds three images to the CI dev build. The commit names only `.qubership/docker.cfg`.
- `test/k8s/authn/REALM-DESCRIPTION.md` corrects the issuer to `/auth`. This is a fix to an existing doc error, since the old `keycloak.yaml` already set `/auth`.

## Item 3: boundaries, partitions, and the negative control

**pip-stub.** The control "a stub without `*` answers 404" is present and holds on the base commit. One partition is missing: a routed path with an empty response list and no default route (`→ 404`). That is exactly the input that indexed at -1 on the base commit. With rules loaded (`PIP_STUB_CONFIG` set), a matching rule takes precedence, but that code did not change, so no case is owed there.

**Inherited state.** The documented remedy is `make e2e-down`, which deletes the cluster. `run-suite` also deletes a leftover `kubectl apply` Job before `helm test`. No finding beyond item 7's row.

**Values users already pass (finding).** `E2E_HELM_ARGS` now also reaches the test-stand install (`Makefile:90`, `:155`). Two names are read by both the old consumers and the new one: `TAG` and `IMAGE_PULL_POLICY`.
- `--set TAG=<x>`, meant to choose the agent image, now also asks for `local/pip-stub:<x>`, `local/tenant-manager:<x>` and `local/authz-runtime-suite:<x>`. `e2e-images` never builds those, so `--wait` runs out after 10 minutes.
- `--set IMAGE_PULL_POLICY=Always` makes the stand try to pull `local/*:ci` from a registry.
- The documented example, `IMAGE_PULL_POLICY=Never`, means the same thing in all three charts.

**Replaced mechanism (finding).** On the documented fault, the suite image missing from the node (`ErrImageNeverPull`, a troubleshooting row):
- **Old `e2e-suite`:** `wait --for=condition=Ready pod … --timeout=3m` failed after about 3 minutes and printed `timed out waiting for the condition on pods/runtime-suite-…`.
- **New `run-suite` (`Makefile:105-111`):**
  1. `wait --for=create` returns at once.
  2. The `kubectl logs` loop polls silently, with stderr sent to `/dev/null`: 90 rounds of a 2-second sleep plus the call, at least 3 minutes.
  3. `logs -f` prints one `waiting to start` error.
  4. `wait $helm_pid` then blocks until `helm test --timeout 15m` returns, or until the Job's `activeDeadlineSeconds: 900` fails it.

  The run fails after about 15 minutes instead of 3, and no sentence in the change accepts that. The longest single attempt is a `kubectl logs` call. It has no `--request-timeout`, so I count it as never returning on a hung API server, with no bound over the whole loop.

**Limits on the suite's run (finding).** The limits, inner to outer:
- `-test.timeout 600s` in `suite.args` (`values.yaml:95-96`, `test/k8s/test-stand-values.yaml:55-56`)
- `suite.activeDeadlineSeconds: 900` (`values.yaml:99`)
- `helm test --timeout $(E2E_SUITE_TIMEOUT)`, 15 minutes (`Makefile:51-52`)
- CI `timeout-minutes: 30` per kind job, which starts earlier because it also covers the image build, the harness and the installs

At the defaults the innermost limit fires first, which is correct. But raise `E2E_SUITE_TIMEOUT` and `activeDeadlineSeconds` past 15 minutes, as the `Makefile:49-50` comment and the chart README's last paragraph say, and `-test.timeout 600s` still stops the suite at 10 minutes. The commit's headline case therefore has no effect unless `suite.args` changes too, and no comment says so. In addition, `run-suite` asks for a timeout "no shorter than" `activeDeadlineSeconds`. Helm's clock starts before the Pod is scheduled and its image pulled, so at equal values `helm test` fires first while the Job is still running. That is the very symptom 5dcb6be describes. In CI, a raise past about 15 minutes runs into the 30-minute job limit.

## Item 3a: level, placement, and the environment

The pip-stub tests are small, in-process, in `main_test.go` next to the existing `TestHandlePIP_*` tests, and they use `resetState`. They are correctly placed.

The chart has a smaller level than kind that would show its claims: `test/scripts/test-chart-render.sh`, which CI already runs for the other two charts. The test-stand chart has no render assertions there for:
- the security contexts
- the read-only root filesystem except Keycloak
- the `/tmp` emptyDir
- the labels and the `app` selectors
- the realm checksum
- the `fail` messages when files are missing

The restricted Pod Security Standard is only enforced across the cluster boundary. No harness namespace carries `pod-security.kubernetes.io/enforce=restricted`, so CI never tests that claim. **Finding.**

## Item 4: names by content, not by position

None. The test and case names describe their content. The counts in the prose are correct: "the three charts" in the transfer image, "the two stubs", "the two tenant realms" from `authn/`.

## Item 5: the failure report

None. The Go tests use `t.Errorf` and `t.Fatalf` with got before want and both operands printed. The table cases are named by condition. `reflect.DeepEqual` is wrapped with a message that prints both slices.

## Item 6: what the writer says it verified

The commits state no evidence that the tests can fail: no red run of the new pip-stub tests on `58316ca`, and no mutation verdict. They also state no kind run under the new security contexts (read-only root filesystem on `qubership-core-base` images) and no run of a raised `E2E_SUITE_TIMEOUT`. The only reported observations are the Helm 4.3.1 and 3.22.1 behaviors in 5dcb6be.

## Item 7: siblings of the change

- **`README.md:59`** still reads "CI builds both via `.github/docker-dev-config.json`". That file now lists five images.
- **`test/k8s/README.md:66-69`** lists the overridable Makefile variables (`KIND_CLUSTER`, `E2E_NAMESPACE`, `PARITY_NAMESPACE`, `E2E_ARTIFACTS`, `E2E_HELM_ARGS`, `E2E_BASE_URL`, `PARITY_AC_BASE_URL`) without the new `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`.
- **`docs/local-integration-tests.md:104`** says `e2e-harness` installs "…and the suite Job; waits until they are Ready". The Job is a `helm test` hook that the install does not create, as `test/k8s/README.md` says ("installing the stand does not start it"), so the two pages contradict each other.
- **`docs/local-integration-tests.md:190`**: the symptom names `make e2e-harness` and `make parity-harness`, but the action ends with `make e2e` only. A parity user needs `make parity`.
- **`configure` and `counters`**: `handleConfigure` does not reset `counters`, so reconfiguring `*` continues the old sequence. This holds for every route and predates the change, so it is not a finding here.

## Findings

| # | Finding | Label | File:line | Requested change |
| --- | --- | --- | --- | --- |
| 1 | On a missing image, `run-suite` fails after about 15 minutes instead of 3, silently until the end, with no overall deadline on the log-polling loop | Substantive | `Makefile:105-111` | Run that fault and give both durations and outputs; bound the wait at the old 3 minutes (for example, stop when the Pod reports `ErrImageNeverPull`) or say in the description that the later failure is accepted |
| 2 | `-test.timeout 600s` fires before the raised `E2E_SUITE_TIMEOUT` and `activeDeadlineSeconds`; an equal `helm test` timeout fires before the Job's deadline | Substantive | `Makefile:49-52`, `:103-104`; chart `README.md:69-70`; `values.yaml:92-99` | Derive one limit from the other (for example, `-test.timeout` from `activeDeadlineSeconds`), name all three in the comment and the README, and make the helm timeout longer than the deadline by the Pod's start time |
| 3 | `E2E_HELM_ARGS` now reaches the test stand, where `TAG` and `IMAGE_PULL_POLICY` mean something else | Substantive | `Makefile:46-48`, `:90`, `:155` | Give the stand its own variable (for example, `TEST_STAND_HELM_ARGS`), or a run with `--set TAG=…` |
| 4 | Hunks no commit claims: `parity-realm.json` gains clients, users and roles; SVT Keycloak bump; dev-config images; `REALM-DESCRIPTION` issuer fix | Substantive | `test/k8s/parity/idp-seed/parity-realm.json`; `test/svt/common/compose/docker-compose.yml:3`; `.github/docker-dev-config.json` | A commit sentence for each, with its check, or move them to their own change |
| 5 | The restricted Pod Security Standard, the read-only root filesystem, labels and selectors are not asserted | Substantive | `test/scripts/test-chart-render.sh`; `Makefile:90` | Render assertions for the test-stand chart, and label the kind namespaces `enforce=restricted` |
| 6 | Profile filling and duplicate detection in the `chart-files` stage are untested (the input set is empty) | Substantive | `build/authz-agent-transfer/Dockerfile:338-352`; `profile.jq` | A CI check on a sample user file, and one on a duplicate |
| 7 | No pip-stub case for a routed path with empty responses and no default route; none through `handleConfigure` with `*` | Substantive | `test/integration/pipstub/main_test.go:508-523` | Add the row `→ 404`; add a case that POSTs `[{"path":"*",…}]` to `handleConfigure` |
| 8 | pip-stub comments leave out the empty-route fallthrough and describe history ("as it did before…") | Substantive | `main.go:33-38`, `:122-123` | Add the empty-route case to both comments; drop the history clause |
| 9 | The local-tests doc says `e2e-harness` installs the suite Job and waits for it | Substantive | `docs/local-integration-tests.md:104` | Drop "the suite Job" from the row, as `test/k8s/README.md` does |
| 10 | The troubleshooting action names `make e2e` for a `parity-harness` symptom | Substantive | `docs/local-integration-tests.md:190` | "…then `make e2e` or `make parity`" |
| 11 | "CI builds both" is stale; the variable list lacks the two new timeouts | Substantive | `README.md:59`; `test/k8s/README.md:66-69` | Update the count; add both variables |
| 12 | No red run or mutation verdict; no stated kind run under the new security contexts | Substantive | commit messages | State the red run of the new tests on `58316ca` and the kind CI results |
| 13 | "No request path is *, so it never shadows a real route": the real reason is that routes are looked up before `*` | Taste | `main.go:36` | Say the default route is consulted only after the path's own route |
| 14 | The README generalizes "Helm 4" and "Helm 3" from the two versions the commit observed (4.3.1, 3.22.1) | Taste | chart `README.md:61-62` | Name the versions observed |

I did not run the kind suites, the release workflow, `docker build` (no network pulls), or Helm 3. The drift script parses no language this change uses, so I checked comment drift by hand. I did not do a style-only pass over the prose.

# Final review: `58316ca..HEAD` (three commits)

There was no task statement, so the claimed cases come from the three commit messages and the comments above the new tests. The drift script printed nothing because it parses only Java, Kotlin, Groovy, and Scala. I compared the Go comments with the code by hand. There is no previous report of this form, so there is no table of earlier findings.

What I ran, all outside the repository: I copied the chart into the scratchpad and built its `files/` by hand, because `make test-stand-files` would write into the checkout. On that copy I ran `helm lint` and `helm template` with both values files and with `--set TAG=1.2.3`. I ran `go test` on `test/integration/pipstub`, which passes, and I ran the jq merge in `profile.jq` on a sample user file.

## Item 1: comments consistent with the code and with each other

- **`docs/local-integration-tests.md`, row `e2e-harness`.** It says the target installs "the client-credentials Secret, and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` (`suite.yaml:21`), so installing the release does not create it. `test/k8s/README.md` says so correctly ("installing the stand does not start it"), so the two pages contradict each other. A reader looking for the Job after `e2e-harness` will not find it.
- **`test/integration/pipstub/main.go:37-38`.** "…answers an unrouted request 404, as it did before the default route existed" describes the history of the change in a package comment. Lines 31-32 already do the same ("exactly as before"), so this is taste.
- **Checked with no finding:** the package comment on precedence (lines 29-36), the comments on `defaultRoute` and `callRecord.RequestURI`, the helper comments in `_helpers.tpl`, the comments in the chart templates and values, and the comment changes in `helpers.go` and the testify `Dockerfile`. All match the code. "No request path is `*`" holds: `ServeMux` answers a request target of `*` with 400 before `handlePIP` sees it.

## Item 2: claimed cases covered

Cases claimed by commit 9d25da7 (pip-stub):

| Claimed case | Test |
| --- | --- |
| An unrouted path gets the default route's answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer (the control) | `…/a_routed_path_keeps_its_own_answer` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| A stub with no default route answers an unrouted path 404 | `…/an_unrouted_path_without_a_default_route_is_404` |
| A route with no responses with no default route answers 404, which is the `-1` index the message names | **none**. The table's "empty default route" row sends an unrouted path, which answered 404 on the base commit too. No row sends `/routed` with `[]pipResponse{}` and no default route, which is the input that panicked on the base commit. |
| The default route serves its responses in sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the request target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| `/pip-stub/configure` takes the path `*` | **none** through `handleConfigure`. Every test writes `routes[defaultRoute]` directly. The configure code did not change, so this is taste. |

Cases claimed by commits 8b85515 and 17b17fc (the chart):

| Claimed case | What covers it |
| --- | --- |
| The chart renders and lints with both values files | CI: `helm lint` on both values files after `make test-stand-files`. I also ran it. |
| e2e and parity harnesses on the chart | CI jobs `kind-e2e` and `kind-parity` |
| The stand starts in a namespace that enforces the restricted Pod Security Standard | **none**. The harness namespaces come from `--create-namespace` with no `pod-security.kubernetes.io/enforce` label, and `git grep pod-security` finds nothing. The claim depends on what the admission controller checks: `runAsNonRoot`, seccomp, capabilities, privilege escalation, and volume types. I read the rendered output and see nothing it would reject, but no run proves it. |
| OpenShift's restricted SCC can assign a uid | none; there is no OpenShift run. This is a design note, not a claim the change can test. |
| Profile fill and duplicate check in `profile.jq` | **none** in the repository. `test/parity/suite/testdata/realm/` contains only `README.md`, so `find` returns nothing and CI never runs `profile` or the user part of the uniqueness check. My jq 1.8.2 run on a sample file produced `R29LevelM2M` and rejected a duplicate `parity-reader`, so it works today, but nothing will catch a regression. |

Command lines the change asks people to run:

| Command | Promised outcome | What runs it |
| --- | --- | --- |
| `make test-stand-files`, `make e2e-harness`, `make e2e-suite`, `make parity-harness`, `make parity-suite` | The stand is installed; the suite runs and its log streams | CI jobs `kind-e2e` and `kind-parity` |
| `helm lint helm-templates/authz-test-stand -f …` (both values files) | Lint passes | CI job `chart` |
| `helm … upgrade authz-test-stand … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string suite.env.FULL_RUNTIME_SUITE=false`, then `make e2e-suite` (`docs/local-integration-tests.md`) | A subset of the suite runs | **none** |
| `helm upgrade --install authz-test-stand ./charts/authz-test-stand --set TAG=<version> -f my-test-stand-values.yaml` (chart README) | The stand installs on a cluster that is not kind | **none** |
| `helm test authz-test-stand --timeout 15m --logs` (chart README) | The suite runs, its log prints, and the exit code is non-zero on failure | **none**. The Makefile runs `helm test` without `--logs`. |
| `docker create` / `docker cp` from the transfer image (chart README) | The charts are copied out of the image | **none** |

For the `none` rows:

- The `--reuse-values` recipe depends on Helm merging `--set` into the stored values, and CI pins Helm v4.3.1. Rendering the chart with `--set suite.env.RUNTIME_SUITE_RUN=…` gives the expected env entry, but `--reuse-values` needs a release, and nothing has run the recipe on Helm 4.
- The transfer-image commands depend on published images that do not exist until a release.
- `--logs` in Helm 4.3 prints the Pod logs once the test is complete. I did not verify that on a Job hook.

Hunks no sentence of a commit message claims:

- **`test/svt/common/compose/docker-compose.yml`:** Keycloak in the SVT compose stack moves from `26.0` to `26.3.5@sha256:…`. That is a version bump in a stack the change does not otherwise touch, and no SVT run is mentioned.
- **`test/k8s/parity/idp-seed/parity-realm.json` (+318 lines):** new clients `parity-m2m-tenant-a`, `-b`, `-unknown`, `-empty`, and `parity-end-user-tenant-a`; users `parity-r29-scope`, `parity-r30-scope`, `mt-a`, and `mt-a-admin`; roles `ROLE_MT_READER` and `ROLE_MT_ADMIN`. The message says only "The parity realm gains a second tenant realm, parity-mt-b". `git grep` finds no case in the change that uses any of them.
- **`.github/docker-dev-config.json`:** three new dev builds. The message names only `.qubership/docker.cfg`.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub.** The table has a control ("a routed path keeps its own answer"). The empty-responses partition is covered only when a default route exists; the boundary case that names the fix, an empty route with no default, is missing (see item 2). The sequence test covers clamping to the last response.
- **State left by the earlier version.** A namespace where the earlier `make e2e-harness` or `make parity-harness` ran still holds the objects `kubectl apply` created: `deploy/keycloak` or `deploy/idp`, `pip-stub`, `pip-mock`, `entitlements-mock`, `tenant-manager`, the Secret `authz-agent-client-credentials`, and the ServiceAccount `runtime-suite`. None carries Helm ownership metadata, so `helm upgrade --install authz-test-stand` stops with "exists and cannot be imported into the current release: invalid ownership metadata". CI always starts from a fresh kind cluster, and no page names the remedy (`make e2e-down`, or deleting the namespace) for a cluster set up before this change.
- **Values that `E2E_HELM_ARGS` now passes to the test stand.** The Makefile now hands `E2E_HELM_ARGS` to the test-stand install as well (`Makefile:86,150`). Two key names are shared with the product charts:
  - `IMAGE_PULL_POLICY` (the documented example) means the same thing in all three charts.
  - `TAG` is the agent's and policy-admin's image tag in the product charts. In the test stand it tags `local/pip-stub`, `local/authz-runtime-suite`, and `local/tenant-manager`. `helm template … --set TAG=1.2.3` renders `image: local/pip-stub:1.2.3`, and `make e2e-images` builds no such image. With `IMAGE_PULL_POLICY: Never`, `--wait` then runs to its 10-minute timeout.
- **Replaced mechanism: harness wait.**
  - Old: `rollout status` with `--timeout=2m` per stub and 10m for Keycloak.
  - New: one `helm --wait --timeout 10m`.
  - A missing stub image (`ErrImageNeverPull`) used to fail after 2 minutes, naming the Deployment. Now it fails after 10 minutes with Helm's status summary.
- **Replaced mechanism: suite.**
  - Old: `kubectl wait --for=condition=Ready pod … --timeout=3m`.
  - New: `helm test --timeout 15m` in the background, plus `wait --for=create` (2m), plus up to 90 × (one `kubectl logs` + 2 s) before `logs -f`, then `wait $helm_pid`.
  - A missing suite image used to fail after 3 minutes. Now Helm waits for the Job until its 15-minute timeout, and `activeDeadlineSeconds: 900` fails the Job at about the same moment.
  - Nothing in the commit message accepts either slowdown. I did not run either fault.
- **Limits on the suite run:**
  - `-test.timeout 600s` in `suite.args`, set in the values;
  - `suite.activeDeadlineSeconds: 900`, set in the values;
  - `helm test --timeout 15m`, fixed in the Makefile `run-suite` and in the chart README.

  At the defaults the innermost limit, 600 s, fires first, which is correct. But Helm's 15-minute clock starts before the Job exists, so raising `activeDeadlineSeconds` above 900 has no effect: `helm test` gives up first. The Helm timeout should be derived from `activeDeadlineSeconds`, or the values comment should say the value is capped at 15 minutes.

## Item 3a: level, placement, and the environment

- The pip-stub behavior is observable in one process, and the new tests drive `handlePIP` through `httptest` (small tests). They sit in the existing `main_test.go` and reuse `resetState`. The `go-build.yaml` matrix runs this directory (line 63), and the tests pass locally.
- The chart's behavior exists only on a cluster. Two partitions have no CI run: the restricted-PSS namespace (item 2) and the inherited state (item 3).
- `test/scripts/test-chart-render.sh` checks the two product charts but has no assertion for the test-stand chart. A render assertion on the security context of every container would be the smaller test for commit 17b17fc.

## Item 4: names by content, not by position

None. The test and subtest names describe the case (`an unrouted path with an empty default route is 404`). "below" in `values.yaml:3` ("own image and pull policy below") and in `test/k8s/README.md` ("The Makefile targets below") points at text a few lines away, which is acceptable.

## Item 5: the failure report

None. Each table row asserts with `t.Errorf("GET %s = %d %s, want %d %s", …)`, which names the input and prints got and want. The sequence test prints `%v` of both slices. The request-target test prints both fields and both wanted values. Its `t.Fatalf` on `len(calls)` guards the dereference after it, which is the right place for a hard stop. The compound conditions all print every operand.

## Item 6: what the writer says it verified

Neither the commit messages nor any other text in the change show a red run on the base commit or a mutation verdict. Two pip-stub rows would fail on the base commit: the routed path with no responses panicked at index -1, and the unrouted path with a default route answered 404. That is my reading, not evidence from the writer. Nothing in the change describes running the chart in a namespace that enforces the restricted standard.

## Item 7: siblings of the change

- **`README.md:59`** still says "CI builds both via `.github/docker-dev-config.json`", but that file now lists five images. The paragraph below it was updated, so the count is now wrong.
- **Old file names.** `git grep` for the deleted manifests (`test/k8s/keycloak.yaml`, `runtime-suite-job.yaml`, `pip-mock.yaml`, `keycloak-realms`, `m2m-credentials`, and the rest) finds no reference outside `docs/handovers/done/`.
- **Restart and log targets.** `E2E_LOCAL_DEPLOYMENTS`, `PARITY_LOCAL_DEPLOYMENTS`, `e2e-logs`, and `parity-logs` still name Deployments the chart creates under the same names.
- **Callers of the pip-stub change.**
  - The new `requestUri` field is read only by consumers of `/pip-stub/calls`. `test/parity/suite/pip_control.go:66` mirrors `callRecord`, and nothing in the repository decodes it with `DisallowUnknownFields`, so the additive field is safe.
  - `counters[key]` is used only in `handlePIP`, and `handleReset` clears the `*` counter along with the rest.
- **Read-only root filesystem.** The base image's entrypoint rebuilds the CA store only when certificates are present, as `authz-policy-admin/values.yaml:20-23` explains, so a read-only root is safe for pip-stub and the suites. The parity suite's `writeObservedSidecar` (`compare.go:145`) writes under the image's root-owned `testdata/` and ignores the error, which was true before this change too.

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| The case the fix names, a routed path with no responses and no default route, has no row | Substantive | `test/integration/pipstub/main_test.go:233` | Add the row `/routed` with `[]pipResponse{}` and no default route → 404 |
| `e2e-harness` row says it installs the suite Job and waits for it to be Ready, but the Job is a test hook | Substantive | `docs/local-integration-tests.md`, `e2e-harness` row | Drop "and the suite Job", as `test/k8s/README.md` does |
| `E2E_HELM_ARGS` now reaches the test stand, and `TAG` there selects `local/*` images nothing builds | Substantive | `Makefile:86,150` | Give the test stand its own args variable, or document that `TAG` must not be passed through `E2E_HELM_ARGS` |
| A namespace from the previous kubectl-applied harness makes `helm upgrade --install` fail on ownership metadata, and no page gives the remedy | Substantive | `Makefile:85-86,149-150`; `test/k8s/README.md` | A run over the old harness, or a documented remedy (`make e2e-down` or deleting the namespace) |
| Harness and suite waits fail later on a missing image (2m→10m and 3m→about 15m), and no sentence accepts it | Substantive | `Makefile:86,103-110` | Run that fault on the new targets and state the durations, or bound the waits |
| Raising `suite.activeDeadlineSeconds` past 900 has no effect because `helm test --timeout 15m` is fixed | Substantive | `values.yaml` (`suite.activeDeadlineSeconds`); `Makefile:104`; chart `README.md` | Derive the Helm timeout from the value, or document the cap |
| The restricted-PSS claim has no run or render check | Substantive | `helm-templates/authz-test-stand/templates/_helpers.tpl:19-41` | Label a kind namespace `pod-security.kubernetes.io/enforce=restricted`, or add a render assertion |
| The `profile.jq` merge and the duplicate check never run in CI because no user file exists | Substantive | `build/authz-agent-transfer/Dockerfile:39-44` | A fixture user file the build merges, or a check over a sample |
| `--reuse-values` subset recipe, the transfer-image install, and `helm test --logs` are documented but never run | Substantive | `docs/local-integration-tests.md` (subset bullet); chart `README.md`, install section | Run each once on Helm 4.3 and say so, or align the documented forms with the Makefile |
| Unclaimed hunks: SVT Keycloak bump, new clients, users, and roles in `parity-realm.json`, `docker-dev-config.json` entries | Substantive | `test/svt/common/compose/docker-compose.yml:3`; `test/k8s/parity/idp-seed/parity-realm.json`; `.github/docker-dev-config.json` | A sentence in the message for each, with its run, or move them to their own change |
| README still says CI builds "both" images | Substantive | `README.md:59` | Restate the count or the list |
| The package comment narrates history ("as it did before the default route existed") | Taste | `test/integration/pipstub/main.go:37-38` | State the current behavior only |
| `/pip-stub/configure` with `*` is not tested through the handler | Taste | `test/integration/pipstub/main_test.go` | One test that configures `*` over HTTP |

Not checked: I did not run the kind harnesses or `make test-stand-files`, so I made no Docker builds or cluster runs, and none of the timing or ownership faults above was reproduced. I did not run the drift script on Go, and I did not review the prose for style.

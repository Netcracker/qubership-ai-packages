# Final review of `58316ca..HEAD`

There was no task statement, so the claimed cases in item 2 come from the four commit messages and the test comments alone.

I loaded `final-review`, `test-authoring` (with `references/go/testing.md`) and `english-developer-style`. The drift script ran and printed nothing, because it parses only JVM files (`EXT = (".java", ".kt", …)`). I checked the Go comments by hand instead.

To check the chart I copied it to the scratchpad and generated its `files/` there with `docker build --target chart-files`. Then I ran `helm lint` and `helm template` with both values files on Helm 4.3.0. Both lint cleanly. I also ran `profile.jq` on a fixture of my own. Nothing in the repository was changed.

## Item 1: comments consistent with the code and with each other

**Finding: two Go comments leave out the new empty-route case (`test/integration/pipstub/main.go:34-38` and `:122-123`).** The package comment says the default route "answers every request whose path has no route of its own". The `defaultRoute` comment says the same. But `handlePIP` (`if !ok || len(route.Responses) == 0 { key = defaultRoute …`) also falls back to the default route when a route exists with no responses. The commit message and the test comment state that case. A reader of these two comments would expect a route with no responses to answer 404. Request: add "or whose route has no responses" to both comments.

**Finding: one docs row says the harness installs and waits for the suite Job (`docs/local-integration-tests.md:104`).** The row reads "…the client-credentials Secret, and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` object, so `helm upgrade --install` never creates it. The matching row in `test/k8s/README.md` correctly leaves the Job out. Request: drop "and the suite Job" from that row, or say that only `e2e-suite` creates it.

**Taste: one comment narrates the change (`main.go:37-38`).** It says a stub "answers an unrouted request 404, as it did before the default route existed". That clause describes the change rather than the code. "answers an unrouted request 404" is enough.

I also re-read the other new or changed comments: the chart helpers, values, templates and READMEs; the Makefile define and target comments; `LoadConfig`; the testify `Dockerfile`; `test/k8s/values.yaml`; and the realm docs. Apart from the findings above they match the code. I checked the idp-seed README's claims about `parity-mt-b` and `parity-m2m-tenant-b` against the JSON, and they hold.

## Item 2: claimed cases covered

| Claimed case | Covered by |
| --- | --- |
| `*` answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| A stub with no `*` answers 404 as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| …or to 404 | **none** (see item 3) |
| The default route serves its sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| `/pip-stub/configure` takes the path `*` | none directly; the tests write to `routes` themselves (taste, item 3a) |
| The chart replaces the loose manifests, and both harnesses install it | CI `kind-e2e` and `kind-parity` |
| Every part is off by default | none; `helm template t chart` renders 1 byte in my run |
| The profile fields are filled in, and a duplicate user fails the build | **none**: `testdata/realm/` holds no user file, so this path never runs |
| The stand starts under the restricted Pod Security Standard | **none** |
| All objects carry `app.kubernetes.io/*` and `helm.sh/chart` | none; my render shows them on all 12 objects |
| `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` set the wait | CI at the default 15m only |

Commands the change tells someone to run:

| Command | Outcome it promises | What runs the same form |
| --- | --- | --- |
| `make test-stand-files`, then `helm lint` of the test stand | files generated, lint passes | CI `chart` job |
| `make e2e-harness` / `e2e-suite` / `parity-harness` / `parity-suite` | stand installed, suite runs | CI kind jobs |
| docs subset: `helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false` | a filtered run | none; my `helm template` with the same `--set` flags renders the intended env |
| chart README: `docker create` / `docker cp` / `docker rm`, then `helm upgrade --install … --set TAG=<version>` | charts copied out with `files/` | none; the Dockerfile copies `files/` into `/charts/authz-test-stand/files/`, so no doubt |
| chart README: `helm test authz-test-stand --timeout 15m`, then `kubectl logs job/parity-suite` | prints the suite log | **none** (the Makefile streams with `logs -f` while the Job runs, which is a different form) |
| `make e2e-down` as the remedy for leftover objects | the next install succeeds | none; deleting the cluster leaves no state, so no doubt |

**Finding: the profile fill-in and duplicate check have no test (`build/authz-agent-transfer/Dockerfile:38-53`, `profile.jq`).** These behaviors are claimed, but there is no user file, so no build executes them. My scratchpad run with two files for `parity-r29-level-m2m` produced `R29LevelM2M` and `parity-r29-level-m2m@example.test`, and the username check exited 1. So the code works, but nothing in the repository shows it. Request: a fixture user file (or a CI step that builds the stage with a temporary one), plus a duplicate pair that must fail.

**Finding: the restricted Pod Security Standard claim has no run (`helm-templates/authz-test-stand/README.md:8-11`).** The kind namespaces are created by `--create-namespace` with no `pod-security.kubernetes.io/enforce` label. `test/scripts/test-chart-render.sh` does not render this chart. There is also a second risk. The pip-stub and both suite images keep the base image's entrypoint, which "loads certificates" (`test/integration/tenantmanager/Dockerfile:15-16`), and they now run with a read-only root filesystem. No run is stated for that either. Request: label the namespace `enforce=restricted` in `e2e-harness` and `parity-harness` so CI exercises the claim, and state the green run.

**Finding: the documented log command can print nothing in one case (`helm-templates/authz-test-stand/README.md:61-70`).** When a suite exceeds `activeDeadlineSeconds`, the Job controller ends its running Pod and the Pod is removed. `kubectl logs job/<name>` then has no Pod to read, which is exactly the case the timeout advice in the same section is about. Request: run the documented form on a suite that times out, or say that the log is lost on a deadline and stream it with `-f` while the suite runs.

**Finding: four hunks are not claimed by any commit message:**
- `test/svt/common/compose/docker-compose.yml:3` changes the SVT Keycloak image from `26.0` to `26.3.5@sha256:…`.
- `test/k8s/parity/idp-seed/parity-realm.json` gains 318 lines: the clients `parity-m2m-tenant-a`/`-b`/`-unknown`/`-empty` and `parity-end-user-tenant-a`, the users `mt-a`, `mt-a-admin`, `parity-r29-scope` and `parity-r30-scope`, and two roles. The commit claims only the new `parity-mt-b` realm, and no code uses these entries.
- `.github/docker-dev-config.json` now has CI dev builds produce three more images. The commit claims only the release file `.qubership/docker.cfg`.

Request: add a sentence claiming each hunk, or move it to the change that uses it. Commit 3 already does this for the stub ("The stub instance itself comes with the cases that use it").

## Item 3: boundaries, partitions, and the negative control

**Finding: the regression case of the pipstub fix has no test (`test/integration/pipstub/main_test.go:515-523`).** Before the fix, a route with no responses indexed its sequence at -1. That is a panic on the base commit. The table tests an empty route with a default route, and an empty default route, but not an empty route with no default route, which should now answer 404. Request: add the row `{"a routed path with no responses and no default route is 404", "/routed", []pipResponse{}, nil, 404, …}`. The existing 404-without-default row is the control.

**Finding: the new suite wait fails much later than the old one (`Makefile:199-206`).** The usual fault is the image missing from the node; the docs troubleshooting row for `ErrImageNeverPull` shows this.
- **Old:** `wait --for=condition=Ready pod … --timeout=3m` failed after 3 minutes with kubectl's timeout message.
- **New:** `wait --for=create` succeeds, the log loop polls for about 3 minutes, and `logs -f` fails at once. Then `wait $helm_pid` blocks until `helm test --timeout 15m` or `activeDeadlineSeconds: 900` ends it, about 15 minutes.

The harness wait shows the same pattern: the stubs' `rollout status --timeout=2m` became one `--wait --timeout 10m`. No sentence in the change accepts this. Request: run the missing-image fault on the new target and state both durations and outputs. Then either bound the wait at the old time to fail (for example, end it when the Pod reports `ErrImageNeverPull` or `ImagePullBackOff`) or say why the later failure is acceptable.

**Finding: the new timeout setting cannot take effect past 10 minutes (`Makefile:129-130`, `values.yaml:92-99`, chart `README.md:69-70`).** The comment says a longer suite "raises this together with suite.activeDeadlineSeconds". But `suite.args` still carries `-test.timeout 600s` in `values.yaml` and in `test/k8s/test-stand-values.yaml:55-56`. If someone sets `E2E_SUITE_TIMEOUT=30m` and `activeDeadlineSeconds: 1800` as told, the Go test binary still stops the suite at 10 minutes. At the defaults the inner 600s limit fires first, which is correct. In CI, the job's `timeout-minutes: 30` (`integration-tests.yaml:120,168`) also encloses the wait, after the image build, harness and install time have been spent. Request: have the comment and the chart README name `-test.timeout` in `suite.args` as a third value to raise, or derive it from `activeDeadlineSeconds`. Also note the CI job limit.

**Finding: `E2E_HELM_ARGS` now reaches the test-stand chart, where `TAG` means something else (`Makefile:126-128, 182, 256`).** Both the old charts and the test stand read `TAG` and `IMAGE_PULL_POLICY`.
- `IMAGE_PULL_POLICY` (the documented example) means the same in both.
- `TAG` does not. Passed for the agent, for example `--set TAG=dev`, it makes the stand ask for `local/pip-stub:dev`, `local/tenant-manager:dev` and the suite image under the same tag. `make e2e-images` builds only `:ci`, so those Pods fail with `ErrImageNeverPull`.

Request: give the test-stand install its own variable (for example `TEST_STAND_HELM_ARGS`), or run the target with `--set TAG=<other>` and document the result.

The earlier-version state is covered by the documented `make e2e-down` remedy, and the commit quotes the error it fixes. The test table includes the negative control ("…without a default route is 404").

**Taste:** `kubectl wait --for=create` needs kubectl 1.31 or later. The docs prerequisites name no version, and with an older kubectl the log is not streamed.

## Item 3a: level, placement, and the environment

The pipstub tests are in-process, sit beside the existing `TestHandlePIP_*` tests and reuse `resetState`, and `go-build.yaml:63` runs that module in CI.

**Finding: the chart has no render-level test (`test/scripts/test-chart-render.sh`).** Its security contexts, labels, off-by-default rendering, the `fail` messages for missing files, and the `emptyDir` `sizeLimit` can all be checked with `helm template`, in one process with no cluster. Today they are covered only by the kind jobs, which do not check them. The same script already holds the render assertions for the other two charts, including the image-repository loop at `:439`. Request: add test-stand cases to that script.

**Taste:** one case could go through `handleConfigure` with path `*`, so the configure path the commit names is exercised.

## Item 4: names by content, not by position

none. I checked the test and subtest names, Makefile and template comments, and the README cross-references. The `$(1)`…`$(4)` in the Makefile define are make's own parameter syntax and are documented as such.

## Item 5: the failure report

none. Each new Go assertion prints the function and input with got before want (`GET %s = %d %s, want %d %s`, `statuses of /a, /b, /a = %v, want %v`, `requestUri %q, path %q, want …`). Subtests are named by condition, and `t.Fatalf` is used only before the `calls[0]` index.

## Item 6: what the writer says it verified

- **pipstub commit:** no red run on the base commit is stated. From the code, the routed-path-with-no-responses row would panic on the base, but nobody has shown it.
- **Chart and restricted-PSS commits:** no kind run is stated, and in particular no run under an enforcing namespace.
- **Timeout and README commit:** it quotes Helm 4.3.1's and 3.22.1's `--logs` behavior and the ownership-metadata error, which is evidence for those two claims.

## Item 7: siblings of the change

**Finding: two places still count two images:**
- `README.md:59` says "CI builds both via `.github/docker-dev-config.json`".
- `.github/docs-for-publication-task.md:77` says "the two-entry array".

That file now lists five images. Request: update both counts.

**Finding: the new timeout variables are missing from the override list (`test/k8s/README.md:66-70`).** The paragraph lists `KIND_CLUSTER`, `E2E_NAMESPACE`, `PARITY_NAMESPACE`, `E2E_ARTIFACTS`, `E2E_HELM_ARGS`, `E2E_BASE_URL` and `PARITY_AC_BASE_URL`, but not `E2E_SUITE_TIMEOUT` or `PARITY_SUITE_TIMEOUT`. Request: add them, with how they relate to `activeDeadlineSeconds` and `-test.timeout`.

**Finding: one troubleshooting row gives the e2e remedy for the parity symptom too (`docs/local-integration-tests.md:190`).** The symptom names `make e2e-harness` or `make parity-harness`; the action says "Run `make e2e-down` once, then `make e2e`." For parity, the follow-up step is `make parity`. Request: name both.

Other siblings check out:
- The labels and security-context helpers are used by every object and Pod in all five templates.
- `defaultRoute` and the `counters[key]` change have no other call site; the rule engine and `handleReset` are unaffected.
- `E2E_LOCAL_DEPLOYMENTS` and `PARITY_LOCAL_DEPLOYMENTS` still match the Deployment names the values render.

## Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| The package and `defaultRoute` comments leave out the empty-responses fall-through | Substantive | `test/integration/pipstub/main.go:34`, `:122` | 1 |
| The `e2e-harness` row says the suite Job is installed and awaited | Substantive | `docs/local-integration-tests.md:104` | 1 |
| A comment narrates the change ("as it did before…") | Taste | `test/integration/pipstub/main.go:37` | 1 |
| The profile fill-in and duplicate check have no test or fixture | Substantive | `build/authz-agent-transfer/Dockerfile:38` | 2 |
| The restricted-PSS claim has no run, and the read-only root FS behind the base entrypoint was not shown to run | Substantive | `helm-templates/authz-test-stand/README.md:8` | 2 |
| `kubectl logs job/…` after `helm test` finds no Pod when the deadline is hit | Substantive | `helm-templates/authz-test-stand/README.md:61` | 2 |
| Unclaimed hunks: SVT Keycloak bump, 318 unused lines in the parity realm, dev-config images | Substantive | `test/svt/common/compose/docker-compose.yml:3` | 2 |
| No test for a route with no responses and no default route (404) | Substantive | `test/integration/pipstub/main_test.go:515` | 3 |
| The new suite wait fails about 12 minutes later on a missing image | Substantive | `Makefile:199` | 3 |
| Raising the timeout as documented is capped by `-test.timeout 600s` | Substantive | `Makefile:129` | 3 |
| `E2E_HELM_ARGS` passes `TAG` to the stand, which asks for images nothing builds | Substantive | `Makefile:182` | 3 |
| `kubectl wait --for=create` needs kubectl 1.31 or later | Taste | `Makefile:202` | 3 |
| No render-level test for the test-stand chart | Substantive | `test/scripts/test-chart-render.sh:439` | 3a |
| The configure path for `*` is not exercised | Taste | `test/integration/pipstub/main_test.go:527` | 3a |
| "builds both" and "two-entry array" are stale counts | Substantive | `README.md:59` | 7 |
| The override list omits `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` | Substantive | `test/k8s/README.md:66` | 7 |
| The troubleshooting row names parity in the symptom but only `make e2e` in the action | Substantive | `docs/local-integration-tests.md:190` | 7 |

The drift script does not parse Go, YAML or Makefiles, so I checked item 1 by hand. Without a cluster, the timing and Pod-deletion findings in items 2 and 3 come from reading the code and Kubernetes' documented behavior, not from a run.

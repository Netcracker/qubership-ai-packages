# Final review: `58316ca..HEAD` (3 commits)

**Inputs.** No task statement was handed over, so the claimed cases come from the three commit messages (`git log 58316ca..HEAD`) and the test comments in `test/integration/pipstub/main_test.go`. This is the first review of this change, so there is no previous report to open with. The working tree is unchanged.

**Skills.** I loaded `test-authoring` (its `go/testing.md` and `go/testify.md`). `english-developer-style` is not in the skills directory, so I did not load it and wording was checked only where it changes meaning. No Go doc-comment skill is present either.

**Drift script.** It printed nothing. It parses only Java, Kotlin, Groovy and Scala, and this change touches none of them. I checked the Go, Helm, Makefile, Dockerfile and doc comments by hand.

## 1. Comments consistent with the code and with each other
Finding: `main.go:36` says "No request path is \*". That is false. A Go request `OPTIONS *` has `URL.Path == "*"`; I confirmed this with `httptest.NewRequest`. So an `OPTIONS *` request reaches the default route and consumes its sequence. The stub answers it instead of 404.

Narration: `main.go:37-38` says the 404 is "as it did before the default route existed". That narrates the change, which the form does not allow outside a regression test's comment.

Checked and consistent: the `defaultRoute` const comment, the `RequestURI` field comment, the `suite.args` and `suite.env` pointers in the testify comments, the startup-probe arithmetic (60 × 5 s = five minutes), the "no admin API" note (`admin` is a realm password-grant user, not the admin API), and the `_helpers.tpl` callers.

## 2. Claimed cases covered
- Default route answers unrouted paths: `…/an_unrouted_path_gets_the_default_answer`, and the routed-path and clamping cases.
- Stub with no `*` answers 404: `…/an_unrouted_path_without_a_default_route_is_404`.
- Route with no responses falls through to the default route: `…/a_routed_path_with_no_responses_gets_the_default_answer`.
- Route with no responses falls through to 404: **none** (finding 2).
- `/pip-stub/configure` takes `*`: no test goes through `handleConfigure` (finding 3).
- `requestUri` keeps the target as sent: `TestHandlePIP_RecordsTheRequestTargetAsSent`.
- Chart claims (8b85515, 17b17fc): no Go test. I rendered and linted offline. The security-context claim is checked by reading only (finding 5).

## 3. Boundaries, partitions, and the negative control
The sequence test covers the boundaries (first, second, clamped third). The default-route partitions have a control: the unrouted path without a default route gives 404. The missing cell is the routed-empty, no-default case (finding 2). The `requestUri` test has no control (finding 6).

## 3a. Level, placement, environment
In-process `go test` at the smallest level, in `main_test.go` beside the existing handler tests and using `resetState`. CI runs it through `go-build.yaml`, which covers `test/integration/pipstub`. I ran `GOWORK=off GOPROXY=off go test ./...` in that module: all pass. Both values files pass `helm lint`, `helm template` renders, and the CI chart job runs `make test-stand-files` before linting.

## 4. Names by content
None. The test names are content-based.

## 5. Failure report
None. The `t.Errorf` calls print got before want, and the case names describe content.

## 6. What the writer says it verified
Neither the red run on the base commit nor a mutation verdict is stated in any of the three commit messages. The `-1` index fix (9d25da7) is a regression, so its red run is the evidence the form asks for and it is absent. Not run here, per the form.

## 7. Siblings of the change
- `containerSecurityContext` has five callers with explicit values, and all five containers in the rendered e2e output carry them.
- `podSecurityContext` is set on every Pod.
- The `labels` helper is used by every rendered object (awk check over the e2e render).
- `run-suite` serves both `e2e-suite` and `parity-suite`.
- `handleReset` clears `counters`, including the default-route key.
- Nothing in the repo still references the deleted `test/k8s/*.yaml` manifests, outside the doc in finding 4.
- `callRecord` consumers decode additively; `PipStubCall` mirrors fields as needed by design.

## Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| 1. `OPTIONS *` has path `*`, so "No request path is \*" is false | substantive | `test/integration/pipstub/main.go:36` | Correct the sentence to say `OPTIONS *` reaches the default route. |
| 2. Claimed "route with no responses falls through to 404" has no test | substantive | `test/integration/pipstub/main_test.go:~232-241` (case table) | Add a case: routed `[]pipResponse{}`, no default, expects 404 with `no rule or route for /routed`. |
| 3. Claimed `/pip-stub/configure` takes `*` is never exercised through `handleConfigure` | substantive | `test/integration/pipstub/main_test.go:225-263` | One test that PUTs `[{"path":"*",…}]` through `handleConfigure`, then GETs an unrouted path. |
| 4. Troubleshooting row names `rollout status deploy/keycloak` as the harness timeout; the harness now waits through `helm upgrade --wait` | substantive | `docs/local-integration-tests.md:190` | Name the Helm wait failure instead. |
| 5. Restricted-PSS claim has no test; kind namespaces carry no enforce label | substantive | `test/scripts/test-chart-render.sh` (not changed) or the kind namespace | Add a render assertion for `runAsNonRoot`, `readOnlyRootFilesystem` and `drop: ALL`, or name the gap as follow-up. |
| 6. `requestUri` test has one spelling and no control | taste | `test/integration/pipstub/main_test.go:276-287` | Add the unencoded spelling of the same path and assert the two `requestUri` values differ. |
| 7. "as it did before the default route existed" narrates the change | taste | `test/integration/pipstub/main.go:37-38` | Drop the clause. |

**Not checked:**
- No cluster was available, so nothing was applied or admitted. The Keycloak image's numeric USER, the `kubectl wait --for=create` support in CI's kubectl, and the Keycloak `KC_HTTP_RELATIVE_PATH` management-path claim are unverified.
- The drift script was not run for any member, since no JVM files changed.
- No wording pass was made beyond sense, because the English skill was not provided.

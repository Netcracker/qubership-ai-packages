# Final review: `58316ca..HEAD` (three commits: `8b85515`, `9d25da7`, `17b17fc`)

**Inputs.** There was no separate task statement. The claimed cases come only from the three commit messages and the comments on the tests. Of the three skills, only `final-review` and `test-authoring` exist under the given directory. `english-developer-style` is missing and I loaded no other copy, so no finding cites a style rule. `comment-drift.py` exited 0 with no output, because it parses only Java, Kotlin, Groovy and Scala. I checked comment drift by hand for the Go code, the templates, the Makefile and the docs. `AGENTS.md` has no test-stack line, so I propose one (§0): `Tests: Go testing engine and assertions (test/integration/pipstub, tenantmanager); testify for test/integration/testify`.

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:18-20` and `:34-36`.** The package comment still says "Responses are served sequentially per path (clamped to the last)". The new paragraph says the default route answers "in sequence like any other route". But the default route keeps one counter (`counters["*"]`) shared by every unrouted path. `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` asserts this: `/a`, `/b`, `/a` → 503, 200, 200. A reader of the package comment would expect `/a` and `/b` each to get the first response.
- **`main.go:37-38`.** "…answers an unrouted request 404, as it did before the default route existed" describes the change, in a package comment rather than in a regression test's comment.
- **`docs/local-integration-tests.md:104`.** It says `e2e-harness` installs "…and the suite Job; waits until they are Ready". The Job is a `helm test` hook, so `helm upgrade --install` does not create it. `test/k8s/README.md:53` leaves the Job out of the same row, and `test/k8s/README.md` itself says "installing the stand does not start it".
- **`test/parity/README.md:69-72`.** It says the parity realm "also holds the users of `suite/testdata/realm/`, so the cases that need those users run on the kind harness… their files declare none". That directory holds only `README.md`, and the commit message itself says "none so far". As written, it says such users and cases exist. The Dockerfile comment (`build/authz-agent-transfer/Dockerfile:32`, "if any") is hedged correctly.
- **Taste:**
  - `helm-templates/authz-test-stand/values.yaml:9-11` lists the images that take `TAG` as "pip-stub, authz-parity-suite, and tenant-manager". The e2e stand also runs `local/authz-runtime-suite` under `TAG`.
  - `test/k8s/authn/REALM-DESCRIPTION.md:82` names two of the four e2e realms the chart imports.
- **Checked and consistent:**
  - the `callRecord.RequestURI` and `defaultRoute` doc comments and the `handlePIP` step comment;
  - every comment in `_helpers.tpl`;
  - the Keycloak security-context comment;
  - the hook comment in `suite.yaml`, against helm's `before-hook-creation`;
  - the `run-suite` comment (90 × 2 s is three minutes);
  - the test-stand chart README;
  - `test/k8s/README.md`;
  - the `idp-seed` README, whose claims about the tenant users, the clients and the `tenant-id` values I checked with `jq` against both realm files;
  - the `LoadConfig` comment and the testify Dockerfile comment.
- No reference to a deleted manifest is left outside `docs/handovers`.

## Item 2: claimed cases covered

| Claimed case (source) | Test |
|---|---|
| `*` answers a path with no route (9d25da7) | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| A stub with no `*` answers 404 as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| …"or to 404" for a **routed** path with no responses and no `*` (the old index −1 case) | **none.** `…with_an_empty_default_route_is_404` covers the default route being empty, not a routed path |
| The default route serves its responses in sequence, clamped to the last | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| "`/pip-stub/configure` now takes the path `*`" | **none through `handleConfigure`.** The tests write to `routes[defaultRoute]` directly. Low risk, because `handleConfigure` is unchanged. |
| The stand starts under the `restricted` Pod Security Standard (17b17fc); non-root, RuntimeDefault, drop ALL, no escalation, read-only root filesystem except Keycloak, `/tmp` emptyDir, labels on every object, selectors kept | **none.** I rendered both values files: every Pod and container carries the settings and every object carries the labels. No repository test asserts any of it, and no CI namespace enforces `restricted` (Item 3a). |
| Keycloak writes under `/opt/keycloak`, so it keeps a writable root filesystem | The kind jobs start Keycloak, so they fail if this is replaced by a read-only root filesystem. They also show that the other parts start read-only. |
| Realm files imported at every start; the Pod restarts on change (`checksum/realms`) (8b85515) | none. Only the kind runs show the import. |
| `profile.jq` fills the profile fields; the build fails on a duplicate username or id | **none, and no input exists.** No `*.json` user file is in the repository, so this path never runs. When I ran it by hand, `parity-r29-level-m2m` became `R29LevelM2M`, as the comment says. |
| `parity-mt-b` realm and the `mt-a*` users | Keycloak imports them on kind-parity. No case uses them yet. |
| make targets and `helm test` streaming | kind-e2e and kind-parity jobs |

## Item 3: boundaries, partitions, and the negative control

- **pip-stub.** The partitions that vary are: path routed or not; routed responses empty or not; default route absent, empty, or non-empty. The 404 rows and "keeps its own answer" are controls that also pass on the base commit. Two gaps:
  - **Routed path with empty responses and no default route.** This is the old crash input, and it has no case.
  - **Rule engine with `*` configured.** The package comment puts rules first, then the legacy routes, then the default route. No test configures both a matching rule and `*`. Moving the default-route lookup ahead of `matchRule` would pass the whole suite.
- **Chart.** The `fail` branches (`tenantManager.tenants is required`, missing realm files, missing stub file) and the `sizeLimit` fallback when `suite.resources.limits` is absent have no render case. The values files reach only the non-empty branches.

## Item 3a: level, placement, and the environment

- **pip-stub.** The tests are small and in-process. They sit beside the existing `TestHandlePIP_*` tests, share `resetState`, and the Build workflow runs them (`go-build.yaml:63`). That is right.
- **Chart: substantive.** Pod Security admission is enforced by the API server, so the test of the restricted claim has to cross that boundary. But neither `e2e-harness` nor `parity-harness` labels its namespace `pod-security.kubernetes.io/enforce=restricted`. As a result, a part added later without a security context still passes CI. The agent and policy-admin charts installed into the same namespaces render compliant (`runAsNonRoot`, RuntimeDefault, drop ALL, no escalation), so enforcing the label is feasible.
- **Smaller-level option.** The repository already has an in-process render harness, `test/scripts/test-chart-render.sh`, run in CI after `make test-stand-files`, but it has no case for `authz-test-stand`. It would be the place to assert the security contexts, the labels, the checksum annotation, and the `fail` branches.

## Item 4: names by content, not by position

none. I scanned every added line for ordinals and position words. The ones that occur ("a second stub instance", "own image and pull policy below", "`$(1)` is kubectl…") either name their subject or are make's positional parameters. The subtest names describe the condition.

## Item 5: the failure report

none.
- `if status != tc.wantStatus || body != tc.wantBody` prints all four operands, got before want, together with the method and path.
- The sequence test uses `reflect.DeepEqual` and prints got and want.
- The `requestUri`/`path` check prints both got values and both want values.
- `t.Fatalf` is used only before indexing `calls[0]`.
- Subtests are named by condition.

## Item 6: what the writer says it verified

None of the three commit messages states a red run on the base commit or a mutation verdict, and none states a kind run for either chart commit. I did not supply that evidence myself. As a consistency check, `go test ./...` in `test/integration/pipstub` passes. `helm lint` passes, and `helm template` renders both values files; I ran both on a scratch copy of the chart with placeholder `files/`.

## Item 7: siblings of the change

- **`handlePIP` routing.** Its only other caller is the parity suite's `PipController`.
  - `ResetPinnedRoutes` (`test/parity/suite/pip_control.go:184`) "unregisters" a path by configuring a 404 response. The path keeps a route of its own, so the new `*` route will never answer it.
  - The fix this change makes possible is to configure `Responses: []`, which now falls through. Today nothing uses `*`, because the commit defers the stub instance, so this is a follow-up to name rather than a live defect.
- **`callRecord`.**
  - The mirror `PipStubCall` (`pip_control.go:72`) has no `RequestURI`. Its comment says fields are added as needed, which matches the stated deferral.
  - The testify readers decode without `DisallowUnknownFields`.
- **`authz-test-stand.containerSecurityContext` / `podSecurityContext`.** All five workloads use them, and the rendered output shows no Pod or container left out.
- **The Keycloak image pin.** The same pin was applied to `test/svt/common/compose/docker-compose.yml` (26.0 → 26.3.5). That is correct, but the commit message doesn't mention it.

## Findings

| Finding | Label | File:line | Change requested |
|---|---|---|---|
| The restricted-PSS claim has no test, and no CI namespace enforces `restricted` | Substantive | `Makefile:86,150`; `test/scripts/test-chart-render.sh` | Label the e2e and parity namespaces `pod-security.kubernetes.io/enforce=restricted` in the harness targets. Optionally add test-stand render assertions for the security contexts, labels, checksum annotation, and `fail` branches. |
| The package comment says sequences are per path; the default route's sequence is shared across paths | Substantive | `test/integration/pipstub/main.go:18-20,34-36` | Say that the default route keeps one sequence for every unrouted path. |
| No case for a routed path with no responses and no default route | Substantive | `test/integration/pipstub/main_test.go:225` | Add the row: `/routed` with `[]`, no default route → 404. |
| No case for rule precedence over `*` | Substantive | `main_test.go` (beside `TestHandlePIP_RuleThenLegacyFallback`) | A matching rule plus `*` → the rule's answer; a non-matching path → the default answer. |
| `profile.jq` and the duplicate checks have no test and no input | Substantive | `build/authz-agent-transfer/profile.jq`, `Dockerfile:39-46` | Add a jq check for the `parity-r29-level-m2m` → `R29LevelM2M` example and for a duplicate username, or name it as a follow-up. |
| The parity README describes user files and cases that do not exist | Substantive | `test/parity/README.md:69-72` | Hedge it as the Dockerfile does ("any users…"), or drop it until users exist. |
| The docs say `e2e-harness` installs the suite Job and waits for it to be Ready | Substantive | `docs/local-integration-tests.md:104` | Drop the Job from the row, as `test/k8s/README.md:53` does. |
| `ResetPinnedRoutes` leaves 404 routes that the default route will never answer | Substantive | `test/parity/suite/pip_control.go:184` | Name it as a follow-up for the cases that bring in `*`, or reset with `Responses: []`. |
| "configure takes `*`" is not exercised through `handleConfigure` | Substantive | `main_test.go` | One case that PUTs `[{"path":"*",…}]` and then GETs an unrouted path. |
| The doc comment describes the change ("as it did before…") | Taste | `main.go:37-38` | State the current behavior only. |
| The `TAG` comment leaves out the runtime-suite image | Taste | `helm-templates/authz-test-stand/values.yaml:9-11` | Add `authz-runtime-suite`. |
| REALM-DESCRIPTION names two of the four e2e realms | Taste | `test/k8s/authn/REALM-DESCRIPTION.md:82` | Say "the realms of `test/k8s/authn/`". |

This review did not run either kind harness or any cluster admission, did not build the images or the `chart-files` stage, did not run a mutation tool, did not check `kubectl wait --for=create` against the kubectl version in CI, and did not do a style pass on the prose, because `english-developer-style` was not available.

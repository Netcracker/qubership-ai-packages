## Final review: `58316ca..HEAD` (three commits, no cluster)

**Inputs.** No task statement was handed over, and as a subagent I could not ask for one. Item 2 therefore comes from the three commit messages (`17b17fc`, `9d25da7`, `8b85515`) and the test and package comments in `test/integration/pipstub`. No previous report of this form exists for this change.

**Skills.** I loaded `test-authoring` and `english-developer-style` from the supplied skills directory. The Go doc-comment skill (`godoc-authoring`) is not in that directory, so Go comments were checked against the form's wording rules only.

**Drift script.** It ran and printed nothing. It parses only Java, Kotlin, Groovy and Scala, and this change has three Go files and no JVM files. Item 1 was therefore done by reading.

**Checks run.** `gofmt -l` (clean), `go vet` and `go test -count=1 -v` for `test/integration/pipstub` (all 9 top-level tests pass), `go vet` for `test/integration/testify` (clean). Using a copy of the chart with generated files built by the Dockerfile's own commands, `helm lint` passes for both value files, and `helm template` renders. I checked labels and security contexts on every rendered object, and the realm checksum changes when a realm file's content changes. The `profile.jq` example in the Dockerfile comment produces the stated output. I confirmed with `ServeMux` that `OPTIONS *` is answered 400 before the handler, so the comment "No request path is *" holds.

---

### Item 1: comments consistent with the code and with each other
Findings: S4 (`main.go:32`), T1 (`idp.yaml:65`), T2 (`test-stand-values.yaml:21`). Members read: `handlePIP` (step 2 comment), `callRecord`, `defaultRoute`, `handleConfigure`. Checked against code and other files: `helpers.go` and the testify Dockerfile point at `suite.env` and `suite.args` in `test/k8s/test-stand-values.yaml`, which exist. `REALM-DESCRIPTION.md` and the parity `README.md` agree with the templates. The removed manifests have no remaining references.

### Item 2: claimed cases covered
Claimed case → test (`main_test.go`):
- Unrouted path gets the default answer → `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer`
- Routed path keeps its own answer → `.../a_routed_path_keeps_its_own_answer`
- Route with no responses falls through to default → `.../a_routed_path_with_no_responses_gets_the_default_answer`
- No default route gives 404 → `.../an_unrouted_path_without_a_default_route_is_404`
- Empty default gives 404 → `.../an_unrouted_path_with_an_empty_default_route_is_404`
- Default route sequence, clamped, across paths → `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths`
- Request target kept as sent → `TestHandlePIP_RecordsTheRequestTargetAsSent` (checks the Go field only; see S6)
- "or to 404" for a route with no responses → no case (see S5)

The chart claims (restricted-profile fields, labels, hooks, Secret, realm import) have no test. Only `helm lint` runs in CI, and the rest is checked by reading and by my render. The Keycloak `startupProbe` and `helm test` timeouts are not exercised anywhere.

Findings: S5, S6. The default-route design has no caller in this change. The commit's motivating parity case is deferred to a later change, so nothing in this change claims it.

### Item 3: boundaries, partitions, negative control
The Go tests cover the boundary of the sequence (first, second, clamped), the routed path that must keep its own answer, and the stub with no default route as the control that stays green. Findings: S1, S3.

### Item 3a: level and placement
The new Go tests are in-process and sit in the existing `main_test.go`, sharing `resetState`. The restricted-profile behaviour can be observed offline with `helm template`, but no CI job renders it, so it is covered only by the kind run, which does not enforce the profile. Finding: S2.

### Item 4: names by content
No ordinals in test names or case ids. The only ordinal is T2.

### Item 5: failure report
Every new `t.Errorf` and `t.Fatalf` prints its operands, and no new test has a boolean assertion on a comparison. None.

### Item 6: what the writer says it verified
Not stated. None of the three commit messages mentions a red run on the base commit, a mutation verdict, or a cluster run. I did not run the suite to supply this.

### Item 7: siblings
- `callRecord` literals: one in `handlePIP` (`main.go:212`) and one in `TestRuleMatches`. The new `requestUri` key is additive.
- `routes` and `counters` readers: `main.go:235/238/246/250`, reset at `378`, configure at `398`. `defaultRoute` is set only through configure.
- Chart: `podSecurityContext` is used by all four Pod templates (idp, pip-stub, tenant-manager, suite). `containerSecurityContext` is used for every container, and Keycloak alone passes `false`. The labels helper is used by every object; my render confirmed all of them.
- Makefile deployment names `E2E_LOCAL_DEPLOYMENTS` and `PARITY_LOCAL_DEPLOYMENTS`, and the `e2e-logs` and `parity-logs` exec targets, all exist in the render.
- Pod-level non-root holds for the repo-built images (`USER 10001:10001` in each Dockerfile). The Keycloak image is not built here, so its numeric uid is not checked.

---

### Report table

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| S1: Stands from the earlier `kubectl apply` targets are not covered. Helm will not adopt the same-named objects (Deployments `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`, `pip-mock`; ConfigMaps `keycloak-realms`, `pip-mock-config`; Secret `authz-agent-client-credentials`; ServiceAccount `runtime-suite`). The expected Helm 3 ownership error is not run here. No test, run, or remedy starts from that state. | Substantive | `Makefile:85-86`, `Makefile:149-150` | Run `e2e-harness` and `parity-harness` on a stand created by the earlier targets, or state the remedy (delete the namespace or `make e2e-down`) in the commit description and docs. |
| S2: The title says the stand runs under the restricted Pod Security Standard. Nothing labels the harness namespaces, and no CI job renders or checks the security context or labels. | Substantive | `17b17fc` title; `Makefile:86`, `Makefile:150` (`--create-namespace`); `helm-templates/authz-test-stand/README.md` (restricted paragraph) | Label both namespaces `pod-security.kubernetes.io/enforce: restricted`, and add a render assertion in the style of `test/scripts/test-chart-render.sh`. Otherwise reword the title and README to "can run under". |
| S3: The `helm test --timeout 15m` fixed in `run-suite` caps the documented `suite.activeDeadlineSeconds: 900`. Raising the value has no effect under `make e2e-suite` or `parity-suite`. The inner `-test.timeout 600s` does fire first at the defaults, which is fine. | Substantive | `Makefile:102`; `helm-templates/authz-test-stand/values.yaml:99`; `README.md:64` | Derive the helm test timeout from `suite.activeDeadlineSeconds`, or set both in one place, or document the pair next to `activeDeadlineSeconds`. |
| S4: "When PIP_STUB_CONFIG is unset … behaviour is exactly as before" is false. `/pip-stub/configure` can register a default route without the env var, and a route with zero responses now answers 404 where it used to panic (index -1). | Substantive | `test/integration/pipstub/main.go:31-32` | Say that unrouted paths answer 404 unless `/pip-stub/configure` registers a default route, and note the zero-response change. |
| S5: The claim "a route with no responses falls through to the default route, or to 404" has no case for the 404 half (routed path, empty responses, no default). | Substantive | `test/integration/pipstub/main_test.go`, table in `TestHandlePIP_DefaultRouteAnswersUnroutedPaths` | Add `{"a routed path with no responses and no default route is 404", "/routed", []pipResponse{}, nil, 404, ...}`. |
| S6: The `requestUri` JSON key, which the commit names as the wire contract, is untested. The test reads the Go field `RequestURI`, so a dropped or renamed tag passes. | Substantive | `main_test.go:~278-287` (`TestHandlePIP_RecordsTheRequestTargetAsSent`); tag at `main.go:77` | Marshal the call record, or read it through `/pip-stub/calls`, and assert the `requestUri` key. |
| T1: "the startup probe allows five" has no unit. The value is 60 × 5 s, so five minutes. | Taste | `helm-templates/authz-test-stand/templates/idp.yaml:65` | Write "allows five minutes". |
| T2: "A second instance for the entitlements endpoint" names the instance by ordinal, which goes stale on insertion. | Taste | `test/k8s/test-stand-values.yaml:21` | Name it by content, such as "The entitlements endpoint instance". |

**Not checked:** the e2e and parity suites were not run, since there is no cluster. The `make test-stand-files` Docker stage was not run; I reproduced its commands in a scratch copy at `/private/tmp/claude-501/-private-var-folders-hq-dhvxggnd1gv0fpmt8lg8xzkc0000gn-T-tmp-BIGwYv1FYo-repo/6ed57d3a-7563-4250-be93-8f117ca14d68/scratchpad/stand`. The `jqlang` image path `/jq`, the `kubectl wait --for=create` version requirement, the OpenShift SCC wording, and the Helm ownership error text are unverified offline. The wording pass under `english-developer-style` was not run as a style pass; I read only for sentences that state a false fact. The repository was not modified and nothing was committed. Along the way I wrote and removed `/tmp/x` in a `jq` check, which is outside the scratchpad.

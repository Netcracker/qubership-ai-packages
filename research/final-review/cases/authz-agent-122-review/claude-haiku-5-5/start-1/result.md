## Final review: `58316ca..HEAD` (three commits)

**Inputs.** No task statement was handed over, so the claimed cases come from the commit messages of `17b17fc`, `9d25da7` and `8b85515`, as you asked. No previous report exists, so there is no table over earlier findings.

**Skills.** I loaded `final-review`, `test-authoring` and `english-developer-style` from the skills directory. The change is Go, Helm, Make and Markdown. The doc-comment skill for Go (`godoc-authoring`) is not in that directory, so I did not load it and checked comments against the form only.

**Drift script.** It produced no output. Its parser covers Java, Kotlin, Groovy and Scala only, so I read the changed comments by hand.

**What I ran.** `go test -count=1 -v ./...` and `go vet ./...` in `test/integration/pipstub` both pass. For the chart, I copied it to the scratch directory and generated `files/` there by hand, mirroring the `chart-files` stage, because Docker was not run. `helm lint` passes with both values files. `helm template` renders 12 objects for the e2e values and 10 for the parity values. Every Pod has `runAsNonRoot` and `RuntimeDefault`; every container has `allowPrivilegeEscalation: false` and drops `ALL`; the root filesystem is read-only except Keycloak's. Every object has the `app.kubernetes.io` labels and `helm.sh/chart`. The `checksum/realms` annotation changes when a realm file changes. The `profile.jq` merge gives the documented values on a sample user. `make -n` shows the `run-suite` recipes are well formed.

### Item 1: comments consistent with the code and with each other
Finding: the default-route comments (`main.go:35`, `main.go:122-123`) say the default answers paths with "no route of its own". The code and `main_test.go:237` also send a route with zero responses to the default, so the comments are incomplete.
Finding: `main.go:31-32` says "When PIP_STUB_CONFIG is unset … behaviour is exactly as before". With that variable unset, a `PUT /pip-stub/configure` with `*` still changes unrouted answers.
Also: the `values.yaml` comments and the `docs` text were checked against the templates and Makefile. The only stale statement is in Item 3a and the docs finding below.

### Item 2: claimed cases covered
- `9d25da7`, default route: covered by `TestHandlePIP_DefaultRouteAnswersUnroutedPaths` (unrouted gets default, routed keeps its own, routed-empty gets default, no default → 404, empty default → 404), `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths`, and `TestHandlePIP_RecordsTheRequestTargetAsSent` for `requestUri`.
- `9d25da7`, "a route with no responses falls through to the default route, or to 404": the 404 half is untested. No case has a routed path with empty responses and no default route.
- `17b17fc`, restricted Pod Security Standard, labels, selectors, `/tmp` emptyDir: no test or CI check (see Item 3a).
- `8b85515`, parts off by default, realm restart, `helm test` path: no test or CI check.

### Item 3: boundaries, partitions, negative control
The control arms are present: the routed-keeps-answer case and the no-default-route 404 case are green on the base commit. The routed-empty case is the defect, and it is red on the base commit (the old code indexes at -1). The commit messages do not state a red run.

Pre-existing state: the e2e and parity namespaces may already hold objects created by the old `kubectl apply` and `kubectl create` targets: Deployments `keycloak`, `pip-stub`, `entitlements-mock` and `tenant-manager`; ConfigMap `keycloak-realms`; Secret `authz-agent-client-credentials`; ServiceAccount and Job `runtime-suite`. Helm refuses to adopt objects without its ownership annotations, so `make e2e-harness` on such a stand should fail. I have not run this against a cluster. Every run in CI starts from a fresh kind cluster, and no documented remedy is named.

Limits: the Job's `activeDeadlineSeconds: 900` fires before `helm test --timeout 15m`, and the Keycloak startup probe (300 s) fires before `--wait --timeout 10m`. The inner limits fire first, so no finding there.

### Item 3a: level, placement, environment
The Go tests are in-process, sit beside the existing `TestHandlePIP_*` tests and reuse `resetState`. For the chart, the only CI checks are `helm lint` of the two values files. Nothing renders the test stand and checks its security context, and no namespace carries a `pod-security.kubernetes.io/enforce` label (I searched the whole repository).

### Item 4: names by content
Finding: `test/k8s/test-stand-values.yaml:21` says "A second instance for the entitlements endpoint." The entry below it is `entitlements-mock`, so name it by that.

### Item 5: failure report
none. The Go `if got != want { t.Errorf(...) }` form prints both operands.

### Item 6: what the writer says it verified
Neither a red run on the base commit nor a mutation verdict is stated in any of the three commit messages. The `-1` index defect in `9d25da7` has no stated red run.

### Item 7: siblings
- `route.Responses[idx]` (`main.go:251`) is the only other indexing site. Both branches of its guard run before it, and `matchRule` guards `RespondSequence` with `len > 0`.
- The new `requestUri` field is additive. Testify's consumers of `/pip-stub/calls` do not decode strictly.
- All seven chart templates use the shared label helper. `pip-stub`, `parity-suite` and `tenant-manager` run as numeric users, so `runAsNonRoot` can be verified for them. I did not verify Keycloak's image user.
- No stale references remain to the removed manifests.

### Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| The troubleshooting row says `make e2e-harness` times out at `rollout status deploy/keycloak`. That command is gone; the wait is now Helm's `--wait --timeout 10m`. | substantive | `docs/local-integration-tests.md:190` | Reword the row to the Helm wait and its timeout. |
| The restricted Pod Security Standard claim in `17b17fc` is untested. No namespace is labelled `enforce: restricted`, and CI only lints the chart. | substantive | `Makefile:85`, `:149`; `helm-templates/authz-test-stand/README.md:8-11` | Label the two namespaces `pod-security.kubernetes.io/enforce: restricted` in the harness targets, or add a render assertion to `test/scripts/test-chart-render.sh`, or name the follow-up. |
| A stand created by the old targets will not be adopted by `helm upgrade --install`. No remedy is documented. (Not run on a cluster.) | substantive | `Makefile:85`, `:149`; `docs/local-integration-tests.md` | Document the remedy (`make e2e-down`, or delete the namespace or the old objects), and run the install over a stand the old targets created. |
| The default-route comments do not name the zero-response route the code and test cover. | substantive | `test/integration/pipstub/main.go:35`, `:122-123` | Name the case: "a path whose route has no responses, or no route at all". |
| "When PIP_STUB_CONFIG is unset … behaviour is exactly as before" is false once `*` is configured. | substantive | `test/integration/pipstub/main.go:31-32` | Qualify it with "and no default route is configured". |
| The commit's "or to 404" case has no test: a routed path with no responses and no default route. | substantive | `test/integration/pipstub/main_test.go:225-249` | Add a case: routed `/routed` with `[]pipResponse{}`, no default, expecting 404 and `{"error":"no rule or route for /routed"}`. |
| Ordinal in a comment: "A second instance". | taste | `test/k8s/test-stand-values.yaml:21` | Name the instance `entitlements-mock`. |
| The 404 cases pin the exact error body text, which is a wording change detector. | taste | `main_test.go:241-244` | Compare the status, and the body only where it is the wire contract. |

**Not checked:** I did not run the Docker `chart-files` stage, `make e2e` or `make parity`, and I did not run anything against Kubernetes, so pod admission, the realm import and the suite's own pass or fail are unverified. The English-style pass over the new prose was not done, as this review covers wording only where it changes a sentence's reading.

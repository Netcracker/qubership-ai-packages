## Final review: `58316ca..HEAD` (three commits: 8b85515, 9d25da7, 17b17fc)

**Inputs.** No task statement was handed over, so the claimed cases come from the three commit messages and the test class comments. Skills loaded: `final-review`, `test-authoring`, and `english-developer-style`. `godoc-authoring` is not among the provided copies, so Go doc comments were checked against the form and the English style skill only. No previous report exists.

**Drift script.** `comment-drift.py 58316ca6 HEAD` printed nothing and exited 0. It parses Java, Kotlin, Groovy, and Scala only. The three changed Go files were read by hand, and the chart, Makefile, and docs were read as analogues.

**What I ran (no repo files changed).** I copied `HEAD` with `git archive` into the scratchpad and ran there:
- `go test`, `go vet`, and `gofmt` on `test/integration/pipstub` all pass. The three new tests pass when run verbosely.
- I generated the chart `files/` as the transfer Dockerfile does, then `helm lint` passes for both stand values files and for no values.
- I rendered both stands and inspected every Pod, Job, and Service with a parser. Security contexts, labels, selectors, and the realm checksum annotation match the commit claims.
- A small Go program confirmed that `OPTIONS *` yields `URL.Path == "*"`.

### Item 1: comments consistent with code and with each other

Findings: `main.go:34-35`, `main.go:122-123`, `main.go:36`, `REALM-DESCRIPTION.md:82`, `parity-realm.json:30`, `parity-mt-b-realm.json:14`, `Makefile:83`, `_helpers.tpl:21`, `_helpers.tpl:30-31`, `values.yaml:9`. See the table.

The default-route comment in `main.go` says the route answers requests "whose path has no route of its own". The code (`main.go:236-240`) also falls through when the route exists with zero responses, and the test comment at `main_test.go:222-224` says so correctly.

### Item 2: claimed cases covered

- **9d25da7, "a route with no responses falls through to the default route, or to 404":** the fall-through is tested, but the 404 leg is not. No case covers a routed path with no responses and no default route. The table at `main_test.go:227-241` lacks it.
- **17b17fc, restricted Pod Security Standard:** no test asserts any of it. `test/scripts/test-chart-render.sh` renders only the agent and policy-admin charts, and CI only runs `helm lint` on the stand. The render confirms the claimed contexts: every container drops `ALL` and disallows escalation, and every container except Keycloak has a read-only root filesystem. No `runAsUser` is pinned. Every object carries the labels. Nothing enforces `restricted`, though: the namespace is created with `--create-namespace` (`Makefile:86`, `:150`) and no `pod-security.kubernetes.io/enforce` label is set anywhere. Keycloak's image user is external and was not verified.
- **8b85515, "restarting when one changes" and "each off by default":** true by render (`idp.yaml:34-35`), with no test.
- **8b85515, "the parity realm gains a second tenant realm":** `parity-realm.json` also gains `ROLE_MT_READER` and `ROLE_MT_ADMIN`, the `mt-a` and `mt-a-admin` users, a `parity-m2m-tenant-b` client, `tenant-id` mappers, and a `parity-level-claim` mapper. That is about 318 added lines, and no commit message mentions them.
- The `test/svt/common/compose/docker-compose.yml:3` change, Keycloak 26.0 to 26.3.5, is not in any commit message.

### Item 3: boundaries, partitions, negative control

- The pipstub partitions are covered: unrouted, routed, routed with empty responses, no default, and empty default. The controls are present: a routed path keeps its own answer, and with no default route an unrouted path is 404. The missing boundary is the one in Item 2.
- **Pre-existing state (finding).** The Helm install meets objects the old harness created with `kubectl apply`, under the same names: Deployments `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`, `idp`, and `pip-mock`; ConfigMaps `keycloak-realms` and `pip-mock-config`; and Secret `authz-agent-client-credentials`. Helm will most likely refuse to adopt them, since they lack its ownership labels. I did not run this, as there is no cluster. CI starts from a fresh kind cluster, and `docs/local-integration-tests.md` §6 names no remedy.
- **Limits.** `-test.timeout 600s` in the suite args fires before `activeDeadlineSeconds: 900`, which is fine at the defaults. The 3-minute log poll is a different piece of work. None.

### Item 3a: level, placement, environment

The new pipstub tests are in-process with `httptest`, the smallest level. They sit beside the existing tests in `main_test.go` and reuse `resetState`. `go-build.yaml` has a matrix entry for `test/integration/pipstub`; I read that entry and did not run the workflow. For the chart, the smallest observing test is a render assertion, which is missing; see Item 2.

### Item 4: names by content

None. I scanned the added lines for ordinal and positional references. The counts such as "a second stub instance" name things by content.

### Item 5: failure report

None. The new Go assertions print both operands through `t.Errorf` with got and want, and the subtest names are conditions.

### Item 6: what the writer says it verified

Neither commit message states a red run or a mutation verdict. For 9d25da7, the claimed regression (a route with no responses indexing at -1) has no stated base-commit failure. I did not run the red run, as the form asks.

### Item 7: siblings

- **Callers checked.** `containerSecurityContext` has four callers (idp with `false`; pip-stub, tenant-manager, and suite with `true`), and all four containers are covered. `podSecurityContext` is covered for every Pod. The labels helper is used by every object. `run-suite` is used by `e2e-suite` and `parity-suite` with the right arguments. No references to the deleted manifests remain in HEAD.
- **Pip-stub rule files (finding).** The stub reads `PIP_STUB_CONFIG` only at start (`main.go:147`). `pip-stub.yaml:30-33` has no config checksum, while `idp.yaml:34-35` restarts Keycloak on a realm change. So a rule-file edit through `make parity-harness` updates the ConfigMap but not the Pod. The old harness did the same, but this change added the mechanism for Keycloak and left out the stub.
- `callRecord.requestUri` is an additive JSON field. I did not read each consumer of `/pip-stub/calls`.
- `handleConfigure` accepts the `*` path with no validation, so the default route can be configured.

### Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| Default-route comment says "no route of its own", but a route with zero responses also falls through | substantive | `test/integration/pipstub/main.go:34-35`, `:122-123` | Add "or whose route has no responses", as `main_test.go:222` already says |
| "No request path is *" is false: `OPTIONS *` has path `*` | substantive (low) | `main.go:36` | Drop the clause or rewrite it; no route is registered at `*` except the default |
| Claimed 404 leg of "route with no responses" is untested | substantive | `test/integration/pipstub/main_test.go:227-241` | Add a case: routed path with empty responses and no default is 404 |
| Realm list says the e2e Keycloak imports two realms; the chart imports four (both tenant realms too) | substantive | `test/k8s/authn/REALM-DESCRIPTION.md:82` | List all four realm files |
| Realm descriptions name `TestTenantScopedDecisions` and `t9a`; neither exists in the repo | substantive | `test/k8s/parity/idp-seed/parity-realm.json:30`, `parity-mt-b-realm.json:14` | Name the existing test or drop the reference |
| Restricted Pod Security Standard never enforced; no render assertion for the contexts | substantive | `Makefile:86`, `:150`; `templates/_helpers.tpl:17-21`; `README.md:8-11` | Label both namespaces `pod-security.kubernetes.io/enforce: restricted`, and add stand render assertions to `test/scripts/test-chart-render.sh` |
| Pre-existing kubectl-created objects will likely block `upgrade --install`; no test or remedy | substantive | `Makefile:86`, `:150`; `docs/local-integration-tests.md` §6 | Delete the old objects in the harness targets, or document the remedy |
| Pip-stub Pods do not restart on rule-file change, unlike Keycloak | substantive | `templates/pip-stub.yaml:30-33` | Add a `checksum/config` annotation as `idp.yaml:34-35` does |
| parity-realm additions (+318 lines) and the svt Keycloak bump are in no commit message | substantive | `test/k8s/parity/idp-seed/parity-realm.json`; `test/svt/common/compose/docker-compose.yml:3` | Describe them in the commit or PR, or split them out |
| No base-commit red run stated for the regression claim | substantive | 9d25da7 message | State the failure on the base commit in the PR |
| Makefile says the platform provisions the M2M Secret, but this stand creates it | substantive (low) | `Makefile:83` | Say "the M2M client-credentials Secret, which this chart creates" |
| "Rejects a pinned one" overstates the restricted SCC (only out-of-range uids) | substantive (low, not verified here) | `templates/_helpers.tpl:21` | Say "rejects a uid outside that range" |
| "Release version" sentence includes tenant-manager, which is not published | substantive (low) | `templates/../values.yaml:9` | Drop tenant-manager from the sentence |
| "Takes the value of readOnlyRootFilesystem: true for every container except Keycloak" reads as if the helper takes `true` | taste | `templates/_helpers.tpl:30-31` | Reword to say the argument is `true` except for Keycloak, which gets `false` |

Churn: none reported.

**Not checked.** I did not run the style pass beyond the wording that makes a sentence read wrongly. I did not check the cluster-side behavior: PSS admission, Helm adoption, OpenShift SCC, and Keycloak's image user. I did not run the red run or the workflows, did not read the Go doc-comment rules (`godoc-authoring` was not provided), and did not read each consumer of `/pip-stub/calls`.

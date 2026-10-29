## Final review: `58316ca..HEAD` (three commits)

**Inputs.** There was no separate task statement, so the claimed cases come from the three commit messages: 17b17fc (restricted Pod Security Standard), 9d25da7 (pip-stub default route and request target), and 8b85515 (test-stand chart, realm generation, `make` targets). The drift script ran and printed nothing, because the change has no Java, Kotlin, Groovy, or Scala files. I read the changed Go, Helm, Makefile, YAML, and Dockerfile comments by hand. No previous report exists. I loaded `test-authoring` with `references/go/testing.md` and `english-developer-style`. `godoc-authoring` is not in the provided skills directory, so Go doc comments were checked against the function bodies only.

**Checks I ran (no repo files changed, nothing committed):** `go test` on `test/integration/pipstub` (passes); `helm lint` of the test-stand chart with both values files, and `helm template` of both, in a scratch copy with generated `files/` (passes; every rendered object has the labels, and every pod and container has the claimed security context); a probe showing `OPTIONS *` gives `URL.Path == "*"`; a run of the `profile.jq` stage expression on a one-user fixture. I did not run a cluster, `docker`, or `make test-stand-files`.

### Item 1: comments consistent with the code and with each other
Findings F4 (false claim about `*`), F6 (incomplete realm list), F8 and F9 (taste). Checked and consistent: the `callRecord` and `handlePIP` comments; the `_helpers.tpl` comments; the `idp.yaml` claim that no suite uses the admin API (the suites use a password grant as the realm user `admin`); the Dockerfile's `parity-mt-b` and realm list; and the profile example `R29LevelM2M`. No comment narrates the change with `now` or `no longer`.

### Item 2: claimed cases covered
- Default route: `TestHandlePIP_DefaultRouteAnswersUnroutedPaths` and `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths`.
- Request target: `TestHandlePIP_RecordsTheRequestTargetAsSent`.
- Route with no responses falls through: a case in the first test.
- Finding F10: the claim that `/pip-stub/configure` "takes the path `*`" has no test. Every test writes `routes` directly and never calls `handleConfigure`.
- Finding F3: the security contexts, labels, and read-only roots (17b17fc) have no test. Only lint and manual render.
- Finding F7: the profile fill-in in the transfer image has no test and no user file to run it on.

### Item 3: boundaries, partitions, and the negative control
Covered: the empty value (`[]pipResponse{}`), the absent default route (nil, the negative control, which is 404 on the base commit), and a routed path beside the default. Missing: a request whose path is `*` (F4), which is the one request that reaches the default key. Pre-existing state: the chart adopts a state the old harness created with `kubectl` (F1). Limits on the same work: F5. The Go timeout (600s) sits inside the Job deadline (900s), which is correct.

### Item 3a: level, placement, environment
The pip-stub tests are in-process, use `httptest`, and sit beside the existing tests. `go-build.yaml` lists the directory, so CI runs them. The chart has no small-level test (F3). The restricted-PSS claim needs a cluster, and nothing in the repo sets `pod-security.kubernetes.io/enforce`, so the claim is unexercised (F2).

### Item 4: names by content
One finding, F8. Otherwise the test names and table case names are by content, and no parameterized case uses an index.

### Item 5: the failure report
None. The Go tests print operands with `t.Errorf` (`got`/`want`) and name each row through `t.Run`. The status-and-body comparison is a condition that is the assertion itself, which §6 allows.

### Item 6: what the writer says it verified
Neither commit states a red run on the base commit or a mutation verdict. 9d25da7 describes a fix for a `-1` index panic, and its regression case ("a routed path with no responses gets the default answer") should carry that evidence. I did not run the base commit to supply it.

### Item 7: siblings
- `handlePIP` is the only reader of `routes` that needs the default. `handleReset` and `handleConfigure` need no change.
- `containerSecurityContext` is called on all five containers and `podSecurityContext` on all four pod templates. The render confirms each.
- Every rendered object carries the labels.
- The e2e restart target's deployment names match the chart's names.
- Finding F6 is the one stale sibling: `REALM-DESCRIPTION.md`.
- Finding F1 is the sibling that matters most: the objects the old harness created.

### Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | Existing kind objects from the old `kubectl apply` harness (Secret `authz-agent-client-credentials`, ConfigMap `pip-mock-config`, Deployment `idp`, and so on) are not Helm-owned. `make e2e-harness` and `make parity-harness` on an existing cluster should fail with Helm's "cannot be imported" error. This is from reading the code; I did not run it. | Substantive | `Makefile:85`, `:149`; `templates/idp.yaml`; `templates/client-credentials.yaml` | Name the remedy (`make e2e-down`, or delete those objects) in `docs/local-integration-tests.md` and `test/parity/README.md`, and run the target on that inherited state |
| F2 | Commit 17b17fc's subject says the stand runs "under the restricted Pod Security Standard". No namespace is labeled `enforce: restricted`, and no run does it. | Substantive | commit subject; `Makefile` harness targets | Label the namespaces and run it, or reword the subject to what the commit does |
| F3 | No small-level test for the claimed security contexts, labels, or read-only roots | Substantive | `helm-templates/authz-test-stand/templates/*.yaml`; `test/scripts/test-chart-render.sh` | Add render assertions for the test-stand chart to the existing CI render script |
| F4 | "No request path is `*`" is false: `OPTIONS *` arrives with `URL.Path == "*"` (verified). | Substantive | `test/integration/pipstub/main.go:36-37` | Reword ("only the `OPTIONS *` request has path `*`"), and add a case for it if the boundary matters |
| F5 | `helm test --timeout 15m` equals the Job's `activeDeadlineSeconds: 900`. The outer timeout starts no later than the Job's deadline, so the outer failure can hide the Job's own `DeadlineExceeded`. | Substantive | `Makefile:102`; `values.yaml:99` | Make the Job's deadline shorter than the wait, or derive one from the other, or document the pair |
| F6 | `REALM-DESCRIPTION.md` says the e2e Keycloak runs with two realm files. It imports all four in `files/realms/e2e/`, including the two tenant realms that `test-stand-values.yaml` uses. | Substantive | `test/k8s/authn/REALM-DESCRIPTION.md:81-82` | List all four, or say "the realms of `test/k8s/authn/`" |
| F7 | The `profile.jq` fill-in is claimed but never exercised, because `testdata/realm/` holds no user file. My probe filled the fields correctly and `jq -e` rejected a duplicate username, so the code looks right. | Substantive | `build/authz-agent-transfer/Dockerfile:34-47`; `test/parity/suite/testdata/realm/README.md` | Run the stage on a fixture user file in a test, or state in the Dockerfile that the path is unexercised |
| F8 | Ordinal "second" where the entry is named | Taste | `test/k8s/test-stand-values.yaml:21`; `docs/local-integration-tests.md:18` | Drop "second"; the name is in the same entry |
| F9 | The realm note names Keycloak 26.6.4 while the stand pins 26.3.5 | Taste | `test/k8s/parity/idp-seed/README.md:18`; `helm-templates/authz-test-stand/values.yaml:21` | Say which version the import check was made on |
| F10 | `/pip-stub/configure` with path `*` is claimed but untested. The tests write `routes` directly and never call `handleConfigure`. | Substantive | `test/integration/pipstub/main.go:385-402`; `main_test.go` | Add a test that sends `PUT /pip-stub/configure` with path `*` through `handleConfigure` |

**Not checked:** I did not run a cluster, `docker`, `make test-stand-files`, or the restricted-PSS admission; the Keycloak image's numeric `USER` for `runAsNonRoot` cannot be verified offline; the drift script parsed no members, so the Go, Makefile, and YAML comments were read by hand; no wording pass was done beyond the sentences that misread; and `godoc-authoring` was not available.

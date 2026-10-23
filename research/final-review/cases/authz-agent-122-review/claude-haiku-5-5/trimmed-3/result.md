## Final review of `58316ca..HEAD` (three commits, no edits made)

**Inputs.** No task statement was handed over, so the claimed cases come from the three commit messages (17b17fc, 9d25da7, 8b85515). The test-authoring and english-developer-style skills were loaded from the given directory. The Go doc-comment skill (`godoc-authoring`) is not among the three skills provided, so Go comments were checked against the form only.

**Drift script.** Ran it. It printed nothing because it parses only `.java`, `.kt`, `.kts`, `.groovy` and `.scala`, and this change is Go, Helm, Make, YAML and Dockerfile. Item 1 was therefore done by hand.

**Prior report.** None; this is the first round.

### Item 1: comments consistent with code and each other
- The Go default-route comment says "No request path is `*`". That is false: `httptest.NewRequest("OPTIONS", "*", nil)` gives `URL.Path == "*"`, which I checked by running it. (F4)
- "Imported at every start" appears in several places. It holds for a new Pod, which always has a fresh database, but not for a container restart. The old `test/k8s/keycloak.yaml` set `JAVA_OPTS_APPEND=-Dkeycloak.migration.strategy=OVERWRITE_EXISTING`, and the new chart drops it without any mention in the commits. (F3)
- `REALM-DESCRIPTION.md` says Keycloak "runs with `authz-test-realm.json` and `cloud-common-realm.json`", but the chart imports all four e2e realms, and the same file relies on the tenant realms being present. (F5)

### Item 2: claimed cases covered
- Covered: the default answer for unrouted paths, the routed path keeping its own answer, an empty routed path falling through, 404 with no default, 404 with an empty default, sequence across paths, and `requestUri` as sent.
- Not covered: "falls through to the default route, or to 404" has no case for a routed path with no responses and no default route. (F6)
- Not covered: "`/pip-stub/configure` now takes the path `*`". The tests write `routes[defaultRoute]` directly and never go through `handleConfigure`. (F7)
- Not covered: the restricted Pod Security Standard and label claims (17b17fc, 8b85515) have no detection anywhere in the repository. `test/scripts/test-chart-render.sh` already asserts the agent chart's rendered output in CI, and nothing does so for the test stand. (F8)

### Item 3: boundaries, partitions, negative control, pre-existing state
- Pre-existing state: `make e2e-harness` and `make parity-harness` (Makefile:86, :150) install over a kind cluster that the previous version populated with `kubectl apply`. Those objects include the Deployments, Services, `keycloak-realms`, `authz-agent-client-credentials`, the `runtime-suite` ServiceAccount, and for parity `idp`, `pip-mock-config`, and the rest. Helm does not adopt objects without its ownership metadata, so the first install should fail. No test or run starts from that state, and no remedy is documented. CI uses fresh clusters, so it does not hit this. (F1)
- Limits: the Makefile hard-codes `helm test --timeout 15m` (Makefile:102, chart README:64). The Job's `suite.activeDeadlineSeconds` is 900 (values.yaml:99, suite.yaml:25). Helm's wait and the Job deadline both end the same work, and the Helm wait starts first. Raising `activeDeadlineSeconds` therefore has no effect. The inner `-test.timeout 600s` does fire first at the defaults, so that part is fine. (F2)
- Negative control: the 404 cases and the routed-path-keeps-its-answer case are present.

### Item 3a: level and placement
The pipstub tests run in-process through `httptest`, which is the smallest level. The chart has no in-process analogue, so its checks are the render assertions in F8.

### Item 4: names by content
One ordinal reference: "A second instance for the entitlements endpoint" in `test/k8s/test-stand-values.yaml:21`. The instance is already named by its key. (F9)

### Item 5: failure report
None. Every assertion prints its operands.

### Item 6: what the writer says it verified
Not stated. None of the three commit messages reports a red run on the base commit or a mutation verdict for the new pipstub tests.

### Item 7: siblings
- Stale references: a grep of HEAD finds no remaining references to the deleted manifests outside historical handover docs.
- Consumers of `/pip-stub/calls`: the new `requestUri` field is additive. `ResetPinnedRoutes` still registers 404 routes, which remain routes, so it is unaffected.
- Unnamed change: `test/svt/common/compose/docker-compose.yml:3` moves Keycloak from 26.0 to a pinned 26.3.5 digest, and no commit names it. (F10)

### Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| F1 | Install over the objects an earlier version left behind has no test, run, or documented remedy | substantive | `Makefile:86`, `:150`; `docs/local-integration-tests.md` (`e2e-harness` row) | Document deleting the `authz-e2e` and `authz-parity` namespaces (or `make e2e-down`) before the first harness install on an existing cluster, or show an install over the old objects |
| F2 | `helm test --timeout 15m` fires before `suite.activeDeadlineSeconds`, so raising the deadline does nothing | substantive | `Makefile:102`; `helm-templates/authz-test-stand/README.md:64`; `values.yaml:99`; `templates/suite.yaml:25` | Derive the Helm timeout from the deadline, or drop `--timeout` and let the Job deadline stand |
| F3 | "Imported at every start" is true only for a fresh database. The `OVERWRITE_EXISTING` flag was dropped unnamed | substantive | `helm-templates/authz-test-stand/values.yaml:16`; `test/k8s/authn/REALM-DESCRIPTION.md:72`; `test/parity/README.md:69`; `test/k8s/parity/idp-seed/README.md:5`; `templates/idp.yaml` | Restore the flag in `templates/idp.yaml`, or narrow the sentences to a new Pod, and name the removal. I did not check Keycloak 26.3.5's import default against its docs offline |
| F4 | "No request path is `*`" is false: `OPTIONS *` has path `*` | substantive | `test/integration/pipstub/main.go:36` | "Only `OPTIONS *` has the path `*`, and it gets the default answer like any unrouted path." |
| F5 | The Keycloak sentence omits the two tenant realms the same file relies on | substantive | `test/k8s/authn/REALM-DESCRIPTION.md:82` | "imports the four realm files of `test/k8s/authn/`" |
| F6 | No test for "a route with no responses falls through to ... 404" | substantive | `test/integration/pipstub/main_test.go:225-258` | Add a case: routed path with empty responses and no default route gives 404 |
| F7 | No test goes through `/pip-stub/configure` with path `*` | substantive | `main_test.go:249`, `:263`; `main.go:385` | One test that PUTs `[{"path":"*",…}]` to `handleConfigure`, then requests an unrouted path |
| F8 | Restricted-PSS and label claims have no detection | substantive | `test/scripts/test-chart-render.sh` (CI "Render assertions" step) | Assert the test stand's rendered output: `runAsNonRoot` and seccomp on every Pod, `drop: ALL` and no escalation on every container, `readOnlyRootFilesystem` false only for `keycloak`, and the `app.kubernetes.io` labels on every object |
| F9 | Ordinal "A second instance" where the key names the instance | taste | `test/k8s/test-stand-values.yaml:21` | Name it `entitlements-mock`. Expect this to be declined |
| F10 | Keycloak image bump in the svt compose file is not named by any commit | taste | `test/svt/common/compose/docker-compose.yml:3` | Name it in the pull request description, or revert it |

**Not checked:** no cluster, so no install, no suite or parity run, and no admission check of the restricted profile. I did not run the `docker build` for `chart-files`. I simulated its commands with local `jq`, `cp` and `helm` into the scratchpad at `/private/tmp/claude-501/-private-var-folders-hq-dhvxggnd1gv0fpmt8lg8xzkc0000gn-T-tmp-tALIJEUEEb-repo/81d80f1d-a45b-4234-9258-fbaf28e78283/scratchpad/review`, and the chart lints and renders from there. The Keycloak image user and the Keycloak import default were not verified. The Go comments were not checked against the Go doc-comment skill.

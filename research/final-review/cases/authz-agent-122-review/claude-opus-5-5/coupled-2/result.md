I've reviewed the three commits against the final-review form. Two findings matter most:

- **Upgrading an existing cluster fails.** Running `make e2e-harness` or `make parity-harness` on a kind cluster set up before this change stops at the first install.
- **No test checks the restricted Pod Security Standard.** Nothing in CI confirms the restricted-Pod-Security claim in `17b17fc`. The repository already has render checks for the other two charts that this chart could join.

There was no separate task statement, so the claimed cases in item 2 come from the commit messages (`git log 58316ca6..HEAD`) and the comments above the tests.

**What I ran:**
- `comment-drift.py 58316ca6 HEAD` exited 0 and printed nothing, so it found no members in the Go, YAML, Makefile or Helm template files. I read every comment by hand.
- `go test ./...` in `test/integration/pipstub` passes.
- I built the `chart-files` stage into a scratch copy of the chart. `helm lint` and `helm template` pass with both values files.
- I ran `local/pip-stub:ci` and `local/tenant-manager:ci` with `--read-only --cap-drop ALL` as uid 10001 and as uid 1000770000:0. Both start and serve.

## Item 1: comments consistent with the code and with each other

1. **`test/integration/pipstub/main.go:34-37` and `:122-123` leave out a case the change added.** Both comments say the default route answers "every request whose path has no route of its own". The code at `main.go:243` (`!ok || len(route.Responses) == 0`) also hands it a path whose route has no responses. The commit message says so, but the comments do not, so a reader would expect such a route to answer 404.
2. **`main.go:31-32` and `:37-38` describe the code by its history.** "behaviour is exactly as before" and "as it did before the default route existed" both do this. The developer-style rule asks a comment to state the current behaviour.
3. **`docs/local-integration-tests.md:104` says the wrong thing about the suite Job.** It says `e2e-harness` installs "…the client-credentials Secret, and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` (`templates/suite.yaml:21`), so `upgrade --install` never creates it. `test/k8s/README.md` gets this right, which means the two files contradict each other.
4. **The `run-suite` comment in `Makefile` is not true of this command.** It says "`helm test` … prints the log only at the end". That is only true with `--logs`, which this call does not pass.
5. **`test/k8s/authn/REALM-DESCRIPTION.md:83`** says the harness "runs Keycloak with `authz-test-realm.json` and `cloud-common-realm.json`". It also imports the two tenant realms.

The rest is consistent:
- The `_helpers.tpl` comments match the rendered output, which I checked.
- The `idp.yaml` probe comment (60 × 5 s = 5 min) is correct.
- The `suite.yaml` hook comment is correct.
- The comments in `helpers.go`, the testify `Dockerfile`, `test/k8s/values.yaml` and `docker-release.yaml` point to files that exist.
- `git grep` finds no reference left to any deleted manifest.

## Item 2: claimed cases covered

| Claimed case | Test |
|---|---|
| Unrouted path → default route | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/"an unrouted path gets the default answer"` |
| Routed path keeps its own answer | same table, "a routed path keeps its own answer" |
| No `*` configured → 404 as before | same table, "…without a default route is 404" |
| Route with no responses → default route | same table, "a routed path with no responses gets the default answer" (it panics on the base commit, so it does catch the `-1` index) |
| Route with no responses → **404** when there is no default route | **none** |
| `/pip-stub/configure` takes the path `*` | **none at the interface.** Every case writes `routes[defaultRoute]` directly; nothing sends `{"path":"*"}` through `handleConfigure` |
| The default route serves its responses in order, clamped to the last | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| The call record keeps the request target in `requestUri` | `TestHandlePIP_RecordsTheRequestTargetAsSent` checks the struct field only. The JSON name `requestUri`, which the parity cases will read from `/pip-stub/calls`, is never asserted |
| Restricted PSS: non-root, RuntimeDefault, drop ALL, no escalation, read-only root except Keycloak, `/tmp` emptyDir | **none.** The kind namespaces are created by `--create-namespace` with no `pod-security.kubernetes.io/enforce` label, and `test/scripts/test-chart-render.sh` does not render this chart. I checked by hand that the output complies; no test does |
| `app.kubernetes.io/*` and `helm.sh/chart` on every object, selectors keep `app` | **none** (I checked by hand) |
| No `runAsUser`, so OpenShift can assign a uid | **none in the repo.** I checked by hand: the stub and tenant-manager images start read-only with uid 1000770000:0 |
| `profile.jq` fills first name, last name and email; the build fails on a duplicate username or id | **none.** `testdata/realm/` holds no user files, so the merge, the profile function and both duplicate checks only ever run with zero users |
| Both kind harnesses run on the chart | CI jobs `make e2e-*` and `make parity-*` |
| The release publishes three more images | config only; it can only be checked by a release run |
| Second tenant realm `parity-mt-b`, plus the `mt-a` users added to `parity-realm.json` (not in the message) | fixtures only; nothing in this change uses them |
| *(not claimed)* SVT compose Keycloak `26.0` → `26.3.5@sha256…` | not in any commit message |

## Item 3: boundaries, partitions, and the negative control

1. **No test for a rule combined with a default route.** The package comment says rules come before legacy routes, which come before the default route. `TestHandlePIP_RuleThenLegacyFallback` covers a rule against a legacy route, but no case has both a matching rule and `*` set.
2. **Clusters set up before this change.** The old `e2e-harness` and `parity-harness` used `kubectl apply` to create:
   - in `authz-e2e`: `keycloak`, `keycloak-realms`, `pip-stub`, `entitlements-mock`, `tenant-manager`, `authz-agent-client-credentials`, `sa/runtime-suite`;
   - in `authz-parity`: `idp`, `pip-mock`, `pip-mock-config`, `entitlements-mock`, the Secret.

   The chart renders objects with the same names but without Helm ownership metadata, so `helm upgrade --install` fails with "invalid ownership metadata" on any cluster built before this change. CI always starts from a fresh kind cluster, and the docs give no fix. A one-time `make e2e-down`, or deleting both namespaces, would fix it.
3. **Limits on how long the suite may run.** There are three, set in three places:
   - `-test.timeout 600s` in `suite.args` (values);
   - `suite.activeDeadlineSeconds: 900` (values);
   - `helm test --timeout 15m`, fixed in the Makefile `run-suite` and in the chart README, step 3.

   The Job deadline and the helm timeout are both 900 s, and helm's clock starts before the Job's. So setting `activeDeadlineSeconds` (or the Go timeout) above about 900 has no effect: helm gives up first and reports a timeout instead of the Job's `DeadlineExceeded`.
4. **Pod template labels.** `helm.sh/chart` (which includes the chart version) and `managed-by` are on the Pod template. Any chart-version upgrade from the transfer image therefore restarts Keycloak, which creates new realm keys, and the agent's JWKS goes stale. The docs say the Pod is replaced only when a realm file changes. This interacts with item 7.

The chart's guards (missing realm files, a missing stub config file, empty `tenants`, empty `TAG`) are covered by the render request under item 3a.

## Item 3a: level, placement, and the environment

- **Pipstub tests:** they run in-process and sit beside the existing `TestHandlePIP_*` tests, sharing `resetState`. Fine.
- **Chart claims:** they can be checked by rendering, with no cluster. `test/scripts/test-chart-render.sh` already asserts seccomp, read-only root, labels and what stays off the Pod template for the other two charts; this chart is not in it.
- **CI:** the lint job runs `make test-stand-files` before `helm lint`, which is correct. No CI job enforces the restricted standard on a namespace.

## Item 4: names by content, not by position

`helm-templates/authz-test-stand/values.yaml:11` says "Keycloak has its own image and pull policy below", which points to it by position. Naming it ("under `idp`") would be clearer; this is a matter of preference. The test case names are all named by what they test. Nothing else found.

## Item 5: the failure report

None. Every `t.Errorf`/`t.Fatalf` prints both the actual and the expected values. The table cases are named by content, not by index.

## Item 6: what the writer says it verified

Neither the commits nor any report state a run that fails on the base commit or a mutation verdict, for the pipstub tests or the chart.

## Item 7: siblings of the change

- **The other two charts.** `authz-agent` and `authz-policy-admin` keep `managed-by` (and the session id) off the Pod template; the render script asserts this. The test-stand chart puts `managed-by` and `helm.sh/chart` on the Pod template (see item 3, point 4).
- **Read-only root filesystem.** The product charts turn it on for Kubernetes only. The test stand turns it on everywhere. This does not apply as a defect: my read-only runs with an arbitrary uid show the stub images work.
- **Keycloak image pins.** The two places that name the Keycloak image (`values.yaml:21` and the SVT compose) now pin the same digest.
- **`handleReset`.** It clears the counters, including the one for `*`, and keeps the routes, the same as for any other route. Nothing to fix.
- **Callers of `counters[...]`.** There are two (`main.go:246` and `:250`), both changed. Done.

## Findings

| Finding | Label | File:line | Requested change |
|---|---|---|---|
| Clusters set up before this change fail at `helm upgrade --install` (ownership conflict on keycloak, pip-stub, idp and others) | Substantive | `Makefile` `e2e-harness`/`parity-harness`; `docs/local-integration-tests.md` | Document the one-time fix (`make e2e-down` or delete the namespaces), or run it once on an old cluster |
| No test for the restricted-PSS, labels and selector claims | Substantive | `helm-templates/authz-test-stand/templates/*`; `test/scripts/test-chart-render.sh` | Render this chart in the script and assert both securityContexts, the `/tmp` emptyDir and the labels. Optionally label the kind namespaces `enforce=restricted` |
| "Route with no responses and no default route → 404" not tested | Substantive | `test/integration/pipstub/main_test.go:492-500` | Add the case to the table |
| `requestUri` JSON name not asserted | Substantive | `main_test.go:533` | Read the record back through `handleCalls` and check the `requestUri` key |
| `profile.jq` and the duplicate checks never run (no user files exist) | Substantive | `build/authz-agent-transfer/Dockerfile:322-329`, `profile.jq` | Add a check that runs the stage, or the jq, on a sample with an unnamed user and a duplicate |
| Default-route comments leave out the "route with no responses" case | Substantive | `main.go:34-37`, `:122-123` | Add "or whose route has no responses" |
| Docs say `e2e-harness` installs the suite Job | Substantive | `docs/local-integration-tests.md:104` | Drop "and the suite Job" |
| `activeDeadlineSeconds` equals the fixed `helm test --timeout 15m`; raising it does nothing | Substantive | `values.yaml:99`, `Makefile` `run-suite`, chart README step 3 | Derive the helm timeout from the Job deadline plus a margin, or document the pair |
| Chart version and `managed-by` on the Pod template restart Keycloak on every upgrade, unlike the sibling charts | Substantive | `templates/_helpers.tpl:7-15` | Use a separate, smaller label set for Pod templates |
| No test for a rule combined with a default route | Substantive | `main_test.go` | Add a case with a matching rule and `*` set |
| SVT Keycloak re-pin and `mt-a` users not in any commit message | Substantive | `test/svt/common/compose/docker-compose.yml:3`; `parity-realm.json` | Mention them in the message of `8b85515` |
| "prints the log only at the end" is false without `--logs` | Taste | `Makefile` `run-suite` comment | Say `helm test` prints no log unless given `--logs` |
| Comments describe history ("as before", "before the default route existed") | Taste | `main.go:31-32`, `:37-38` | State the current behaviour |
| Realm list leaves out the tenant realms | Taste | `test/k8s/authn/REALM-DESCRIPTION.md:83` | List all four, or say "the realms of `authn/`" |
| "below" refers by position | Taste | `values.yaml:11` | "under `idp`" |
| `kubectl wait --for=create` needs kubectl 1.31 or later; not documented | Taste | `Makefile` `run-suite`; docs prerequisites table | State the minimum kubectl version |

Not checked: I did not run the kind suites, deploy to a cluster, run a release, run `test-chart-render.sh`, or do a style-only pass over the prose.

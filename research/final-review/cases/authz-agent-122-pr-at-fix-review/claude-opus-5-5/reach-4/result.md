# Final review: `58316ca..HEAD` (four commits)

There was no task statement, so I took the claimed cases from the four commit messages and the test comments. No previous report exists. I loaded `test-authoring` (with `references/go/testing.md`) and `english-developer-style`. The drift script printed nothing because it only parses Java, Kotlin, Groovy and Scala files. I checked the Go members, the YAML and Makefile comments, and the docs by hand.

## Item 1: comments consistent with the code and with each other

I read every changed comment against the code: the pip-stub package comment, `defaultRoute`, `callRecord.RequestURI`, the handler's step 2 comment, `LoadConfig`, the testify Dockerfile, the Makefile target comments, the chart templates and values, all eight READMEs and docs pages, and `REALM-DESCRIPTION.md`.

- **`test/integration/pipstub/main.go:34-35` and `:122-123`** say the default route answers "every request whose path has no route of its own". `handlePIP` (`:236-238`) also sends a path to it when its own route has no responses. A reader would expect such a path to get 404.
- **`docs/local-integration-tests.md:111`** says `e2e-harness` installs "… and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test`, so `helm upgrade --install` never creates it. The matching row in `test/k8s/README.md:56` correctly leaves it out.
- **`README.md:59`** still says "CI builds both via `.github/docker-dev-config.json`", but that file now lists five images. **`.github/docs-for-publication-task.md:77`** still says "The two-entry array".
- Narration (taste): `main.go:37-38` "as it did before the default route existed" describes history in a package comment.
- Everything else matches the code. That includes the startup-probe arithmetic (5 s × 60 = 5 min), the claim that the Job is kept for its log (only `before-hook-creation`), the "no runAsUser" note (it matches `helm-templates/authz-agent/templates/deployment.yaml:79`), the `/auth` issuer, and the profile example `R29LevelM2M`. I ran `profile.jq` on a fixture and it produced that value.

## Item 2: claimed cases covered

**pip-stub (9d25da7):**

| Claim | Test |
|---|---|
| An unrouted path gets the `*` route's answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| …"or to 404" when there is no default route | **none.** No case has a routed path with empty responses and no `*`. |
| Without `*`, an unrouted path is 404 as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| The default route serves its responses in sequence | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| "`/pip-stub/configure` now takes the path `*`" | **none.** Every test writes `routes[defaultRoute]` directly and never goes through `handleConfigure`. |
| Rules still win over the default route | **none** |

**Test stand (8b85515):**
- Off-by-default parts, Keycloak import, stubs, tenant-manager, Secret, the helm-test Job, and the `make *-harness` / `*-suite` targets: covered by the kind CI jobs `kind-e2e` and `kind-parity`.
- Every part off by default: no test. I rendered the defaults myself and got 0 objects.
- "Restarting when one [realm file] changes": no test. The checksum annotation renders.
- `make test-stand-files`: the CI `chart` job runs it. I also built the `chart-files` stage locally into the scratchpad, and it wrote the 8 expected files.
- **Merging user files and filling in profile fields, and failing on a duplicate user: no test.** `test/parity/suite/testdata/realm/` holds no `.json`, so CI never runs the merge on a user. I ran it ad hoc: the fill-in works, and a duplicate makes `jq -e` exit 1.
- parity-mt-b realm: the file exists, and no suite case uses it (grep).

**Restricted PSS (17b17fc):**
- **"The stand starts in a namespace that enforces restricted": no run or test.** No namespace carries a `pod-security.kubernetes.io/enforce` label, and `test/scripts/test-chart-render.sh` never renders this chart.
- The security-context fields and labels: no assertion. I checked them in `helm template`.

**Timeouts and docs (5dcb6be):**
- `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`: CI uses the 15m default. A raised value is untested, which is acceptable because it is a pass-through.
- The `make e2e-down` remedy: it runs `kind delete cluster`, so it works on any old state.

**Commands the change tells someone to run:**

| Command | Where it runs |
|---|---|
| `make test-stand-files` | CI `chart` job, and my local run |
| `docker build … -f build/authz-agent-transfer/Dockerfile .` | Dev CI, through `docker-dev-config.json` (same file and context) |
| `docker create/cp/rm` (chart README) | none. `docker create` takes the explicit `true` on a scratch image and does not execute it; no risk found. |
| `helm upgrade --install … ./charts/authz-test-stand --set TAG=<version>` | none. It depends on the published image names, and those match `docker.cfg`; no risk found. |
| `helm test --timeout 15m` then `kubectl logs job/parity-suite` | `make *-suite` runs `helm test --timeout`, but streams with `logs -f` during the run instead of reading the log afterwards. In both Helm 3 and 4 the Job and its Pod stay after the test, because there is no `hook-succeeded` policy and no `ttlSecondsAfterFinished`. No finding. |
| The `helm upgrade --reuse-values --set suite.env.RUNTIME_SUITE_RUN=…` subset recipe (docs) | none. `TestCheckResource` exists as a suite method, and the `$(RUNTIME_SUITE_RUN)` expansion is exercised by CI with the default value. No finding. |

**Hunks no sentence of the commit messages claims:**
- `.github/docker-dev-config.json`: the commit only says the *release* publishes three new images through `docker.cfg`. This hunk adds them to every dev CI build.
- `test/svt/common/compose/docker-compose.yml`: Keycloak moves from 26.0 to a pinned 26.3.5, and no SVT run is mentioned.
- `test/k8s/parity/idp-seed/parity-realm.json`: +318 lines of new clients (`parity-m2m-tenant-{a,b,unknown,empty}`, `parity-end-user-tenant-a`), users (`parity-r29-scope`, `parity-r30-scope`, `mt-a`, `mt-a-admin`) and roles. The message only claims the parity-mt-b realm, and no case uses these yet.
- `test/k8s/authn/REALM-DESCRIPTION.md`: corrects the issuer to `/auth`. The old manifest already used `/auth`, so this fixes a stale doc rather than following a code change.

## Item 3: boundaries, partitions, and the negative control

**pip-stub partitions:**
- The negative control (no `*` → 404) is present.
- An empty default route is present.
- Missing: an empty routed path with no default route, and a rule matching while `*` is set.

**State left by the old harness:** `make e2e-down` removes all of it. This is documented in `test/k8s/README.md:47-49` and `docs/local-integration-tests.md:190`. Two gaps:
- The troubleshooting row's symptom names `make e2e-harness` **or** `make parity-harness`, but its action says only "then `make e2e`".
- `test/parity/README.md`, the page parity readers follow, has no note at all.

**Values that `E2E_HELM_ARGS` now also passes to the test-stand chart:** `TAG` and `IMAGE_PULL_POLICY` are the only keys the stand shares with the agent and policy-admin charts. Any value that works for the agent (for example `local/authz-agent:<tag>`, or `Never`) needs the same of the stand's local images. Nothing new breaks, so there is no finding.

**Limits on how long a suite can run, from the start of the suite:**

| Limit | Where it is set | Default |
|---|---|---|
| Go `-test.timeout` | `suite.args` in `values.yaml:95-96` and `test/k8s/test-stand-values.yaml:55-56` | 600s |
| Job `activeDeadlineSeconds` | `values.yaml:99` | 900s |
| `helm test --timeout` | Makefile `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT`; chart README | 15m |
| CI job `timeout-minutes` | `integration-tests.yaml:120,168`, counted from job start, so not strictly the same limit | 30 min |

Two findings come out of this table:
- **The 600s Go timeout caps the setting the change documents.** `Makefile:49-50`, `helm-templates/authz-test-stand/README.md:69-70` and the 5dcb6be message tell a longer suite to raise `activeDeadlineSeconds` and the helm wait. With the default `args`, the suite still panics at 10 minutes.
- **The Job deadline does not fire before helm gives up.** 900s equals 15m, and helm's clock starts before the Job's. Helm's "timed out" therefore arrives first and hides the Job's `DeadlineExceeded`. Today the 600s Go timeout fires before both, so this only shows when the hang happens outside the test binary, such as a Pod stuck in `Pending`.

## Item 3a: level, placement, and the environment

- The pip-stub tests are small and in-process. They sit in `main_test.go` beside the existing `TestHandlePIP_*` tests and share `resetState`. `go test` in `test/integration/pipstub` passes.
- The chart has a repository-standard place for offline checks, `test/scripts/test-chart-render.sh`, and it gets no assertion for this chart: security context, labels, the `/tmp` `sizeLimit` derived from the limits, the realm checksum, and the `fail` messages.
- The restricted-PSS behavior only exists across the API-server boundary, and no CI job enforces it (the item 2 finding).
- `helm lint` with both stand value files passes on a scratch copy of the chart with its files in place.

## Item 4: names by content, not by position

No ordinals in test names or table rows. Taste: `values.yaml:21` says "Keycloak has its own image and pull policy below"; naming `idp.image` and `idp.imagePullPolicy` would be clearer.

## Item 5: the failure report

None. The table-driven test prints `GET %s = %d %s, want %d %s`, which gives the input, what came back and what was wanted. The sequence test prints both slices, and the request-target test prints both fields against their expected values. Case ids are condition names, not indices.

## Item 6: what the writer says it verified

No red run on the base commit and no mutation verdict are stated for the pip-stub tests. Reading the base code, `a_routed_path_with_no_responses_gets_the_default_answer` would panic at index −1 there, but nobody has shown that run. The Helm 3.22.1 and 4.3.1 behaviors of `--logs` are stated in the 5dcb6be message as observed. Nothing in the repository records them, and I could not reproduce them without a cluster.

## Item 7: siblings of the change

- `run-suite` is used by both suite targets, and the timeouts reach both.
- `e2e-logs`, `parity-logs` and `E2E_LOCAL_DEPLOYMENTS` still name Deployments the chart creates.
- No reference to any deleted manifest, `m2m-credentials`, `keycloak-realms`, `parity-realms` or `pip-mock-config` remains (grep).
- The rule engine's `respondSequence` already guards the empty case (`main.go:275`), so the −1 defect has no sibling there.
- **The set of Makefile override variables grew** by `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`, but the list in `test/k8s/README.md:66-71` names the old members only.
- The image count has gone stale in two places (item 1).
- The remedy rows cover only one of two paths (item 3).

## Findings

| # | Finding | Label | File:line | Request |
|---|---|---|---|---|
| 1 | Go's `-test.timeout 600s` caps how long a suite can run; the docs and commit name only `activeDeadlineSeconds` and the helm wait | Substantive | `Makefile:49-50`, `helm-templates/authz-test-stand/README.md:69-70` | Name `-test.timeout` in `suite.args` as the third limit, or derive the limits from one another |
| 2 | Helm's 15m wait equals the 900s Job deadline and starts earlier, so helm's timeout hides `DeadlineExceeded` | Substantive | `Makefile:51-52`, `values.yaml:99`, README `:65` | Give helm a wait longer than the deadline by default (for example 16m), and say "longer than" |
| 3 | No run or test shows the stand starts under the restricted PSS; no render assertion for this chart | Substantive | `Makefile:90,155`; `test/scripts/test-chart-render.sh` | Label the kind namespaces `pod-security.kubernetes.io/enforce=restricted` so CI runs the claim, or add render assertions |
| 4 | The user-file merge, the profile fill-in, and the duplicate-user failure never run on a user | Substantive | `build/authz-agent-transfer/Dockerfile:338-353`, `profile.jq` | A fixture run with one user file and one duplicate (a script test or a CI step) |
| 5 | Missing pip-stub cases: empty routed path with no `*` → 404; `*` registered through `/pip-stub/configure`; a rule beats `*` | Substantive | `test/integration/pipstub/main_test.go:225-259` | Add the table row, plus one test through `handleConfigure` and one with a rule set |
| 6 | The default-route comments leave out "a path whose route has no responses" | Substantive | `test/integration/pipstub/main.go:34-35,122-123` | Add that case to both sentences |
| 7 | The `e2e-harness` row says it installs the suite Job and waits until it is Ready | Substantive | `docs/local-integration-tests.md:111` | Drop the Job from the row, or say the release only holds the test hook |
| 8 | The ownership-metadata remedy names `make e2e` only, and the parity README has no note | Substantive | `docs/local-integration-tests.md:190`; `test/parity/README.md` | "then `make e2e` or `make parity`"; add the note to the parity README |
| 9 | The override-variable list leaves out the two new timeouts | Substantive | `test/k8s/README.md:66-71` | Add `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` |
| 10 | Stale image counts: "builds both", "two-entry array" | Substantive | `README.md:59`; `.github/docs-for-publication-task.md:77` | Update both to the five entries |
| 11 | Unclaimed hunks: dev CI publishing three images, the SVT Keycloak bump, the parity-realm additions, the issuer correction | Substantive | `.github/docker-dev-config.json`; `test/svt/common/compose/docker-compose.yml:4`; `test/k8s/parity/idp-seed/parity-realm.json`; `REALM-DESCRIPTION.md` | A sentence for each (with an SVT run for the bump), or move them to their own change |
| 12 | `kubectl wait --for=create` needs kubectl 1.31 or later; with an older kubectl the suite log is not streamed | Substantive | `Makefile:202`; `docs/local-integration-tests.md:37` | State the minimum version in the prerequisites table |
| 13 | A package comment narrates history ("as it did before the default route existed") | Taste | `test/integration/pipstub/main.go:37-38` | State the current behavior only |
| 14 | "below" where the thing has a name | Taste | `helm-templates/authz-test-stand/values.yaml:21` | "under `idp`" |

**Not checked:** I did not run the kind suites, any Helm 3 command, or a cluster with restricted enforcement. I ran `go test` for pip-stub only, did not do a style pass over the prose, and checked the commit messages' Helm-version claims only by reading.

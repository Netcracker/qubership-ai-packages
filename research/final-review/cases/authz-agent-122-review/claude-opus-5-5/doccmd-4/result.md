# Final review: `58316ca..HEAD` (3 commits)

**Inputs.** There was no task statement, so the claimed cases come from the three commit messages and the comments above the tests. The drift script printed nothing: it parses only Java, Kotlin, Groovy and Scala. I checked the changed Go members in `test/integration/pipstub/main.go` by hand. The repo's `AGENTS.md` has no test-stack line. I'd propose adding one: `Tests: Go testing engine and assertions; testify in test/integration/testify`.

## Item 1: comments consistent with the code and with each other

- **Package doc and the `defaultRoute` doc (`pipstub/main.go:34-38`, `:122-123`).** Both say the default route answers "every request whose path has no route of its own". The code (`main.go:235`) also sends a path whose route has an empty `Responses` list to the default route. The commit message says so, but neither comment does. A reader would expect such a path to get 404 or its own empty answer.
- **`pipstub/main.go:37-38`.** "…answers an unrouted request 404, as it did before the default route existed" describes the change, not the code. `english-developer-style` (around lines 190-193) allows past tense only in a regression test's comment.
- **Comments in `parity-realm.json:30` and `:34`.** The role descriptions cite "the two-tenant cases (TestTenantScopedDecisions and others)" and "the wildcard policy of tenant A". `git grep` finds no `TestTenantScopedDecisions` and no policy that names `ROLE_MT_*` anywhere in the repo. The comments describe tests and policies that don't exist.
- **`docs/local-integration-tests.md`, `e2e-harness` row.** It says the target installs "… and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test`, so an install doesn't create it. `test/k8s/README.md` says so correctly ("installing the stand does not start it"). The two documents now contradict each other.
- **`RequestURI` field comment, `callRecord`, `LoadConfig` and the `testify/Dockerfile` comment, `values.yaml` part comments, `_helpers.tpl` comments.** I checked each against the rendered output (`helm template` with both values files) and found them true.

## Item 2: claimed cases covered

| Claimed case | Covered by |
| --- | --- |
| `*` answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its answer | `…/a_routed_path_keeps_its_own_answer` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| …**or to 404** (the old index −1 defect, with no default route) | **none**: both 404 rows use an *unrouted* path |
| No `*` configured → 404 as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| The default route serves its sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `/pip-stub/configure` **takes** `*` | **none**: the tests write `routes` directly; `handleConfigure` has no test |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| Chart parts off by default | none in the repo (I rendered the defaults: 0 objects) |
| Keycloak restarts when a realm file changes | none (CI always starts from a fresh install) |
| `test-stand-files` merges user files and fills profile fields; fails on a duplicate | **none**: `testdata/realm/` holds no `*.json`, so CI never runs the merge, the profile or the duplicate check. I ran `profile.jq` by hand and it gives `R29LevelM2M` as claimed |
| `parity-mt-b` realm, new tenant clients and users | **none**: nothing in the repo uses them |
| Stand starts under restricted PSS | **none**: no namespace in CI or the Makefile enforces it. I checked the rendered fields by hand and they comply |
| `app.kubernetes.io/*` and `helm.sh/chart` on every object, `app:` selectors kept | none in the repo (I checked them by rendering) |
| Release publishes three more images | config only |

**Commands the change documents, and what runs them:**

| Command | Promised outcome | Same form run by |
| --- | --- | --- |
| `make test-stand-files` | writes `files/` | CI `chart` job ✓ |
| `make e2e-harness` / `e2e-suite` / `parity-harness` / `parity-suite` | stand up; suite exit status | CI kind jobs ✓ (fresh cluster only) |
| `helm test authz-test-stand --timeout 15m --logs` (chart README) | prints the suite log; exits non-zero on failure | **none** |
| `docker create … true; docker cp …:/charts` (chart README) | charts copied out | **none** |
| `helm upgrade --install … ./charts/authz-test-stand --set TAG=<version> -f my-values` | stand from published images | **none** |
| `helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false`, then `make e2e-suite` (`docs/local-integration-tests.md`) | runs a subset | **none** |

- **`--logs`.** Whether it works depends on how `helm test` handles a hook that is a Job, not a Pod. In the Helm v3.15.2 source (`pkg/action/release_testing.go:127`), `GetPodLogs` asks for the logs of a **Pod named after the hook**, here `parity-suite`. The Job's Pod is `parity-suite-<hash>`, so the call fails with "unable to get pod logs", and `helm test` then exits non-zero even when the suite passed. I could not read the Helm 4 source (CI pins v4.3.1), so that version is not verified. The Makefile avoids `--logs` and streams the log with `kubectl` instead.
- **`--reuse-values` recipe.** It depends on Helm 4 keeping the previous release's values under `--reuse-values`. Not verified.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub.** The control "a routed path keeps its own answer" is present. Missing are:
  - the routed path with an empty `Responses` list and **no** default route (the −1 corner of the base commit);
  - a rule-engine match over a configured `*` (rules should still win).
- **Restricted PSS.** Only the control runs: CI's kind namespaces don't enforce anything. The corner the commit fixes, a namespace labelled `pod-security.kubernetes.io/enforce=restricted`, never runs.
- **State an earlier version left behind.** A developer's existing kind cluster holds the objects the old Makefile created with `kubectl apply`:
  - Deployments and Services `keycloak`, `pip-stub`, `idp`, `pip-mock`, `entitlements-mock`, `tenant-manager`;
  - the Secret `authz-agent-client-credentials`;
  - the ServiceAccount `runtime-suite`.

  `helm upgrade --install authz-test-stand` refuses to take over objects that lack Helm ownership metadata, so `make e2e-harness` and `make parity-harness` will fail there. Every CI run starts from a fresh cluster, and no doc names the remedy (`make e2e-down`, or deleting the namespace).
- **Dropped `OVERWRITE_EXISTING`.** I checked that dropping it from the e2e Keycloak is harmless: each restart gets a fresh container filesystem and H2 database. That is not a finding.

## Item 3a: level, placement, and the environment

- **pip-stub.** The new tests are small (`httptest`), sit beside the existing tests in `main_test.go`, share `resetState`, and run in `go-build.yaml`'s matrix. `go vet` and the new tests pass.
- **Chart.** The restricted-PSS fields and the labels can be observed with `helm template`, with no cluster. The repo has a render-assertion gate, `test/scripts/test-chart-render.sh`, but it doesn't render `authz-test-stand`. CI only lints the chart. The smallest level that would catch a regression is a render assertion in that script.
- **Read-only root filesystem.** The suites write only under `/tmp`, apart from `writeObservedSidecar` in `test/parity/suite/compare.go`, which ignores errors and could not write under the root-owned `testdata/` before this change either.

## Item 4: names by content, not by position

Nothing substantive. Subtest names state the condition. `values.yaml` line 3 of the TAG comment says "its own image and pull policy below" where `idp.image` could be named instead (taste).

## Item 5: the failure report

None. Every comparison prints got and want, in got-before-want order (`GET %s = %d %s, want %d %s`; `statuses of /a, /b, /a = %v, want %v`; `requestUri %q, path %q, want %q and %q`). `t.Fatalf` is used only before indexing `calls[0]`.

## Item 6: what the writer says it verified

None of the three commits states a red run on the base commit or a mutation verdict. That matters most for the −1 defect, which has no test either, and for the PSS fix, which has no run under enforcement.

## Item 7: siblings of the change

- **`routes` and `counters`** have four other users: `handleConfigure`, `handleReset`, `loadDefaultRoutes`, and `handlePIP`. None has the defect, and `handleReset` clears the `*` counter along with the rest.
- **`matchRule`** guards its `respondSequence` index, so it doesn't have the −1 defect.
- **`PipController.ResetPinnedRoutes`** in the parity suite also works on `*`.
- **`writeRespond`'s `echo`** also reports the received request but leaves out `requestUri`. A case that needs to see the encoding through `echo` can't (follow-up, taste).
- **Security contexts.** The sibling charts `authz-agent` and `authz-policy-admin` already set restricted contexts.
- **Leftover references.** No references to the deleted manifests remain (`git grep`).

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Upgrading an existing kind stand fails, because the objects `kubectl` created can't be taken over by Helm; untested and undocumented | Substantive | `Makefile` (`e2e-harness`, `parity-harness`); `test/k8s/README.md` | Run the harness over a cluster set up by the base commit, or document `make e2e-down` / deleting the namespace and run that remedy |
| Restricted PSS is claimed but never exercised | Substantive | `helm-templates/authz-test-stand/templates/*`; `.github/workflows/integration-tests.yaml` | Label the kind namespaces `enforce=restricted` in CI, and add a render assertion to `test-chart-render.sh` for the security contexts and labels |
| `helm test … --logs` in the chart README: in the v3.15.2 source it fetches a Pod named after the Job hook and fails; Helm 4 not verified | Substantive | `helm-templates/authz-test-stand/README.md`, step 3 | Run it on the Helm versions supported, or document the `kubectl logs job/<name>` form the Makefile uses |
| No test for a routed path with no responses and no default route (the −1 defect) | Substantive | `pipstub/main_test.go:236` | Add the row "a routed path with no responses and no default route is 404" |
| `/pip-stub/configure` accepting `*` has no test through the handler | Substantive | `pipstub/main_test.go` | One test that PUTs `[{"path":"*",…}]` to `handleConfigure`, then GETs an unrouted path |
| Doc comments omit the empty-route fall-through | Substantive | `pipstub/main.go:34-38`, `:122-123` | Add "or whose route has no responses" |
| Realm descriptions cite a nonexistent `TestTenantScopedDecisions` and a tenant-A policy that doesn't exist | Substantive | `test/k8s/parity/idp-seed/parity-realm.json:30,34` | Drop the citations, or land the cases with the fixture |
| `parity-mt-b` realm and the new tenant clients and users have no consumer; the commit message mentions only the realm | Substantive | `test/k8s/parity/idp-seed/*` | Land them with the cases that use them (as the commit does for the pip-stub instance), or name them as follow-up |
| The user merge, profile fill and duplicate check never run, because there are no user files | Substantive | `build/authz-agent-transfer/Dockerfile:37-45` | A fixture user file (or a script test) that the build merges, plus one with a duplicate that must fail |
| Docs say `e2e-harness` installs the suite Job | Substantive | `docs/local-integration-tests.md` (`e2e-harness` row) | Remove "and the suite Job" |
| Documented commands never run: `--reuse-values` subset recipe, transfer-image `docker create/cp`, published-image install | Substantive | `docs/local-integration-tests.md`; chart README | Run each once on kind with Helm 4.3, or say they are not verified |
| Comment narrates the change ("as it did before the default route existed") | Taste | `pipstub/main.go:37-38` | State the present behavior only |
| The TAG comment lists the images that use TAG but leaves out the runtime suite image | Taste | `values.yaml` (TAG comment) | Say "the images of `pipStub`, `tenantManager`, and `suite`" |
| `echo` responses carry no `requestUri` | Taste | `pipstub/main.go` (`writeRespond`) | Follow-up, if a case needs it |

I did not check a cluster run (none was available), the Helm 4 `--logs` behavior, the uid the Keycloak and base images declare, OpenShift SCC admission, or the prose for style alone; I ran only the new pip-stub tests, not the full suites.

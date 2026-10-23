# Final review: `58316ca..17b17fc` (three commits)

There was no task statement, so the claimed cases come from the three commit messages and the test comments. No earlier report of this form exists. The drift script ran but printed nothing, because it parses only Java, Kotlin, Groovy, and Scala. I checked Item 1 by hand over the Go file, the templates, the Dockerfiles, and the docs. Under test-authoring §0: `AGENTS.md` has no stack line. I propose this one, and I have not edited any file: `Tests: Go testing as engine and assertions (testify in test/integration/testify); chart render assertions in test/scripts/test-chart-render.sh`.

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:34-35`**: the new paragraph says the default route answers "in sequence like any other route". The bullet at `:19-20` says "Responses are served sequentially per path". A reader would expect each unrouted path to start its own sequence. In fact `"*"` has one counter that every unrouted path shares. `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` asserts exactly this (`/a, /b, /a` → `503, 200, 200`).
- **`main.go:36`**: "No request path is *, so it never shadows a real route." The route can't shadow anything because the default is looked up only after a miss, not because no path is `*`. On its own `handlePIP` would see `Path == "*"` for `OPTIONS *`; only `ServeMux` rejects that with 400 first. *Taste.*
- **`main.go:37-38`**: "as it did before the default route existed" narrates the change in a package comment (Item 1 rule).
- **`docs/local-integration-tests.md`, the `e2e-harness` row**: says the target installs "… and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` and is not created at install. `test/k8s/README.md` says the opposite ("installing the stand does not start it"), and so does that file's own `e2e-harness` row.
- **`helm-templates/authz-test-stand/README.md:8`** and the commit message say "Every Pod runs as the non-root user its image names". `_helpers.tpl` says that on OpenShift the restricted SCC assigns a uid from the namespace range. On the platform the commit names, the README sentence is false.
- **`_helpers.tpl`, the `podSecurityContext` comment**: "rejects a pinned one". `restricted-v2` rejects a pinned uid only when it is outside the range. *Taste.*
- **`test/parity/README.md`, Identity provider**: "The `parity` realm it imports also holds the users of `suite/testdata/realm/`, so the cases that need those users run…". That directory holds only a README. The commit message says "none so far"; the README reads as though users and cases exist.
- Checked and consistent: the `callRecord.RequestURI` comment, the `defaultRoute` comment, the test comments, the labels and containerSecurityContext helper comments, the `idp.yaml` Keycloak comment, the `suite.yaml` `/tmp` comment, the `testify/Dockerfile` and `helpers.go` reference updates, the transfer Dockerfile header against `test/k8s/authn/` and `idp-seed/`, and the `idp-seed/README.md` users, roles, and `tenant-id` claim checked with `jq` against the JSON.

## Item 2: claimed cases covered

| Claimed case | Covered by |
| --- | --- |
| An unrouted path gets the default answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its answer | `…/a_routed_path_keeps_its_own_answer` |
| No `*` configured → 404 as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| A route with no responses falls through to the default | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| A route with no responses falls through **"or to 404"** (the base panicked at index −1) | **No test.** The 404 case with an empty default route uses an unrouted path; no row has a routed path with `[]` and no default route |
| `/pip-stub/configure` **takes the path `*`** | **No test through `handleConfigure`.** Every test writes `routes[defaultRoute]` directly, so the wire form the parity cases will send is not exercised |
| The default route answers in sequence | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| Rules take precedence over the default route (package comment) | **No test.** `TestHandlePIP_RuleThenLegacyFallback` has no `*` route |
| Chart parts off by default | No test. I ran `helm template` with defaults: 0 objects |
| Keycloak imports realms at every start; restarts on change (checksum) | Import: the kind CI runs. Restart on change: no test or render assertion |
| pip-stub instances, tenant-manager map, Secret, suite as `helm test` hook, make targets | The `e2e` and `Parity on kind` CI jobs |
| `tenantManager.tenants is required` / `no realm files under …` failures | No test |
| `test-stand-files` merges user files, fills profile fields, fails on duplicates | **No test, and no input in the repository exercises it.** I ran it by hand: `parity-r29-level-m2m` → `R29LevelM2M`; a duplicate username fails `jq -e` |
| Restricted PSS: runAsNonRoot, seccomp, drop ALL, no escalation | **No run under an enforcing namespace** (Item 3a) |
| Read-only root fs on all but Keycloak | The kind CI runs, for pip-stub, tenant-manager, and both suites |
| `app.kubernetes.io/*` and `helm.sh/chart` on every object; selectors keep `app` | No committed test. I checked by hand on both values files: all 7 labels on every object; selectors `app` only |

## Item 3: boundaries, partitions, and the negative control

- **pipstub table:** the partition "routed path with empty responses, no default route" is missing. That is the input that panicked on the base commit (see Item 2).
- **Earlier state, harness switch (`8b85515`):** `e2e-cluster` reuses an existing `authz-e2e` cluster. On a cluster set up by the old `kubectl apply` harness, `helm upgrade --install authz-test-stand` meets the existing `keycloak-realms`, `authz-agent-client-credentials`, the Deployments, and the `runtime-suite` ServiceAccount. It fails with "invalid ownership metadata". The parity namespace has the same problem. Every run starts from a fresh cluster, and neither README nor `docs/local-integration-tests.md` names the remedy (`make e2e-down`, or deleting the namespace).
- **Earlier state, `17b17fc` over a release from `8b85515`:** selectors are unchanged, so the upgrade is safe as far as I can see. Not run.
- **Limits on the suite's duration:** there are three:
  - `-test.timeout 600s`, in the values `args`;
  - `suite.activeDeadlineSeconds: 900`, a documented value;
  - `helm test --timeout 15m`, fixed in the Makefile `run-suite` and in the transfer README.

  The deadline equals the helm timeout, and helm's clock starts before the Job exists. So helm times out first and reports a generic timeout instead of the Job's `DeadlineExceeded`. Raising `activeDeadlineSeconds` past 900 has no effect under `make e2e-suite`.
- **Limits on `/tmp`:** the emptyDir `sizeLimit` is derived from `suite.resources.limits.ephemeral-storage`, which is the whole container limit (256Mi). The volume limit can never fire before the Pod-level limit, which also counts logs. This is low impact: either eviction names the cause.
- **Negative control for restricted PSS:** no namespace in CI carries `pod-security.kubernetes.io/enforce=restricted`.

## Item 3a: level, placement, and the environment

- pipstub: the tests are small and in-process, beside the existing `TestHandlePIP_*` tests and on their `resetState` fixture. Good.
- Chart: `test/scripts/test-chart-render.sh` already asserts seccomp, `readOnlyRootFilesystem`, and labels for the two product charts, offline. The test-stand chart has no assertions there, so security contexts, labels, selectors, the hook annotation, and the `sizeLimit` derivation are checked only by `helm lint`.
- The restricted-PSS claim is a cluster behavior. The kind jobs exist but don't label the namespace for enforcement, so they don't test the claim.

## Item 4: names by content, not by position

None. I checked the subtest names, the test function names, the comments, and the Makefile `run-suite` comment. Its `$(1)`, `$(2)`, `$(3)` are Make's positional parameters and are named on the same line.

## Item 5: the failure report

None. The table and record tests print got and want for every operand (`GET %s = %d %s, want %d %s`). The sequence test prints both slices. `t.Fatalf` is used only before indexing `calls[0]`.

## Item 6: what the writer says it verified

None of the commit messages states a red run on the base commit or a mutation verdict. Nothing shows that the pipstub tests or the chart changes can fail. I did not run the suite on the base commit to supply that evidence.

## Item 7: siblings of the change

- **`routes`/`counters` lookups:** `handlePIP` is the only reader. `handleReset` clears `counters`, including `"*"`. `loadDefaultRoutes` doesn't touch `*`. No sibling has the defect.
- **Read-only filesystem and the Qubership base entrypoint:** `authz-policy-admin/templates/deployment.yaml:133-137` notes that the base entrypoint rebuilds the CA store when it finds certificates under `/tmp/cert` or the service-account mount. Every test-stand Pod sets `automountServiceAccountToken: false` and mounts nothing at `/tmp/cert`, so this doesn't apply. The pip-stub and suite images use the older `core-base:2.4.2`, which I could not inspect offline.
- **Product charts:** they keep the root filesystem writable on OpenShift "as on the platform's charts". The test stand makes it read-only everywhere. That is a decision, not a defect, but neither comment mentions the difference.
- **Parity suite writes:** `test/parity/suite/compare.go:145-146` writes `.observed.json` under the root-owned `testdata/` and ignores the error. It already failed for uid 10001 before this change, so nothing changes.
- **`activeDeadlineSeconds`/`--timeout` pair:** it appears in two places, the Makefile and the transfer README. Both are reported above.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Empty routed responses with no default route (the base panic) has no case | Substantive | `test/integration/pipstub/main_test.go:236` | Add the row: `/routed` with `[]`, no default → 404 |
| `configure` accepting `*` is not tested through its endpoint | Substantive | `main_test.go:225` | One test that PUTs `[{"path":"*",…}]` to `handleConfigure`, then GETs an unrouted path |
| Rule-over-default precedence untested | Substantive | `main.go:29-31` | A case with a matching rule and a `*` route that expects the rule's answer |
| "in sequence like any other route" reads as per-path; the sequence is shared | Substantive | `main.go:34-35` (and `:19-20`) | Say that every unrouted path draws from the default route's one sequence |
| "as it did before the default route existed" narrates the change | Substantive | `main.go:37-38` | State the current behavior only |
| Docs say `e2e-harness` installs the suite Job and waits for it | Substantive | `docs/local-integration-tests.md`, `e2e-harness` row | Drop the Job, or say it is a `helm test` hook created by `e2e-suite` |
| "runs as the non-root user its image names" is false on OpenShift | Substantive | `helm-templates/authz-test-stand/README.md:8` | Add the OpenShift uid assignment, as `_helpers.tpl` does |
| Parity README implies `testdata/realm/` users and cases exist | Substantive | `test/parity/README.md`, Identity provider | Add "none so far", as in the commit |
| `profile.jq` merge, fill-in, and duplicate check are exercised by nothing | Substantive | `build/authz-agent-transfer/Dockerfile:39-45` | A fixture user file in a test build, or a CI step running the stage on one |
| Helm install over a cluster left by the old harness fails with no documented remedy | Substantive | `Makefile:85,149`; `test/k8s/README.md` | Document `make e2e-down` (or deleting the namespace) for clusters from the old harness, or run it once |
| `helm test --timeout 15m` equals `activeDeadlineSeconds: 900` and caps it | Substantive | `Makefile` `run-suite`; `values.yaml` `suite.activeDeadlineSeconds`; transfer README step 3 | Derive the helm timeout from the deadline plus a margin, or document the pair |
| emptyDir `sizeLimit` equals the whole container ephemeral limit, so it can't fire first | Substantive (low impact) | `templates/suite.yaml`, last line | Set it below the limit, or document that the Pod limit governs |
| No run in a namespace that enforces `restricted` | Substantive | `.github/workflows/integration-tests.yaml`; `Makefile` harness targets | Label the kind namespaces `pod-security.kubernetes.io/enforce=restricted` before install |
| Test-stand chart has no render assertions; siblings have them | Substantive | `test/scripts/test-chart-render.sh` | Assert pod/container security contexts, the labels, `app`-only selectors, and the hook annotation |
| "No request path is *, so it never shadows" gives the wrong reason | Taste | `main.go:36` | The default is consulted only after a miss |
| "rejects a pinned one" overgeneralizes `restricted-v2` | Taste | `_helpers.tpl`, `podSecurityContext` comment | "rejects a uid outside the range" |

What I did not check: I ran `go test` for pipstub (green), `helm lint` and `helm template` on both values files with stand-in `files/`, and `jq` on `profile.jq`. I did not run the kind suites, any cluster admission, the transfer image build, or the tests on the base commit. I did not do a style-only pass over the prose.

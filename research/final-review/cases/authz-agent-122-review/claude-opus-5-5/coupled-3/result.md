# Final review: `58316ca..HEAD` (three commits)

There was no task statement, so the claimed cases come from the three commit messages, the comments of the new tests, and the comments the change added or edited. No earlier report of this form exists, so there is no table of carried-over findings.

What I ran:
- **Drift script:** it ran and printed nothing. It only parses `.java`, `.kt`, `.kts`, `.groovy` and `.scala` files, so I did item 1 by hand for the Go, Helm, Makefile and Markdown files.
- **Chart:** I ran `helm lint` and `helm template` with both harness values files on a scratchpad copy of the chart with stand-in `files/`. Both passed. The rendered output has the restricted fields on every workload (5 in the e2e render, 4 in the parity render), and a render with default values is empty.
- **pip-stub:** `go test ./...` in `test/integration/pipstub` passes.
- **Profile filter:** I ran `profile.jq` on its own documented example, and it produces `R29LevelM2M`.
- **Skills:** I loaded `test-authoring` and `english-developer-style`.

Per `test-authoring` §0: `AGENTS.md` has no stack line. The proposal is `Tests: Go testing (engine and assertions) for test/integration/pipstub; testify suites in test/integration/testify; chart behavior through test/scripts/test-chart-render.sh`. Nothing was edited.

## Item 1: comments consistent with the code and with each other

1. **`_helpers.tpl:2-4` gives a reason that isn't true.** It says the selectors keep `app: <name>` "so the Makefile's deploy/<name> and a reader's kubectl -l app=<name> address a part by its Service name".
   - `deploy/<name>` finds a Deployment by its name, not by its selector.
   - Nothing in the repository uses `-l app=` (I checked with `git grep`).
   - The real constraint goes unsaid: a Deployment's selector can't be changed after creation, so changing it breaks `helm upgrade` on an existing stand.
   - A reader could conclude the selector is free to change once the Makefile stops using `deploy/`.
2. **`README.md:8` and the commit message disagree with `_helpers.tpl:18-21`.** The README says "Every Pod runs as the non-root user its image names". The helper comment, correctly, says OpenShift's restricted SCC assigns a uid from the namespace range. So the README sentence is false on OpenShift, a platform the change says it supports.
3. **`values.yaml:9-11` leaves an image out of its list.** It lists "pip-stub, authz-parity-suite, and tenant-manager" as the images `TAG` applies to. The e2e values run `local/authz-runtime-suite` under the same `TAG`, through `suite.imageRepository`. In fact `TAG` applies to whatever suite image is configured.
4. **`pipstub/main.go:37-38` narrates the change** ("as it did before the default route existed"). The statement is true; dropping the clause loses nothing. Taste.
5. **`pipstub/main.go:18-19` reuses the word "default".** It says "the hardcoded defaults" (`loadDefaultRoutes`), while the new text introduces "the default route" (`defaultRoute`). A reader can take `loadDefaultRoutes` to be the function that registers `*`, which it doesn't. Taste.

Checked and consistent: the `callRecord.RequestURI` comment, the `defaultRoute` const comment, the precedence paragraph against `handlePIP`, the startup-probe "allows five" (5 s × 60), the suite.yaml hook comment, and the `idp.yaml` comment about the writable root filesystem.

## Item 2: claimed cases covered

| Claimed case | Test |
|---|---|
| `*` answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an unrouted path gets the default answer` |
| A routed path keeps its own answer | `…/a routed path keeps its own answer` |
| No default route → 404, as before | `…/an unrouted path without a default route is 404`, and `TestHandlePIP_RuleThenLegacyFallback` (`/nope`) |
| An empty default route → 404 | `…/an unrouted path with an empty default route is 404` |
| A route with no responses falls through to the default route | `…/a routed path with no responses gets the default answer` |
| **A route with no responses falls through "or to 404"** | **None.** This is the input that indexed at -1 on the base commit: a routed path with `[]` and no `*` |
| **"/pip-stub/configure now takes the path *"** | **None.** Every test writes `routes[...]` directly, and none goes through `handleConfigure` |
| **Rules take precedence over the default route** (package comment) | **None.** `RuleThenLegacyFallback` has no `*` route |
| The default route serves its sequence across paths, clamped | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| Restricted PSS: runAsNonRoot, RuntimeDefault, drop ALL, no escalation, read-only root except Keycloak, `/tmp` emptyDir, no runAsUser | **None.** I only checked them by rendering for this review |
| `app.kubernetes.io/*` and `helm.sh/chart` labels; selectors keep `app` | **None** |
| Chart parts off by default | **None** in the repository; I checked the empty render by hand |
| Keycloak restarts when a realm changes (`checksum/realms`) | **None** |
| Realm merge fills in profile fields; the build fails on a duplicate user | **None.** `testdata/realm/` holds no user files, so CI never runs the merge, the profile filter, or the duplicate check on a user |
| Harness targets (`e2e-harness`, `parity-harness`, `*-suite`) | The `kind-e2e` and `kind-parity` CI jobs; no green run is cited |

## Item 3: boundaries, partitions, and the negative control

- **pip-stub response counts:** 0, 1 and 2 responses and the clamp are all covered. The missing combinations are the ones in item 2: a routed path with `[]` and no default, and a rule together with a `*` route.
- **No negative control for restricted PSS.** `make e2e-harness` and `make parity-harness` use `--create-namespace` and never set the `pod-security.kubernetes.io/enforce=restricted` label. Nothing fails if a later container drops its `securityContext`, and nothing shows the stand actually starts under the standard the commit names.
- **State left behind by the earlier setup.** `e2e-cluster` reuses an existing kind cluster. On a developer's cluster, the objects the old loose manifests created with `kubectl apply` are still there (`deploy/keycloak`, `pip-stub`, `tenant-manager`, the Services, the realm ConfigMap). `helm upgrade --install authz-test-stand` refuses to adopt them ("exists and cannot be imported into the current release"). Every documented run starts from a fresh cluster, and neither `test/k8s/README.md` nor `docs/local-integration-tests.md` gives the fix (`make e2e-down`, or deleting the namespace).
- **Three time limits on the same suite run, which don't fit together:**
  - `-test.timeout 600s` in `suite.args` (a documented setting).
  - `activeDeadlineSeconds: 900` in `values.yaml` (a documented setting).
  - `helm test --timeout 15m` (900 s), fixed in the Makefile's `run-suite` and in README step 3.

  Helm starts its clock before the Job exists, so at the defaults Helm's timeout fires at or before the Job's deadline, and the Job's `DeadlineExceeded` reason never shows up. Raising `activeDeadlineSeconds`, or `-test.timeout` past 900 s, has no effect under `make *-suite` or the README command.
- **emptyDir `sizeLimit`:** it is taken from the container's ephemeral-storage limit, so both are set in one place. No finding.

## Item 3a: level, placement, and the environment

- **The chart needs a render check, which is the smallest test level.** `test/scripts/test-chart-render.sh` already checks the security context of the agent chart (around lines 788-843: seccomp, read-only root per platform). The test stand's restricted settings and labels have no equivalent check, even though `helm template` can see all of them with no cluster.
- **pip-stub:** the tests are in-process, sit in `main_test.go` next to the existing tests, reuse `resetState`, and CI runs this module through `go-build.yaml`. No finding.

## Item 4: names by content, not by position

None in the change. Test and subtest names describe their cases. One older problem the change makes worse is in item 7: `pip_control.go` refers to `pipstub/main.go` by line numbers (`:50-183`, `:52`, `:110`), which were already wrong at the base commit.

## Item 5: the failure report

None. The table test uses `t.Errorf("GET %s = %d %s, want %d %s", …)` and keeps going after a failure. The sequence test prints both slices. The `requestUri` test prints all four values. No index is used as a case id.

## Item 6: what the writer says it verified

None of the commits gives evidence that the tests can fail: no red run on the base commit (the routed-empty input panicked there), and no mutation result. None of them reports a kind run of the chart, under the restricted standard or otherwise. Nothing shows that the `qubership-core-base` entrypoint starts with a read-only root filesystem.

## Item 7: siblings of the change

1. **`test/parity/suite/pip_control.go:17-31` now says false things about the stub.**
   - Caveat 3 says "No wildcards"; `*` is now one.
   - Caveat 2 says the only way to unregister a route is to re-PUT it with responses; a route with `responses: []` now falls through.
   - `ResetPinnedRoutes` (line 181) resets pinned paths to an explicit 404 response. That response now hides a configured `*` route on those paths, which matters for the User Management stub the commit says is coming.
2. **The authz-agent and authz-policy-admin charts make the root filesystem read-only only on Kubernetes.** They use `READONLY_CONTAINER_FILE_SYSTEM_ENABLED && PAAS_PLATFORM == KUBERNETES`, "as on the platform's charts". The stand sets it unconditionally, while pointing to the agent chart as its model for OpenShift. Taste: the request is to follow the agent chart or say why the stand differs.
3. **The rest checked clean:**
   - `containerSecurityContext` has 5 callers, all checked.
   - The other readers of `routes`/`counters` are fine: `handleReset` clears the `*` counter, `loadDefaultRoutes` never registers `*`, and `handleConfigure` stores paths as given.
   - The callers of `/pip-stub/calls` are the testify suites and `pip_control.go`. None decodes strictly, so the new `requestUri` field breaks nothing.

## Findings

| Finding | Label | File:line | Requested change |
|---|---|---|---|
| Restricted PSS and the labels have no render check, though one exists for the sibling charts | Substantive | `test/scripts/test-chart-render.sh` (none for the stand); `templates/_helpers.tpl:17-40` | Add test-stand blocks for both harness values files: every Pod and container carries the restricted fields; read-only root everywhere except Keycloak |
| Harness namespaces don't enforce restricted, so the commit's main claim has no control | Substantive | `Makefile:86,150` | Label the namespaces `pod-security.kubernetes.io/enforce=restricted` before the installs |
| Existing kind clusters keep the old `kubectl apply` objects, and the Helm install fails on them; no fix is documented | Substantive | `Makefile:59-86`; `test/k8s/README.md` | Document (and run once) `make e2e-down` or deleting the namespace on that state, or delete the old objects in `e2e-harness` |
| `helm test --timeout 15m` equals `activeDeadlineSeconds: 900`, so the Job's deadline never reports and raising it or `-test.timeout` does nothing | Substantive | `Makefile:102`; `README.md:64`; `values.yaml:93-99` | Derive Helm's timeout from `activeDeadlineSeconds` plus a margin, or document the three limits together |
| Routed path with `[]` and no default route (the old -1 input) is untested | Substantive | `pipstub/main_test.go:236-242` | Add a row: `/routed` with `[]`, no default → 404 |
| `*` through `/pip-stub/configure` is untested | Substantive | `pipstub/main_test.go` | One test that PUTs `[{"path":"*",…}]` to `handleConfigure`, then GETs an unrouted path |
| Rule-over-default-route precedence is untested | Substantive | `pipstub/main.go:29-31` | A matching rule beats `*` |
| `pip_control.go` caveats 2–3 are now false; `ResetPinnedRoutes` hides `*` | Substantive | `test/parity/suite/pip_control.go:17-31,181` | Update the caveats; reset with `responses: []`, or record it as follow-up in the description |
| The selector comment gives a false reason and omits the real one (immutable selector) | Substantive | `templates/_helpers.tpl:2-4` | State the immutability and `helm upgrade` reason |
| README says the image's user even on OpenShift | Substantive | `helm-templates/authz-test-stand/README.md:8` | Add "on Kubernetes; OpenShift's SCC assigns a uid" |
| `TAG` image list leaves out the runtime suite | Substantive | `values.yaml:9-11` | Say "the suite image of `suite.imageRepository`" |
| Realm merge, profile filter and duplicate check never run on a user | Substantive | `build/authz-agent-transfer/Dockerfile:39-46` | A fixture user file (or a build-time check) that runs the merge and the duplicate failure |
| No red run on the base commit and no kind run cited | Substantive | commits `9d25da7`, `17b17fc` | State the red run on the base commit and the restricted kind run in the description |
| Read-only root set unconditionally, unlike the agent chart | Taste | `templates/*.yaml` `containerSecurityContext true` | Follow the sibling's condition, or say why the stand differs |
| "as it did before the default route existed" narrates the change | Taste | `pipstub/main.go:37-38` | Drop the clause |
| "hardcoded defaults" vs "default route" | Taste | `pipstub/main.go:18-19` | Say "the built-in routes" |

Not checked: no Kubernetes cluster was available, so nothing was installed and the images were never started read-only; the CI kind jobs and the full suites weren't run; and there was no style-only pass over the prose.

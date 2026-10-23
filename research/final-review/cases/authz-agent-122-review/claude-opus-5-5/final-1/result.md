# Final review: `58316ca..17b17fc` (three commits)

There was no task statement. I took the claimed cases for item 2 from the three commit messages and from the comments above the new tests. The drift script `comment-drift.py` parses only JVM files (`EXT = .java, .kt, …`), so it printed nothing for this Go, Helm, Makefile and Markdown change. I did its job by hand: I read every changed Go comment, chart comment and doc paragraph against the code.

Commands I ran: `go test ./pipstub/` passes. `helm lint` and `helm template` pass on a scratch copy of the chart, with `files/` filled by hand from the source realms and rule files, using both harness values files and the defaults. I also ran `profile.jq` and the duplicate-user check by hand.

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:34-38`, package doc.** It says the default route answers "in sequence like any other route". The legacy bullet above it says routes serve "sequentially per path". But the default route keeps one counter (`counters["*"]`) shared by every unrouted path. `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` asserts exactly that (`/a, /b, /a` → `503, 200, 200`). A reader who configures `*` with a sequence will expect each unrouted path to start at its first response. The precedence sentence (lines 29-31) also leaves out a case the commit claims: a route with no responses falls through to the default route.
- **`main.go:31-32` and `main.go:37-38` narrate history.** "behaviour is exactly as before" is old text; the change added "as it did before the default route existed". Godoc says what the code does, not what it did before.
- **Sibling comment made false: `test/parity/suite/pip_control.go:29-30`.** Caveat 3 says "Path matching is strictly literal against r.URL.Path … No wildcards". That is no longer true of the stub: `*` is now a catch-all route.
- **`docs/local-integration-tests.md`, the `e2e-harness` row.** It says the target installs "… the client-credentials Secret, and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` (`templates/suite.yaml:21`), so install does not create it. `test/k8s/README.md` says the opposite: "installing the stand does not start it".
- **`test/parity/suite/testdata/realm/README.md:6-7`.** It says the build "fails when two files declare the same username or id". The `jq -e` check in `build/authz-agent-transfer/Dockerfile` also fails on a duplicate inside one file, or against a user of the seed realm. I confirmed this with a fixture. The sentence states the narrower condition.
- **Checked and consistent:**
  - `_helpers.tpl` labels and security-context comments match the render: every object carries all seven labels; every Pod has `runAsNonRoot` and `RuntimeDefault`; every container drops `ALL` and sets `allowPrivilegeEscalation: false`; only Keycloak has `readOnlyRootFilesystem: false`.
  - `values.yaml` part descriptions.
  - `callRecord.RequestURI` and `defaultRoute` doc comments.
  - The `LoadConfig` and Dockerfile cross-references now point to `suite.env` and `suite.args`, which exist.
  - The realm READMEs match the JSON: `mt-a` and `mt-a-admin` have the claimed roles, the `parity-mt-b` users and client are present, and `parity-m2m-tenant-b` carries the `tenant-id` claim `parity-mt-b`.
  - `REALM-DESCRIPTION.md` now has `/auth` in the issuer and matches `KC_HOSTNAME`.

## Item 2: claimed cases covered (taken from the commit messages; there was no task statement)

| Claimed case | Test or evidence |
| --- | --- |
| `*` answers a path with no route of its own | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| A route with no responses falls through to the default route, or to 404 | `…/a_routed_path_with_no_responses_gets_the_default_answer`. The "or to 404" half, for a routed path with no responses and no default route, has no row. The two 404 rows use an unrouted path. |
| A stub nobody configures with `*` answers 404 as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| The default route serves in sequence, clamped | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| The call record keeps the target as it arrived, **in `requestUri`** | `TestHandlePIP_RecordsTheRequestTargetAsSent` checks the struct field only. Nothing reads `/pip-stub/calls`, so a typo in the JSON tag `requestUri`, the name the commit gives consumers, stays green. |
| `/pip-stub/configure` takes `*` | No test goes through `handleConfigure`; the tests write `routes` directly. `handleConfigure` is unchanged and accepts any path, so this is low risk. |
| Rules still win over the default route (package doc precedence) | **No test.** `TestHandlePIP_RuleThenLegacyFallback` configures no `*`. |
| The stand starts under the restricted Pod Security Standard | **No test.** The render shows the fields. But neither kind harness labels its namespace `pod-security.kubernetes.io/enforce=restricted`, and nothing in the repository mentions `pod-security`, so CI would stay green if a Pod broke the standard. |
| Read-only root FS on every container but Keycloak; `/tmp` emptyDir for the suite | Render only (I checked by hand; no assertion in the repo). |
| App labels on every object; selectors keep `app` | Render only (I checked by hand). |
| Each part off by default | Render only: the default render is empty. |
| Realms re-imported at every start; restart on change | `checksum/realms` annotation, render only. |
| Missing files fail with the quoted message (`no realm files under …`, `no file files/pip-stub/…`) | **No test.** |
| `make test-stand-files` fills in the Keycloak 26 profile fields; a duplicate user fails the build | **No test, and no input.** `testdata/realm/` holds only a README, so CI never runs the merge path. By hand, `profile.jq` turns `parity-r29-level-m2m` into `R29LevelM2M`, and the duplicate check returns `false`. |
| Release publishes pip-stub, parity-suite and transfer images | Config only (`.qubership/docker.cfg`, `docker-dev-config.json`). |
| `parity-mt-b` realm added | Present in the generated parity directory. No case in this change uses it. |

## Item 3: boundaries, partitions, and the negative control

- **pip-stub partitions.** Covered:
  - default route absent (`nil`), empty, and with responses;
  - routed path with responses (the control, green on the base commit) and with no responses;
  - sequence clamped past its end.

  Missing:
  - a matching rule while `*` is configured (the control showing the default route does not shadow rules);
  - a routed path with no responses and no default route, which is the base commit's `-1` index defect on its own.
- **Inherited state: finding.** The old harness used `kubectl apply` to create objects with the same names as the chart's objects, in the same namespaces:
  - `authz-e2e`: Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`; ConfigMap `keycloak-realms`; Secret `authz-agent-client-credentials`; ServiceAccount `runtime-suite`.
  - `authz-parity`: `idp`, `pip-mock`, `entitlements-mock`, `pip-mock-config`, and the Secret.

  On a kind cluster from before this change, `helm upgrade --install authz-test-stand` should refuse every one of them for missing Helm ownership metadata. Every documented run starts from a fresh cluster (CI's `kind-action`), and no doc names the remedy (`make e2e-down`, or deleting the two namespaces).
- **Limits on the suite run: finding.** The limits are:
  - `-test.timeout 600s`, set in `values.yaml` and in `suite.args` of `test/k8s/test-stand-values.yaml`;
  - `suite.activeDeadlineSeconds: 900`, a documented setting;
  - `helm test --timeout 15m` (900 s), fixed in the Makefile's `run-suite` and in the chart README's install step;
  - CI `timeout-minutes: 30`, which starts much earlier, so it is not one of these limits.

  The Job deadline counts from Job start and `helm test`'s timeout from an earlier start, both 900 s. So at the defaults the Job's `DeadlineExceeded` (for example, a Pod stuck in Pending) never fires before `helm test` gives up: the outer failure hides the inner one's report. Raising `suite.activeDeadlineSeconds` past 900 has no effect, because the 15 m is fixed outside the values. The Keycloak `startupProbe` (60 × 5 s = 300 s) fires before `helm --wait --timeout 10m`; that pair is fine.

## Item 3a: level, placement, and the environment

- **pip-stub.** The tests are small, in-process, and sit in `main_test.go` next to the existing `TestHandlePIP_*`, sharing `resetState`. Placement and level are right.
- **Chart: finding.** Every chart claim of commit 3 (security contexts, labels) and of commit 1 (off by default, `required` and `fail` messages, the `/tmp` mount) can be seen with `helm template`, with no cluster. The repository already has `test/scripts/test-chart-render.sh`, which CI runs as "Render assertions". It renders only `authz-agent` and `authz-policy-admin`. CI adds only `helm lint` for the test stand, and lint checks none of these properties.
- **Cluster level: finding.** The restricted-PSS claim crosses the API-server boundary. The kind jobs that exist run without the namespace label, so they cannot fail on it.
- Not owed: Keycloak's writable root filesystem is consistent with the restricted standard, which does not require a read-only root. The parity suite writes `*.observed.json` next to its goldens and ignores the error (`test/parity/suite/compare.go:145-146`). Under a read-only root that write now fails silently. It already did as uid 10001 if the directory is root-owned, so no behavior is lost. I could not check the claim that `qubership-core-base:2.4.2`'s entrypoint writes nothing under a read-only root: the production charts note this for `alpine-2.5.8` only, and no run is stated.

## Item 4: names by content, not by position

- `helm-templates/authz-test-stand/values.yaml:11`: "Keycloak has its own image and pull policy below" could say "under `idp`". This is a nit.
- Test names and `t.Run` ids name the condition (`an_unrouted_path_with_an_empty_default_route_is_404`); no ordinals.

## Item 5: the failure report

None.
- `t.Errorf("GET %s = %d %s, want %d %s", …)` prints function, input, got and want in Go order.
- The sequence test prints `%v` of both slices.
- `RecordsTheRequestTargetAsSent` puts two comparisons in one condition, but the message prints all four operands.
- `t.Fatalf` is used only before the `calls[0]` index.

## Item 6: what the writer says it verified

None stated: no red run on the base commit for the empty-route `-1` index or the 404 fallback, and no mutation verdict. No message says a kind run of either harness was made with these commits. The commit messages state no evidence that the tests can fail, or that the stand starts under the restricted standard.

## Item 7: siblings of the change

- **`callRecord` readers** (`git grep` for `pip-stub/calls`; 3 code sites):
  - `test/parity/suite/pip_control.go` `PipStubCall` claims to mirror `callRecord` but has no `RequestURI`. Its comment says fields are "added as needed", and the commit defers the users ("comes with the cases that use it"), so this is acceptable. Its caveat 3 is wrong now (item 1).
  - `test/integration/testify/entitlements_test.go` and `pip_admin_test.go` decode the fields they use and are unaffected.
- **`writeRespond` echo** builds its own map and does not carry `requestUri`. That is not claimed, so it is not a finding.
- **`PipController.ResetPinnedRoutes`** re-pins every pinned path with a 404 response, so a future pin of `*` would turn into a catch-all 404 `{"error":"reset"}`. The status matches the unconfigured stub, so this is fine.
- **Old harness names in the Makefile:** `E2E_LOCAL_DEPLOYMENTS`, `PARITY_LOCAL_DEPLOYMENTS` and the `*-logs` `exec deploy/pip-stub|pip-mock` targets match the chart's instance names.

## Findings

| Finding | Label | File:line | Requested change |
| --- | --- | --- | --- |
| Package doc says the default route sequences "like any other route" (per path); it is shared across all unrouted paths. The precedence list omits "a route with no responses falls through". | Substantive | `test/integration/pipstub/main.go:29-38` | State the shared counter and the empty-route fall-through. |
| Caveat 3, "No wildcards", is false now that `*` exists | Substantive | `test/parity/suite/pip_control.go:29-30` | Update it in this change. |
| Doc says `e2e-harness` installs the suite Job and waits for it; it is a `helm test` hook | Substantive | `docs/local-integration-tests.md`, `e2e-harness` row | Drop the Job from the row, as `test/k8s/README.md` does. |
| Restricted-PSS claim has no test: no namespace enforces it in either kind harness | Substantive | `Makefile` `e2e-harness` and `parity-harness`; `.github/workflows/integration-tests.yaml` | Label both namespaces `pod-security.kubernetes.io/enforce=restricted` before install, so CI fails on a violation. |
| No render assertions for the test-stand chart; only `helm lint` | Substantive | `test/scripts/test-chart-render.sh` | Add assertions for security contexts, labels, default-off, the missing-files `fail` text, and the `/tmp` mount. |
| Old kubectl-created objects collide with the chart's objects; no run or documented remedy for an existing cluster | Substantive | `test/k8s/README.md`, `docs/local-integration-tests.md` | Document the remedy (`make e2e-down`, or delete the namespaces) and run it once on an old-harness cluster, or adopt the objects. |
| Job `activeDeadlineSeconds: 900` equals the fixed `helm test --timeout 15m`; the inner limit never reports, and raising the setting has no effect | Substantive | `values.yaml:99`, `Makefile` `run-suite`, chart `README.md:64` | Derive the `helm test` timeout from the deadline (plus margin), or set both in one place. |
| `profile.jq` and the duplicate-user check have no test, and CI gives them no input | Substantive | `build/authz-agent-transfer/Dockerfile`, `profile.jq` | Add a fixture user file and a check that runs the stage, or a `jq` test of `profile` and the duplicate check. |
| No test that a rule still wins with `*` configured, and none for a routed path with no responses and no `*` | Substantive | `test/integration/pipstub/main_test.go` | Add the two cases beside the existing table. |
| JSON key `requestUri` not asserted | Substantive | `main_test.go`, `TestHandlePIP_RecordsTheRequestTargetAsSent` | Read the record back through `handleCalls` and check the key. |
| No red run or verification evidence stated | Substantive | commit messages | State the red run on the base commit for the empty-route panic, and the kind runs of both harnesses. |
| "as it did before the default route existed" narrates the change | Taste | `main.go:37-38` | Drop the history clause. |
| README says only "two files" can collide | Taste | `test/parity/suite/testdata/realm/README.md:6-7` | Say any duplicate username or id in the merged realm. |
| "below" where the block has a name | Taste | `helm-templates/authz-test-stand/values.yaml:11` | "under `idp`". |

I did not run the kind harnesses or any cluster, so collision with old objects, image behavior under a read-only root, and PSS admission were judged from manifests and code. The drift script does not parse Go, YAML or Make, so item 1 was done by hand. I made no pass over the prose for style alone.

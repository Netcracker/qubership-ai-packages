# Final review: `58316ca..HEAD` (3 commits: 8b85515, 9d25da7, 17b17fc)

I found eight substantive findings. The biggest are that a kind cluster set up by the old `kubectl apply` harness will make the new `helm upgrade --install` fail, and that nothing checks the claim that the stand starts under the restricted Pod Security Standard (PSS). I changed no file in the repository.

**Inputs:**
- **Task statement:** there was none. Every claimed case below comes from the three commit messages and the comments on the new tests.
- **Previous report:** none, so this is the first round.
- **Skills loaded:** `final-review` and `test-authoring` from the given directory, with its Go reference. `english-developer-style` is not in that directory, so it was not loaded and no other copy was used. No doc-comment skill for Go (`godoc-authoring`) is in the directory either.
- **Drift script:** it ran and printed nothing. It only parses Java, Kotlin, Groovy and Scala, so I checked the Go members and the chart's comments by hand.
- **Proposed test-stack line (`test-authoring` §0):** `AGENTS.md` names no test stack. I propose adding `Tests: Go standard testing package (engine and assertions); Helm charts checked by helm lint and test/scripts/test-chart-render.sh`. Per §0, this review edits no file to add it.

## Item 1: comments consistent with the code and with each other

Go members, checked by hand: the package doc, the `callRecord.RequestURI` field comment, the `defaultRoute` const, and the step-2 comment in `handlePIP`. Chart: `_helpers.tpl`, the template comments, `values.yaml` and the READMEs.

- **`test/integration/pipstub/main.go:34-36` and `:122-123`:** both comments say the default route answers "every request whose path has no route of its own". The code also sends a request there when its route exists but has no responses (`main.go:236`). The commit message, the test comment and the test case "a routed path with no responses gets the default answer" all claim that second case. A reader of the doc would expect an empty route to answer 404 instead.
- **`helm-templates/authz-test-stand/templates/_helpers.tpl:2-4`:** the comment says the selectors keep `app: <name>` "so the Makefile's deploy/<name> … address a part". `deploy/<name>` finds the object by its name, not by a label. The real constraint goes unstated: `spec.selector` cannot be changed, so a new selector would break `helm upgrade` of an existing release. Without that, the next author has no reason not to "tidy" the selector.
- **`docs/local-integration-tests.md:104`:** says `e2e-harness` installs "… and the suite Job; waits until they are Ready". The Job is a `helm test` hook (`suite.yaml:21`), so the install neither creates it nor waits for it. `test/k8s/README.md` says the opposite: "installing the stand does not start it".
- **Narration, `main.go:37-38`:** "…answers an unrouted request 404, as it did before the default route existed" tells the history of the change inside the package doc.
- **`values.yaml:9-11`:** the list of images that take `TAG` leaves out `authz-runtime-suite`, which the e2e values run with `TAG`.
- Everything else checks out:
  - `containerSecurityContext` and the comment in `idp.yaml` agree with the chart README and the commit message about Keycloak.
  - The new `LoadConfig` and Dockerfile references point to files that exist.
  - The fixed issuer in `REALM-DESCRIPTION.md` (`/auth/realms/...`) matches what the old and new manifests set.

## Item 2: claimed cases covered

| Claimed case (source) | Test or check |
| --- | --- |
| Unrouted path answered by `*` (9d25da7) | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| Routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| A stub with no `*` route still answers 404 (pip-mock and entitlements-mock behave as before) | `…/an_unrouted_path_without_a_default_route_is_404` |
| Route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| **Route with no responses falls through to 404** (the old `-1` index) | **None.** The two 404 cases use an unrouted path, so the combination "routed with no responses, and no default route" never runs. That is the case that panicked on the base commit. |
| Empty default route answers 404 | `…/an_unrouted_path_with_an_empty_default_route_is_404` |
| The default route serves its responses in sequence | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| `/pip-stub/configure` takes `*` | Covered only indirectly: the tests write `routes[defaultRoute]` directly, but `handleConfigure` did not change and stores any path as given |
| Rules take precedence over the default route (package doc) | None. The order in the code did not change. |
| Chart parts, values, harness targets (8b85515) | `helm lint` on both values files in CI (`integration-tests.yaml`), plus the kind jobs |
| Realm restart when a file changes | No committed check. I rendered the chart twice with a realm file changed: the `checksum/realms` annotation changed. |
| **User files merged into the parity realm, profile fields filled, duplicate users fail the build** | **No committed check.** There are no user files ("none so far"), so CI only ever runs the empty input. On scratchpad fixtures the jq pipeline filled `R29LevelM2M` as the comment says and rejected a duplicate username. |
| **Stand starts under restricted PSS** (17b17fc) | **None.** No namespace carries `pod-security.kubernetes.io/enforce`, and `test-chart-render.sh` has no assertions for `authz-test-stand`. I rendered both values files: every Pod and container has `runAsNonRoot`, `RuntimeDefault` seccomp, `allowPrivilegeEscalation: false` and `drop: [ALL]`, with only configMap and emptyDir volumes. Nothing in CI would fail if one of those were dropped. |
| `app.kubernetes.io/*` and `helm.sh/chart` labels on every object, selectors kept | No committed check. My render shows all seven labels on all 22 objects and every selector matching its Pod template. |

- **Unclaimed content:** 8b85515 also adds five clients and their service-account users to `parity-realm.json` (318 lines), which the commit message does not mention.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub partitions:** the "unrouted path, no `*` route → 404" case is the control that also passes on the base commit. The missing partition is the routed-empty-and-no-default case from item 2.
- **State an earlier version left behind: substantive.** Before 8b85515, `make e2e-harness` and `make parity-harness` created Deployments, Services and the `authz-agent-client-credentials` Secret with `kubectl apply`, with no Helm ownership labels. The new targets (`Makefile:85`, `Makefile:149`) run `helm upgrade --install` against objects with the same names (`keycloak`/`idp`, `pip-stub`, `pip-mock`, `entitlements-mock`, `tenant-manager`).
  - `e2e-cluster` reuses an existing cluster, so a developer who ran the old harness will hit Helm's "exists and cannot be imported into the current release" error.
  - CI always starts from a fresh kind cluster, so it never meets this state.
  - No document names the remedy: `make e2e-down`, or deleting the two namespaces.
- **Labels change (17b17fc):** an upgrade from a release made by 8b85515 is safe, because the selectors did not change.

## Item 3a: level, placement, and the environment

- The pip-stub tests run in one process through `handlePIP`, sit in `main_test.go` beside the existing tests and share `resetState`. CI runs them through the `go-build.yaml` matrix. `go test ./...` passes locally.
- The restricted-PSS behavior only shows up at admission, which is a cluster boundary. The kind jobs exist but run in namespaces that enforce nothing, so the test that would observe the claim does not run.
  - Request: label the kind namespaces `pod-security.kubernetes.io/enforce=restricted`, which means creating them instead of relying on `--create-namespace`.
  - The authz-agent and authz-policy-admin charts share those namespaces and would have to pass too.
  - If that is not wanted, add render assertions for the chart to `test/scripts/test-chart-render.sh`.

## Item 4: names by content, not by position

none. The subtest names describe their condition, the new test names state behavior, and the new comments refer to files and values by name. The `pipstub/main.go:NN` line references in `test/parity/suite/pip_control.go` were already there before this change.

## Item 5: the failure report

none. Each comparison prints got and want (`GET %s = %d %s, want %d %s`; `statuses of /a, /b, /a = %v, want %v`; `requestUri %q, path %q, want …`). `t.Fatalf` is used only where the next line would index `calls[0]`. Subtests are named, not numbered.

## Item 6: what the writer says it verified

None is stated. No commit gives a red run on the base commit for the `-1` index or the 404 fallback, and none gives a mutation verdict. None says the chart was installed in a namespace that enforces restricted PSS, or that the harness ran on kind.

## Item 7: siblings of the change

- **`test/parity/suite/pip_control.go:29-30`, caveat 3:** it reads "Path matching is strictly literal … No wildcards", which is now false because `*` is a catch-all. `ResetPinnedRoutes` would also turn a pinned `*` into a catch-all 404 with body `{"error":"reset"}`, not the stub's own 404. The commit defers the stub instance to "the cases that use it", so this is a follow-up to fix now or name in the description.
- **Readers of the call record** (`PipStubCall` in `pip_control.go:72` and the testify decoders): they decode loosely, so the new `requestUri` field breaks nothing. The defect does not apply.
- **`writeRespond`'s echo** (the rule-engine surface) does not carry `requestUri`, and no claim covers it. Does not apply.
- **Writes under a read-only root filesystem:** `writeObservedSidecar` (`compare.go:145-146`) writes next to the goldens and ignores errors. The parity image already keeps that directory root-owned, so the write failed before this change as well. Not a regression.
- **Makefile siblings:** `E2E_LOCAL_DEPLOYMENTS`, `PARITY_LOCAL_DEPLOYMENTS`, and the `exec deploy/...` lines in `e2e-logs` and `parity-logs` still name the Deployments the chart creates.
- **Leftover references:** `git grep` finds none to the deleted manifests or ConfigMap names outside `docs/handovers`.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| The harness migration fails on a namespace created by the old `kubectl apply` harness (ownership conflict); no remedy documented or run | Substantive | `Makefile:85`, `Makefile:149` | Document and run the remedy (`make e2e-down` or delete the namespaces), or remove the old objects in the target |
| Restricted-PSS claim has no check | Substantive | `templates/_helpers.tpl:23-40` | Enforce `restricted` on the kind namespaces, or add render assertions for the chart |
| Default-route docs leave out the empty-route fall-through | Substantive | `pipstub/main.go:34-36`, `:122-123` | Say "has no route of its own, or a route with no responses" |
| Routed path with no responses and no `*` route is untested | Substantive | `pipstub/main_test.go:224-243` | Add a case expecting 404 (this is the base commit's panic) |
| Realm merge, profile fill and duplicate check have no committed test | Substantive | `build/authz-agent-transfer/Dockerfile:38-46`, `profile.jq` | A fixture user file run through the stage in CI, or a jq test of `profile` |
| Docs say `e2e-harness` installs and waits for the suite Job | Substantive | `docs/local-integration-tests.md:104` | Drop the suite Job from that row, as `test/k8s/README.md` does |
| Caveat "No wildcards" is now false | Substantive | `test/parity/suite/pip_control.go:29-30` | Update it, or name it as a follow-up in the description |
| Selector comment gives the wrong reason | Substantive | `templates/_helpers.tpl:2-4` | State that selectors are immutable and that existing releases upgrade only while they stay the same |
| No red-run or mutation evidence stated | Substantive | 9d25da7 | State the red run on 58316ca for the new cases |
| Package doc narrates history ("as it did before…") | Taste | `pipstub/main.go:37-38` | Drop the clause |
| `TAG` image list leaves out the runtime suite | Taste | `values.yaml:9-11` | Add `authz-runtime-suite` |
| Commit message leaves out the clients and users added to `parity-realm.json` | Taste | 8b85515 | Mention them |

I did not run the kind harnesses or install the chart on a cluster, and I did not do a wording-only pass over the prose. I rendered and linted a copy of the chart with placeholder files in the scratchpad, ran `go test` for pip-stub as a consistency check, and ran the realm-merge jq pipeline on scratchpad fixtures.

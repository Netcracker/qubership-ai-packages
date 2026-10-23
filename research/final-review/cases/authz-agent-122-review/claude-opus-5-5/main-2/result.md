## Final review of `58316ca..HEAD`: three commits (test-stand chart, the pip-stub default route, restricted Pod Security Standard)

The skill has no task statement to work from, so item 2 takes its claimed cases only from the three commit messages and the comments above the tests. There was no previous report, so the report has no table of earlier findings.

Inputs and what I ran:
- **Drift script:** it ran and printed nothing. It only parses Java, Kotlin, Groovy and Scala, so I did item 1 by hand for the Go, Helm, Dockerfile and Markdown files.
- **Skills:** `test-authoring` and its `go/testing.md` are loaded. `english-developer-style` is not in the skills directory, so I did not load it, and nothing below is cited from it.
- **Stack line:** `AGENTS.md` has none. I propose this one: `Tests: Go testing (engine and assertions) in test/integration/pipstub; chart behaviour in test/scripts/test-chart-render.sh`.
- **Gates I ran myself:** `go vet` and `go test` in `test/integration/pipstub` pass. I built the `chart-files` stage into the scratchpad and ran `helm lint` with both values files: both pass. `helm template` with both values files followed by `kubeconform -strict` gives 22 of 22 objects valid. Every container renders the security context the commit claims, and every object and Pod template carries the claimed labels.

### Item 1: comments consistent with the code and with each other
- `test/integration/pipstub/main.go:34-38` (package comment) and `:122-123` (the `defaultRoute` doc) say the default route answers "every request whose path has no route of its own". The code at `:234-236` also sends a path whose route has no responses to the default route, and the commit message and the test comment at `main_test.go:222-224` both say so. A reader of the doc comment would expect such a path to get 404.
- `main.go:20`, unchanged, still says "Responses are served sequentially per path". The new paragraph at `:35-36` and the test at `main_test.go:259-260` say the default route keeps one sequence across all unrouted paths. The two statements disagree.
- `main.go:37-38`: "as it did before the default route existed" describes the change itself. Item 1 forbids that outside a regression test's comment.
- `main.go:19`, "the hardcoded defaults" (`loadDefaultRoutes`), and the new "default route" (`*`) are two different things with almost the same name. A reader of `:37` ("a stub nobody configures with it answers an unrouted request 404") could think the hardcoded routes are affected. (Taste.)
- `helm-templates/authz-test-stand/templates/_helpers.tpl:3-5` gives as the reason for keeping `app: <name>` in the selectors that "the Makefile's deploy/<name>" addresses a part through it. `deploy/<name>` refers to the object by name and does not depend on labels at all. Only the `kubectl -l` half of that reason is true.
- `docs/local-integration-tests.md:104`: the `e2e-harness` row says the install creates "the suite Job" and "waits until they are Ready". The Job is a `helm test` hook, so the install never creates it. `test/k8s/README.md:23` says exactly that ("installing the stand does not start it"), and its own `e2e-harness` row leaves the Job out.
- `test/parity/README.md:69-73` says the parity realm "also holds the users of `suite/testdata/realm/`, so the cases that need those users run on the kind harness". That directory has no user files, and the commit message itself says "none so far". A reader would look for users and cases that do not exist. `idp-seed/README.md:7` and `test/k8s/README.md` say the same thing more mildly.

The other new comments match the code and the rendered output. I checked `suite.yaml` (hook delete policy), `idp.yaml`, `values.yaml`, `REALM-DESCRIPTION.md` (the `/auth` issuer, which the base commit already used), and the `testify` Dockerfile and `helpers.go` references.

### Item 2: claimed cases covered
| Claimed case (source) | Test |
| --- | --- |
| `*` answers an unrouted path (commit 2) | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `.../a_routed_path_keeps_its_own_answer` |
| A route with no responses falls through to the default route | `.../a_routed_path_with_no_responses_gets_the_default_answer` |
| …"or to 404", for a routed path with no responses and no `*`. This is the base commit's index −1 input. | **none** |
| A stub not configured with `*` answers 404 | `.../an_unrouted_path_without_a_default_route_is_404`, `.../an_unrouted_path_with_an_empty_default_route_is_404` |
| The default route serves its sequence, clamped, across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` (a per-path counter would fail it) |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| Rules take precedence over the default route (package comment, `:29-30`) | **none.** `TestHandlePIP_RuleThenLegacyFallback` covers rules over the legacy routes only. |
| Each part is off by default; the realm checksum restarts Keycloak when a file changes; the `fail` messages when generated files are missing (commit 1) | **none.** `helm lint` only renders the two values files. |
| The `chart-files` stage merges user files, fills in profile fields, and fails on a duplicate username or id (commit 1, `profile.jq`) | **none.** The stage has never run on any input, because there are no user files. |
| Restricted PSS: non-root, RuntimeDefault, drop ALL, no escalation, read-only root filesystem except Keycloak, `/tmp` emptyDir (commit 3) | **none.** See 3a. |
| `app.kubernetes.io/*` and `helm.sh/chart` labels on every object (commit 3) | **none** |
| The e2e and parity stands install and their suites pass (commit 1) | The CI jobs `kind-e2e` and `kind-parity` (`make e2e-harness`/`e2e-suite`, `parity-harness`/`parity-suite`) |

Changes no commit message mentions:
- `parity-realm.json` gains 318 lines: `ROLE_MT_*`, `mt-a` and `mt-a-admin`, and five clients `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a`. Commit 1 only says "the parity realm gains a second tenant realm, parity-mt-b", which also describes the wrong file. Nothing outside the realm file refers to the new clients.
- `test/svt/common/compose/docker-compose.yml` moves Keycloak from 26.0 to 26.3.5. (Taste.)

### Item 3: boundaries, partitions, and the negative control
- The pip-stub inputs are route state (absent / with responses / empty) × default route (absent / with responses / empty). Two combinations are missing:
  - **Routed but empty, with no default route.** This is the input that indexed at −1 on the base commit.
  - **Routed but empty, with an empty default route.**
  
  The routed-path case is the control, and it is present. No input type admits an empty value beyond these.
- Chart partitions: `idp.realms` e2e and parity, `suite.serviceAccount` on and off, a pip-stub with and without `config`, and `tenantManager` on and off. The two values files that CI lints cover all of them.
- **Missing negative control for commit 3:** no CI run uses a namespace that enforces `restricted`. A Pod that breaks the standard would still go green. `git grep pod-security` finds nothing.

### Item 3a: level, placement, and the environment
- The pip-stub tests are small and in-process, and they sit beside the existing `TestHandlePIP_*` tests and share `resetState`. That is the right level and the right place.
- The chart claims (labels, security context, off by default, the checksum, the `fail` texts) can all be seen with `helm template`, offline. The repository already checks the same properties for its other two charts in `test/scripts/test-chart-render.sh:785-850`, the `for chart in "${CHART_DIR}" "${STUB_CHART_DIR}"` loop with its seccomp and readOnlyRootFilesystem assertions. The test-stand chart is not in that script. That script is the place for these checks, and CI's `chart` job already generates the files first.
- Whether the stand actually starts under `restricted` can only be seen in a cluster. The kind jobs exist but create the namespace without `pod-security.kubernetes.io/enforce=restricted`, so the test that exists does not check the claim.

### Item 4: names by content, not by position
None. The subtest names, `serve`, and the new comments all name things by content. The count words in docs and comments ("the three charts", "the two tenant realms") match the files.

### Item 5: the failure report
None. Every comparison is a `!=` condition whose `t.Errorf` prints the input and got-before-want (`GET %s = %d %s, want %d %s`, `statuses of /a, /b, /a = %v, want %v`). `t.Fatalf` is used only where `calls[0]` comes next. The table rows run under `t.Run` with names describing their condition.

### Item 6: what the writer says it verified
None stated. No commit gives a red run on the base commit (commit 2 says the base indexed at −1, but its tests sit in the same commit as the fix and no failing output is quoted) or a mutation verdict. Nor does any commit say the stand was installed into a namespace that enforces `restricted`.

### Item 7: siblings of the change
- `handlePIP`'s route lookup is the only place that indexes `route.Responses`. Its rule-engine sibling `matchRule` (`main.go:275-281`) already guards `len(rule.RespondSequence) > 0`, so the defect does not apply there.
- `handleReset` clears `counters`, which includes the `*` key. Not affected.
- I found no stale references to the removed manifests: `git grep` for `runtime-suite-job`, `keycloak.yaml`, `m2m-credentials`, `parity-realms` and the stub manifests finds nothing. The old values carried over unchanged: ports, env, M2M credentials (`test-app-client`/`test-app-secret`, `parity-m2m`), tenant map, args.
- The security-context helper's siblings are the authz-agent and authz-policy-admin charts. They make `readOnlyRootFilesystem` true on Kubernetes only, while the test stand makes it true everywhere. That is allowed under OpenShift's restricted SCC and is a deliberate difference. (Taste.)

### Findings
| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| The test-stand chart has no render assertions: labels, security contexts, off by default, the checksum, the `fail` texts | Substantive | `test/scripts/test-chart-render.sh:785` | Add `helm-templates/authz-test-stand` checks beside the existing chart loop. |
| The claim that the stand starts under `restricted` is never checked; the kind namespaces do not enforce it | Substantive | `Makefile:86,150`, `.github/workflows/integration-tests.yaml` | Label the e2e and parity namespaces `pod-security.kubernetes.io/enforce=restricted` before installing, or name it as a follow-up. |
| The "default route" doc omits that a route with no responses also falls through to it | Substantive | `test/integration/pipstub/main.go:34-36,122-123` | Name both cases in each comment. |
| "Served sequentially per path" contradicts the shared sequence of the default route | Substantive | `main.go:20` | Say "per route". |
| A comment describes the change ("as it did before the default route existed") | Substantive | `main.go:37-38` | State the behavior and leave out the history. |
| No case for a routed path with no responses and no default route, the base commit's −1 input; also missing: routed-empty with an empty default | Substantive | `main_test.go:234-242` | Add both rows. |
| No test that a matching rule wins over the default route | Substantive | `main_test.go:135` | Configure `*` in `TestHandlePIP_RuleThenLegacyFallback` and assert `/rule` still answers from the rule. |
| The `chart-files` merge, the profile fill, and the duplicate check have never run on any input | Substantive | `build/authz-agent-transfer/Dockerfile:39-46`, `profile.jq` | Run the stage on a fixture user file (and a duplicate) in CI, or name it as a follow-up. |
| The `e2e-harness` row says the install creates the suite Job and waits for it | Substantive | `docs/local-integration-tests.md:104` | Drop the Job from the row, as `test/k8s/README.md` does. |
| The README says the parity realm holds users and cases from `testdata/realm/`, but there are none | Substantive | `test/parity/README.md:69-73` | Say the directory is empty for now and that the stage merges whatever files are added there. |
| The selector comment cites `deploy/<name>`, which does not depend on labels | Substantive | `templates/_helpers.tpl:3-5` | Give only the `-l app=<name>` reason. |
| The commit message does not describe the `parity-realm.json` additions (tenant roles, `mt-a*`, five clients) and gives the new realm as "the parity realm gains" | Substantive | commit `8b85515` message | Describe the additions and what they are for. |
| No red run or mutation verdict stated | Substantive | all three commits | State the base-commit failure of the new pip-stub cases. |
| "Default route" next to `loadDefaultRoutes` / "hardcoded defaults" | Taste | `main.go:19,122` | Pick a name that is not "default", e.g. "the fallback route". |
| Keycloak version bump in the SVT compose file is not in any commit message | Taste | `test/svt/common/compose/docker-compose.yml:3` | Mention it, or move it to its own commit. |
| Read-only root filesystem is unconditional, unlike the platform charts | Taste | `templates/_helpers.tpl:24-31` | Keep it, or follow the `PAAS_PLATFORM` convention. |

The review did not run the kind suites, did not install the chart in any cluster, did not do a style pass over the prose (`english-developer-style` was not available), and did not run the mutation tool.

# Final review of `58316ca..HEAD` (8b85515, 9d25da7, 17b17fc)

I found 14 substantive findings and 3 taste findings. The pip-stub change is in good shape: its tests pass and run in-process. Most of the findings are about the test-stand chart and the Makefile wait that replaced the old manifests. Nothing claimed for the chart's security settings is checked by anything that runs: no Pod Security enforcement, no render test.

There was no task statement, so the claimed cases come from the three commit messages and the test comments. There is no previous report, so there is no carry-over table. I loaded `test-authoring`, its `references/go/testing.md` file, and `english-developer-style`. No Go doc-comment skill was among the three provided, so Go comments were checked against `test-authoring` and the form only. The drift script ran but printed nothing, because it only parses Java, Kotlin, Groovy, and Scala files. I read every changed comment in the Go, Makefile, YAML, Dockerfile, and Markdown files myself.

What I ran: `go test` in `test/integration/pipstub` (passes). In a scratch copy I built the `chart-files` stage, ran `helm lint` and `helm template` with both values files, and changed a realm file to confirm the `checksum/realms` annotation changes. I also deleted the generated files to confirm the documented error text appears. I tried the `profile.jq` example and the duplicate check with `jq`. I ran `local/pip-stub:ci` with a read-only root and all capabilities dropped, once as uid 10001 and once as uid 1000770000:0 (gid 0); it started both times. I read the base image's `entrypoint.sh`.

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:34-36` and `:122-123`.** The package comment and the `defaultRoute` comment say the default route answers "every request whose path has no route of its own". The code (`main.go:234-238`) also sends a path whose route has no responses to the default route. The commit message and the test comment (`main_test.go:222-223`) both say so. A reader of the package doc would expect such a route to answer 404 or fail. **Substantive.**
- **`main.go:37-38`.** "…answers an unrouted request 404, as it did before the default route existed" tells the history of the change, outside a regression test. **Taste.**
- **`main.go`: one name for two things.** "The default route" (`*`) and `loadDefaultRoutes` / "the hardcoded defaults" (line 19) now mean different things in the same file. **Taste:** a name such as "catch-all route" avoids the clash.
- **`docs/local-integration-tests.md:104`.** It says `e2e-harness` installs "…and the suite Job; waits until they are Ready". That is false: a `helm.sh/hook: test` Job is created only by `helm test`, not by an install. `test/k8s/README.md`'s row for the same target correctly leaves the Job out, so the two pages disagree. **Substantive.**
- **`test/parity/README.md:115`.** "The harness lives under `test/k8s/parity/`: the manifests, …". That directory no longer holds any manifests. **Substantive.**
- **`README.md:59`.** "CI builds both via `.github/docker-dev-config.json`". The change adds three entries to that file, so it now lists five images. **Substantive.**
- **`docs/local-integration-tests.md:190`.** The troubleshooting row "`make e2e-harness` times out at `rollout status deploy/keycloak`" describes a step that no longer exists; the harness is now one `helm --wait`. **Substantive.**

Checked and fine: the `callRecord.RequestURI` comment, `LoadConfig`, the Makefile `run-suite` comment, `_helpers.tpl`, the comments in `idp.yaml` and `suite.yaml`, the image list in `docker-release.yaml` (it matches `docker.cfg`), and the Dockerfile and `profile.jq` header comments (the `R29LevelM2M` example holds).

## Item 2: claimed cases covered

| Claimed case | Covered by |
| --- | --- |
| An unrouted path gets the default route's answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| An empty route falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` (would panic with index -1 on the base commit) |
| An empty route falls through "or to 404" | Only the empty *default* route (`…/an_unrouted_path_with_an_empty_default_route_is_404`). **A routed path with no responses and no default route has no test.** Substantive. |
| A stub not configured with `*` answers 404 as before | `…/an_unrouted_path_without_a_default_route_is_404`, and `TestHandlePIP_RuleThenLegacyFallback` |
| `/pip-stub/configure` accepts the path `*` | **None.** The tests write to `routes` directly. `handleConfigure` stores any path, so the gap is small. Taste. |
| The default route serves its responses in sequence | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the request target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| The chart parts; `make e2e-harness`, `parity-harness`, `e2e-suite`, `parity-suite` | CI jobs `kind-e2e` and `kind-parity` run the same targets |
| `make test-stand-files` | CI job `chart`, step "Generate the test-stand files" |
| User files are merged and their profile fields filled in; the build fails on a duplicate | **None.** There are no user files ("none so far"), so the `jq` merge, `profile`, and both uniqueness checks never run on any input. Substantive. |
| The stand starts under the `restricted` Pod Security Standard | **None.** Neither harness labels its namespace `pod-security.kubernetes.io/enforce=restricted`, and no render assertion checks the security contexts. Substantive. |
| Labels on every object; selectors keep `app: <name>` | None. I checked them by rendering by hand. Grouped under item 3a. |
| No `runAsUser` pinned, so OpenShift can assign a uid | No test in the repository. My pip-stub run as uid 1000770000:0 with a read-only root started. |
| The release publishes three more images | None; the release workflow's dry run was not shown. |
| The parity realm gains `parity-mt-b` | The realm file is added, but nothing in the suite or harness uses it (no reference outside `idp-seed/`, the transfer Dockerfile, and `test/parity/README.md`). |

**Commands the change tells people to run:**
- `make test-stand-files`, `e2e-*`, `parity-*`: run by CI.
- `helm-templates/authz-test-stand/README.md:42-44` (`docker create … true`, `docker cp`, `docker rm`): nothing runs it. It depends on a released transfer image, which does not exist yet.
- `README.md:58` (`helm upgrade --install … --set TAG=<version> -f my-test-stand-values.yaml`): nothing runs it. It depends on the images published under `<version>`. The kind jobs install only `local/*:ci` images.
- `README.md:64` (`helm test … --timeout 15m --logs`): nothing runs it. The Makefile runs it without `--logs`. `--logs` exists in helm v4.3.0.
- `docs/local-integration-tests.md`, the subset recipe (`helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …`): nothing runs it. `TestCheckResource` exists, and helm's `--set` parsing does not treat `^`, `$`, or `/` specially.

All of these are `none`. **Substantive:** the request is one run of the transfer-image flow on a stand that is not kind, after the first release.

**Hunks no sentence claims (substantive):**
- `test/svt/common/compose/docker-compose.yml:4`: the SVT Keycloak goes from `26.0` to `26.3.5@sha256:…`.
- `.github/docker-dev-config.json`: the dev CI build now builds three more images on every run. The commit message only claims `.qubership/docker.cfg`.
- `test/k8s/parity/idp-seed/parity-realm.json`: it gains clients `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a`, users `parity-r29-scope`, `parity-r30-scope`, `mt-a`, and `mt-a-admin`, and roles `ROLE_MT_*`. The commit claims only `parity-mt-b`, and nothing uses any of these.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub:** the boundaries and controls are present: empty versus non-empty responses, default route present or absent, routed versus unrouted. Two cases are missing:
  - the routed-empty route with no default route (see item 2);
  - a rule match while a default route exists. The precedence "rules first, … then the default route" (`main.go:29-31`) has no control.

  **Substantive.**
- **State left by the old harness: no test or run.** A kind namespace set up by the old `kubectl apply` harness still holds objects with the same names and no Helm ownership metadata: ConfigMap `keycloak-realms`, Secret `authz-agent-client-credentials`, Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`, and ServiceAccount `runtime-suite` (`idp` and `pip-mock` in `authz-parity`). `helm upgrade --install` refuses to adopt such objects ("invalid ownership metadata"). No document names the remedy (`make e2e-down`, or deleting the namespace). **Substantive:** the request is a run from that state, or a troubleshooting row that names the remedy.
- **Values users pass through `E2E_HELM_ARGS`.** It now also reaches the test-stand install (`Makefile:86`, `:150`). The test stand reads two names the agent chart and the policy-admin chart also define: `TAG` and `IMAGE_PULL_POLICY`.
  - `IMAGE_PULL_POLICY`, the documented example, means the same thing in all three charts.
  - `--set TAG=<x>`, passed to test a differently tagged agent and policy-admin, would also retag `local/pip-stub`, `local/tenant-manager`, and the suite image, which `e2e-images` builds only as `:ci`. With `IMAGE_PULL_POLICY: Never` the stand never becomes Ready.

  **Substantive:** the request is a setting of the test stand's own, or keeping `E2E_HELM_ARGS` out of the stand's install.
- **Replaced wait: `e2e-suite` / `parity-suite`.** Fault: the suite Pod never starts, which the existing troubleshooting row "`ErrImageNeverPull`" shows is the common one. I reasoned these timings from the code; I did not run them.
  - **Old:** `wait --for=condition=Ready pod … --timeout=3m` fails at about 3 minutes and prints `timed out waiting for the condition`.
  - **New** (`Makefile:100-107`): about 3 minutes of silent polling (90 × (`kubectl logs` + 2 s), output sent to `/dev/null`). Then `logs -f` fails at once with the waiting reason. Then `wait $helm_pid` blocks until `helm test --timeout 15m`, or the Job's 900 s deadline, ends it.
  - The new form fails about 12 minutes later, and no sentence in the change accepts that.

  **Substantive:** the request is a run of that fault, and a deadline of about 3 minutes on the container start, ending the background `helm test`.
- **Replaced wait: `e2e-harness`.** A stub that never becomes Ready used to fail at `rollout status … --timeout=2m`. Now it fails at helm's `--wait --timeout 10m`. **Substantive:** the same request, a run of the fault, or a sentence that accepts the delay.
- **Limits on the suite run.** Three limits nest:
  - `helm test --timeout 15m`, fixed in the Makefile (`:102`) and in the chart README (`:64`);
  - `suite.activeDeadlineSeconds: 900` (`values.yaml:99`);
  - `-test.timeout 600s` in `suite.args`.

  At the defaults the innermost fires first, which is correct. But raising `activeDeadlineSeconds` past 900 has no effect, because helm's 15 minutes fire first and `make` fails while the Job keeps running. Raising `-test.timeout` past 900 s gets the Job killed with `DeadlineExceeded` and no Go test summary. Nothing derives one limit from another or documents how they relate. **Substantive.**

## Item 3a: level, placement, and the environment

- The pip-stub tests are small, in-process tests in `main_test.go`, next to the existing `TestHandlePIP_*` tests, and they reuse `resetState`. Fine.
- `helm template` can show several of the chart's claims with no cluster: every Pod has `runAsNonRoot`, `RuntimeDefault` seccomp, dropped capabilities, and no privilege escalation; `readOnlyRootFilesystem` is false only for Keycloak; the labels are present; every part is off by default; the missing-files error appears. `test/scripts/test-chart-render.sh:439` covers only the two product charts. The only check across the cluster boundary, the kind jobs, does not enforce `restricted`. **Substantive:** the request is render assertions for the test-stand chart, plus an `enforce=restricted` label on the harness namespaces.

## Item 4: names by content, not by position

None. The subtest names and test names are by content. `$(1)`, `$(2)`, `$(3)` in `run-suite` are Make macro parameters, and their comment names each one.

## Item 5: the failure report

- The Go tests are fine: `t.Errorf` messages give the input, then the result, then the expected value (`GET %s = %d %s, want …`), and a stopping assertion (`t.Fatalf`) is used only before indexing `calls[0]`.
- **`build/authz-agent-transfer/Dockerfile:346-347`.** `jq -e '[.users[].username] | length == (unique | length)'` prints only `false` on a duplicate; I reproduced this. The build fails without naming the user. **Substantive:** print the duplicated usernames and ids, for example with `group_by(.) | map(select(length > 1))`.

## Item 6: what the writer says it verified

Not stated. No commit shows a red run on the base commit for the `-1` index panic or the 404 behavior, and none gives a mutation verdict. My `go test` run is a consistency check only, not that evidence.

## Item 7: siblings of the change

- Sentences that still count the old set: `README.md:59` ("both") and `test/parity/README.md:115` ("the manifests"). See item 1.
- Remedy rows: `docs/local-integration-tests.md:190` names a step that no longer exists. No row covers the ownership conflict from item 3, for either the e2e or the parity namespace.
- `test-chart-render.sh` lists the product charts but not the new one (item 3a).
- **Taste:** `run-suite` uses `kubectl wait --for=create`, which needs kubectl 1.31 or later. The prerequisites table names no kubectl version. With an older kubectl the log is not streamed, but the exit code still comes from `helm test`.
- No other callers: the default route is reached only through `handlePIP`. The other realm users already have the profile fields `profile.jq` fills in; I checked all seven realm files.

## Findings

| Finding | Label | File:line | Requested change |
| --- | --- | --- | --- |
| Pod Security `restricted` claim never exercised | Substantive | `Makefile:86,150`; `test/scripts/test-chart-render.sh:439` | Label the harness namespaces `enforce=restricted`; add render assertions for the test-stand chart |
| Objects left by the old harness block `helm upgrade --install` | Substantive | `Makefile:86,150`; `docs/local-integration-tests.md` §8 | Run from that state, or add a troubleshooting row naming `make e2e-down` / deleting the namespace |
| `E2E_HELM_ARGS` `TAG` now retags the stand's local images | Substantive | `Makefile:46-48,86,150` | A stand-only setting, or keep `E2E_HELM_ARGS` off the stand's install |
| Suite wait fails at about 15 min instead of 3 when the Pod never starts | Substantive | `Makefile:100-107` | Run the fault; add a deadline of about 3 min on the container start |
| Harness wait fails at 10 min instead of 2 when a stub never becomes Ready | Substantive | `Makefile:86,150` | Run the fault, or a sentence that accepts it |
| `activeDeadlineSeconds` and `-test.timeout` not tied to the fixed `helm test --timeout 15m` | Substantive | `values.yaml:92-99`; `Makefile:102`; `helm-templates/authz-test-stand/README.md:64` | Derive the helm timeout from the value, or document how the three relate |
| Profile fill and duplicate check run on no input | Substantive | `build/authz-agent-transfer/Dockerfile:344-347` | A fixture user file, or a build check run on one |
| Duplicate check prints only `false` | Substantive | `build/authz-agent-transfer/Dockerfile:346-347` | Print the duplicated names and ids |
| Routed empty route with no default route has no test; rules over the default route has no control | Substantive | `test/integration/pipstub/main_test.go:225` | Add both cases |
| Package and const comments omit the empty-route fall-through | Substantive | `test/integration/pipstub/main.go:34-36,122-123` | Name the case |
| `e2e-harness` row says it installs the suite Job | Substantive | `docs/local-integration-tests.md:104` | Drop the Job from the row |
| Stale "manifests", "builds both", and `rollout status deploy/keycloak` | Substantive | `test/parity/README.md:115`; `README.md:59`; `docs/local-integration-tests.md:190` | Update the three sentences |
| Unclaimed hunks: SVT Keycloak bump, dev CI images, unused parity realm clients, users, and roles | Substantive | `test/svt/common/compose/docker-compose.yml:4`; `.github/docker-dev-config.json`; `test/k8s/parity/idp-seed/parity-realm.json` | A sentence that claims each one, or move them to their own change |
| Transfer-image install flow never run | Substantive | `helm-templates/authz-test-stand/README.md:39-65` | One run on a stand that is not kind after the first release |
| "As it did before" narrates the change | Taste | `test/integration/pipstub/main.go:37-38` | Drop the history |
| "Default route" clashes with `loadDefaultRoutes` | Taste | `test/integration/pipstub/main.go:19,34,122` | Rename to "catch-all route" |
| `kubectl wait --for=create` needs kubectl 1.31 or later, not stated | Taste | `Makefile:103`; `docs/local-integration-tests.md` prerequisites | State the minimum version |

This review did not check: any run on a Kubernetes cluster (helm's actual timeout output, the ownership conflict, and Pod Security admission are all reasoned, not observed), the release workflow, Keycloak running with a read-only or arbitrary-uid setup, or the wording of the prose for style alone.

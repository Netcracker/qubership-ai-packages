# Final review of `58316ca..5dcb6be` (four commits)

There was no separate task statement, so the claimed cases come from the four commit messages, the comments in the changed files, and the commands written into the changed READMEs. The drift script ran and listed no members. It does not parse Go templates, Makefiles, YAML or Markdown, and the only changed Go members were checked by hand. I loaded `test-authoring` and `english-developer-style`. No Go doc-comment skill is in the provided set, so item 1 relies on the form's own questions for the Go comments. I did not change any file. I rendered the chart from a copy in the scratchpad, with `files/` filled by hand from the source realms.

## Item 1: comments consistent with the code and with each other

- **`docs/local-integration-tests.md:180`**: the `e2e-harness` row says the target installs "… the client-credentials Secret, and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` (`templates/suite.yaml:21`), so an install does not create it. Three other places say the same thing correctly: `test/k8s/README.md:272-273` ("installing the stand does not start it"), the `test/k8s/README.md` `e2e-harness` row, and `Makefile:177-180`. A reader of the docs page will look for a Job after `make e2e-harness` and find none.
- **`test/integration/pipstub/main.go:37`**: "as it did before the default route existed" narrates the change in a package comment that is not a regression test's comment.
- **`Makefile:49-50`**: "A suite that runs longer raises this together with suite.activeDeadlineSeconds". This is incomplete. The `-test.timeout 600s` in both suites' `suite.args` (`test/k8s/test-stand-values.yaml:55-56`, `values.yaml:95-96`) fires first. Details are under item 3.
- `main.go` comments on `defaultRoute`, `callRecord.RequestURI` and step 2 of `handlePIP`: these match the code. The package comment's precedence paragraph names the default route; the bullet on legacy routing does not, and that is acceptable.
- `_helpers.tpl` and the chart README's security paragraph: these match the rendered output. Every Pod has `runAsNonRoot`; `readOnlyRootFilesystem` is false only for Keycloak.

## Item 2: claimed cases covered

| Claimed case | Covered by |
| --- | --- |
| Default route answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an unrouted path gets the default answer` |
| Routed path keeps its own answer (control) | `…/a routed path keeps its own answer` |
| Route with no responses falls through to the default route | `…/a routed path with no responses gets the default answer` |
| Route with no responses and no default route → 404 (the old index −1 crash) | **none**. The table has no case with `routedResponses` empty and `defaultResponses` nil, which is the regression the commit names. |
| No `*` configured → 404, as before | `…/an unrouted path without a default route is 404` |
| "`/pip-stub/configure` now takes the path `*`" | **none through `handleConfigure`**. Every test writes `routes[defaultRoute]` directly. |
| Sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| Restricted PSS: non-root, RuntimeDefault, drop ALL, no escalation, read-only root fs except Keycloak | **none**. `test/scripts/test-chart-render.sh` has no test-stand assertions, and the kind namespaces are created by `--create-namespace` with no `pod-security.kubernetes.io/enforce` label. Nothing in CI rejects a regression. Nothing shows that the qubership-core-base entrypoint of pip-stub or tenant-manager starts on a read-only root with no writable `/tmp`. |
| app.kubernetes.io labels + `helm.sh/chart`, selectors keep `app:` | Only by rendering. I checked it in the render; no assertion covers it. |
| Chart error texts `no realm files under files/realms/<realms>/` and `no file files/pip-stub/<file>` (chart README:30) | No assertion. I rendered the pip-stub text by hand and it matches. |
| `profile.jq` fills firstName / lastName / email; the build fails on a duplicate user | **none**. `testdata/realm/` holds no user file, so the merge and the duplicate checks never run. I ran it by hand: `parity-r29-level-m2m` becomes `R29LevelM2M`, which matches the comment. |
| Suite waits `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT` | Only the 15m default runs in CI. See item 3 for raised values. |
| Release publishes pip-stub, parity-suite, transfer | `.qubership/docker.cfg`. Not run here. |

Commands in the changed files:

| Command and promised outcome | Run by | Notes |
| --- | --- | --- |
| `make test-stand-files` | CI chart job (`integration-tests.yaml:76`) | Covered |
| `helm lint … authz-test-stand -f …` ×2 | CI chart job | Covered. I linted both locally on Helm 4.3.0. |
| `make e2e-harness/-suite`, `make parity-harness/-suite` | CI kind jobs (Helm 4.3.1 only) | Covered |
| Chart README: `docker create … transfer:<version> true`, `docker cp`, `docker rm` | **none** | Depends on a FROM-scratch multi-arch image accepting a command that does not exist. `docker create` does not check it, so it should work, but nothing runs it. |
| Chart README: `helm upgrade --install … ./charts/authz-test-stand --set TAG=<version> -f my-test-stand-values.yaml` with imageRepository/TAG/IMAGE_PULL_POLICY deleted | **none** | Depends on the release tagging the images with exactly `<version>`. |
| Chart README: `helm test authz-test-stand --timeout 15m; kubectl logs job/parity-suite` | `make parity-suite` runs the same form on Helm 4 only | The README's statement about Helm 3 (`unable to get pod logs`) comes from the commit's Helm 3.22.1 run. No job runs Helm 3. |
| Docs: `helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false`, then `make e2e-suite` | **none** | Depends on `--reuse-values` keeping the earlier `--set suite.env.BASE_URL` and the `-f` values. Helm 3 and 4 both do, so the risk is low, but it has not been run. |
| `make e2e-down` once, after the `invalid ownership metadata` error | **none** | The cluster is deleted, so the remedy works by construction. The quoted error text has not been reproduced from a cluster left by an older harness. |

Hunks that no sentence of the commit messages claims:

- **`test/svt/common/compose/docker-compose.yml:3`**: SVT Keycloak goes from `26.0` to `26.3.5@sha256:…`.
- **`test/k8s/parity/idp-seed/parity-realm.json`**: +318 lines. These add the `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a` clients and the users `parity-r29-scope`, `parity-r30-scope`, `mt-a` and `mt-a-admin`. The commit claims only the new realm `parity-mt-b`.
- **`.github/docker-dev-config.json`**: adds the three images to dev CI builds. The commit claims only release publishing through `docker.cfg`.
- **`test/k8s/authn/REALM-DESCRIPTION.md`**: the issuer changes from `/realms` to `/auth/realms`. This fixes a stale doc, since the old manifest already set `/auth`.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub partitions.** Each partition (routed or unrouted path, empty route, empty or missing default) is present except the routed-empty with no default case listed under item 2. The control (a routed path keeps its answer, and no default gives 404) is present.
- **Pre-existing state.** A cluster set up by the old `kubectl apply` harness is documented, but nothing runs from that state (item 2). The remedy row is also incomplete; see item 7.
- **Values users already pass.** `E2E_HELM_ARGS` now reaches the test-stand install (`Makefile:182, 256`). It shares the keys `TAG` and `IMAGE_PULL_POLICY` with the agent and policy-admin charts. Two values break the stand:
  - `E2E_HELM_ARGS='--set TAG=1.2.3'`, used to run a published agent tag, now makes the stand ask for `local/pip-stub:1.2.3` and `local/authz-runtime-suite:1.2.3`. `e2e-images` builds neither, and the pull policy is `Never`, so the result is ErrImageNeverPull and the harness fails at its 10-minute `--wait`.
  - `--set IMAGE_PULL_POLICY=Always` makes the stand try to pull `local/*` images from a registry.
  
  Only the documented example (`IMAGE_PULL_POLICY=Never`) means the same thing in both places.
- **Replaced mechanism: suite run.** The fault the old mechanism met most often is the Job Pod not starting (the troubleshooting row "stays Pending or reports ErrImageNeverPull").
  - Old: `wait --for=condition=Ready pod … --timeout=3m` failed at about 3 minutes with `timed out waiting for the condition`.
  - New:
    1. `wait --for=create` returns at once.
    2. The poll loop then spends 90 × (one failing `kubectl logs` + 2 s) ≈ 3–4 minutes.
    3. `kubectl logs -f` fails with the waiting reason.
    4. `wait $helm_pid` blocks until `activeDeadlineSeconds` (900 s) or `helm test --timeout 15m`.
  
  The new mechanism fails at about 15 minutes, five times later. No sentence in the change accepts that.
- **Replaced mechanism: harness wait.** The old harness waited 2 minutes per stub `rollout status`. Now everything waits on one 10-minute `--wait`, so a stub that crash-loops or cannot pull its image fails at 10 minutes instead of 2, and Helm's message names no Deployment.
- **Limits.** The limits on the same work are:
  - `-test.timeout 600s`, fixed in `suite.args` in both values files and in chart `values.yaml`.
  - `suite.activeDeadlineSeconds` 900.
  - `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT` 15m, in the Makefile.
  - CI `timeout-minutes: 30`, which encloses the image builds, the harness and the installs.
  
  Following the Makefile comment by raising `E2E_SUITE_TIMEOUT` and `activeDeadlineSeconds` to 20m/1200 still kills the suite at 10 minutes with `panic: test timed out after 10m0s`. The documented settings do nothing past 600 s, which defeats the case commit 4 was written for. In CI, raising `E2E_SUITE_TIMEOUT` past about 30 minutes minus the build and install time also has no effect, because the job limit fires first.

## Item 3a: level, placement, and the environment

- **pip-stub.** The tests are in-process with `httptest`, sit in `main_test.go` beside the existing `TestHandlePIP_*`, and share `resetState`. Good.
- **Chart security context and labels.** These can be observed with `helm template`, with no cluster, and the repository already has a render-assertion script run by CI. Nothing was added to it for `authz-test-stand`. The in-process level is missing, and the in-cluster check is missing too, because the kind namespaces do not enforce `restricted`.
- No optional prerequisites, so skips do not apply.

## Item 4: names by content, not by position

- **`helm-templates/authz-test-stand/values.yaml:11`**: "Keycloak has its own image and pull policy below." It could name `idp.image` and `idp.imagePullPolicy` instead.
- Test case names are by content.

## Item 5: the failure report

None. The table assertion prints the status and body, both got and want. The `reflect.DeepEqual` failure prints both slices. The `RequestURI`/`Path` assertion prints all four values. Case ids are descriptive names.

## Item 6: what the writer says it verified

- No commit states a red run of the new pip-stub tests on the base commit, or a mutation verdict.
- Commit 4 reports observed Helm 4.3.1 and 3.22.1 output for `--logs`, so that claim was run.
- No commit states a run of the stand in a namespace that enforces `restricted`, or a run from a cluster left by the old harness.

## Item 7: siblings of the change

- **`README.md:61`**: "CI builds **both** via `.github/docker-dev-config.json`". That file now lists five images.
- **`test/k8s/README.md:63-68`**: the list of Makefile overrides (`KIND_CLUSTER`, `E2E_NAMESPACE`, `PARITY_NAMESPACE`, `E2E_ARTIFACTS`, `E2E_HELM_ARGS`, `E2E_BASE_URL`, `PARITY_AC_BASE_URL`) does not name the new `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`. `git grep` finds them only in the Makefile.
- **`docs/local-integration-tests.md:225`**: the troubleshooting row's symptom names `make e2e-harness` **or `make parity-harness`**, but its action says "Run `make e2e-down` once, then `make e2e`". There is no step for the parity path.
- **`run-suite`**: both callers, `e2e-suite` and `parity-suite`, share it, so the item 3 timing applies to both.
- **`E2E_LOCAL_DEPLOYMENTS` / `PARITY_LOCAL_DEPLOYMENTS`**: still match the chart's Deployment names.
- **Removed manifests**: `git grep` finds no remaining reference to any of them.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Raising the suite timeout and `activeDeadlineSeconds` as the comment says has no effect past 600 s; `-test.timeout 600s` fires first | Substantive | `Makefile:49-50`, `test/k8s/test-stand-values.yaml:55-56`, chart `values.yaml:95-96` | Derive `-test.timeout` from `activeDeadlineSeconds` (or name it in the comment and in the chart README:69), and run one raised value end to end |
| Suite run fails at about 15 min instead of about 3 min when the Job Pod never starts | Substantive | `Makefile:199-206` | Fail when the log-poll loop runs out (kill helm, exit non-zero) so the whole wait is bounded near the old 3 min, and show that fault's run, duration and output. Or state in the change that the later failure is accepted. |
| Restricted-PSS claim has no check: no render assertion, kind namespaces not labelled `enforce=restricted`, read-only root of pip-stub and tenant-manager unproven on the qubership base entrypoint | Substantive | `templates/_helpers.tpl:23-40`, `Makefile:182,256` | Label the harness namespaces `pod-security.kubernetes.io/enforce=restricted` before install, and add test-stand assertions to `test-chart-render.sh` |
| `E2E_HELM_ARGS` now reaches the test stand; `--set TAG=…` or `IMAGE_PULL_POLICY=Always` aimed at the agent breaks the stand's `local/*` images | Substantive | `Makefile:126-128,182,256` | Give the stand its own args variable, or document that these keys now apply to the stand too |
| Docs say `e2e-harness` installs the suite Job and waits for it; the Job is a test hook | Substantive | `docs/local-integration-tests.md:180` | Drop "and the suite Job", as in `test/k8s/README.md` |
| Remedy row names `make e2e` only, though its symptom names `parity-harness` too | Substantive | `docs/local-integration-tests.md:225` | Add the parity step (`make parity`) |
| New `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT` missing from the README list of overrides | Substantive | `test/k8s/README.md:63-68` | List them |
| "CI builds both" is stale; the dev config builds five images | Substantive | `README.md:61` | Recount, or name the two services explicitly |
| Routed-empty route with no default route → 404 (the named −1 crash) has no case | Substantive | `test/integration/pipstub/main_test.go:508-523` | Add the case `routedResponses: []`, `defaultResponses: nil`, expecting 404 |
| `/pip-stub/configure` accepting `*` is not tested through `handleConfigure` | Substantive | `main_test.go:505` | Configure `*` through the handler in one case |
| `profile.jq` merge and the duplicate-user checks never run (no user file) | Substantive | `build/authz-agent-transfer/Dockerfile:338-352` | Add a fixture user file, or a jq check run in CI, with one duplicate case |
| Unclaimed hunks: SVT Keycloak pin; parity-realm tenant-a/unknown/empty clients and r29/r30/mt-a users; dev-config images; REALM-DESCRIPTION issuer fix | Substantive | `test/svt/common/compose/docker-compose.yml:3`, `test/k8s/parity/idp-seed/parity-realm.json`, `.github/docker-dev-config.json`, `test/k8s/authn/REALM-DESCRIPTION.md:361` | Add a sentence to the commit message claiming each, or move each to its own change |
| README commands for the transfer image, the docs `--reuse-values` subset, and the `make e2e-down` remedy on an old-harness cluster are never run | Substantive | chart `README.md:42-66`, `docs/local-integration-tests.md:210-216`, `test/k8s/README.md:296-298` | Run each documented form once (Helm 3 and 4 for the chart README) and record it |
| No red run or mutation verdict stated for the pip-stub tests | Substantive | commit `9d25da7` | State the red run on `58316ca` |
| Package comment narrates history ("as it did before the default route existed") | Taste | `test/integration/pipstub/main.go:37` | "answers an unrouted request 404" |
| "below" refers by position | Taste | `helm-templates/authz-test-stand/values.yaml:11` | "under `idp`" |

Not checked: I did not install anything on a cluster or build any image, I did not run `make test-stand-files` or `test-chart-render.sh` (the chart was rendered from a scratch copy with hand-made `files/`), I ran no Helm 3 commands, and I did not review the prose for style.

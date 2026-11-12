**Final review of `58316ca..HEAD`** (commits `8b85515`, `9d25da7`, `17b17fc`)

Task statement: none was handed over. The claimed cases come from the three commit messages and the test comments, so item 2 rests on those alone.

Drift script: `comment-drift.py 58316ca HEAD` printed nothing, although `pipstub/main.go` and `testify/helpers.go` changed. I read the changed Go comments by hand instead. The rest of the change is chart, Makefile, Dockerfile and docs.

Checks run: `helm lint` and `helm template` on a copy of the chart with `files/` filled in. Both values files lint clean, and the render shows `runAsNonRoot` on all four workloads, `readOnlyRootFilesystem: false` only on Keycloak, and an emptyDir `sizeLimit: 256Mi` on the suite Job. I also ran `profile.jq` through `jq` on two sample users. I did not run Docker, a cluster, or the Go tests.

## Item 1: Comments consistent with the code and with each other

Doc comments in the Go files: `main.go` header and `defaultRoute`, `callRecord.RequestURI`, and the `LoadConfig` comment in `helpers.go` are true of the new code, and the `LoadConfig` pointer to `suite.env` resolves. I checked the "No request path is `*`" claim against `net/http`: `ServeMux` answers `OPTIONS *` with 400, so it holds. None of these has a finding.

**F1 (substantive): the docs say the harness installs the suite Job, but the Job is a `helm test` hook.**
- `docs/local-integration-tests.md:104` says `e2e-harness` installs "the stubs, … and the suite Job; waits until they are Ready". The chart makes the Job a `helm.sh/hook: test` object, so installing the stand never creates it.
- `test/k8s/README.md:25` ("installing the stand does not start it") and `:53` agree with the chart. The Makefile comments at `Makefile:81` and `:143` ("and the suite Job, which e2e-suite runs") are close to the docs line.
- Request: drop "and the suite Job" from `docs/local-integration-tests.md:104`, as `test/k8s/README.md:53` already does.

**F2 (substantive): an uncommented expression a reader will find arbitrary.**
- `templates/suite.yaml:68` sets `sizeLimit: {{ .Values.suite.resources.limits | default dict | dig "ephemeral-storage" "256Mi" }}`. A reader will not know why the `/tmp` volume takes the container's whole `ephemeral-storage` limit, or where `256Mi` comes from.
- The comment must answer: why the emptyDir limit equals the container limit, and why that fallback.

**F3 (substantive, wording): a sentence the reader has to parse twice.**
- `main_test.go:222-224`: "a stub with no default route, or one with no responses, answers 404". "One" could be the stub or the default route.
- Unpacked: "a stub answers 404 when it has no default route or when its default route has no responses".

Terms the change coins: none. "Default route" is defined once in the `main.go` header, and `defaultRoute` is its identifier.

## Item 2: Claimed cases covered

Claimed cases and the test that covers each:

| Claim | Test |
| --- | --- |
| `*` answers unrouted paths | `DefaultRouteAnswersUnroutedPaths/an unrouted path gets the default answer` |
| A routed path keeps its own answer | `…/a routed path keeps its own answer` |
| A route with no responses falls through to the default | `…/a routed path with no responses gets the default answer` |
| No default route gives 404 as before | `…/an unrouted path without a default route is 404` |
| An empty default route gives 404 | `…/an unrouted path with an empty default route is 404` |
| The default route serves its sequence | `DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as sent | `RecordsTheRequestTargetAsSent` |
| "A route with no responses falls through … to 404" | **no test** (see F7) |
| `/pip-stub/configure` takes `*` | **no test through `handleConfigure`** (see F7) |
| "pip-mock and entitlements-mock behave as they did" | no test of its own; the existing pre-change tests cover the unrouted-404 path |
| Every Pod non-root with `RuntimeDefault` seccomp | **none** (F4) |
| Every container drops all capabilities and cannot escalate privileges | **none** (F4) |
| Every container but Keycloak has a read-only root | **none** (F4) |
| The suite Job gets an emptyDir at `/tmp` | **none** (F4) |
| No `runAsUser` is pinned | **none** (F4) |
| `app.kubernetes.io/*` labels and `helm.sh/chart` | **none** (F4) |
| Selectors keep `app: <name>` | **none** (F4) |
| The stand "could not start" under `restricted` PSS | **none**: no namespace in any harness carries the enforce label (F4) |
| The generator merges user files, fills the profile fields, and fails on a duplicate user or id | **none in CI** (F5) |

Commands the change tells someone to run, with the job that runs the same form:

| Command | Job that runs the same form |
| --- | --- |
| `make test-stand-files` | CI lint job (`integration-tests.yaml:74-77`) |
| `helm lint helm-templates/authz-test-stand -f <values>` | CI lint job (`integration-tests.yaml:83-84`) |
| `make e2e-harness`, `make parity-harness`, `make e2e-suite`, `make parity-suite` | the kind jobs, as per the CI header (not runnable here) |
| `helm upgrade authz-test-stand … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false` (`docs/local-integration-tests.md`, subset recipe) | **none** |
| `helm test authz-test-stand --timeout 15m --logs` (chart README step 3) | **none**: the Makefile runs `helm test` without `--logs` and streams the log with `kubectl` instead |
| `kubectl wait --for=create job/…` (inside `run-suite`) | the kind jobs run it, but on whatever kubectl the runner has |

**F4 (substantive): the security-context and label claims have no check that can fail.**
- `helm lint` passes with or without the securityContext blocks. `test/scripts/test-chart-render.sh` asserts securityContext only for the agent chart (around `:828`) and never renders the test-stand chart.
- `Makefile:86` and `:150` create the namespaces with `--create-namespace`, with no `pod-security.kubernetes.io/enforce: restricted` label. A drop of any of these fields would stay green.
- Request: render assertions for both values files in `test-chart-render.sh`. They should check `runAsNonRoot`, `seccompProfile.type`, `drop: [ALL]`, `allowPrivilegeEscalation: false`, `readOnlyRootFilesystem` true on every container except Keycloak, no `runAsUser`, the selector being only `app`, and the `/tmp` emptyDir. Better still, label the harness namespaces `enforce=restricted` so the kind jobs fail on a violation.

**F5 (substantive): the jq generator's behavior is claimed, but no CI run reaches it.**
- `testdata/realm/` holds only a README, so in CI `[.[1:][][]]` is empty. The `profile` function and both uniqueness checks (`Dockerfile`, `generate` stage) never run on a user file.
- I ran `profile.jq` on `parity-r29-level-m2m` and got `Parity`, `R29LevelM2M` and `parity-r29-level-m2m@example.test`, and a user that already had a `firstName` kept it. The duplicate-username and duplicate-id failures were not exercised.
- Request: a fixture directory fed to the same jq expression, with a duplicate pair that must fail the build. The documented and shipped form of the jq command should be the one that runs.

**F6 (substantive): `kubectl wait --for=create` needs kubectl 1.31 or newer, and no minimum is stated.**
- `Makefile:103` uses it, and the prerequisites table (`docs/local-integration-tests.md:37`) names only `kubectl version --client`.
- On an older kubectl the flag is rejected, the `&&` chain skips the polling loop, and the log is not streamed. `helm test` still runs, so the outcome is a missing log rather than a wrong result.
- Request: state the minimum kubectl version where the prerequisite is listed, or use a form that works on older versions.
- The subset recipe in the docs and `helm test --logs` in the chart README run in no job. Run the recipe once, or state that it is untested.

**F7 (substantive): hunks the commit messages do not claim.**
- `test/svt/common/compose/docker-compose.yml` moves Keycloak from `26.0` to `26.3.5` with a digest. No sentence of `8b85515` claims it, and the SVT stand is not part of the kind harness.
- `test/k8s/parity/idp-seed/parity-realm.json` gains 318 lines: roles `ROLE_MT_READER` and `ROLE_MT_ADMIN`, the `parity-m2m-tenant-a/b/unknown/empty` and `parity-end-user-tenant-a` clients, the `mt-a`, `mt-a-admin`, `parity-r29-scope` and `parity-r30-scope` users, and their mappers. The message says only "The parity realm gains a second tenant realm, parity-mt-b", which covers `parity-mt-b-realm.json` (98 lines) and not these.
- Request: a sentence claiming each, with the run that checks it, or move them to a change of their own.

## Item 3: Boundaries, partitions, and the negative control

**F8 (substantive): the replaced `*-suite` mechanism fails later and says less.**
- Fault: the suite image never starts (`ImagePullBackOff`, or the Pod unschedulable).
- Old code (`Makefile` at `58316ca`): `kubectl wait --for=condition=Ready pod -l job-name=… --timeout=3m` fails after about 3 minutes and prints `timed out waiting for the condition on pods/…`.
- New code (`run-suite`):
  - `wait --for=create` succeeds as soon as `helm test` creates the Job.
  - The loop then polls `kubectl logs` for 90 × 2 s, about 180 s, and each attempt may add its own time.
  - `kubectl logs -f` then fails and prints one error line.
  - `wait $helm_pid` blocks until `helm test --timeout 15m` returns, with `activeDeadlineSeconds: 900` as the other bound. That is 15 minutes, five times the old time, and the output is a single `logs` error, not the Pod state.
- The same wait also applies to the second fault, `helm test` failing before the Job exists: `wait --for=create` runs to its full 2 minutes before the `&&` chain stops, where the old code failed at the first `kubectl` error.
- No sentence of the change accepts the slower or quieter failure.
- Request: bound the whole wait at the old 3 minutes plus run time, and print the Pod state on failure (`kubectl get pod -l job-name=… -o wide` or `describe`). Then run the image-pull fault on the new target and record its duration and output.

**F9 (substantive): no test or run starts from the state the loose manifests left.**
- A kind cluster that ran the old `make e2e-harness` holds kubectl-applied objects: ConfigMap `keycloak-realms`, Secret `authz-agent-client-credentials`, Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`, and `idp`/`pip-mock` in the parity namespace.
- The new chart renders objects with the same names, and `helm upgrade --install` refuses to adopt objects it did not create ("exists and cannot be imported into the current release").
- The docs name `make e2e-down` only as a generic "cluster left behind" remedy (`docs/local-integration-tests.md:193`) and never tie it to this failure.
- I did not run this (no cluster). The Helm behavior is as I recall it from Helm's ownership check, not from a run.
- Request: the remedy in the docs (delete the namespace or the cluster), shown run on a stand installed by the old targets.

**F10 (substantive): the pip-stub partitions miss two claimed cases.**
- Partitions present: unrouted path with a default, routed path, routed with empty responses plus a default, no default route, and an empty default route.
- Missing: a routed path with empty responses and no default route. That is the claimed fall-through "or to 404", and it is the original `-1` index defect, since `route.Responses[-1]` indexed after `idx = len-1`.
- Missing: the claim "`/pip-stub/configure` now takes the path `*`" goes through `handleConfigure`, but every test writes `routes[...]` directly.
- Request: two small cases, a routed-empty path with no default giving 404, and a PUT of `[{"path":"*",…}]` to `handleConfigure` followed by an unrouted GET.

Other limits: the suite Job has `activeDeadlineSeconds: 900`, `helm test --timeout 15m` and `-test.timeout 600s`. The inner limit fires first at the defaults; nothing in the change raises these.

## Item 3a: Level, placement, and the environment

- The pip-stub tests sit beside the existing handler tests in `main_test.go` and use the same `resetState`. `serve` is a new helper and no existing helper builds the same thing. None.
- Chart behavior can only be checked as rendered YAML, which is a medium test. It is covered only by `helm lint` (F4). Skips: none added.

## Item 4: Names by content, not by position

None. Case names (`a routed path keeps its own answer`) and test names are by content, and the README sections use headings that name what they cover.

## Item 5: The failure report

None. The pip-stub table test prints method, path, status and body for got and want. `RecordsTheRequestTargetAsSent` prints both values, and the count check carries a message. No boolean-around-comparison assertion and no indexed case id was added.

## Item 6: What the writer says it verified

Neither commit message states a red run on the base commit or a mutation verdict. The default-route tests were not shown failing on `58316ca`, and no render of the securityContext was shown to differ from the unhardened chart. I did not run the suite, as the form says.

## Item 7: Siblings of the change

- `grep` for `docker.cfg` and "two images" in docs and workflows shows the release workflow header and the README updated for the three added images. No sentence still counts two. None.
- Helpers touched: `handlePIP`'s route lookup is the only reader of `routes` and `counters` for a request path. `counters` is documented as "legacy per-path response index" and is now also keyed by `*`, which is harmless.
- **F11 (taste):** `test/parity/suite/compare.go:139` writes `*.observed.json` next to the goldens and swallows errors. With the new read-only root filesystem on the parity Job those sidecars are silently not written. They are marked not evidence in `.gitignore`. The only reader is a human with a local run, so I would leave it, but it is a changed behavior of the suite that no sentence mentions.
- Labels and the security context were added to every template of the chart (ConfigMap, Deployment, Service, Secret, Job, ServiceAccount). I found no template without them.

## Index of findings

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Docs say `e2e-harness` installs the suite Job, which is a test hook | Substantive | `docs/local-integration-tests.md:104` | 1 |
| `sizeLimit` expression with no comment on its source | Substantive | `helm-templates/authz-test-stand/templates/suite.yaml:68` | 1 |
| Test comment sentence with an ambiguous "one" | Substantive | `test/integration/pipstub/main_test.go:222` | 1 |
| Security context, seccomp, read-only root, `/tmp` emptyDir, labels, selectors: no assertion; no `restricted` namespace | Substantive | `test/scripts/test-chart-render.sh`, `Makefile:86` | 2 |
| jq profile and duplicate checks never run on a user file | Substantive | `build/authz-agent-transfer/Dockerfile` (`generate` stage) | 2 |
| `kubectl wait --for=create` needs 1.31+, no minimum stated; two documented commands run in no job | Substantive | `Makefile:103`, `docs/local-integration-tests.md:37` | 2 |
| Unclaimed SVT Keycloak bump and +318 lines in `parity-realm.json` | Substantive | `test/svt/common/compose/docker-compose.yml:3`, `parity-realm.json` | 2 |
| `run-suite` fails in 15 minutes with one `logs` error, against 3 minutes with a `wait` message before | Substantive | `Makefile:98-108` | 3 |
| No run from the loose-manifest state, no remedy for the Helm ownership error | Substantive | `docs/local-integration-tests.md:193`, `Makefile:86` | 3 |
| Missing routed-empty with no default case; configure with `*` untested | Substantive | `test/integration/pipstub/main_test.go:225` | 3 |
| No red-run or mutation evidence in any commit | Substantive | commit messages | 6 |
| Read-only root silently stops the parity `*.observed.json` sidecar | Taste | `test/parity/suite/compare.go:139` | 7 |

Checks I could not do: the three runs that need a cluster or Docker (F8, F9, and the kind jobs themselves), and the drift script, which listed no members for this range.

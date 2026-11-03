The review found 11 substantive findings and 3 taste findings, listed in the table at the end. There was no task statement, so the claimed cases come from the three commit messages alone (`git log 58316ca..HEAD`). There is no previous report to compare against. The drift script exited 0 but printed nothing, because it does not parse Go, Helm templates, Makefiles, or Markdown. I went through the changed members of `test/integration/pipstub/main.go` by hand instead: the package comment, `callRecord`, `defaultRoute`, `handlePIP`, and the new tests.

## Item 1: comments consistent with the code and with each other

- **`docs/local-integration-tests.md:104`** (the `e2e-harness` row) says `e2e-harness` installs "…the client-credentials Secret, and the suite Job; waits until they are Ready". That is false. The Job carries the `helm.sh/hook: test` annotation (`templates/suite.yaml:21`), so `helm upgrade --install --wait` never creates it. `test/k8s/README.md:53`, `templates/suite.yaml`, and `values.yaml:86` all say only `helm test` runs it. A reader of this row expects a Job after the harness step, and looks for it when debugging. **Substantive.**
- **`test/integration/pipstub/main.go:38-39`**: "A stub nobody configures with it answers an unrouted request 404, as it did before the default route existed." The clause after the comma describes the change, not what the code does, so it is narration in a package comment. **Taste.**
- Everything else I checked holds:
  - the `defaultRoute` comment and the `RequestURI` field comment;
  - the "then the default route" precedence sentence;
  - "No request path is *". This holds because `net/http` sends `OPTIONS *` to its own global handler, so it never reaches `handlePIP`.
  - the `suite.yaml` comment on hook deletion;
  - the `values.yaml` comments, the Makefile comments for `run-suite`, `e2e-restart` and `test-stand-files`, and the `profile.jq` example. I ran `jq` on `parity-r29-level-m2m` and it gives `R29LevelM2M`.
  - `test/k8s/README.md` and `REALM-DESCRIPTION.md`.

## Item 2: claimed cases covered

Claimed cases and the evidence for each:

| Claimed case | Covered by |
| --- | --- |
| `*` as the default route answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer (control) | `…/a_routed_path_keeps_its_own_answer` |
| No `*` configured gives 404 as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| A route with no responses falls through **to 404** when there is no default route. This is the old index −1 path. | **No test.** The table has no row with an empty `routedResponses` and no default route. **Substantive.** |
| `/pip-stub/configure` takes the path `*` | **No test goes through `/pip-stub/configure`.** Every test assigns `routes[defaultRoute]` directly, so nothing checks that a JSON `{"path":"*"}` registers the default route. **Substantive (small).** |
| The default route serves its sequence clamped, across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| The chart's parts, each off by default, with the e2e and parity values | `helm lint` for both values files in CI (`integration-tests.yaml:74-75`). I ran `helm template` on a copy with the files filled in: e2e renders 12 objects and parity 10. |
| `make test-stand-files` fills in the profile fields; the build fails on a duplicate user | **Nothing exercises it.** `test/parity/suite/testdata/realm/` holds only `README.md`, so `profile` and both duplicate checks run on an empty set in every build. **Substantive.** |
| Restricted Pod Security Standard: the stand starts in an enforcing namespace | **No test or run.** The kind jobs create namespaces with no `pod-security.kubernetes.io/enforce` label, and `test/scripts/test-chart-render.sh` does not render this chart. **Substantive.** |
| Every object carries the `app.kubernetes.io/*` labels and `helm.sh/chart`; selectors keep `app` | Seen in my `helm template` output; no automated assertion |
| The release publishes three more images | `.qubership/docker.cfg` and `.github/docker-dev-config.json` entries; the `build_context` key matches `.agents/skills/qubership-actions-guide/docker.md:234` |

Command lines in the changed files:

| Command | Runs in | Outcome |
| --- | --- | --- |
| `make test-stand-files` | CI `chart` job (`integration-tests.yaml:77`) and both harness targets | covered |
| `make e2e-harness` / `e2e-suite` / `parity-harness` / `parity-suite` | CI `kind-e2e` and `kind-parity` | covered |
| `helm lint … authz-test-stand -f …` (twice) | CI `chart` job | covered |
| `docker build … -f build/authz-agent-transfer/Dockerfile .` | the dev build through `.github/docker-dev-config.json` | covered |
| `helm … upgrade authz-test-stand … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false`, then `make e2e-suite` (`docs/local-integration-tests.md:94-95`) | **none** | Depends on `--reuse-values` keeping `suite.env.BASE_URL` from the earlier `--set`, on Helm 4.3. **Substantive:** the request is one run of it. |
| Chart README transfer recipe: `docker create/cp/rm`, `helm upgrade --install … --set TAG=<version>`, `helm test … --timeout 15m --logs` | **none** | Depends on the tag form the release's `docker-action` gives the published images, and on the 15m limit (Item 3). **Substantive:** the request is one run on a non-kind stand, or a sentence that this recipe is untested. |

Hunks that no sentence of any commit message claims (**substantive**; the request is a sentence that claims each, or a separate commit):

- `test/svt/common/compose/docker-compose.yml:3`: Keycloak `26.0` → `26.3.5@sha256:…`, in the SVT compose stack.
- `test/k8s/parity/idp-seed/parity-realm.json` gains 318 lines: roles `ROLE_MT_READER` and `ROLE_MT_ADMIN`; clients `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a`; users `mt-a`, `mt-a-admin`, `parity-r29-scope`, `parity-r30-scope`. The commit message claims only "a second tenant realm, parity-mt-b". The `idp-seed/README.md` describes part of this, but no commit does.
- `test/k8s/authn/REALM-DESCRIPTION.md`: the issuer is corrected from `/realms/…` to `/auth/realms/…`. This fixes an error that predates the change, and no commit says so.

## Item 3: boundaries, partitions, and the negative control

**Partitions and controls in the pipstub tests.** The table holds the control: a routed path keeps its own answer. The boundaries of the response list (empty and non-empty) are covered for the default route. They are not covered for a routed path when no default route exists (see Item 2).

**State an earlier version left behind.** Any kind cluster that ran the old `make e2e-harness` or `make parity-harness` holds objects that `kubectl apply` created under the same names the chart now renders:

- e2e: Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`; ConfigMap `keycloak-realms`; Secret `authz-agent-client-credentials`; ServiceAccount `runtime-suite`.
- parity: Deployment and Service `idp`; ConfigMap `pip-mock-config`; Secret `authz-agent-client-credentials`.

`helm upgrade --install` refuses to adopt objects without Helm's ownership label and annotations ("invalid ownership metadata"), so the next `make e2e-harness` on such a cluster fails. Every CI run starts from a fresh kind cluster, and the docs give no remedy. **Substantive.** The request is a run of the new harness on a cluster set up by the old one, or a documented remedy (`make e2e-down`, or deleting the namespace first) that has been run on that state.

**Values users already pass.** `E2E_HELM_ARGS` now reaches the test-stand chart. It shares two names with the agent and policy-admin charts:
- `TAG` (`authz-agent/values.yaml:5`, `authz-test-stand/values.yaml:12`)
- `IMAGE_PULL_POLICY` (`authz-agent/values.yaml:88`, `authz-test-stand/values.yaml:13`)

What a value meant for the agent does to the test stand:
- `--set TAG=<x>`, meant to point the agent at another build, makes the stand ask for `local/pip-stub:<x>`, `local/tenant-manager:<x>`, and `local/authz-runtime-suite:<x>`. Nothing builds those, so the harness waits out its 10m.
- `--set IMAGE_PULL_POLICY=Always` makes the stand try to pull `local/*` images from a registry.

**Substantive.** The request is a separate setting for the test stand's install, or a run with `--set TAG=…`.

**Replaced mechanism: the suite run** (`Makefile:194-201` replaces the `wait Ready` / `logs -f` / `wait Complete` sequence):
- Old: a suite Pod that never starts, for example because the image was not side-loaded, failed at 3m (`wait --for=condition=Ready … --timeout=3m`) with `timed out waiting for the condition on pods/…`.
- New, on the same fault:
  1. `kubectl wait --for=create` returns at once.
  2. The log poll runs 90 × (2s + one `kubectl logs` call), about 3 minutes.
  3. `logs -f` prints the waiting reason and exits.
  4. `wait $helm_pid` then blocks until the Job's `activeDeadlineSeconds` (900s) or `helm test --timeout 15m` fires.

  So it fails at about 15 minutes instead of 3, and no sentence accepts that. **Substantive.** The request is a run of this fault with its duration and output, and a bound near the old 3 minutes on a Pod that never starts.
- The longest single attempt is `kubectl logs -f`, which has no timeout and is bounded only by the container's end.

**Replaced mechanism: the harness wait.** Old: the stubs failed at 2m each (`rollout status … --timeout=2m`). New: one `helm --wait --timeout 10m` covers everything, so a stub that never becomes Ready fails at 10m, not 2m. **Substantive**, with the same request: a run of that fault with both durations and outputs, or a sentence that accepts the change.

**Limits on the suite run:**
- `-test.timeout 600s` (`suite.args`, `values.yaml:95-96`)
- `suite.activeDeadlineSeconds: 900` (`values.yaml:99`, a documented setting)
- `helm test --timeout 15m`, fixed in `Makefile:196` and in `README.md:182`

Raise `activeDeadlineSeconds` to 1200 and `helm test` still gives up at 900s and exits as a timeout while the Job keeps running, so the setting has no effect. At the defaults, helm's 15m clock starts before the Job exists, so helm fires first by the seconds spent creating the Job. The Job's `DeadlineExceeded` is never what the user sees. **Substantive.** The request is to derive the `helm test` timeout from `suite.activeDeadlineSeconds` plus a margin.

## Item 3a: level, placement, and the environment

- The pipstub tests are small, sit beside the existing `TestHandlePIP_*` tests, and share `resetState`. That is fine.
- The chart's claims are observable without a cluster, through `helm template`: the security contexts on every Pod and container, the labels on every object, the `/tmp` emptyDir, and the `fail` messages when the generated files or `tenantManager.tenants` are missing. The repository already has render assertions for its other two charts in `test/scripts/test-chart-render.sh`, and none were added for this one. **Substantive.** The request is render assertions for these properties beside the existing ones.
- The kind CI jobs would show the restricted-PSS claim only if their namespaces enforced it, and they do not (see Item 2).

## Item 4: names by content, not by position

None. The test names and case ids name their condition. "The three charts" counts by content, and the count is right.

## Item 5: the failure report

None. Every new check is an `if … { t.Errorf(…) }` that prints got and want with the request target. The one `t.Fatalf` is the guard before indexing `calls[0]`. Table case ids are sentences.

## Item 6: what the writer says it verified

None of the three commits states a red run on the base commit, a mutation verdict, or the outcome of a kind run. I ran `go test ./...` in `test/integration/pipstub` as a consistency check, and it passed. `helm lint` passed on a copy of the chart with the files filled in by hand.

## Item 7: siblings of the change

- **The image set.** The three new images appear in both `.qubership/docker.cfg` and `.github/docker-dev-config.json`, in `README.md`, and in the release workflow comment. `git grep 'qubership-authz-policy-admin'` finds no other list of the images. None.
- **The removed manifests.** No file still names `runtime-suite-job.yaml`, `keycloak.yaml`, `pip-mock.yaml`, `m2m-credentials`, `keycloak-realms`, or `parity-realms` (checked with `git grep`). `e2e-logs` and `parity-logs` address `deploy/pip-stub` and `deploy/pip-mock`, and the chart keeps those names. None.
- **The `run-suite` helper's two call sites.** Both get the 15m limit and the late failure from Item 3.
- **`kubectl wait --for=create`**, which `run-suite` now relies on, exists only from kubectl 1.31. `docs/local-integration-tests.md:52` lists kubectl with no version. With an older kubectl the wait fails, the poll is skipped, and the log is not streamed. **Taste**, because I am working from memory on the version boundary.
- **`values.yaml:9-11`** lists the images the repository builds as "pip-stub, authz-parity-suite, and tenant-manager", but the e2e stand also runs `authz-runtime-suite` under the same `TAG`. **Taste.**

## Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| The `e2e-harness` row says the harness installs the suite Job and waits for it | Substantive | `docs/local-integration-tests.md:104` | Drop "and the suite Job"; it is a `helm test` hook |
| No test for a routed path with no responses and no default route (the old index −1 path) | Substantive | `test/integration/pipstub/main_test.go:225` | Add the row "a routed path with no responses and no default route is 404" |
| `*` is never registered through `/pip-stub/configure` | Substantive | `test/integration/pipstub/main_test.go:225` | One test that registers `*` with a JSON PUT to `/pip-stub/configure` |
| The profile filling and duplicate checks of `chart-files` run on an empty set | Substantive | `build/authz-agent-transfer/Dockerfile:322-329` | A fixture user file and a run showing the filled fields; a duplicate showing the build fails |
| The restricted-PSS claim is not exercised | Substantive | `.github/workflows/integration-tests.yaml` (kind jobs), `test/scripts/test-chart-render.sh` | Label a kind namespace `enforce=restricted`, or add render assertions on the security contexts |
| No render assertions for the test-stand chart | Substantive | `test/scripts/test-chart-render.sh` | Assert the security contexts, labels, `/tmp` emptyDir, and `fail` messages under `helm template` |
| Objects left by the old harness block `helm upgrade --install` | Substantive | `Makefile:177`, `Makefile:250` | A run from a cluster the old harness set up, or a documented remedy run on that state |
| `E2E_HELM_ARGS` sends `TAG` and `IMAGE_PULL_POLICY` meant for the agent to the stand | Substantive | `Makefile:126-128`, `:178`, `:251` | A setting of the stand's own, or a run with `--set TAG=…` |
| The suite run fails at about 15m where it failed at 3m; the harness at 10m where it failed at 2m | Substantive | `Makefile:194-201`, `:178` | Runs of both faults with durations and outputs; a bound at the old time, or a sentence that accepts the change |
| `helm test --timeout 15m` overrides `suite.activeDeadlineSeconds` | Substantive | `Makefile:196`, `helm-templates/authz-test-stand/README.md:182`, `values.yaml:99` | Derive the helm timeout from `activeDeadlineSeconds` plus a margin |
| Documented subset command and transfer-image recipe never run | Substantive | `docs/local-integration-tests.md:94-95`, `helm-templates/authz-test-stand/README.md:157-183` | One run of each, or say they are untested |
| Unclaimed hunks: SVT Keycloak bump, new `parity-realm.json` clients and users, `REALM-DESCRIPTION.md` issuer fix | Substantive | `test/svt/common/compose/docker-compose.yml:3`, `test/k8s/parity/idp-seed/parity-realm.json`, `test/k8s/authn/REALM-DESCRIPTION.md:7` | A commit-message sentence for each, or a separate commit |
| Package comment narrates history ("as it did before …") | Taste | `test/integration/pipstub/main.go:38-39` | End at "answers an unrouted request 404" |
| `kubectl wait --for=create` needs kubectl 1.31+, not listed in prerequisites | Taste | `docs/local-integration-tests.md:52` | Name the minimum kubectl version |
| The image list in the `TAG` comment omits `authz-runtime-suite` | Taste | `helm-templates/authz-test-stand/values.yaml:9-11` | Add it to the list |

Not checked: no kind run, no `docker build` of `chart-files` (I put the realm files in by hand to render the chart), and no prose pass for style alone. Go, the Helm templates, the Makefile, and the docs were read by hand.

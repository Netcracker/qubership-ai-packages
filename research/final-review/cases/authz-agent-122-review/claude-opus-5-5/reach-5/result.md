# Final review: `58316ca..HEAD` (three commits: test-stand chart, pip-stub default route, restricted PSS)

There was no separate task statement, so the claimed cases come only from the three commit messages and the comments of the tests. There is no previous report for this change.

The drift script exited 0 and printed nothing, because it only parses JVM files (`EXT = (".java", ".kt", …)`). I read every changed Go member, template comment, and values comment by hand. I lint-rendered the chart with `helm lint` and `helm template` against both values files. To do that without touching the repo, I copied the chart to the scratchpad and built its `files/` there the way the `chart-files` stage does. `go test` in `test/integration/pipstub` passes.

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:34-36`, and `defaultRoute` at `:122`**: these say the default route answers "every request whose path has no route of its own". The code also sends a path whose route has no responses to it (`!ok || len(route.Responses) == 0`, `:236`). The commit message and the test comment state that case; the package doc and the constant's doc leave it out.
- **`main.go:37-38`** says "as it did before the default route existed". This narrates the change (taste).
- **`helm-templates/authz-test-stand/templates/_helpers.tpl:2-4`** says the selectors keep `app: <name>` "so the Makefile's deploy/<name> and a reader's kubectl -l app=<name> address a part". That reason is false: `deploy/<name>` resolves by the Deployment's name, whatever its selector. The real constraint is that `spec.selector` is immutable, so changing it would break `helm upgrade` of a release installed earlier.
- **`test/k8s/parity/idp-seed/parity-realm.json:29-34`**: the role descriptions cite "TestTenantScopedDecisions and others" and "the wildcard policy of tenant A". `git grep` finds no such test and no such policy anywhere in the repository.
- **`helm-templates/authz-test-stand/values.yaml:9-11`**: the list of images that `TAG` applies to leaves out `authz-runtime-suite`, which the e2e values use (taste).
- Checked and consistent:
  - `callRecord.RequestURI`, the handler's step-2 comment, and `serve`.
  - `testify/helpers.go` `LoadConfig` and the testify `Dockerfile` pointer.
  - The `suite.yaml` hook comment and the `idp.yaml` probe arithmetic (60 × 5 s = 5 min).
  - The idp-seed README's claims about `mt-a`, `mt-b`, and `parity-m2m-tenant-b`, which I checked against the JSON with `jq`.

## Item 2: claimed cases covered

| Claim (commit) | Covered by |
| --- | --- |
| An unrouted path gets the default route's answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer (control) | `…/a_routed_path_keeps_its_own_answer` |
| A stub with no `*` route answers 404 as before | `…/an_unrouted_path_without_a_default_route_is_404` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| …**or to 404** | **none**: no row has a routed path with empty responses and no default route |
| The default route is served in sequence | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` checks the struct field, not the JSON key `requestUri` that `/pip-stub/calls` returns (taste) |
| `/pip-stub/configure` takes `*` | Tests write `routes[defaultRoute]` directly; `handleConfigure` itself is unchanged (taste) |
| The chart installs each harness | CI `kind-e2e` and `kind-parity` run `make e2e-harness` and `make parity-harness`, on a fresh cluster only |
| Restricted PSS: the stand starts in a namespace that enforces it | **none**: no namespace is labeled `pod-security.kubernetes.io/enforce=restricted`. CI's kind namespaces admit any Pod, so a missing `seccompProfile` or `runAsNonRoot` would pass. The kubelet still enforces read-only root, non-root, and dropped capabilities, so the CI kind runs do exercise those. |
| `profile.jq` fills the profile fields, and the build fails on a duplicate user | **none** in the repo: `testdata/realm/` has no user file. I ran `profile` by hand on three users and got the documented output (`R29LevelM2M`, etc.). |
| `make test-stand-files` | CI lint job |
| `helm lint` for both values files | CI lint job |

Commands in the changed docs:

| Command | What runs it |
| --- | --- |
| Chart README transfer-image steps (`docker create`/`docker cp`, `helm upgrade --install … --set TAG`, `helm test --logs`) | **none**. I rendered step 2: removing the four keys and passing `--set TAG=1.2.3` yields `ghcr.io/netcracker/qubership-authz-{pip-stub,parity-suite}:1.2.3`, which matches `.qubership/docker.cfg`. |
| `docs/local-integration-tests.md` subset recipe (`helm upgrade --reuse-values --set …RUNTIME_SUITE_RUN=…`) | **none**. I rendered it, and the env values come out as intended. |
| `docker build … build/authz-agent-transfer/Dockerfile .` | Same file and context in `.github/docker-dev-config.json` |

Hunks that no sentence of any commit message claims:

- **`test/svt/common/compose/docker-compose.yml`**: Keycloak goes from `26.0` to `26.3.5@sha256:…`. This changes the version the SVT stack runs.
- **`parity-realm.json`** adds:
  - the clients `parity-m2m-tenant-a`, `-unknown`, `-empty`, and `parity-end-user-tenant-a`;
  - the `parity-level-claim` mapper;
  - the users `parity-r29-scope` and `parity-r30-scope`.

  The message claims only "a second tenant realm, parity-mt-b". Nothing in the repository uses any of these (`git grep` outside `idp-seed/`).
- **`.github/docker-dev-config.json`** adds three images to the CI dev builds. The message only says the release publishes them, from `docker.cfg`.
- **`REALM-DESCRIPTION.md`** corrects the issuer to `/auth/realms/…`. The old text was already wrong, but the message doesn't mention the fix (taste).

## Item 3: boundaries, partitions, and the negative control

**Pip-stub.** The partitions of route state × default state are covered except one: a routed path with empty responses and no default route. On the base commit that input indexed at -1; the commit claims it now gets 404, and no row tests it.

**State left by the earlier version.** Before this change, `make e2e-harness` and `make parity-harness` used `kubectl apply` to create objects with no Helm ownership metadata:
- Deployments `keycloak`/`idp`, `pip-stub`/`pip-mock`, `entitlements-mock`, `tenant-manager`
- Secret `authz-agent-client-credentials`
- ConfigMaps `keycloak-realms` and `pip-mock-config`
- ServiceAccount `runtime-suite`

The new chart renders objects with the same names, so on a namespace the old harness set up, `helm upgrade --install authz-test-stand` should fail with "invalid ownership metadata". Every CI run starts from a fresh kind cluster, and no doc names the remedy (`make e2e-down`, or deleting the namespace). The selectors still match the previous commit's chart, so the upgrade from `8b85515` to `17b17fc` itself is fine.

**Values users already pass.** `E2E_HELM_ARGS` now also reaches the test stand (`Makefile:85`, `:149`). The keys both the old and the new consumers read are `TAG` and `IMAGE_PULL_POLICY`:
- `IMAGE_PULL_POLICY=Never` is harmless. The stand's values already set it, and Keycloak has its own `idp.imagePullPolicy`.
- `--set TAG=dev`, meant for the agent, renders `local/pip-stub:dev`, `local/tenant-manager:dev`, and `local/authz-runtime-suite:dev` (I checked with `helm template`). With pull policy `Never`, those Pods fail with `ErrImageNeverPull`, and `--wait` runs until its 10 m timeout.

**Limits.** These limits bound the suite run:
- `-test.timeout 600s`, in `suite.args`
- `suite.activeDeadlineSeconds: 900`, in `values.yaml`
- `helm test --timeout 15m`, fixed in `Makefile:102`
- the CI job's `timeout-minutes: 30`

The documented `suite.activeDeadlineSeconds` has no effect past 900 under `make e2e-suite`, because the fixed `helm test --timeout 15m` fires first. The chart README's step 3 repeats the same fixed 15 m. At the defaults the inner limits fire first.

The `/tmp` emptyDir's `sizeLimit` is derived from the container's `ephemeral-storage` limit, so the two move together.

## Item 3a: level, placement, and the environment

- The pip-stub tests are small. They sit in `main_test.go` beside the existing `handlePIP` tests and reuse `resetState`.
- The chart's security context is observable at render level, with no cluster. `test/scripts/test-chart-render.sh` exists for render assertions but does not render `authz-test-stand`. So no render assertion covers the restricted-PSS fields on every Pod and container, or the `fail` messages for missing `files/`.
- The cross-boundary check would be the kind namespace labeled `enforce=restricted`, which CI already provisions in the kind jobs. That label is missing (item 2).

## Item 4: names by content, not by position

Test and subtest names are by content. `values.yaml:11` ("Keycloak has its own image and pull policy below") could name `idp.image` instead (taste). Nothing else turned up.

## Item 5: the failure report

None found. `TestHandlePIP_DefaultRouteAnswersUnroutedPaths` prints the method, path, got, and want with `t.Errorf` inside named `t.Run` rows. The sequence test prints got and want slices. The `requestUri` test prints all four operands. No row ids are indexes.

## Item 6: what the writer says it verified

No commit message states a red run on the base commit, a mutation verdict, or a kind run (fresh state or under restricted PSS).

## Item 7: siblings of the change

**Set membership.** Three images were added to `docker.cfg` and `docker-dev-config.json`. `README.md:59` still reads "CI builds **both** via `.github/docker-dev-config.json`", which now lists five images. `README.md:66` already counts "the two services" correctly.

The other places that list the members are consistent:
- `.github/workflows/docker-release.yaml` comments
- `test/k8s/README.md` file table (old manifests removed)
- `.PHONY`, which includes `test-stand-files`
- `E2E_LOCAL_DEPLOYMENTS` and `PARITY_LOCAL_DEPLOYMENTS`, which match the chart's Deployment names

`git grep` for the deleted manifest names finds nothing outside `docs/handovers` and `docs/decisions`.

**Callers.** There are 7 callers of `/pip-stub/configure` (testify ×6, parity config). None configures empty responses or `*`, so the new fall-through changes nothing for them.

**Contradiction between docs.** `docs/local-integration-tests.md:104` says `e2e-harness` installs "the suite Job; waits until they are Ready". `test/k8s/README.md` says correctly that the Job is a `helm test` hook and installing does not start it.

## Findings

| Finding | Label | File:line | Change requested |
| --- | --- | --- | --- |
| Restricted-PSS claim has no run: kind namespaces don't enforce `restricted`, and no render assertion covers the fields | Substantive | `Makefile:85`, `:149`; `test/scripts/test-chart-render.sh` | Label the namespace `pod-security.kubernetes.io/enforce=restricted` in both harness targets, or add render assertions for every Pod and container |
| Upgrade over the old `kubectl apply` harness collides with unowned objects; no remedy documented | Substantive | `Makefile:85`, `:149`; `docs/local-integration-tests.md` | Document `make e2e-down` (or deleting the namespace) for an existing stand, and run it once on such a stand |
| `E2E_HELM_ARGS` with `--set TAG=…` now retags the stand's local images | Substantive | `Makefile:48`, `:85`, `:149` | Give the stand its own args variable, or stop passing `E2E_HELM_ARGS` to it |
| `suite.activeDeadlineSeconds` past 900 has no effect: `helm test --timeout 15m` is fixed | Substantive | `Makefile:102`; chart `README.md` step 3; `values.yaml:99` | Derive the `helm test` timeout from the value, or document the coupling |
| SVT compose Keycloak bump claimed by no sentence | Substantive | `test/svt/common/compose/docker-compose.yml:3` | A sentence that claims it plus an SVT run, or move it to its own change |
| Parity realm gains clients, users, and a mapper that nothing uses and no sentence claims; role descriptions cite a nonexistent test | Substantive | `test/k8s/parity/idp-seed/parity-realm.json:29-34`, `:121-330`, `:449-475` | Claim them in the message and fix the descriptions, or move them to the change that adds the cases |
| `profile.jq` merge and the duplicate-user check are exercised by no input in the repo | Substantive | `build/authz-agent-transfer/Dockerfile:39-47` | A fixture user file, or a CI step that runs the stage on a sample with a duplicate and expects failure |
| Empty route with no default route → 404 is claimed but untested | Substantive | `test/integration/pipstub/main_test.go:237` | Add the row `"/routed", []pipResponse{}, nil, 404` |
| Package doc and `defaultRoute` doc omit the empty-route fall-through | Substantive | `test/integration/pipstub/main.go:34-36`, `:122` | Name that case in both comments |
| Labels helper gives a false reason for keeping the selectors | Substantive | `_helpers.tpl:2-4` | State the real reason: `spec.selector` is immutable across upgrades |
| Stale count: "CI builds both" | Substantive | `README.md:59` | Update the count, or name the list |
| `e2e-harness` row lists the suite Job as installed and waited for | Substantive | `docs/local-integration-tests.md:104` | Drop the Job from that row, as `test/k8s/README.md` does |
| `docker-dev-config.json` additions and the REALM-DESCRIPTION issuer fix are unclaimed | Taste | `.github/docker-dev-config.json`; `test/k8s/authn/REALM-DESCRIPTION.md` | One sentence each in the message |
| Tests write `routes[...]` directly and check the struct field, not `/pip-stub/configure` or the `requestUri` JSON key | Taste | `main_test.go:246-250`, `:276-286` | One test through `handleConfigure` and `handleCalls` |
| Narration ("as it did before…"); `TAG` image list incomplete; positional "below" | Taste | `main.go:37-38`; `values.yaml:9-11` | Reword |

This review did not run anything on a cluster: not the kind harnesses, not an install over the old harness's objects, and not a namespace that enforces `restricted`. It did not inspect what the `qubership-core-base` entrypoint does on a read-only root filesystem, and ran no Go suite other than pip-stub's. It did not review the prose for style.

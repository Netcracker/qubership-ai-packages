# Final review: `58316ca..HEAD` (8b85515, 9d25da7, 17b17fc)

There was no task statement, so the claimed cases come from the three commit messages and the test comments. There was no earlier report of this form to check against. I loaded `test-authoring` and `english-developer-style`. The repository has no Go doc-comment skill copy, so I read the Go comments against the form's own Item 1 rules.

I ran `comment-drift.py 58316ca… HEAD` and it printed nothing (exit 0). So I read the changed members of `test/integration/pipstub/main.go` by hand:
- The package comment changed.
- Three comments are new: `defaultRoute`, `callRecord.RequestURI`, and `serve`.
- `handlePIP` changed and has no doc comment.

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:37-38`** narrates the change: "A stub nobody configures with it answers an unrouted request 404, as it did before the default route existed." "As it did before" is history. The fact can be stated on its own: "A stub with no default route answers an unrouted request 404."
- **`README.md:59`** says "CI builds both via `.github/docker-dev-config.json`". That file now lists five images (`.github/docker-dev-config.json:12-31`), so "both" is false.
- **`.github/docs-for-publication-task.md:77`** says "The two-entry array in this repository's `docker-dev-config.json`". It now has five entries.
- **`docs/local-integration-tests.md:104`** says `e2e-harness` installs "… the client-credentials Secret, and the suite Job; waits until they are Ready". The Job is a `helm.sh/hook: test` (`templates/suite.yaml:21`), so an install never creates it. `test/k8s/README.md:53` and `:41-42` say the opposite ("installing the stand does not start it"). A reader of the docs page will look for a Job that does not exist after the harness step.
- **`Makefile:189-190`** says "`helm test` … prints the log only at the end, so the log is streamed while it runs". The recipe runs `helm test` without `--logs`, and without it Helm prints no log at all. The sentence describes a flag the command does not pass.
- **`helm-templates/authz-test-stand/values.yaml:9-11`** lists the images that `TAG` applies to as "pip-stub, authz-parity-suite, and tenant-manager". The e2e stand also tags `local/authz-runtime-suite` with it (`test/k8s/test-stand-values.yaml:48`), and `templates/suite.yaml:40` applies `TAG` to whatever suite image is set. The list should name the suite image in general.

The other new comments are true of the code:
- `defaultRoute`, `RequestURI` and `serve`.
- The comments in the chart templates and helpers.
- The `profile.jq` header: I ran it, and `parity-r29-level-m2m` becomes `R29LevelM2M`.
- `idp.yaml:34` "A changed realm file restarts the Pod": I edited one file and the checksum annotation changed from `1fb38d…` to `a31518…`.

## Item 2: claimed cases covered

| Claimed case | Covered by |
| --- | --- |
| Default route `*` answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an unrouted path gets the default answer` |
| A routed path keeps its own answer | `…/a routed path keeps its own answer` |
| Route with no responses falls through **to the default route** | `…/a routed path with no responses gets the default answer` |
| Route with no responses falls through **to 404** when there is no default route. This is the base-commit `-1` index case | **none**. Every empty-route case either has a default route or uses an unrouted path. |
| A stub with no `*` answers 404 as before | `…/an unrouted path without a default route is 404` |
| Precedence: rules first, then the path routes, then the default route (package comment, `main.go:29-31`) | **none**. No test sets a rule and a default route together, so a default route consulted before the rules would still pass. |
| Default route serves its sequence across paths, clamped to the last response | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| `/pip-stub/configure` takes the path `*` | Indirect only: the tests write `routes` directly. `handleConfigure` did not change and stores any path. Taste. |
| Chart parts off by default | Not tested in the repo. I rendered the chart with defaults and got 0 objects. |
| Keycloak imports realms at every start and restarts on a change | Covered only by the kind jobs. I checked the checksum offline (Item 1). |
| Stubs by Service name, tenant map, Secret, suite as a `helm test` hook | `helm lint` in the CI `chart` job, plus `kind-e2e` and `kind-parity` |
| `make test-stand-files` / `e2e-harness` / `parity-harness` / `e2e-suite` / `parity-suite` | CI jobs `chart`, `kind-e2e`, `kind-parity` |
| Merge of the users under `testdata/realm/`, fill-in of the profile fields, build fails on a duplicate user | **none** in the repo, because the directory holds no users and every CI run merges nothing. I ran the jq locally: the fields are filled, declared fields are kept, and a duplicate `mt-a` makes `jq -e` exit 1. |
| Error texts `no realm files under files/realms/<realms>/` and `no file files/pip-stub/<file>` | Not tested in the repo. I reproduced the second one with `helm template`. |
| Restricted Pod Security Standard (17b17fc) | **none**. No namespace in CI or the Makefile carries a `pod-security.kubernetes.io/enforce=restricted` label, and no render assertion checks the security contexts. |
| Read-only root filesystem works for pip-stub, tenant-manager and the suites | Covered only by the kind jobs. The change states no run of them. |

Commands in the changed files:

| Command | Runs in | Status |
| --- | --- | --- |
| `make test-stand-files`, `make e2e-*`, `make parity-*` | CI `chart`, `kind-e2e`, `kind-parity` on Helm v4.3.1 | Covered |
| `helm lint helm-templates/authz-test-stand -f …` | CI `chart` job | Covered |
| README transfer-image recipe: `docker create … true`, `docker cp`, `helm upgrade --install … --set TAG=<version>` | **none** | Sound on reading: `docker create` does not exec `true` on a scratch image. |
| `docs/local-integration-tests.md:137` `helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=…` | **none** | Sound on reading. |
| `helm-templates/authz-test-stand/README.md:64` `helm test authz-test-stand --timeout 15m --logs` | **none** | Substantive, see below. |

The `--logs` recipe needs a closer look. Its outcome depends on the test hook being a **Job**, not a Pod:
- **Helm 3** (read in the v3.15.2 source, `pkg/action/release_testing.go:127`): `GetPodLogs` asks for the Pod named after the hook, `Pods(ns).GetLogs(h.Name)`. No Pod is named `parity-suite`; the Job's Pod has a generated suffix. Helm 3 therefore fails with `unable to get pod logs for parity-suite` and exits non-zero even when the suite passed.
- **Helm 4.3.0** (the local binary): its strings include `job-name=` and `POD LOGS: %s (%s)`. That suggests Helm 4 resolves the Pods of a Job, but I did not confirm it.
- The README names no Helm version.

**Hunks no sentence of the commit messages claims:**
- **`test/svt/common/compose/docker-compose.yml:3`**: the SVT Compose Keycloak goes from `26.0` to `26.3.5@sha256:…`.
- **`.github/docker-dev-config.json`**: three images are added to the dev build that runs on every CI build. The message speaks only of the release (`docker.cfg`).
- **`test/k8s/parity/idp-seed/parity-realm.json`** (+318 lines):
  - What it adds:
    - the roles `ROLE_MT_READER` and `ROLE_MT_ADMIN`;
    - the clients `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a`;
    - the users `parity-r29-scope`, `parity-r30-scope`, `mt-a` and `mt-a-admin`.
  - The message says only "The parity realm gains a second tenant realm, parity-mt-b", which also reads wrongly: a realm does not gain a realm.
  - Nothing outside `idp-seed/` uses any of these names.
- **`test/k8s/authn/REALM-DESCRIPTION.md`**: the issuer is corrected from `/realms/…` to `/auth/realms/…`. It is a small doc fix, but still unclaimed.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub partitions.** The test set varies two inputs: whether the path has a route and how many responses that route has. It covers an unrouted path, a routed path, and empty-route and empty-default cases. It is missing:
  - the routed-but-empty path with **no** default route (Item 2);
  - the rule-engine control: a matching rule plus a default route, which must answer from the rule.
  
  The clamp-to-last boundary is covered.
- **Pre-existing state.** A developer kind cluster that ran the old harness has these in `authz-e2e` and `authz-parity`, created by `kubectl apply` with no Helm ownership metadata:
  - the Deployments and Services `keycloak` / `idp`, `pip-stub` / `pip-mock` and `entitlements-mock`, plus `tenant-manager` in `authz-e2e` only;
  - the ConfigMaps `keycloak-realms`, `parity-realms` and `pip-mock-config`;
  - the Secret `authz-agent-client-credentials`;
  - the ServiceAccount `runtime-suite`.
  
  `helm upgrade --install authz-test-stand` then refuses each name the chart also renders: `… exists and cannot be imported into the current release: invalid ownership metadata`. Every run in the change starts from a fresh cluster, and no doc gives the remedy. The only one available is `make e2e-down`, or `kubectl delete namespace` for parity.
- **Values that now reach a new consumer.** `E2E_HELM_ARGS` now also reaches the test-stand install (`Makefile:178`, `:251`). Two names are read by all three charts, `TAG` and `IMAGE_PULL_POLICY`:
  - The documented example, `IMAGE_PULL_POLICY=Never`, is harmless.
  - `--set TAG=1.4.0`, passed to run the agent chart on a published build, makes the stand ask for `local/pip-stub:1.4.0`, `local/tenant-manager:1.4.0` and the suite image under the same tag. Nothing builds those, so the stand's `--wait` runs out after 10 minutes.
  - `IMAGE_PULL_POLICY=Always` makes kind try to pull `local/…:ci` from a registry.
  
  `test/k8s/README.md:63` and `Makefile:126` present this as intended.
- **Limits on the suite run.** Three limits apply to the same suite run:
  - the suite's `-test.timeout 600s`;
  - the Job's `activeDeadlineSeconds: 900`, a documented value at `values.yaml:99`;
  - `helm test --timeout 15m`, fixed in `Makefile:196`.
  
  `helm test` starts counting before the Job exists, so at the defaults its 15 minutes run out at or before the Job's 900 s. The outer `timed out waiting for the condition` hides the Job's `DeadlineExceeded`. Raising `suite.activeDeadlineSeconds` past 900 has no effect under `make e2e-suite` / `parity-suite`. Before this change, `e2e-suite` had no outer cap on the Job. The CI job's `timeout-minutes: 30` already bounded the old flow; I only note it.

## Item 3a: level, placement, and the environment

- The pip-stub tests are at the smallest level (`httptest` against `handlePIP`). They sit in the existing `main_test.go` and share its `resetState` fixture. Good.
- The chart's behavior can be seen with `helm template`, which needs no cluster:
  - the security contexts and labels;
  - the `required` / `fail` messages;
  - the checksum annotation;
  - the `sizeLimit` default;
  - the Job hook annotations.
  
  The repository already runs such checks offline in `test/scripts/test-chart-render.sh`, on the agent and policy-admin charts. The change adds none for `authz-test-stand`, so all of these are seen only by `helm lint` (which asserts nothing about them) and by the kind jobs. That is substantive. In particular, the restricted-PSS claim is checked nowhere.
- The CI `chart` job now needs Docker for `make test-stand-files`. `ubuntu-latest` provides Docker, so this is fine.

## Item 4: names by content, not by position

None. I checked the subtest names, which are all descriptive sentences, the comments in the values files ("A second instance for the entitlements endpoint" names its content), and the Makefile and README references. All refer to things by content.

## Item 5: the failure report

None. The new tests use `t.Errorf` / `t.Fatalf` with every operand printed:
- `GET %s = %d %s, want %d %s`;
- `statuses of /a, /b, /a = %v, want %v`;
- `requestUri %q, path %q, want %q and %q`.

The table cases are named, not indexed. The `||` in `TestHandlePIP_RecordsTheRequestTargetAsSent` is acceptable because the message prints both fields.

## Item 6: what the writer says it verified

None of the three commits states a red run on the base commit, a mutation verdict, or a run of the kind harnesses or the restricted-PSS claim. As gate-level consistency checks, I ran:
- `go test` of `test/integration/pipstub`: passes.
- `helm lint` and `helm template` of the chart with both values files, using stand-in `files/`: passes.

## Item 7: siblings of the change

- **The image set** grew from two to five in `docker-dev-config.json` and from two to five in `docker.cfg`. `README.md:62-66` and the `docker-release.yaml` header were updated. `README.md:59` ("both") and `.github/docs-for-publication-task.md:77` ("two-entry") were not (Item 1).
- **The `E2E_HELM_ARGS` readers**: all three installs per harness now read it (Item 3).
- **`readOnlyRootFilesystem`**: the sibling charts set it only when `PAAS_PLATFORM` is `KUBERNETES` (`helm-templates/authz-agent/templates/deployment.yaml:266`, `authz-policy-admin/…:138`). The stand sets it unconditionally. The stand claims OpenShift compatibility only for `runAsUser`. This is taste: the platform convention is the reason the sibling charts give.
- **`run-suite`**: both callers, `e2e-suite` and `parity-suite`, use the same macro, so the timeout pair in Item 3 applies to both.
- **`handlePIP` callers**: there is one route registration (`main.go:155`). No other code indexes `counters`.

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | `helm test --logs` with a Job hook: Helm 3 asks for a Pod named `parity-suite` and fails after a passing suite. Helm 4 is unverified. No run of this form exists, and the README names no Helm version. | Substantive | `helm-templates/authz-test-stand/README.md:64` | Run the form on Helm 3 and 4, or replace it with the `kubectl logs job/<name>` form the Makefile uses, or state "Helm 4 only" with a run. |
| 2 | Re-running `make e2e-harness` / `parity-harness` on a cluster from the old harness fails on Helm ownership of `keycloak`, `idp`, `pip-stub`, `pip-mock`, `entitlements-mock`, `tenant-manager`, `keycloak-realms`, `authz-agent-client-credentials` and `runtime-suite`. No doc gives a remedy. | Substantive | `Makefile:177-178`, `:250-251` | Document the remedy (`make e2e-down`, or delete the namespace), or run the upgrade on such a cluster. |
| 3 | `E2E_HELM_ARGS` now reaches the stand. `TAG` or `IMAGE_PULL_POLICY` set for the agent charts makes the stand ask for images nothing builds. | Substantive | `Makefile:126-128`, `:178`, `:251` | Give the stand its own setting, or keep `E2E_HELM_ARGS` off the stand install. |
| 4 | `helm test --timeout 15m` runs out at or before `activeDeadlineSeconds: 900`. It hides the Job's report, and raising the documented value has no effect. | Substantive | `Makefile:196`, `values.yaml:99` | Derive one from the other (for example, the helm timeout = the deadline + a margin), or set both in one place. |
| 5 | The restricted-PSS and label claims have no test: no namespace is labeled `enforce=restricted`, and no render assertion exists for the chart. | Substantive | `templates/_helpers.tpl`, `test/scripts/test-chart-render.sh` | Add render assertions for the stand (security contexts, labels, `fail` texts, hook annotations), and label the kind namespaces `restricted`. |
| 6 | No case for a routed path with no responses and no default route, which is the `-1` index case the commit names. | Substantive | `test/integration/pipstub/main_test.go:510-518` | Add `"a routed path with no responses and no default route is 404"`. |
| 7 | No control showing that a matching rule wins over the default route. | Substantive | `test/integration/pipstub/main_test.go` | Add a test with a rule and `*` both configured, expecting the rule's answer. |
| 8 | The docs say `e2e-harness` installs and waits for "the suite Job", which contradicts `test/k8s/README.md` and the hook. | Substantive | `docs/local-integration-tests.md:104` | Drop the Job from that row, or say it is a `helm test` hook that the harness does not start. |
| 9 | "CI builds both" and "two-entry array" are stale: there are five images now. | Substantive | `README.md:59`, `.github/docs-for-publication-task.md:77` | Update the counts. |
| 10 | The Makefile comment says `helm test` prints the log at the end, but the recipe runs it without `--logs`. | Substantive | `Makefile:189-190` | State why the log is streamed without relying on `--logs`. |
| 11 | Hunks no sentence claims: the SVT Keycloak bump, the dev-build image list, and the +318 lines of tenant clients and users in `parity-realm.json` (whose description also reads wrongly). | Substantive | `test/svt/common/compose/docker-compose.yml:3`, `.github/docker-dev-config.json`, `test/k8s/parity/idp-seed/parity-realm.json` | Claim each in the message with its check, or move it to its own change. |
| 12 | The user-merge, profile-fill and duplicate checks of `chart-files` have no run in the repo, because `testdata/realm/` is empty. | Substantive | `build/authz-agent-transfer/Dockerfile:340-347` | Add a fixture run, for example a CI step that builds `chart-files` against a sample user file and a duplicate. |
| 13 | The `TAG` comment omits the runtime-suite image. | Substantive | `helm-templates/authz-test-stand/values.yaml:9-11` | Name the suite image in general. |
| 14 | The package comment narrates history ("as it did before the default route existed"). | Taste | `test/integration/pipstub/main.go:37-38` | State the fact without the history. |
| 15 | `readOnlyRootFilesystem` is unconditional here but limited to Kubernetes in the sibling charts. | Taste | `templates/_helpers.tpl:34-36` | Follow the siblings' `PAAS_PLATFORM` condition, or say why the stand differs. |
| 16 | `/pip-stub/configure` with `*` is tested only by writing `routes` directly. | Taste | `test/integration/pipstub/main_test.go:522-525` | Configure `*` once through `handleConfigure`. |

**Not checked:** I did not install anything on a cluster, so none of these ran: the kind harnesses, `helm test`, the restricted-PSS admission, or the read-only root of the qubership-core-base images. The Helm 4 `--logs` behavior is inferred from strings in the binary, not from its source. `make test-stand-files` was not run (the chart was rendered with stand-in `files/`). I did not run the suites on the base commit, and I did not do a style pass over the prose.

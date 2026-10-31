# Final review of `58316ca..HEAD`, three commits: 8b85515, 9d25da7, 17b17fc

**Task statement:** none was handed over, so claimed cases come from the three commit messages alone.

**Drift script:** I ran it and it printed nothing. It parses only Java, Kotlin, Groovy and Scala. This change is Go, YAML, Helm templates, a Makefile, a Dockerfile and Markdown, so I read the Go comments by hand and used the analogues of §2a for the rest.

**Skills loaded:** `test-authoring` and `english-developer-style`, from the given directory. Wording appears only where a sentence reads wrongly.

**Runs I made** (no cluster, nothing changed in the tree):
- `go test` and `go vet` on `test/integration/pipstub`: pass.
- I copied the chart to the scratchpad and generated `files/` by hand with `cp`. `helm lint` and `helm template` are clean for both values files.
- I ran the `chart-files` `jq` pipeline locally on sample user files, with a jq 1.8.2 binary.

## Item 1: Comments consistent with the code and with each other

Two findings, both under that item.

1. **Substantive:** `docs/local-integration-tests.md:104` says `e2e-harness` installs the chart including "the suite Job" and "waits until they are Ready".
   - The Job is a `helm test` hook (`templates/suite.yaml`, annotation `helm.sh/hook: test`). Installing creates no Job.
   - `test/k8s/README.md` ("installing the stand does not start it") and the Makefile comment say so. The docs page contradicts them.
   - A reader looks for the Job after `e2e-harness`, finds none, and suspects the install.
   - **Request:** drop "and the suite Job" from that row, or write "defines the suite Job as a `helm test` hook".
2. **Taste:** the comment on `containerSecurityContext` in `_helpers.tpl` ("Takes the value of readOnlyRootFilesystem: true for every container except Keycloak") reads as if the argument is `true` for all containers but one.
   - I'd say "Takes the value of `readOnlyRootFilesystem`: `true`, except for Keycloak, which gets `false`." Expect this to be declined.

Everything else checked is consistent:
- `pipstub/main.go` header and `defaultRoute` comments match the code.
- The "five minutes" startup-probe comment is right (5 s × 60).
- Dockerfile file lists, `profile.jq` and the `idp-seed` README match the files.

## Item 2: Claimed cases covered

### Claimed cases

| Claim | Test | Result |
| --- | --- | --- |
| An unrouted path gets the default answer | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an unrouted path gets the default answer` | covered |
| A routed path keeps its own answer | `.../a routed path keeps its own answer` | covered |
| A route with no responses falls through to the default route | `.../a routed path with no responses gets the default answer` | covered |
| A route with no responses falls through "or to 404" | none | **missing**, finding 3 |
| No default route gives 404, as before | `.../an unrouted path without a default route is 404` | covered |
| An empty default route gives 404 | `.../an unrouted path with an empty default route is 404` | covered |
| The default route serves its sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` | covered |
| `requestUri` is kept as received | `TestHandlePIP_RecordsTheRequestTargetAsSent` | covered |
| `/pip-stub/configure` takes `*` | none through `handleConfigure` | taste, see below |
| Realm merge, profile fill, duplicate refusal | none | **missing**, finding 4 |
| Restricted PSS on every Pod; read-only root filesystem except Keycloak; `/tmp` emptyDir; no `runAsUser`; labels; selectors keep `app:` | none | **missing**, finding 5 |
| Realm change restarts Keycloak (checksum annotation) | none | unrun |
| `helm lint` of both values files | CI job `chart` | covered |
| End-to-end harnesses | CI jobs `kind-e2e` and `kind-parity` | covered |

Findings:

3. **Substantive:** the case that used to index the sequence at -1 has no test.
   - That case is a routed path with empty `Responses` and no default route. It should now answer 404.
   - The three tests that exist are "empty route with a default route", "unrouted without a default route" and "unrouted with an empty default route".
   - The commit message claims "falls through to the default route, or to 404".
   - **Request:** add a row such as `a routed path with no responses and no default route is 404`. It would have panicked on the base commit.
4. **Substantive:** the user-file merge, the `profile` fill and the duplicate refusal are claimed in the 8b85515 message, `Dockerfile:36-48` and `testdata/realm/README.md`. The directory holds no user files, so no CI job runs any of these.
   - I ran the pipeline by hand with three sample files. The fill gives `R29LevelM2M` and `parity-r29-level-m2m@example.test`, an existing `firstName` is kept, and a duplicate username makes `jq -e` exit 1. The zero-file case leaves the 14 users unchanged.
   - The repository still contains no fixture for it.
   - **Request:** a small fixture, or a `make` check that runs the stage on one sample file and asserts the three outcomes.
5. **Substantive:** 17b17fc claims restricted Pod Security compliance, but nothing checks it.
   - `helm lint` is the only chart check CI runs on the chart. `test/scripts/test-chart-render.sh` is the repository's render-assertion mechanism and has no test-stand case.
   - The Pod-level and container-level fields can be observed in-process with `helm template`. The test-authoring skill (§3) asks for the smallest level that observes the behavior.
   - **Request:**
     - Add render assertions for both values files: `runAsNonRoot`, `seccompProfile`, `allowPrivilegeEscalation: false`, drop ALL, `readOnlyRootFilesystem` true everywhere except the Keycloak container, the `/tmp` volume on the Job, no `runAsUser` anywhere, and `app:` still the only selector label.
     - Optionally label the kind namespace `pod-security.kubernetes.io/enforce=restricted`. Without that, no CI run ever admits these Pods under the policy the commit is written for.
   - My manual count: of 5 (e2e) and 4 (parity) workloads, all carry `runAsNonRoot` and `allowPrivilegeEscalation: false`. Only Keycloak has `readOnlyRootFilesystem: false`. All four images declare numeric `USER 10001:10001`, or Keycloak's numeric 1000, so `runAsNonRoot` verifies.
6. **Taste:** `handleConfigure` is not exercised with the path `*`. The tests set `routes[defaultRoute]` directly. The code path is the same map assignment, so this is low risk.

### Commands the change tells someone to run

| Command | Promised outcome | Form that runs |
| --- | --- | --- |
| `make test-stand-files` | writes `files/` | CI job `chart`; same form |
| `make e2e-harness` / `make parity-harness` | install the stand | CI, same targets |
| `make e2e-suite` / `make parity-suite` | run the suite, exit with its outcome | CI, same targets |
| `docker create … true; docker cp …` (chart README) | copies `/charts` out of a `FROM scratch` image | none |
| `helm upgrade … --set TAG=<version> -f my-values` (chart README) | install from the copied charts | none |
| `helm test authz-test-stand --timeout 15m --logs` (chart README) | run the suite and print the log | none (the Makefile omits `--logs`) |
| `helm upgrade --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …FULL_RUNTIME_SUITE=false` (`docs/local-integration-tests.md`) | runs a subset | none |

For the `none` rows:
- **`docker create` on `FROM scratch`:** `create` does not check that `true` exists, so `cp` works. This is the common idiom and I expect it to work.
- **`--logs`:** it is a `helm test` flag in Helm 3.4+ and in the pinned 4.3.1, and it prints the hook Pods' logs after the run. I expect it to work.
- **`--reuse-values`:**
  - Helm merges `--set` over the stored values, so only `suite.env.RUNTIME_SUITE_RUN` and `suite.env.FULL_RUNTIME_SUITE` change.
  - `$` and `/` are inert in `--set`.
  - `helm test` renders the hook from the stored release manifest, so the new env reaches the Job.
  - The upgrade needs `files/`, which `e2e-harness` generated earlier. I expect it to work.

I did not run any of these, so they stay unrun. No finding.

### Claims read the other way

7. **Substantive:** `test/svt/common/compose/docker-compose.yml` moves Keycloak from `26.0` to `26.3.5@sha256…`.
   - No commit sentence claims it, and the SVT stack is not a kind harness.
   - A 26.0 → 26.3.5 move can change realm import and token behavior for the SVT runs.
   - **Request:** a sentence in the 8b85515 message claiming it, with a run of the SVT stack, or move the hunk to its own commit.
8. **Substantive:** `parity-realm.json` grows from 192 to 510 lines. These are pure additions: the `mt-a` and `mt-a-admin` users, the `parity-m2m-tenant-a`, `-b`, `-unknown` and `-empty` clients, and `parity-end-user-tenant-a`.
   - The commit says only "The parity realm gains a second tenant realm, parity-mt-b".
   - Nothing in the repository references `mt-a` or the tenant clients outside the realm files and READMEs, and `test/k8s/parity/values.yaml` does not name the new realm as a trusted provider.
   - **Request:** a sentence in the message that names the added users and clients and the cases that will use them, or move those additions to the commit that adds the cases.

The `.dockerignore`, `.gitignore`, `docker.cfg` and `docker-dev-config.json` hunks are claimed by "publishes … from `.qubership/docker.cfg`" and by the generated files.

## Item 3: Boundaries, partitions, and the negative control

**Boundaries and control.** The `pipstub` suite has the control: the routed path keeps its own answer, and no default route still gives 404. It is missing the case from finding 3. There is also no case that a matching rule wins over the default route. The code order is unchanged, so I call that taste.

**Inherited state (substantive).**
9. 8b85515 replaces objects that `kubectl apply` created, and the change shows no test or documented remedy.
   - Examples: Deployment, Service and ConfigMap `keycloak`, ConfigMap `keycloak-realms`, Deployments `pip-stub`, `entitlements-mock`, `tenant-manager`, `pip-mock` and `idp`, ConfigMap `pip-mock-config`, ServiceAccount `runtime-suite`, and Secret `authz-agent-client-credentials`.
   - The Makefile creates them with `kubectl` and keeps the namespace across runs.
   - A developer who runs `make e2e-harness` on an old namespace gets Helm's "exists and cannot be imported into the current release: invalid ownership metadata". The new chart's names collide with the old ones.
   - Every test and CI run starts from a fresh kind cluster. A search of docs, README and Makefile for such a note finds none.
   - **Request:** run the upgrade on a namespace prepared by the base commit. Then document the remedy (for example `make e2e-down`, or deleting the namespace) in the harness README and `docs/local-integration-tests.md §6`.

**Values users already pass.**
10. **Substantive:** `E2E_HELM_ARGS` now reaches the test-stand chart too. The Makefile comment says so ("every chart install, the test stand's included").
    - Names the old charts and the new one both read: `TAG` and `IMAGE_PULL_POLICY`. `TAG` is read at `helm-templates/authz-agent/templates/deployment.yaml:153` and in `pip-stub.yaml`, `suite.yaml` and `tenant-manager.yaml`. `IMAGE_PULL_POLICY` is read at `deployment.yaml:154` and in the same three templates.
    - Only the documented `--set IMAGE_PULL_POLICY=Never` is harmless. A user who sets `--set TAG=<x>` for the agent also retargets `local/pip-stub`, `local/authz-parity-suite` and `local/tenant-manager`. `e2e-images` builds all of them only as `:ci`, so those Pods hit `ErrImageNeverPull`.
    - The new chart has no `values.schema.json`, so nothing flags this.
    - **Request:** a stand-specific key (the way `suite.imageRepository` is), or a run with `E2E_HELM_ARGS='--set TAG=…'` and a stated outcome.

**Mechanism replaced.** `run-suite` replaces `kubectl wait --for=condition=Ready pod … --timeout=3m; logs -f; wait --for=condition=Complete … --timeout=1m`.

11. **Substantive:** the new mechanism fails later and prints less on the most common fault, a Job Pod that never starts (image pull failure or unschedulable).

    | | Old | New |
    | --- | --- | --- |
    | Time to fail | 3 minutes | up to 15 minutes |
    | Output | `error: timed out waiting for the condition on pods/…` | one `kubectl logs` waiting-to-start error after the 180 s poll loop, then silence until helm's timeout |

    - **New path:** `kubectl wait --for=create` succeeds at once, because the Job exists. The 90 × 2 s poll then ends after about 180 s. `logs -f` fails once. `wait $helm_pid` then blocks until `helm test --timeout 15m` gives up (`activeDeadlineSeconds: 900` agrees). The Job's own 900 s deadline was in the old manifest too.
    - **Second fault (one attempt waits longest):** `kubectl logs` has no request timeout, so a hung API call is not bounded either.
    - **Request:** a run of the "image missing" fault with its duration and output. Bound the whole wait at the old 3 minutes to Ready, or print the Pod's waiting reason, or say in the change why 15 minutes is accepted.

**Other limits on the same work.** The change moves no limit: `15m` for `helm test` matches the Job deadline of 900 s, and the `go test` timeout is 600 s inside it. Nothing to report.

## Item 3a: Level, placement, and the environment

- **Substantive:** the rendered security contexts and labels are observable with `helm template`, without a cluster. They are covered only by `helm lint` (finding 5). The in-process method is `test/scripts/test-chart-render.sh`.
- The `pipstub` tests sit in the existing `main_test.go`, reuse `resetState`, and use the file's shape (plain `testing`, `reflect`, `strings`). Placement is fine.
- I found no optional prerequisites that should skip.

## Item 4: Names by content, not by position

None. Test names in `main_test.go` and table case names are by content. The Dockerfile and chart say "the two tenant realms" and "the two stubs", which are counts of a fixed set, not ordinals.

## Item 5: The failure report

None.
- Go `t.Errorf` calls print got and want, with the request path.
- Table cases have content names.
- `TestHandlePIP_RecordsTheRequestTargetAsSent` prints both fields and both wants.
- The one `len(calls) != 1` guard prints the count and the want.

## Item 6: What the writer says it verified

The change carries no evidence that the tests can fail: no red run on the base commit and no mutation verdict. The commit messages state no `helm template`, kind or `make e2e` run for the chart and Makefile changes either.
- I did not run the suite on the base to supply it.
- A red run is easy for `pipstub`: the base commit has no default route and indexes -1 for an empty route.
- The statement is missing for the chart and Makefile changes.

## Item 7: Siblings of the change

- **Set of released images.** I searched for two members by name (`qubership-authz-agent`, `qubership-authz-policy-admin`) and read every file that names both: `.qubership/docker.cfg`, `.github/docker-dev-config.json`, `.github/workflows/docker-release.yaml` and `README.md`. All now list the three added images. The old count ("both images", "the two Docker images", "two images") remains only inside the `qubership-actions-guide` skill files as a generic example. Nothing to fix.
- **Deleted files.** I searched for the removed manifests and Secrets (`test/k8s/keycloak.yaml`, `runtime-suite-job.yaml`, `parity-suite-job.yaml`, `m2m-credentials`, `keycloak-realms`, `parity-realms`, `pip-mock-config`) outside the new chart. No stale reference remains. The two Go comments that cited the Job file were updated.
- **`callRecord.requestUri`.** The only other consumer of the record is the stub's own JSON. Nothing else references `requestUri`.
- **Keycloak version.** The same `26.3.5` digest now appears in the chart, `test/BASELINE.md` and, since this change, the SVT compose file (finding 7).
- **Old Keycloak option dropped.** The removed `keycloak.yaml` set `-Dkeycloak.migration.strategy=OVERWRITE_EXISTING`. The new Deployment does not. With the dev-mode H2 database on the container filesystem every Pod starts empty, so it does not matter.

## Index of findings

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| Docs say `e2e-harness` installs the suite Job; it is a `helm test` hook | Substantive | `docs/local-integration-tests.md:104` | 1 |
| `containerSecurityContext` comment reads as taking `true` for all but one | Taste | `helm-templates/authz-test-stand/templates/_helpers.tpl:23` | 1 |
| No test for a routed path with no responses and no default route (the former -1 case) | Substantive | `test/integration/pipstub/main_test.go:224` | 2 |
| Realm user merge, profile fill and duplicate refusal not run by any CI job | Substantive | `build/authz-agent-transfer/Dockerfile:36` | 2 |
| Restricted-PSS, read-only filesystem, labels and selectors claims have no render assertion | Substantive | `test/scripts/test-chart-render.sh` | 2 / 3a |
| `/pip-stub/configure` with `*` not tested through the handler | Taste | `test/integration/pipstub/main_test.go` | 2 |
| Unclaimed Keycloak bump `26.0` → `26.3.5` in SVT compose | Substantive | `test/svt/common/compose/docker-compose.yml:3` | 2 |
| `parity-realm.json` +318 lines (users and clients) beyond the message's claim | Substantive | `test/k8s/parity/idp-seed/parity-realm.json` | 2 |
| Chart replaces `kubectl`-applied objects; no inherited-state run or documented remedy | Substantive | `Makefile:86`, `:150` | 3 |
| `E2E_HELM_ARGS` `TAG` now retargets the local stub and suite images | Substantive | `Makefile:86`, `helm-templates/authz-test-stand/values.yaml:7` | 3 |
| `run-suite` fails at 15 min and prints less than the old 3 min on a Pod that never starts | Substantive | `Makefile:100-106` | 3 |
| No red-run or mutation evidence stated for any of the three commits | Substantive | commit messages | 6 |

Checks I could not do: no cluster, so the Pod-start behavior (Keycloak under `readOnlyRootFilesystem: false`, the suite under a read-only root with only `/tmp` writable) and the failure timings in finding 11 are derived from the code, not run. I also did not run the Docker build of the transfer image, only the `jq` stage.

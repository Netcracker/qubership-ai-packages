## Final review: `58316ca..HEAD` (three commits)

**Claimed cases:** no task statement was handed over, so the claims come from the three commit messages (17b17fc, 9d25da7, 8b85515), the Go test comments, and the README and comments that the change adds. The change has no Java, Kotlin, Groovy, or Scala files, so the drift script printed nothing. Item 1 was read by hand over the Go and Helm comments.

**Skills:** `test-authoring` was loaded from the given directory. `english-developer-style` is not in that directory, and I did not load another copy, so wording was not checked. No Go doc-comment skill is there either, so Go comments were checked only against this form.

**Checks run:** `go test -count=1 -v ./...` in `test/integration/pipstub` passes, including all five subtests of the default-route test. I staged a copy of the chart in the scratchpad with the generated `files/` tree and ran `helm lint` (passes with both values files), `helm template` with no values (empty, so everything is off by default), and a render with each values file (12 objects in e2e, each carrying `helm.sh/chart`). I ran the profile program from `profile.jq` on a sample user file and the duplicate guard, outside the repo. Nothing in the repo was changed. No previous report exists, so there is no table of prior findings.

### Item 1: comments consistent with the code and with each other
Checked against the code: the `callRecord.RequestURI` and `defaultRoute` comments, the package comment in `main.go`, the tenant-manager 404 claim (`test/integration/tenantmanager/main.go:97`), the issuer and Service-name comments in both values files, the `RUNTIME_SUITE_RUN` comment, the helper comments in `_helpers.tpl`, the probe and `startupProbe` timings, and the parity README's realm, user, and client facts (checked against the realm JSON). The `$(RUNTIME_SUITE_RUN)` arg is expanded by Kubernetes from the container's own env, as the old Job also relied on, so it works. Findings are in the table below.

### Item 2: claimed cases covered
- 9d25da7 Go cases: unrouted path gets the default, routed path keeps its own answer, routed path with no responses gets the default, no default gives 404, empty default gives 404, sequence across paths, and request target as sent. All are named and present. One is missing: a routed path with no responses and no default must give 404 (finding 3).
- 8b85515 profile fill (`R29LevelM2M`, existing first name kept, build fails on a duplicate username): no test or run exercises it, because no user file exists yet (finding 2).
- 17b17fc security claims (restricted PSS, read-only root, non-root, labels, default off): no assertion anywhere. The repo's `test/scripts/test-chart-render.sh` covers the other charts but not this one (finding 4).

### Item 3: boundaries, partitions, and the negative control
Go: the cases split into red on the base commit (unrouted paths, sequence, and the `-1` index panic from the empty-responses case) and green on the base (routed path keeps its answer). The negative control is present.

Pre-existing state: the chart creates objects with the same names as those the old manifests applied (e2e: Deployments and Services `keycloak`, `pip-stub`, `entitlements-mock`, `tenant-manager`, ConfigMap `keycloak-realms`, Secret `authz-agent-client-credentials`, ServiceAccount `runtime-suite`; parity: `idp`, `pip-mock`, `entitlements-mock`, ConfigMap `pip-mock-config`, the Secret). Helm refuses to adopt resources that lack its ownership labels and annotations. So `make e2e-harness` or `make parity-harness` on a cluster built by the old layout should fail at install. I have not run that against a cluster; the claim is from Helm's ownership rule. No run starts from that state and no remedy is documented. The only cluster reset in the docs is `make e2e-down` (`docs/local-integration-tests.md:115`, `:193`).

### Item 3a: level, placement, environment
The Go tests are in-process and sit beside the existing ones in `main_test.go`. `go-build.yaml:63` runs that package in CI. The chart has no level-appropriate test. Lint runs in CI (`integration-tests.yaml:83-84`), but it covers only rendering.

### Item 4: names by content
None. Test names, Helm comments, and Makefile comments refer to content, not ordinals.

### Item 5: the failure report
Go: the `t.Errorf` calls print got and want. Helm: none. Build: the duplicate guard in the Dockerfile prints a bare `false` and names no user (finding 7).

### Item 6: what the writer says it verified
Not stated. None of the three commit messages gives a red run on the base commit or a mutation result for the Go tests, and the regression cases in 9d25da7 are the ones that need one (finding 5). I did not run the base to supply it.

### Item 7: siblings
- `containerSecurityContext` has four call sites (pip-stub ×2, tenant-manager, suite set to true; Keycloak set to false). `podSecurityContext` is used by all five Pods. All 12 objects in the e2e render carry `helm.sh/chart`, so the label helper reaches every object.
- `git grep` finds no remaining references to the removed manifests, `E2E_AUTHN`, or `PARITY_SEED`. The `testify` Dockerfile and `helpers.go` comments were updated.
- The `svt` compose Keycloak bump (26.0 to 26.3.5, `test/svt/common/compose/docker-compose.yml:3`) is in the diff and in no commit message (finding 8).

### Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| 1. Objects from the old manifests (same names as the chart's) will make the first `helm upgrade --install` on an existing kind cluster fail on Helm's ownership check. Not run; no remedy documented. | substantive | `Makefile` `e2e-harness`, `parity-harness`; `helm-templates/authz-test-stand/templates/*.yaml`; `docs/local-integration-tests.md:115`, `:193` | Name the remedy (`make e2e-down`, or deleting the namespace) in the docs and in the change description. Run `make e2e-harness` once from a cluster built by the old layout and state the outcome. |
| 2. Profile fill and duplicate guard are untested: no user file exists, so the `R29LevelM2M` derivation, the kept first name, and the duplicate exit never run. I checked each by hand and they behave as claimed. | substantive | `build/authz-agent-transfer/Dockerfile:39-46`; `test/parity/suite/testdata/realm/README.md` | Add a check that runs `profile.jq` and the two `jq -e` guards on a sample user file kept outside `testdata/realm/`, asserting the derived names and the duplicate failure. |
| 3. Claimed case has no test: a routed path with no responses and no default route should answer 404. The table has the other four 404 and default cases only. | substantive | `test/integration/pipstub/main_test.go:225-260` | Add the case `{"a routed path with no responses and no default is 404", "/routed", []pipResponse{}, nil, 404, ...}`. |
| 4. Chart claims (off by default, non-root, seccomp, read-only root except Keycloak, labels) have no assertion. Verified by hand only. | substantive | `helm-templates/authz-test-stand/templates/*.yaml`; `test/scripts/test-chart-render.sh` | Add test-stand assertions to `test-chart-render.sh`: empty default render, the per-container `securityContext`, and the `helm.sh/chart` label on every object. |
| 5. Regression tests in 9d25da7 (the `-1` index panic and the unrouted default) have no red run on the base commit stated anywhere. | substantive | commit `9d25da7` message; `main_test.go:225`, `:263` | State the base-commit red run for the default-route and request-target tests in the description. |
| 6. The package comment and the `defaultRoute` comment say the default answers requests whose path has "no route of its own". A route with no responses also falls through, as the commit message says. | taste | `test/integration/pipstub/main.go:34-36`, `:122-124` | Say "no route that answers" or name the empty-responses case. |
| 7. The duplicate guard fails with a bare `false` and does not name the user. | taste | `build/authz-agent-transfer/Dockerfile:45-46` | Print the duplicate usernames on failure, for example `jq -r` over the duplicate set. |
| 8. The `svt` compose Keycloak bump appears in no commit message. | taste | `test/svt/common/compose/docker-compose.yml:3` | Mention it in the change description. |
| 9. `REALM-DESCRIPTION.md` says `make e2e-harness` runs Keycloak with two realm files. It imports four (the two tenant realms are left out). | taste | `test/k8s/authn/REALM-DESCRIPTION.md`, "How the Runtime Environment Uses This Import" | List all four, or say "among others". |

**Not checked:** the kind harnesses were not run, and no cluster was available, so the migration failure (finding 1) and the Keycloak 9000 readiness path were not confirmed against a live stand. The Dockerfile's `jq` image path (`/jq`) was not checked offline. `english-developer-style` was not available, so wording was not reviewed, and the Go doc comments were checked only against this form.

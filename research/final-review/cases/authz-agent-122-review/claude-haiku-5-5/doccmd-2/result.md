# Final review: `58316ca..HEAD` (three commits)

**Scope and inputs.** No task statement was handed over, so the claimed cases come from the three commit messages (17b17fc, 9d25da7, 8b85515) and the `TestHandlePIP_*` comments. There is no previous report. The drift script printed nothing: no Java, Kotlin, Groovy, or Scala file changed, and Go and YAML are not parsed, so I read every comment by hand. I loaded `test-authoring` and `english-developer-style` from the provided skills directory. `godoc-authoring` was not among the provided copies, so Go doc comments were checked against the form's own text. For the chart, Makefile, and docs parts I used the §2a analogues where the literal wording did not fit.

**Local runs (nothing in the repo changed):** `go test` and `go vet` in `test/integration/pipstub` passed. `helm lint` passed for both value sets, with the generated `files/` staged in a scratch copy. `helm template` rendered both sets, plus the documented subset `--set` values. `make -n` expanded the `run-suite` recipes. The transfer image's jq stage ran on sample data.

## Item 1: comments consistent with code and each other

Findings: the default-route comments are wrong about scope and contain a false sentence (`main.go:35-36`, `122-123`). The Makefile says `helm test` prints the log at the end, but this invocation has no `--logs` (`Makefile:96`). The tenant-manager tag is called "the release version" although the image is unpublished (`values.yaml:9-10`).

Checked and consistent: the issuer-host comments in both `test-stand-values.yaml` files against the agent values, the `suite.yaml` hook comment, the `idp.yaml` no-bootstrap-admin comment (`KcAdminUser` is a realm user's token, not the Keycloak admin API), the `testify/Dockerfile` and `helpers.go` comments, and the chart README. No narration words (`now`, `no longer`, `used to`) appear in the changed text.

## Item 2: claimed cases covered

| Claim (source) | Test or check | Result |
|---|---|---|
| Unrouted path gets the default answer (9d25da7) | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths`, row 1 | covered |
| Routed path keeps its own answer; this is the negative control (9d25da7) | same test, row 2 | covered, green on base |
| Route with no responses falls to the default (9d25da7) | same test, row 3 | covered |
| Route with no responses falls to 404 (9d25da7) | none | **missing** |
| Unconfigured `*` answers 404 (9d25da7) | same test, rows 4 and 5 | covered |
| `/pip-stub/configure` takes `*` (9d25da7) | none; tests write `routes` directly | **not exercised** |
| Default route serves its sequence across paths, clamped (9d25da7) | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` | covered |
| `requestUri` keeps the target as sent (9d25da7) | `TestHandlePIP_RecordsTheRequestTargetAsSent` | covered |
| Every container drops ALL, no escalation, read-only root except Keycloak (17b17fc) | none | **no render assertion** |
| Pod runs non-root with RuntimeDefault seccomp, no `runAsUser` (17b17fc) | rendered output | matches |
| Job gets an `emptyDir` at `/tmp` (17b17fc) | rendered output | matches |
| Labels on every object, selectors keep `app: <name>` (17b17fc) | rendered: 17 `part-of` labels, 8 selectors | matches |
| Chart off by default; each harness turns on its parts (8b85515) | values and rendered objects | matches |
| Parity realm gains `parity-mt-b` (8b85515) | rendered `idp-realms` ConfigMap | matches |
| Release publishes three images; tenant-manager and runtime suite stay unpublished (8b85515) | `.qubership/docker.cfg` | matches |
| The stub "comes with the cases that use it" (9d25da7) | no case in this range configures `*` | **unmet** |

Commands the change tells someone to run:

| Command (location) | Same form in CI? | Outcome and status |
|---|---|---|
| `make test-stand-files` (Makefile:77; CI:76-77) | yes | writes `files/`; not run here (docker not run) |
| `make e2e-harness`, `make parity-harness` (Makefile:85, 149) | yes (CI:145, 191) | installs release, waits Ready; not run (no cluster) |
| `make e2e-suite`, `make parity-suite` (Makefile:100-115) | yes (CI:151, 197) | runs `helm test`, streams log, exits with helm's status; not run |
| `helm lint ... -f test/k8s/test-stand-values.yaml` (CI:83-84) | yes | passes for both sets |
| `helm test authz-test-stand --timeout 15m --logs` (chart README:64) | none | `--logs` exists in local helm 4.3.0; not run |
| `docker create ... true` and `docker cp` (chart README:42-44) | none | not verified (scratch image, no run) |
| `helm upgrade --reuse-values --set suite.env.RUNTIME_SUITE_RUN=...` (docs §6) | none | rendered: the regex reaches the Job env; install not run |

Not verified: the Keycloak image's numeric USER (needed for `runAsNonRoot`), admission under the restricted PSS, and the Keycloak management path under `KC_HTTP_RELATIVE_PATH`. `kubectl wait --for=create` needs a recent kubectl; the local 1.33.9 accepts it, and the docs name no minimum.

## Item 3: boundaries, partitions, negative control

The boundary is covered: the sequence clamp (third request) and the empty-route row. The missing boundary is the empty-route row with no default route (see Item 2). The pre-existing state is the finding: a cluster stood up by the base harness holds objects the new release would have to adopt, and no migration remedy is documented. See the table.

## Item 3a: level, placement, environment

The pipstub tests are in-process, the smallest level, and CI runs that module (`.github/workflows/go-build.yaml:63`). They sit beside the existing tests and reuse `resetState`. The chart's security claims have no test below the cluster: CI only lints the chart, and `test/scripts/test-chart-render.sh` covers only the agent and policy-admin charts. Nothing skips.

## Item 4: names by content

One ordinal: `test/k8s/test-stand-values.yaml:21` says "A second instance" for `entitlements-mock`, which is named on the next line. The other "first" and "last" uses describe roles, not named things. Test names are content-named.

## Item 5: failure report

None. The `t.Errorf` calls print the operands, and the tests use the values in the message.

## Item 6: what the writer says it verified

Not stated. None of the three commits carries a red run or a mutation verdict. The Go tests cannot be red on base as written, since they reference `defaultRoute` and `RequestURI`, so the evidence should be a base run that fails on the behavior, not on a missing symbol.

## Item 7: siblings

- Read-only root, other write sites: `writeObservedSidecar` writes under the golden tree, which the image copies to `/app/test/parity/suite/testdata` (`Dockerfile:24`). The parity Job is read-only, and the error is discarded, so the `.observed.json` evidence silently disappears. The `/tmp` emptyDir does not cover it.
- Deployment names used by `e2e-restart`, `e2e-logs`, `parity-restart`, and `parity-logs` all exist in the renders.
- Stale doc reference: the troubleshooting row at `docs/local-integration-tests.md:190`.
- Readers of `counters`: `handleReset` and `handlePIP` only.

## Findings

| # | Finding | Label | File and line | Change requested |
|---|---|---|---|---|
| 1 | Parity observed sidecar is discarded silently on the read-only root | substantive | `test/parity/suite/compare.go:139-146`; `helm-templates/authz-test-stand/templates/suite.yaml:57`; `test/parity/suite/Dockerfile:24` | Write the sidecar to a writable mount, or return the error; or name it as follow-up |
| 2 | A cluster from the base harness cannot take the new release | substantive | `Makefile:85-86`, `149-150`; `helm-templates/authz-test-stand/templates/idp.yaml:9`; `client-credentials.yaml:5` | Document the remedy (`make e2e-down` or deleting the base objects), and show it run on such a stand (not run here; reasoned from Helm's ownership check) |
| 3 | Restricted-PSS and read-only claims have no render assertion | substantive | `test/scripts/test-chart-render.sh`; `.github/workflows/integration-tests.yaml:79-84` | Add a render assertion on each container's securityContext, with the Keycloak exception |
| 4 | Route with empty responses and no default has no 404 case; `*` never goes through `handleConfigure` in a test | substantive | `test/integration/pipstub/main_test.go:225-243` | Add the 404 row; add one case that configures `*` through `handleConfigure` |
| 5 | Default-route comments: scope is incomplete, and "No request path is *" is false | substantive | `test/integration/pipstub/main.go:35-36`, `122-123` | Say the default also answers a path whose route has no responses; drop the `*` sentence (`OPTIONS *` has path `*`, checked locally) |
| 6 | "The stub comes with the cases that use it" is unmet in this range | substantive | commit 9d25da7; `main_test.go:249`, `263` | Add the case, or state the claim as follow-up |
| 7 | Makefile says `helm test` prints the log at the end; this call has no `--logs` | substantive | `Makefile:96` | Say the log is streamed by `kubectl logs -f`; `helm test` prints the outcome only |
| 8 | tenant-manager tag described as "the release version" | substantive | `helm-templates/authz-test-stand/values.yaml:9-10` | Drop tenant-manager from that sentence; its image is unpublished (chart README:36-37) |
| 9 | Troubleshooting row names a message `e2e-harness` no longer prints | substantive | `docs/local-integration-tests.md:190` | Replace with the `helm --wait` timeout message |
| 10 | Iteration row applies test-stand values with `make e2e-install` | substantive | `docs/local-integration-tests.md:126` | Split: agent values to `e2e-install`; test-stand values to `e2e-harness` |
| 11 | Ordinal "A second instance" for a named stub | substantive (Item 4) | `test/k8s/test-stand-values.yaml:21` | Say "The `entitlements-mock` instance" |
| 12 | No red run or mutation verdict stated | substantive | the three commit messages; `main_test.go:225-283` | State a base-commit run that fails on the behavior |

Taste: none. Churn: none.

**Not checked:** the suites were not run, and no cluster, image pull, `docker build`, or Helm install was done. Admission under the restricted PSS and the Keycloak image user were not checked. The `godoc-authoring` skill was not loaded, and no style pass was made beyond the items above.

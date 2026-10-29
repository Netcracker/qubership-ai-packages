I've filled the form for `58316ca..HEAD`. There was no task statement, so every claimed case comes from the three commit messages, as the skill allows. There is no previous report of this form over the change, so the report has no opening carry-over table. The drift script printed nothing: it only parses Java, Kotlin, Groovy and Scala. I read the changed Go members, YAML and Markdown by hand instead.

The pip-stub change itself holds up: its tests pass and cover the empty and 404 cases. The real problems are in the kind harness: an existing cluster can't be upgraded in place, `E2E_HELM_ARGS` now reaches the stand, the restricted Pod Security claim has no check, the suite timeouts are set separately, and several hunks and docs don't match the commit messages.

## Item 1: comments consistent with the code and with each other

Members whose code or comment changed:
- In `test/integration/pipstub/main.go`: the package doc, `callRecord.RequestURI`, `defaultRoute`, and step 2 of `handlePIP`.
- `LoadConfig` in `helpers.go`.
- The testify Dockerfile comment.
- Every template, values and helper comment of the new chart.
- The changed docs, read as statements about the repository.

Most of them are true of the code. These are not:

- **`main.go:37-38`** narrates the change: "A stub nobody configures with it answers an unrouted request 404, as it did before the default route existed." A reader of the package doc has no "before". It should state the behaviour only.
- **`docs/local-integration-tests.md`, row `e2e-harness`** says the chart installs "… the client-credentials Secret, and the suite Job; waits until they are Ready".
  - The Job is a `helm test` hook (`suite.yaml:21`), so an install does not create it, and nothing waits for it.
  - `test/k8s/README.md` says the opposite, correctly: "installing the stand does not start it".
- **`test/parity/README.md`, section Identity provider** says the realm "also holds the users of `suite/testdata/realm/`, so the cases that need those users run…" and "their files declare none".
  - That directory holds only a README. The commit message itself says "none so far".
  - A reader concludes that user files and cases depending on them exist.
- **`test/parity/suite/testdata/realm/README.md:6`** says the stage "fails when two files declare the same username or id". The check at `Dockerfile:44-45` runs on the merged realm. It also fails on:
  - a username declared twice within one file;
  - a user that duplicates one already in `parity-realm.json`.

  A reader adding a user already in the seed would expect it to pass.
- `profile.jq:2` says "each part capitalized". The code fully uppercases `r29` and `m2m`, which the example shows. This one is taste.

## Item 2: claimed cases covered

**Commit 9d25da7 (pip-stub):**

| Claimed case | Test |
| --- | --- |
| `*` answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its answer | `…/a_routed_path_keeps_its_own_answer` |
| A route with no responses falls through to the default | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| No default route gives 404 | `…/an_unrouted_path_without_a_default_route_is_404` |
| An empty default route gives 404 | `…/an_unrouted_path_with_an_empty_default_route_is_404` |
| The default route serves its responses in sequence | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` keeps the target as sent | `TestHandlePIP_RecordsTheRequestTargetAsSent` |

- "`/pip-stub/configure` now takes `*`" is exercised only by writing `routes` directly. `handleConfigure` is unchanged and stores any path, so this is taste: one PUT test would pin the wire shape users send.
- The package doc's precedence (rules before the default route) has no test. The code path is unchanged, so this is taste too.

**Commit 17b17fc (restricted Pod Security Standard):**

- "The stand starts under `restricted`" has no test or run.
  - Neither harness labels its namespace `pod-security.kubernetes.io/enforce=restricted`.
  - `test/scripts/test-chart-render.sh` asserts the agent chart's security context but not this chart's.

  This is substantive; see item 3a.
- The labels claim has no assertion either. I checked it by rendering.
- I checked the "non-root user its image names" claim by reading the images: pip-stub, tenant-manager, parity-suite and runtime-suite each declare `USER 10001:10001`. The public Keycloak image is numeric by its upstream Dockerfile.

**Commit 8b85515 (test-stand chart), commands and outcomes:**

| Command | What runs it |
| --- | --- |
| `make test-stand-files` | CI job "Chart lint and render". I ran the same `docker build --target chart-files` into the scratchpad: 8 files, as the Dockerfile header lists. |
| `helm lint` on both values files | CI. Passed locally on Helm v4.3.0. |
| `make e2e-harness`, `e2e-install`, `e2e-suite` and the parity counterparts | CI jobs "Kind end-to-end" and "Parity on kind". Not run here, since there is no cluster. |
| Transfer image `docker build -t authz-agent-transfer -f build/authz-agent-transfer/Dockerfile .` | No repository job. I ran it: `/charts/{authz-agent,authz-policy-admin,authz-test-stand}` plus `files/` are present, and `docker create … true` works on the scratch image. |
| Release of the three new images via `.qubership/docker.cfg` | Only the hand-triggered release. `build_context` is a key the file's `defaults` already use. Not run. |
| docs: `helm … upgrade authz-test-stand … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string suite.env.FULL_RUNTIME_SUITE=false` | **none.** It depends on `--reuse-values` keeping the harness's `-f` values and `BASE_URL` on Helm 4. As I read Helm's merge, it does, and the hook takes the new env at the next `helm test`. Still unverified. |
| Chart README: `helm upgrade --install … --set TAG=<version> -f my-test-stand-values.yaml`, then `helm test authz-test-stand --timeout 15m --logs` | **none.** It depends on published images under `<version>`, and no release has made them yet. |
| `run-suite`: `kubectl wait --for=create` | CI's kind-action kubectl. **Not verified**: `--for=create` exists only in kubectl 1.31 and later, and the docs prerequisites table names no version. On older kubectl the condition errors, no log streams, and the exit code still comes from helm. |

**Hunks no sentence claims:**

- `test/svt/common/compose/docker-compose.yml`: Keycloak `26.0` → `26.3.5@sha256…` in the SVT stack.
- `.github/docker-dev-config.json`: three new dev-build entries. The message claims only the release.
- `test/k8s/parity/idp-seed/parity-realm.json` (+318 lines): adds
  - the clients `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a`;
  - the users `mt-a`, `mt-a-admin`, `parity-r29-scope` and `parity-r30-scope`;
  - the roles `ROLE_MT_*`.

  The message claims only "a second tenant realm, parity-mt-b".
- `REALM-DESCRIPTION.md`: the issuer is corrected to `/auth/realms/…`.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub:** fine.
  - The control (no default route gives 404, as before) is present.
  - Both empty partitions (empty routed responses, empty default responses) are present.
  - The sequence clamp is covered.
- **Earlier state (substantive).** `e2e-harness` and `parity-harness` now run `helm upgrade --install` into namespaces the previous harness filled with `kubectl apply`. These objects already exist with the same names and no Helm ownership metadata:
  - Deployments and Services `keycloak`/`idp`, `pip-stub`/`pip-mock`, `entitlements-mock`, `tenant-manager`;
  - ConfigMaps `keycloak-realms` and `pip-mock-config`;
  - Secret `authz-agent-client-credentials`;
  - ServiceAccount `runtime-suite`.

  Helm refuses to import such objects. CI always starts from a fresh cluster, so it never meets this. The docs name no remedy (`make e2e-down`, or deleting the two namespaces), and nothing ran on that state.
- **Values users already pass (substantive).** `E2E_HELM_ARGS` now reaches the stand. The stand reads two keys the agent and policy-admin charts also read:
  - `IMAGE_PULL_POLICY`: the documented example `Never` means the same thing there, and Keycloak is shielded by `idp.imagePullPolicy`. Fine.
  - `TAG`: a `--set TAG=<x>` meant to install a different agent build now asks for `local/pip-stub:<x>`, `local/tenant-manager:<x>` and the suite image under `<x>`, which `e2e-images` never builds. Under `Never`, the stand's `--wait` runs out after 10 minutes.

  The request is a separate arguments variable for the stand, or no `E2E_HELM_ARGS` on the stand install.
- **Limits (substantive).**
  - The Makefile and the chart README fix `helm test --timeout 15m`, while the chart documents `suite.activeDeadlineSeconds: 900`.
  - Raising `suite.activeDeadlineSeconds` past 900 has no effect, because helm's 15 minutes, which start earlier, fire first.
  - At the defaults, `-test.timeout 600s` fires first, so the order happens to hold.
  - The CI jobs' `timeout-minutes: 30` encloses the image build, the harness `--wait 10m`, the two installs at `5m` each, and `helm test 15m`: 35 minutes of inner limits, plus the build. The old harness had the same overshoot.

  The request is to derive the `--timeout` from `suite.activeDeadlineSeconds` plus a margin.

## Item 3a: level, placement, and the environment

- **pip-stub:** the tests are small, in-process, and sit beside the existing `handlePIP` tests in `main_test.go`, sharing `resetState`. `go test ./pipstub/` passes.
- **Chart:** the restricted Pod Security properties are visible in rendered output, so the smallest level is a render assertion. `test-chart-render.sh` already does this for the agent chart (around line 828). Nothing does it for `authz-test-stand`, and no kind run enforces `restricted` either. This is the substantive request from item 2.

## Item 4: names by content, not by position

None. I checked the test and subtest names, the values comments, and the docs' cross-references: everything is named by content.

## Item 5: the failure report

None. Every new assertion prints its input, what it got, and what it wanted, for example `GET %s = %d %s, want %d %s` and `statuses of /a, /b, /a = %v, want %v`. The subtests are named by condition.

## Item 6: what the writer says it verified

None of the three commits states a red run on the base commit, a mutation verdict, or a kind run. On the base, the routed-path-with-no-responses case would hit the index -1 panic, but that is my reading of the code, not evidence the writer gave.

## Item 7: siblings of the change

- **Image-set counts (substantive):**
  - `README.md:59` still says "CI builds both via `.github/docker-dev-config.json`", which now lists five images.
  - `.github/docs-for-publication-task.md:77` still says "The two-entry array".
- **Restart on change (substantive):** realm files restart Keycloak through `checksum/realms`. The pip-stub rule-file ConfigMap (`pip-stub.yaml`) has no checksum, so a changed `requestargs.responses.yaml` reaches `pip-mock` only after `make parity-restart`. Fix it the same way, or name it as a follow-up.
- **Checked and fine:**
  - No reference to the deleted manifests remains (`git grep`).
  - `E2E_LOCAL_DEPLOYMENTS` and `PARITY_LOCAL_DEPLOYMENTS` match the chart's Deployment names.
  - `e2e-logs` and `parity-logs` exec into `deploy/pip-stub` and `deploy/pip-mock`, which still exist.
  - The `docker-release.yaml` comment was updated.

## Findings

| Finding | Label | File:line | Request |
| --- | --- | --- | --- |
| Install over objects the previous `kubectl apply` harness left fails Helm's ownership check; no remedy documented or run | substantive | `Makefile:86`, `Makefile:150`; `docs/local-integration-tests.md` | Document and run the remedy (`make e2e-down` or delete the namespaces), or adopt the objects |
| Restricted Pod Security claim has no render assertion and no enforcing run | substantive | `helm-templates/authz-test-stand/README.md:8-11`; `test/scripts/test-chart-render.sh` | Add test-stand assertions to the render script and/or label the kind namespaces `enforce=restricted` |
| `E2E_HELM_ARGS` passes `TAG` to the stand; a `TAG` meant for the agent asks for stub and suite images nothing builds | substantive | `Makefile:45-48,86,150` | Separate arguments variable for the stand, or drop `E2E_HELM_ARGS` there |
| `helm test --timeout 15m` is fixed while `suite.activeDeadlineSeconds` is a setting; 30-min CI job is smaller than the sum of inner limits | substantive | `Makefile:103`; `authz-test-stand/README.md:64`; `values.yaml:99` | Derive one timeout from the other; check the CI budget |
| `kubectl wait --for=create` needs kubectl 1.31+; prerequisites name no version | substantive | `Makefile:104`; `docs/local-integration-tests.md` prerequisites table | State the version, or poll with `get` |
| Docs say `e2e-harness` installs the suite Job and waits for it; it is a test hook | substantive | `docs/local-integration-tests.md`, `e2e-harness` row | Drop the Job from that row, or say it is only declared |
| Parity README describes `testdata/realm/` users that don't exist | substantive | `test/parity/README.md`, Identity provider section | Say the directory is empty and what happens when a file is added |
| The duplicate check is described as "two files" only | substantive | `test/parity/suite/testdata/realm/README.md:6` | Say a username or id may appear once in the merged realm |
| Unclaimed hunks: SVT Keycloak bump, dev-build entries, parity-realm clients/users/roles, issuer fix | substantive | `test/svt/common/compose/docker-compose.yml:3`; `.github/docker-dev-config.json`; `parity-realm.json`; `REALM-DESCRIPTION.md` | Claim each in the message with its run, or move it to its own change |
| Stale counts "both" and "two-entry" for the dev-build image list | substantive | `README.md:59`; `.github/docs-for-publication-task.md:77` | Update the counts |
| Rule-file ConfigMap change does not restart the stub, unlike realms | substantive | `helm-templates/authz-test-stand/templates/pip-stub.yaml:30-33` | Add a checksum annotation, or name it as a follow-up |
| Package doc narrates the change ("as it did before the default route existed") | substantive | `test/integration/pipstub/main.go:37-38` | State the behaviour only |
| No PUT `/pip-stub/configure` test with path `*`; no rule-over-default precedence test | taste | `test/integration/pipstub/main_test.go` | One test through the configure handler, one with a matching rule |
| "each part capitalized" vs full uppercase of `r29`/`m2m` | taste | `build/authz-agent-transfer/profile.jq:2` | Say which parts are uppercased |

Not checked:
- I ran no kind cluster, so the Makefile e2e and parity targets, Keycloak startup, and the restricted admission itself are unverified.
- I did not run the release workflow.
- I did not confirm the kubectl version CI's kind-action installs.
- I did no style pass over the prose.
- The drift script does not parse Go, YAML or Markdown, so I covered those by hand.

# Final review: 58316ca..17b17fc (three commits)

**Inputs.** There was no task statement, so item 2 takes its claimed cases from the three commit messages and the comments on the new tests. No earlier report exists. The drift script ran and printed nothing, because it only parses Java, Kotlin, Groovy and Scala. The Go file, the Helm templates, the Makefile and the docs were checked by hand. I loaded `test-authoring` (and its Go `testing` reference) and `english-developer-style`; there is no Go doc-comment skill in the bundle. To check the chart, I copied it to the scratchpad, generated `files/` with the same `jq` program the Dockerfile uses, and ran `helm lint` and `helm template` on that copy with both values files. No file in the repository was changed.

## Item 1: comments consistent with the code and with each other

- **`test/integration/pipstub/main.go:20`, `:34-35`, `:129`.** The package comment still says responses are "served sequentially per path", and `counters` is still described as a "legacy per-path response index". The default route breaks that: its counter is keyed by `*`, so `/a`, `/b`, `/a` get responses 1, 2, 2 (`TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` asserts exactly this). Line 35's "in sequence like any other route" doesn't tell the reader that the sequence is shared across paths. A reader would expect each unrouted path to start at the first response.
- **`test/parity/suite/pip_control.go:29-30`.** This sibling comment describes pip-stub and still says "Path matching is strictly literal … No wildcards / regex / templates". The `*` default route is now a catch-all, which is exactly what this change adds, and the comment tells parity-test authors it doesn't exist.
- **`docs/local-integration-tests.md:104`.** The `e2e-harness` row says the target installs "the suite Job; waits until they are Ready". A `helm.sh/hook: test` Job is not created by `upgrade --install`. `test/k8s/README.md` says so correctly ("installing the stand does not start it"), so the two pages contradict each other.
- **`helm-templates/authz-test-stand/templates/_helpers.tpl:2-4`.** The comment says the selectors keep `app: <name>` "so the Makefile's deploy/<name> … address a part". `deploy/<name>` finds a Deployment by its name and doesn't depend on labels. The real constraint is that Deployment selectors are immutable, so changing them would break `helm upgrade` over the release that commit 8b85515 installed.
- **`main.go:37-38`** ("as it did before the default route existed") describes the change in a doc comment. This is taste.
- **`test/k8s/authn/REALM-DESCRIPTION.md:82`** says the stand "runs Keycloak with `authz-test-realm.json` and `cloud-common-realm.json`". It imports four files; the two tenant realms are described later in the same document. This is taste.

## Item 2: claimed cases covered

| Claimed case | Test or run |
| --- | --- |
| An unrouted path is answered from `*` | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an_unrouted_path_gets_the_default_answer` |
| A routed path keeps its own answer | `…/a_routed_path_keeps_its_own_answer` |
| A route with no responses falls through to the default route | `…/a_routed_path_with_no_responses_gets_the_default_answer` |
| …or falls through to 404 | **none.** The routed-and-empty case with no `*` is untested. This is the original `-1` index crash. |
| No `*` route, or an empty one, gives 404 as before | `…/an_unrouted_path_without_a_default_route_is_404`, `…/an_unrouted_path_with_an_empty_default_route_is_404` |
| "`/pip-stub/configure` now takes the path `*`" | **none.** Every test writes `routes[defaultRoute]` directly; `handleConfigure` is never called with `*`. |
| The call record keeps `requestUri` as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| Every Pod is non-root with RuntimeDefault seccomp; every container drops ALL capabilities and cannot escalate; root filesystem is read-only except Keycloak; `/tmp` emptyDir; labels on every object; selectors keep `app` | No test in the repo. I confirmed all of it by rendering both values files. `test/scripts/test-chart-render.sh` checks these properties for the two product charts and not for this one. The kind jobs do run the read-only containers, but no green run is stated. |
| "The stand … starts in a namespace that enforces the `restricted` Pod Security Standard" | **none.** Neither `--create-namespace` call labels the namespace `pod-security.kubernetes.io/enforce`, so admission is never exercised. |
| A realm change restarts Keycloak (checksum annotation) | **none.** CI always starts from a fresh install. |
| `make test-stand-files` merges user files, fills `firstName`/`lastName`/`email`, and fails on a duplicate | **none.** `testdata/realm/` has no user files, so CI only runs the empty case. I ran `profile.jq` by hand: `parity-r29-level-m2m` becomes `R29LevelM2M`, which matches the comment. |
| Error texts `no realm files under files/realms/<realms>/` and `no file files/pip-stub/<file>` | No test. I rendered both by hand and they read as claimed. |

**Command lines in the changed files:**
- `make test-stand-files`: run by the CI lint job.
- `make e2e-harness`, `make e2e-suite`, `make parity-harness`, `make parity-suite`: run by the kind jobs.
- `docs/local-integration-tests.md:139-140`, `helm upgrade … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string …`: **none** runs it. Reading it, I found nothing wrong for Helm 3 or 4, and the `TestCheckResource` subtest exists.
- `helm-templates/authz-test-stand/README.md`, `docker create` / `docker cp` / `helm upgrade --install … --set TAG`: **none** runs them.
- **`helm-templates/authz-test-stand/README.md:64`, `helm test authz-test-stand --timeout 15m --logs`: none runs it, and it fails on Helm 3.** In Helm v3.15.2, `pkg/action/release_testing.go:127` fetches logs from a Pod whose name is the hook's name (`Pods(ns).GetLogs(h.Name)`). This chart's hook is a Job named `parity-suite`, so no Pod has that name. `cmd/helm/release_testing.go:82` returns that error ahead of the test result. The documented command therefore exits non-zero with `unable to get pod logs for parity-suite` and prints no log. I didn't check Helm 4's behaviour; CI pins v4.3.1. The Makefile avoids `--logs`.

**Hunks no sentence of the commit messages claims:**
- **`test/svt/common/compose/docker-compose.yml:3`**: the SVT Keycloak image goes from `26.0` to `26.3.5@sha256:…`. SVT isn't the kind harness.
- **`.github/docker-dev-config.json`**: the three new entries. The message claims only the release's `.qubership/docker.cfg`.
- **`test/k8s/parity/idp-seed/parity-realm.json`**: +318 lines. These add the clients `parity-m2m-tenant-{a,b,unknown,empty}` and `parity-end-user-tenant-a`, the users `parity-r29-scope`, `parity-r30-scope`, `mt-a` and `mt-a-admin`, and the roles `ROLE_MT_*`. The message only claims the new `parity-mt-b` realm, and no suite code in the change refers to any of these.
- `REALM-DESCRIPTION.md`'s issuer correction (`/realms` to `/auth/realms`) and dropping `JAVA_OPTS_APPEND=…OVERWRITE_EXISTING`. Both look correct; listing them is taste.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub:** there's no control showing that a matching `PIP_STUB_CONFIG` rule still wins over a configured `*`. The package comment states that order. There's also no routed-and-empty-without-default case (see item 2). The nil and empty default-route partitions are both covered.
- **Existing state:** `e2e-harness` and `parity-harness` now run `helm upgrade --install` into namespaces where the old `kubectl apply` left objects with the same names: Deployments `keycloak`/`idp`, `pip-stub`, `pip-mock`, `entitlements-mock`, `tenant-manager`; the Secret `authz-agent-client-credentials`; the ServiceAccount `runtime-suite`. Helm refuses to adopt objects without its ownership metadata ("exists and cannot be imported into the current release"). Every run starts from a fresh kind cluster, and no doc tells a developer with an existing stand to run `make e2e-down` or delete the namespace first.
- **Replaced mechanisms, tested against the most common fault (an image not loaded into kind):**
  - Old `e2e-suite` failed after 3 minutes with `wait --for=condition=Ready pod … --timeout=3m`.
  - New `run-suite` behaves as follows. `wait --for=create` succeeds. The log poll then runs 90 times, each attempt being one `kubectl logs` plus a 2 s sleep, which is at least 3 minutes. `logs -f` then fails right away, at least printing the waiting reason. Finally `wait $helm_pid` blocks until `helm test --timeout 15m` or the Job's 900 s deadline ends it, so about **15 minutes** in total.
  - The harness goes the same way: old per-Deployment `rollout status --timeout=2m` for the stubs, new single `--wait --timeout 10m`.
  - No sentence accepts the longer waits.
- **Limits on the suite run:**
  - The other limits are `-test.timeout 600s` (`suite.args`), `suite.activeDeadlineSeconds: 900` (`values.yaml:99`), `helm test --timeout 15m` (fixed at `Makefile:102` and in the README), and the CI job's `timeout-minutes: 30`.
  - The deadline and Helm's timeout are both 900 s, and Helm's clock starts earlier, so the Job's `DeadlineExceeded` report is hidden behind Helm's timeout.
  - Raising the documented `suite.activeDeadlineSeconds` above 900 changes nothing, because the 15 minutes fixed in the Makefile ends the run first.
  - Raising `-test.timeout` above 900 s lets the deadline kill the test before Go's own timeout can print its report.
- **`E2E_HELM_ARGS` now reaches the stand:** the documented value, `--set IMAGE_PULL_POLICY=Never`, means the same thing there, so no finding. Taste: a `--set TAG=…` meant for the product images would now also point the stand at `local/pip-stub:<tag>`, which doesn't exist.
- Taste: `Makefile:99` says the log poll lasts "up to three minutes". By the attempts-times-longest-attempt rule it is 90 × (2 s + one `kubectl logs` call), with no bound on the call.

## Item 3a: level, placement, and the environment

- The pip-stub tests are small, in-process, in `main_test.go` next to the existing tests, and share `resetState()`. That's correct.
- The chart's security contexts, labels and checksum can all be checked with `helm template`, with no cluster. The repository already has the place for that (`test/scripts/test-chart-render.sh`, run in CI), but it has no assertion for `authz-test-stand`.
- Only admission under `restricted` needs a real cluster, and no CI job runs it.
- The emptyDir at `/tmp`: no test in either suite calls `t.TempDir`/`os.TempDir` (searched with grep). It's harmless.
- Consistency check: `go test ./...` in `test/integration/pipstub` passes, and both `helm lint` runs pass on the scratch copy.

## Item 4: names by content, not by position

- `helm-templates/authz-test-stand/values.yaml:11`, "own image and pull policy below", could name `idp.image` / `idp.imagePullPolicy`. Taste.
- `test/k8s/README.md:4`, "The Makefile targets below", is the same. Taste.
- No test name or case id uses an ordinal.

## Item 5: the failure report

None. Each new assertion prints the request and both values, got before want (`GET %s = %d %s, want %d %s`, `statuses of /a, /b, /a = %v, want %v`, `requestUri %q, path %q, want %q and %q`). Every table case has a descriptive name.

## Item 6: what the writer says it verified

None stated. There's no red run on the base commit; the routed-and-empty case would have panicked while holding `mu`. There's no mutation verdict, no kind-job result for any of the three commits, and no release dry-run for the three new images.

## Item 7: siblings of the change

- **The test stand's security context** differs from its sibling, `helm-templates/authz-agent/templates/deployment.yaml:262-266`, which makes the root filesystem read-only "on Kubernetes only, as on the platform's charts". The test stand makes it read-only everywhere, while claiming OpenShift compatibility for the missing `runAsUser`. The pip-stub and suite images also use a different base (`qubership-core-base:2.4.2`, not the agent's `alpine-2.5.8`). There's no sentence explaining the difference and no OpenShift run.
- **Image set counts.** Three entries were added to `.github/docker-dev-config.json`, but two places still count the old set:
  - `README.md:59` says "CI builds both via `.github/docker-dev-config.json`", which now builds five.
  - `.github/docs-for-publication-task.md:77` still says "the two-entry array".
- **pip-stub routing helpers.** Callers of `/pip-stub/configure` and `/pip-stub/calls` in `test/integration/testify` and `test/parity/suite` (searched with `git grep`):
  - No caller configures a route with no responses.
  - `ResetPinnedRoutes` re-pins with an explicit 404 response, so it isn't affected by the fall-through.
  - `PipStubCall` adds fields as needed, so the new `requestUri` doesn't affect it.
  - The only affected caller is the comment already raised under item 1.
- **References to the removed manifests:** I searched for every removed manifest name, `E2E_AUTHN` and `PARITY_SEED`. Only ADRs remain, which are historical.

## Findings

| # | Finding | Label | File:line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | `helm test … --logs` reads a Pod named after the Job hook; it fails on Helm 3.15 and Helm 4 is unchecked | Substantive | `helm-templates/authz-test-stand/README.md:64` | Run it on Helm 3 and 4 against this Job hook, or document `kubectl logs job/<suite.name>` instead |
| 2 | The `restricted` admission claim has no run; the kind namespaces aren't labeled | Substantive | `Makefile:85,149`; chart README:9 | Label the namespaces `pod-security.kubernetes.io/enforce=restricted` in the harness targets, or drop the claim |
| 3 | No render assertions for the stand's security contexts, labels, realm checksum, or the two quoted error texts | Substantive | `test/scripts/test-chart-render.sh` | Add `authz-test-stand` cases beside the product-chart ones |
| 4 | Unclaimed hunks: SVT Keycloak bump, `docker-dev-config.json` entries, the extra clients, users and roles in `parity-realm.json` | Substantive | `test/svt/common/compose/docker-compose.yml:3`; `.github/docker-dev-config.json`; `test/k8s/parity/idp-seed/parity-realm.json` | Add a sentence claiming each, or move them to the change whose cases use them |
| 5 | Upgrading over a stand that `kubectl apply` created fails on Helm ownership; there's no remedy and no run | Substantive | `docs/local-integration-tests.md`; `test/k8s/README.md` | Document `make e2e-down` or deleting the namespace, run on an old stand |
| 6 | Missing image: the suite now fails after ~15 min instead of 3; the harness after 10 min instead of 2 | Substantive | `Makefile:98-106,86` | Bound the wait (for example fail after the log poll), or add a sentence accepting the delay, with a run of the fault |
| 7 | `activeDeadlineSeconds` (900) equals the fixed `helm test --timeout 15m`; raising it has no effect and its report is hidden | Substantive | `values.yaml:99`; `Makefile:102`; chart README:64 | Derive Helm's timeout from the value, or document the pair |
| 8 | "Per path" sequence wording no longer matches the shared `*` counter | Substantive | `test/integration/pipstub/main.go:20,35,129` | Say that the default route keeps one sequence across all unrouted paths |
| 9 | `pip_control.go` still says "No wildcards" | Substantive | `test/parity/suite/pip_control.go:29-30` | Mention the `*` default route |
| 10 | Docs say `e2e-harness` installs the suite Job and waits for it | Substantive | `docs/local-integration-tests.md:104` | Drop the Job from that row, as `test/k8s/README.md` does |
| 11 | No routed-and-empty → 404 case; no test that a matching rule beats `*`; no test through `handleConfigure` | Substantive | `test/integration/pipstub/main_test.go:225` | Add these three cases |
| 12 | The user-file merge and duplicate check are untested (no input exists) | Substantive | `build/authz-agent-transfer/Dockerfile:380-386` | Add a fixture run with one user and one duplicate |
| 13 | Read-only root everywhere, unlike the agent chart's Kubernetes-only rule; no sentence, no OpenShift run | Substantive | `templates/_helpers.tpl:33-40` | Follow the agent chart's rule, or explain the difference and run it on OpenShift |
| 14 | `README.md` "CI builds both"; the publication doc's "two-entry array" | Substantive | `README.md:59`; `.github/docs-for-publication-task.md:77` | Update the counts |
| 15 | Selector comment gives the wrong reason (`deploy/<name>` doesn't use labels) | Substantive | `templates/_helpers.tpl:2-4` | Give the real reason: selectors are immutable across upgrades |
| 16 | No red run or mutation verdict stated | Substantive | commit messages | State the base-commit failure of the routed-and-empty case and the kind-job results |
| 17 | Doc comment describes the change ("as it did before…") | Taste | `main.go:37-38` | State the behaviour without the history |
| 18 | REALM-DESCRIPTION lists two of the four imported realms | Taste | `test/k8s/authn/REALM-DESCRIPTION.md:82` | Name all four, or say "the realm files of `authn/`" |
| 19 | "below" where a key name is available | Taste | `values.yaml:11`; `test/k8s/README.md:4` | Name `idp.image` / the section |
| 20 | `TAG` passed in `E2E_HELM_ARGS` now also retags the stand's images | Taste | `Makefile:45-47` | Mention it beside the example |
| 21 | Log poll described as "up to three minutes" | Taste | `Makefile:99` | Count the attempts including each `kubectl logs` call |

Not checked: the kind and parity suites, Helm 4's `--logs` behaviour, admission under `restricted`, behaviour on OpenShift, and whether the `qubership-core-base:2.4.2` entrypoint writes to the root filesystem. I only ran the pip-stub unit tests and lint and template on a scratch copy of the chart. I didn't do a style pass over the prose.

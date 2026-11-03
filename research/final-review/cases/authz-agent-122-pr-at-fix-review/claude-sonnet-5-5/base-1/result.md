# Final review: `58316ca..HEAD` (4 commits)

**Inputs.**
- **Task statement:** none was handed over. I took the claimed cases from the four commit messages (8b85515, 9d25da7, 17b17fc, 5dcb6be) and the comments in the changed files.
- **Previous report:** none.
- **Languages:** Go, Helm templates, Makefile, Dockerfile, jq and docs. The Helm, Makefile, Dockerfile and docs parts were read through the analogues in §2a.
- **Skills loaded:** `test-authoring` and `english-developer-style` from the given skills directory. There is no Go doc-comment skill in that directory.
- **Drift script:** it ran and printed nothing for this range, even though `handlePIP`, `callRecord` and `LoadConfig` changed. I read those members by hand and did not rely on the script.
- **What I ran:**
  - `helm lint` and `helm template` on a copy of the chart, with its `files/` filled by plain `cp` (Helm v4.3.0 locally, CI pins v4.3.1), for both values files.
  - `jq` 1.8.2 on the Dockerfile's merge and `profile.jq` with fixtures.
- **What I did not run:** `docker build`, which is how `make test-stand-files` generates `files/`, and no cluster (none available).

## Item 1: comments consistent with the code and with each other

- **`pipstub/main.go`:** `none`.
  - The header precedence sentence (lines 29–32) and the new default-route paragraph match `handlePIP`. A route with empty `Responses` falls through to `*`, then 404.
  - The `defaultRoute` comment ("registers … /pip-stub/configure") is true. `handleConfigure` stores any `Path` verbatim.
  - The `callRecord.RequestURI` comment is true.
  - "Control surface (unchanged)" sits above `handleCalls`, which now returns the new field. That is taste only, so I am not filing it.
- **Makefile `run-suite` comment:** two parts are wrong.
  - It says `$(4)` is "no shorter than its `suite.activeDeadlineSeconds`". Equal values race, because Helm's timer starts before the Job is created, so Helm can report a timeout instead of the Job's failure. "Longer than" is the true condition. Substantive-minor; it is in the table.
  - The comment above `E2E_SUITE_TIMEOUT` says to raise it "together with `suite.activeDeadlineSeconds`". The suite arguments also fix `-test.timeout 600s` (`values.yaml` and `test/k8s/test-stand-values.yaml`). Raising only the deadline and the timeout therefore does not lengthen a suite, which still stops at 600 s. The same applies to the README sentence "keep that at least as long as `suite.activeDeadlineSeconds`". Substantive.
- **`docs/local-integration-tests.md`, `e2e-harness` row:** "…, and the suite Job; waits until they are Ready". The Job is a test hook, so the harness install does not start it and cannot wait for it. Substantive, one line.
- **`test/k8s/README.md`, `e2e-harness` row:** it does not list the suite Job, which is correct. It does disagree with the docs row above. This is the same finding.
- **`build/authz-agent-transfer/Dockerfile` comment:** "The user files under testdata/realm/, if any, hold no first name…" reads as a fact about files that do not exist, and they are "none so far". The wording is hedged correctly, so no finding.
- **Narration (`now`, `no longer`):** none in the changed comments.
- **README claim, "Helm 4 prints nothing / Helm 3 fails with `unable to get pod logs`":** the repository pins only Helm v4.3.1, and I could not check the Helm 3 text. I am recording this as unchecked.

## Item 2: claimed cases covered

**Claims from the commit messages and the test class comments, against tests:**

| Claim | Test or evidence |
| --- | --- |
| `*` answers an unrouted path | `TestHandlePIP_DefaultRouteAnswersUnroutedPaths/an unrouted path gets the default answer` |
| A routed path keeps its own answer | `…/a routed path keeps its own answer` |
| Unconfigured stub answers 404 as before | `…/an unrouted path without a default route is 404` |
| A route with no responses falls through "to the default route, **or to 404**" | The default branch is covered (`…/a routed path with no responses gets the default answer`). **The 404 branch is not.** No case has an empty route plus no default. Case 5 is an unrouted path with an empty default. |
| Default route serves its sequence across paths | `TestHandlePIP_DefaultRouteServesItsSequenceAcrossPaths` |
| `requestUri` kept as it arrived | `TestHandlePIP_RecordsTheRequestTargetAsSent` |
| "`/pip-stub/configure` now takes `*`" | **No test goes through `handleConfigure`.** The tests write `routes[...]` directly. The handler is untouched and accepts any path, so this is low risk. |
| "Index of -1" for a route with no responses | `…/a routed path with no responses gets the default answer` and case 5 |
| pip-mock and entitlements-mock behave as before | Only through the 404 control case. |
| Every Pod non-root with RuntimeDefault seccomp; containers drop ALL and cannot escalate; read-only root except Keycloak; `/tmp` emptyDir on the suite; no `runAsUser`; app.kubernetes.io labels and `helm.sh/chart`; selectors keep `app:` | **No committed test or CI assertion.** `test/scripts/test-chart-render.sh` does not mention the test-stand chart. The CI `helm lint` steps do not look at security contexts. Substantive. I rendered the chart by hand: `runAsNonRoot` appears 5 times (Keycloak, 3 stubs/emulator, Job) and `readOnlyRootFilesystem: false` only on Keycloak. This is a check that holds today, not a test. |
| "Restarting when a realm file changes" | **No test.** I checked by hand that appending a byte to a realm file changes `checksum/realms`. |
| Transfer-image merge: users merged into `parity` realm, profile fields filled in, "fails if a user is declared twice" | **No fixture or test**, since there are no user files. I ran the Dockerfile's `jq` filter on fixtures: it fills in the names and emails, keeps declared values, and `jq -e` returns 1 on a duplicate username. With no user files, the realm is unchanged (14 users). The behaviour works, but only my scratch run shows it. Substantive. |
| "`parity-mt-b` second tenant realm" | The stand starts with it. No run is stated that shows a suite using it. |
| CI runs `make e2e-suite` / `parity-suite` / lint on the chart | Present in `integration-tests.yaml`, and `helm lint` of both values files passes locally. |
| Failure texts quoted: `exists and cannot be imported into the current release: invalid ownership metadata` (Helm); `unable to get pod logs for parity-suite` (Helm 3.22.1) | Neither is reproduced anywhere in the repository. The first is the premise of the `make e2e-down` remedy. |

**Commands the change tells someone to run, and what runs the same command:**

| Command (file) | Promised outcome | Script, target or CI that runs the same form |
| --- | --- | --- |
| `make test-stand-files` (chart README, `values.yaml`) | writes `files/` | CI "Generate the test-stand files" runs it. Yes. |
| `docker create … true`, `docker cp`, `docker rm` (chart README) | charts copied out of the transfer image | **none.** The image is only built by the release workflows, never run. |
| `helm upgrade --install … ./charts/authz-test-stand --set TAG=<v> -f my-test-stand-values.yaml` (README) | installs the stand from the published charts | **none.** CI installs `helm-templates/authz-test-stand` with `--wait` on kind, not the chart out of the image, and not with the edited values. |
| `helm test authz-test-stand --timeout 15m` then `kubectl logs job/parity-suite` (README) | exits non-zero on failure; log readable | `run-suite` runs `helm test` with `--timeout` and `kubectl logs -f` (in the same `$(MAKE)`), not the second plain `kubectl logs` after completion. The Job is kept, so the form should work. |
| `helm … upgrade authz-test-stand … --reuse-values --set suite.env.RUNTIME_SUITE_RUN=… --set-string suite.env.FULL_RUNTIME_SUITE=false` then `make e2e-suite` (`docs/local-integration-tests.md`) | runs a subset | **none.** It differs from every CI form by the `upgrade` of the test-stand release without `--wait`, `--reuse-values` and `--set`. The tool's behaviour with `--reuse-values` after `e2e-harness` set `suite.env.BASE_URL` via `--set` is the property it depends on. Helm 4 `--reuse-values` merges the previous release's values, so the subset arrives. Substantive-minor: the request is one run of this form on kind. |
| `make e2e-down` once, then `make e2e` (docs and `test/k8s/README.md`) | removes the old `kubectl apply` objects | **none** for the failure; `e2e-down` only deletes the kind cluster. The claim "Helm refuses to take them over" depends on the objects lacking Helm ownership labels and annotations. Helm 3 and 4 both import only with the `app.kubernetes.io/managed-by: Helm` label and release annotations, so the claim is plausible. It was not run on a cluster with the old objects. Substantive-minor (see Item 3). |
| `kubectl wait --for=create job/<name> --timeout=2m` (Makefile `run-suite`) | waits for the hook's Job | CI runs it. It needs kubectl 1.31+. CI's `helm/kind-action` provides kubectl, but `docs/local-integration-tests.md` lists kubectl with no minimum. Local kubectl here is 1.33.9. Taste: name the minimum. |

**Hunks no sentence claims.**
- `test/svt/common/compose/docker-compose.yml`: Keycloak `26.0` becomes `26.3.5@sha256:…`. No commit message mentions the SVT compose file, and the file is not otherwise touched. Substantive. The request is a sentence that claims it, with a run of that compose stack on 26.3.5, or a separate change.
- `test/k8s/parity/idp-seed/parity-realm.json` +318 lines. The message claims only "The parity realm gains a second tenant realm, parity-mt-b". The hunk also adds roles `ROLE_MT_READER` and `ROLE_MT_ADMIN`, the `parity-level-claim` mapper, `parity-m2m-tenant-a`, and tenant-A users and clients. The README names the tenant-A users, but no commit sentence claims the hunk. Substantive: add a sentence, or move it to a change of its own.
- `README.md`, `.dockerignore` and `.gitignore` hunks follow from the "transfer image" and "generated files" claims. No finding.

## Item 3: boundaries, partitions, and the negative control

- **pip-stub:**
  - Present: an unrouted path with no default (404, the control), a routed path, an empty `Responses` route, an empty default route, and a sequence clamped at its last element.
  - **Missing partition:** an empty route with no default route (the "or to 404" branch).
  - **Missing:** a path-encoding control for `requestUri`. The test uses one encoded path, but nothing shows that a plain path records the same string for `Path` and `RequestURI`. Taste.
- **Pre-existing state:** the commit says an older `make e2e` leaves `kubectl apply` objects that block the chart install. The remedy is `make e2e-down`. Neither the symptom nor the remedy is shown on such a cluster. There is also a second kind of leftover state: the old harness's `keycloak-realms` and `parity-realms` ConfigMaps and `rollout status` Deployments are removed only by `e2e-down`. Substantive-minor: run it once on a cluster with the base commit's objects.
- **Values users already pass:**
  - `TAG` and `IMAGE_PULL_POLICY` are read by `authz-agent`, `authz-policy-admin` and the new chart.
  - `E2E_HELM_ARGS` now reaches the test-stand install too, as the Makefile comment and README say. Their example `--set IMAGE_PULL_POLICY=Never` is safe, because the chart's Keycloak image has its own `idp.imagePullPolicy`.
  - A user's `E2E_HELM_ARGS='--set TAG=1.2.3'` now makes `local/pip-stub:1.2.3`, `local/tenant-manager:1.2.3` and `local/authz-runtime-suite:1.2.3`. I confirmed it by rendering. None of those images exists, because `e2e-images` builds `:ci`. The old install of the loose manifests ignored `TAG`. Substantive, and the request is a test-stand setting of its own, or a note in the Makefile comment that `TAG` must stay `ci`.
- **Replaced mechanism (suite wait):**
  - Old `e2e-suite`: `kubectl wait --for=condition=Ready pod … --timeout=3m`, then `logs -f`, then `wait --for=condition=Complete --timeout=1m`.
  - New: `helm test --timeout 15m` in the background, a poll of up to 3 minutes for readable logs, `logs -f`, then `wait $helm_pid`.
  - Fault the old target met most often: the images were not loaded (`ErrImageNeverPull`, which `docs/local-integration-tests.md` troubleshooting lists). Old: fails after 3 minutes with `kubectl` output. New: `logs -f` fails at once, and `helm test` keeps waiting for the Job's pod, which cannot start, until the Job's `activeDeadlineSeconds: 900` or `--timeout 15m`, whichever comes first. Each prints only Helm's timeout message at the end. About 15 minutes instead of 3, and quieter. No sentence in the change accepts it. Substantive. The request is a run of that fault, and a deadline for the whole wait at the old 3 minutes: for example kill `helm test` when the pod is not Running after the poll, or fail when no logs after the 3-minute poll.
  - Longest-waiting fault in the new loop (a Job whose pod creates slowly): 2 minutes for create, 3 minutes of polling (90 attempts at 2 s, each `kubectl logs` with no timeout counted as never returning), then Helm's own wait. The last attempt can overrun by one attempt and one sleep. This is the same request.
- **Limits on the same work (suite):** `-test.timeout 600s` (values), `suite.activeDeadlineSeconds: 900` (values), `E2E_SUITE_TIMEOUT`/`PARITY_SUITE_TIMEOUT: 15m` (Makefile), `timeout-minutes: 30` on the kind jobs (workflow, which also covers the harness, install and image builds), and `--timeout 10m` on the harness install. The commit sets the third from the second only by comment. The documented setting `activeDeadlineSeconds` raised past 600 s has no effect while `-test.timeout 600s` stays, and raising `E2E_SUITE_TIMEOUT` past 30 minutes is cut by the job limit. The request is one derived limit: for example `-test.timeout` from the deadline, and the Makefile wait from `suite.activeDeadlineSeconds` read out of the values. The commit's own premise ("a suite given a longer deadline in its values still failed after 15 minutes") is only half repaired.
- **Item 3a:**
  - The pip-stub tests are in-process and sit in the existing `main_test.go`, sharing `resetState`. None.
  - The chart behaviour (security contexts, labels, the realm-checksum annotation, the `required`/`fail` messages for missing `files/`) is observable with `helm template` in one process and no cluster. CI already runs `test/scripts/test-chart-render.sh` for the other charts, so the in-process test is owed: a render assertion. Substantive, in the table.
  - The CI `helm lint` steps run on every change, but lint does not execute the `fail` branches.

## Item 4: names by content, not by position

`none`. Checked the new test names and subtest names (all by content), the chart headings, and cross-references. The phrases "the two coverage checks" and "the first run" are counts and sequence of fixed things, not ordinals that go stale. `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` are by content.

## Item 5: the failure report

`none`. The three Go tests use `t.Errorf` with the operands and the expected values, and the table cases carry content ids. `serve` returns the status and body so the report shows both. The `len(calls) != 1` check uses `t.Fatalf` with the count. No boolean assertion wraps a comparison. The one assertion with no operands, `reflect.DeepEqual` in the sequence test, prints both slices.

## Item 6: what the writer says it verified

Neither the commit messages nor any file states a red run on the base commit, or a mutation result, for the three pip-stub tests. The chart has no tests (Item 2). The `helm lint` jobs and the kind jobs are consistency checks and not that evidence. I did not run the suite.

## Item 7: siblings of the change

- **Deleted files:** `git grep` finds no remaining reference to `keycloak.yaml`, `runtime-suite-job`, `runtime-suite-rbac`, `parity-suite-job`, `pip-mock.yaml`, `pip-stub.yaml`, `entitlements-mock.yaml`, `tenant-manager.yaml`, `m2m-credentials`, `E2E_AUTHN`, `PARITY_SEED`, `parity-realms`, `keycloak-realms` or `pip-mock-config` outside the deleted files. None.
- **Images listed for release:** the release workflow comment, `.qubership/docker.cfg`, `docker-dev-config.json` and the README list the same five images. The prose still says "two images" only in `.agents/skills/qubership-actions-guide/docker.md:151` and its `.claude` twin, which describe an unrelated "minimal generated example". None.
- **`e2e-restart` and `parity-restart`:** they list `E2E_LOCAL_DEPLOYMENTS` including `tenant-manager`, `pip-stub` and `entitlements-mock`, which Helm now owns. A `rollout restart` edits the template's annotations; the next `helm upgrade` resets it, which is harmless. The message says the realm Pod restarts by its checksum, and the Makefile comment says so. None.
- **`handlePIP` callers:** `main_test.go` only. The `requestUri` field: no other reader in the repository (`git grep` over `test`). The `*` key and `/pip-stub/configure`: other callers that configure the stub (parity suite code under `test/parity/suite`) pass real paths, so a user-supplied `*` is the only entry point. None.
- **Set size and listing places:**
  - `docs/local-integration-tests.md` prerequisites row (helm "installs the charts, runs the suite Job") was updated. Its kubectl row ("streams the Job log, restarts Deployments") now omits `wait --for=create`'s kubectl 1.31 minimum. Taste, recorded in Item 2.
  - The CI `helm lint` list was extended for both values files. The `Render assertions` step was not (Item 2).
  - `test/svt` compose Keycloak (see Item 2) now shows the chart-side image, but the other two places that name Keycloak 26.x were not searched beyond that.
- **Symptom paths in the new troubleshooting row:** the `invalid ownership metadata` row names `make e2e-harness` and `make parity-harness`, and its action (`make e2e-down` once) names the single cluster both share. Both targets are covered.
- **Transfer image and chart-README remedy:** the `kubectl logs job/<suite.name>` remedy is the one the symptom needs for both Helm major versions. The page names both.

## Findings

| # | Finding | Label | File and line | Change requested |
| --- | --- | --- | --- | --- |
| 1 | The suite wait now fails after about 15 minutes, and quietly, when the suite image is missing (`ErrImageNeverPull`). The old target failed after 3 minutes with kubectl output. No sentence accepts it. | substantive | `Makefile` `run-suite` (about line 100) | Run that fault on `run-suite`; bound the whole wait, last attempt included, at the old 3 minutes; or add a sentence that accepts the new time. |
| 2 | `-test.timeout 600s`, `suite.activeDeadlineSeconds: 900`, `E2E_SUITE_TIMEOUT: 15m` and the CI job's 30 minutes are four independent limits. Raising the deadline and the Makefile wait does not lengthen a suite, which stops at 600 s. The comments and the README say to raise only two of them. | substantive | `Makefile` (`E2E_SUITE_TIMEOUT` comment), `helm-templates/authz-test-stand/values.yaml` (`suite.args`, `activeDeadlineSeconds`), `README.md` (last paragraph) | Derive `-test.timeout` from the deadline, and the Makefile wait from the values; or name all of them in the comments. |
| 3 | Comment and README say the Helm wait must be "no shorter than"/"at least as long as" the deadline. Equal values race, because the Helm timer starts first. | substantive | `Makefile` `run-suite` comment; chart `README.md` last paragraph | Say "longer than". |
| 4 | `E2E_HELM_ARGS='--set TAG=x'` now reaches the test stand and selects `local/pip-stub:x`, `local/tenant-manager:x` and `local/authz-runtime-suite:x`, none of which exists. The old harness ignored `TAG`. | substantive | `Makefile` `E2E_HELM_ARGS` comment; `test/k8s/README.md:67` | A test-stand setting of its own for the image tag, or a sentence that `TAG` must stay `ci`, with one run of the case. |
| 5 | The Pod/container security settings (restricted PSS), labels, selectors and `/tmp` emptyDir are claimed by 17b17fc and asserted nowhere. | substantive | `test/scripts/test-chart-render.sh` (no test-stand section); `helm-templates/authz-test-stand/templates/*` | Add render assertions for both values files: `runAsNonRoot`, seccomp, drop ALL, `allowPrivilegeEscalation: false`, read-only root except Keycloak, no `runAsUser`, `/tmp` on the Job, selectors `app:` only. |
| 6 | The transfer image's user merge, profile fill-in and duplicate check have no fixture or test. Only my scratch run shows they work. | substantive | `build/authz-agent-transfer/Dockerfile`, `profile.jq`; `test/parity/suite/testdata/realm/` | Add one fixture user file with a missing profile field and a duplicate-user control, run through the `chart-files` stage. |
| 7 | The "or to 404" branch (an empty route and no default route) has no case. | substantive | `test/integration/pipstub/main_test.go`, `TestHandlePIP_DefaultRouteAnswersUnroutedPaths` | Add the case `routed: []pipResponse{}`, default `nil`, want 404. |
| 8 | `svt` compose Keycloak bump `26.0` to `26.3.5@sha256…` is claimed by no sentence. | substantive | `test/svt/common/compose/docker-compose.yml:3` | A sentence that claims it and a run of that stack, or move it to a change of its own. |
| 9 | The `parity-realm.json` additions beyond the second tenant realm (roles, mapper, tenant-A client and users) are claimed by no sentence. | substantive | `test/k8s/parity/idp-seed/parity-realm.json` | A sentence that claims them, or move them. |
| 10 | The `make e2e-down` remedy and the failure text it addresses (and the Helm 3 `unable to get pod logs` text) were never run. The subset recipe in `local-integration-tests.md` has no run either. | substantive | `test/k8s/README.md` Run section; `docs/local-integration-tests.md` troubleshooting and section 6; chart `README.md` step 3 | One run of each on the state it names (a cluster with the base commit's objects; Helm 3 and 4), or state they were not run. |
| 11 | The `e2e-harness` row says the harness waits for "the suite Job". It does not start it. | substantive | `docs/local-integration-tests.md` (step table) | Remove the Job from that row. |
| 12 | The `docker create`/`cp` and `helm upgrade --install ./charts/...` forms in the chart README are run by nothing. | taste | `helm-templates/authz-test-stand/README.md` steps 1–2 | A CI step that builds the transfer image and installs from it; I prefer it, and expect it may be declined. |
| 13 | `kubectl wait --for=create` needs kubectl 1.31+; the prerequisites table lists no minimum. | taste | `docs/local-integration-tests.md` prerequisites; `Makefile` `run-suite` | Name the minimum. |
| 14 | `/pip-stub/configure` accepting `*` is not exercised through the handler. | taste | `test/integration/pipstub/main_test.go` | One request through `handleConfigure` with path `*`. |

Findings 1 to 3 and 5 are the ones I would not let through. Items 10 and 12 mean the documentation's commands have not been shown to run as written.

**Not checked:** the full test suites were not run and no mutation or red run was produced; no cluster or Docker build was available, so `make test-stand-files`, the kind harness, the transfer image and Helm 3 behaviour are unverified; the comment-drift script produced no output for this range; prose style was not reviewed.

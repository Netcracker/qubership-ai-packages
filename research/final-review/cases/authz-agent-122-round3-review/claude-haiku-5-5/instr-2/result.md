## Final review: `5dcb6be..HEAD` (commit `f3b64e0`)

**Setup.** No previous report exists, so §4 has no table. I loaded `test-authoring` and `english-developer-style` from the given directory. The doc-comment skill does not apply because the change adds no code comments. The drift script (`python3 -I comment-drift.py 5dcb6be… HEAD`) printed nothing: the change touches only a Makefile, a Dockerfile, Markdown, YAML and a compose file, so no member moved. The §2a analogues apply throughout. The repository is unchanged (`git status` is clean). My scratch work is in `/private/tmp/claude-501/-private-var-folders-hq-dhvxggnd1gv0fpmt8lg8xzkc0000gn-T-tmp-fMJYNAjFAW-repo/7c47182e-5eb4-449a-b1f4-092f0690608a/scratchpad`.

### Item 1: comments consistent with the code and with each other
Finding S2 (README). The rest is `none`. The Makefile comment on `E2E_HELM_ARGS` (lines 46–49) matches the installs at `e2e-install` and `parity-install`. The `run-suite` comment is accurate. The Helm 4.3 sentence in `helm-templates/authz-test-stand/README.md:62` and the version row in `docs/local-integration-tests.md:38` agree with each other.

### Item 2: claimed cases covered
- **Command lines.** `make e2e-down`, `make e2e` and `make parity` run the same targets. `make parity` recreates the kind cluster that `e2e-down` deletes, so the row's remedy works. `make parity-suite PARITY_SUITE_TIMEOUT=5h30m` (`docs/local-integration-tests.md:196`) does not reach its promised outcome; finding S1. `make e2e-suite` and `make parity-suite` are the same recipe I ran locally (Item 3).
- **Hunks against the commit message.** Every hunk is claimed except `README.md:59–60` and `.github/docs-for-publication-task.md:77`; finding S3.
- **Versions.** The subject and body claim Docker 23.0 and Helm 3.14; finding S4.
- **SVT compose.** Claimed ("back on Keycloak 26.0"). It restores the pre-`8b85515` line exactly. `none`, not run.
- **Helm 4.3 sentence.** I cannot verify it offline. The local Helm is v4.3.0 and no cluster exists.

### Item 3: boundaries, partitions, limits, and state
- **Replaced mechanism (`run-suite`).** Old on ErrImageNeverPull: `wait --for=create` returns, the 3-minute poll runs, `logs -f` fails at once, and `wait $helm_pid` waits out the 15-minute `helm test` timeout. New: about 3 minutes, then the Pod listing, helm killed, exit 1. I ran the recipe with stub `kubectl`, `helm` and `sleep`, through `make e2e-suite`. The failing case printed the message and the Pod listing, killed helm and exited 1. The starts-on-attempt-3 case streamed the log and waited for helm. The stubs remove real timing, so the durations need a cluster run (S5). On the longest-attempt fault (an API server that stalls), `logs -f` in the old code had no timeout either, so the new code is no worse. `none`.
- **Dockerfile merge.** Today `test/parity/suite/testdata/realm/` holds only `README.md`, so the merge branch is a no-op. Builds stay stable as user files are added. Locally, with jq 1.8.2 and sample files (a name with a space, a file with no trailing newline, an empty directory), the output equals the old pipeline apart from the new sorted order. I also ran `docker build --target chart-files` on the Alpine base. The digest-pinned `alpine:3.22` is not cached, so I substituted `alpine:latest`. The build passed and produced 14 users. `none`.
- **`E2E_HELM_ARGS` reaching the stand.** Resolved. No `.github` file passes `E2E_HELM_ARGS`. The stand's `TAG: ''` and `IMAGE_PULL_POLICY: IfNotPresent` defaults are unchanged. `none`.
- **Limits.** The inner limit is the suite Job's `activeDeadlineSeconds: 900` (`helm-templates/authz-test-stand/values.yaml:99`, applied in `templates/suite.yaml:25`), and the parity values do not override it. This is the basis of S1. The CI kind jobs also carry `timeout-minutes: 30` (`.github/workflows/integration-tests.yaml:120,168`), so in CI the timeout cannot be raised past 30 minutes. Only the docs example is affected, and it is local-only.
- **Other sub-items.** `none`.

### Item 3a: level and placement
`none`. Nothing in the change is a unit or a test. The cluster behaviour needs a cluster run, not a unit test.

### Item 4: names by content
`none`. The changed text uses no ordinals.

### Item 5: the failure report
`none`. The new message names the Job and prints the last Pod state. It is the wait-report form that §7 asks for.

### Item 6: what the writer says it verified
The commit states no red run, no run of the new failure path, and no durations for either the old or the new mechanism. Finding S5. The Dockerfile change has no stated run either; my local builds above are the only evidence I have.

### Item 7: siblings
- `E2E_HELM_ARGS` and `TEST_STAND_HELM_ARGS` appear together in `test/k8s/README.md:66–70`. No other file names either one. `none`.
- `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` appear in the same README and in the docs row. `none`.
- `kubectl wait --for=create` no longer appears anywhere. `none`.
- No "two-entry" or "CI builds both" wording remains except the two hunks in S2 and S3.
- The SVT compose file is now the only place on 26.0, which the commit states. `none`.
- The docs row at `docs/local-integration-tests.md:193` names both targets in the symptom and both remedies in the action. Pairing them is left to the reader; S6.

### Findings

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| S1. The example `make parity-suite PARITY_SUITE_TIMEOUT=5h30m` leaves the Job's `suite.activeDeadlineSeconds` at 900, so Kubernetes kills the Job at 15 minutes. | substantive | `docs/local-integration-tests.md:196` | Show the values change too: rerun `make parity-harness TEST_STAND_HELM_ARGS='--set suite.activeDeadlineSeconds=19800'`, then `make parity-suite PARITY_SUITE_TIMEOUT=5h30m`. State that CI caps the run at 30 minutes. |
| S2. The README says CI publishes the two services. The repo's own publication doc says images are pushed on release, and the next paragraph says the release publishes five images. | substantive | `README.md:59–60` | Say the release publishes, and list the five images from `.qubership/docker.cfg`. |
| S3. The commit message has no sentence for the README and publication-doc hunks. | substantive | `README.md:59–60`; `.github/docs-for-publication-task.md:77` | Add a sentence to the commit message that claims each hunk, or move each to its own change. |
| S4. The subject says "run the test stand on year-old tools", and the body states Docker 23.0 and Helm 3.14 floors. Neither has a run or a cited feature. CI pins Helm v4.3.1, so 3.14 never runs in CI. | substantive | commit subject and body; `docs/local-integration-tests.md:35,38`; `.github/workflows/integration-tests.yaml:72,132,180` | Cite the feature that needs 3.14 and 23.0, or run the three kind targets on those versions. Reword the subject to what was actually run. |
| S5. The replaced mechanism's failure has no stated duration or output on a cluster. | substantive | `Makefile`, `run-suite` (around lines 109–120) | Run the ErrImageNeverPull fault on kind (skip `kind load`) on both the old and the new mechanism. Put both durations and outputs in the PR. |
| S6. "Rerun `make e2e` or `make parity`" does not say which pairs with which harness. | taste | `docs/local-integration-tests.md:193` | Name the pairing: `parity-harness` pairs with `make parity`. Expect this to be declined. |

### What this review did not check
- Nothing ran on a cluster: no real durations, no `kubectl` below 1.31, no `helm test --logs` output on Helm 4.3, no SVT run.
- Helm 3.14 and Docker 23.0 were not tested.
- The Dockerfile build used `alpine:latest` in place of the digest-pinned `alpine:3.22`, and jq 1.8.2 locally in place of 1.8.1.
- No style pass was done under `english-developer-style`. I read the new prose only for sentences that misread.

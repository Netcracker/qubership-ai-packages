# Final review of `17b17fc..5dcb6be`: four substantive findings

The commit addresses all three review comments, but four of the documentation and comment sentences it adds are incomplete or name only one of two paths.

**How the form was applied.** The change has no code in a language the form parses: it touches `Makefile` and three Markdown pages. So the form ran through the §2a analogues for a configuration and a docs page. I ran `comment-drift.py 17b17fcf HEAD`; it printed nothing, because it does not parse Makefile or Markdown. I loaded `english-developer-style` and `test-authoring`. `docs-page-authoring` is not among the three skills I was allowed to load, so I did not load it. There is no previous report to check against.

## Item 1: comments consistent with the code and with each other (analogue: statements one file makes about another)

- **`Makefile:49-50`, `Makefile:103-104` and `helm-templates/authz-test-stand/README.md:69-70` leave out the limit that fires first.**
  - All three say a longer suite raises the helm timeout together with `suite.activeDeadlineSeconds`.
  - Both suites also pass `-test.timeout 600s` in `suite.args` (`helm-templates/authz-test-stand/values.yaml:95-96`, `test/k8s/test-stand-values.yaml:55-56`). The Go test binary therefore stops the suite at 10 minutes.
  - A reader who raises only the two named limits to 20 minutes still gets a suite killed at 10. The full analysis is under item 3.
- **`docs/local-integration-tests.md:190` disagrees with `test/k8s/README.md:47` about the same fact.**
  - The page says the leftover objects come from "an older `make e2e`".
  - The README says "an older `make e2e` or `make parity`".
  - The old `parity-harness` (`git show 8b85515^:Makefile`, lines 134–142) applied `parity-realms`, `pip-mock-config`, the Secret and the parity manifests with `kubectl apply`, so the README is right.
- **The Helm claims check out where a source was available.**
  - The quoted install error matches Helm's source: `validate.go:59` (`exists and cannot be imported into the current release: %s`) and `:91` (`invalid ownership metadata`), in v3.15.2.
  - The Helm 3 `--logs` failure is confirmed by `release_testing.go:127-130` in v3.15.2: it asks for a Pod named after every test hook and fails with "unable to get pod logs for …".
  - The Helm 4 "prints nothing" claim rests only on the commit message's 4.3.1 run. The local Helm 4.3.0 help text ("dump the logs from test pods") is consistent with it, but no Helm 4 source was available to confirm it.
- **No sentence narrates the change** (no "now", "no longer" or "used to" in the docs).

## Item 2: claimed cases covered

| Claimed case | Where it is handled |
| --- | --- |
| Comment 1: an older stand blocks `e2e-harness` and `parity-harness` | `test/k8s/README.md:47-49`; the troubleshooting row at `docs/local-integration-tests.md:190`, whose cause and action name only `make e2e` (finding 2) |
| Comment 2: `--logs` does not print the log of a Job hook | Stand README step 3, `:61-66` |
| Comment 3: a timeout variable per suite | `Makefile:51-52`, used at `:115` and `:163`. With `make -n e2e-suite parity-suite E2E_SUITE_TIMEOUT=25m`, `--timeout 25m` reached the e2e suite and `15m` stayed on the parity suite |

**Commands the change documents:**

| Command and promised outcome | Form that runs | Gap |
| --- | --- | --- |
| `helm test authz-test-stand --timeout 15m` (README step 3) | `run-suite` runs the same command, plus context and namespace, in CI jobs `kind-e2e` and `kind-parity` on Helm v4.3.1 | Helm 3 is not run anywhere. `release_testing.go` 3.15.2 shows the call without `--logs` never reads Pod logs, so the README's Helm 3 outcome holds |
| `kubectl logs job/parity-suite` | `run-suite`'s poll loop runs `logs job/<name>` | none |
| `make e2e-down`, then `make e2e` (docs row); `make e2e-down` once (`test/k8s/README.md`) | No run starts from a stand built by the old harness; CI starts fresh | See item 3 |
| Rerun `make e2e-harness` after a Keycloak pull timeout | No run. Helm v3.15.2 `upgrade.go:225-227` upgrades over a failed first release, so a rerun works | none |

**Hunks with no claiming sentence.** The rewrite of the Keycloak row (`docs/local-integration-tests.md:191`, "runs out of its 10-minute wait") is a correct update for the chart-based harness. But no sentence of the commit message claims it (finding 4).

## Item 3: boundaries, partitions, and the negative control

**State left by the old harness.** The change meets it with a documented remedy. Nobody ran the remedy on that state, and the commit does not say it was run. `kind delete cluster` plainly removes everything, so the risk is low, and the quoted symptom text matches Helm's source (item 1). This is finding 5.

**Values users already pass.** None apply: the two variables are new names that only `run-suite` reads.

**Replaced mechanism.** None: only the source of the timeout value changed.

**Limits on the suite's work:**

| Limit | Set at | Default |
| --- | --- | --- |
| Go test timeout `-test.timeout` | `suite.args`: `values.yaml:95-96`, `test/k8s/test-stand-values.yaml:55-56` | 600 s (inner) |
| Job `activeDeadlineSeconds` | `values.yaml:99`; neither stand values file overrides it | 900 s |
| `helm test --timeout` | `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT`, `Makefile:51-52` | 15 m |
| CI job `timeout-minutes` | `.github/workflows/integration-tests.yaml:120` and `:168` | 30 m (encloses the suite, and starts earlier) |

Not counted: `kubectl wait --for=create --timeout=2m` and the 3-minute poll for the log. Each bounds one step, and the work goes on after it.

What happens when each documented setting is raised just past the others:
- **Raise `*_SUITE_TIMEOUT` and `activeDeadlineSeconds` to 20 m together, as the comment says.** `-test.timeout` 600 s still ends the suite at 10 m, so both raises have no effect. This is finding 1.
- **Raise them past what the 30-minute CI job has left after the image build (up to 10 m of harness and 2 × 5 m of install).** The CI job is cancelled first. No sentence names this limit.
- **At the defaults, helm's 15 m equals the Job's 900 s.** "At least as long as" (README `:69`) and "no shorter than" (`Makefile:104`) allow that tie. Helm's clock starts slightly before the Job's `startTime`, so helm times out first and reports a timeout rather than the Job's `DeadlineExceeded`. This only matters once `-test.timeout` is raised past 900 s. The request is a margin: helm strictly longer than the deadline.

## Item 3a: level, placement, and the environment

There is no test level to speak of: the change is configuration and docs. The new variables sit beside `E2E_HELM_ARGS`, which matches the existing layout.

- `helm lint` with `test/k8s/parity/test-stand-values.yaml --set TAG=x` passed.
- `helm template` stops on the missing `files/` (it needs `make test-stand-files`). That predates this change.
- I did not run `make lint`, which needs `npx` and the network.

## Item 4: names by content, not by position

None. I checked the new sentences and the troubleshooting rows; they name commands, targets and values, not positions.

## Item 5: the failure report

None. There are no assertions. For a doc rule the analogue is the symptom a reader sees, and the troubleshooting row quotes Helm's exact error text, which matches the source.

## Item 6: what the writer says it verified

- The commit message states observed runs on Helm 4.3.1 and Helm 3.22.1 for the `--logs` behavior.
- It states no run for the timeout variables, and no run of the `make e2e-down` remedy on a stand built by the old harness. The `make -n` output above shows the wiring only.

## Item 7: siblings of the change

**Variables added to a set (finding 3).** `E2E_HELM_ARGS` and `PARITY_AC_BASE_URL` are named together in `test/k8s/README.md:67-72`, the list of Makefile overrides. That list does not include `E2E_SUITE_TIMEOUT` or `PARITY_SUITE_TIMEOUT`. It also says when each variable takes effect, and the new ones take effect at `e2e-suite` and `parity-suite`, unlike the URL variables. No other file names both existing members.

**Paths of the remedies:**
- **The ownership row** (`docs:190`) has a symptom that names `e2e-harness` and `parity-harness`. Its cause and its action ("then `make e2e`") name only the e2e path (finding 2).
- **The Keycloak row** (`docs:191`) names only `e2e-harness`. `parity-harness` waits on the same first Keycloak pull (`idp`) under the same `--timeout 10m` (finding 4).

**Other `--logs` advice:** `git grep -- '--logs'` finds none left.

## Findings

| # | Finding | Label | File:line | Request |
| --- | --- | --- | --- | --- |
| 1 | The comments on raising the suite limit name `activeDeadlineSeconds` but not `-test.timeout 600s` in `suite.args`, which fires first. Raising the two named limits has no effect past 10 m. The CI job's 30-minute `timeout-minutes` is also unnamed, and "at least as long as" allows a tie, where helm fires before the Job deadline | Substantive | `Makefile:49-50`, `Makefile:103-104`, `helm-templates/authz-test-stand/README.md:69-70` | Name `-test.timeout` in `suite.args` and the CI `timeout-minutes` (`integration-tests.yaml:120`, `:168`) as limits to raise together. Ask for helm's timeout to be strictly longer than `activeDeadlineSeconds`, which is longer than `-test.timeout` |
| 2 | The ownership-error row names both harness targets in its symptom, but its cause ("an older `make e2e`") and its action ("then `make e2e`") cover only e2e. This contradicts `test/k8s/README.md:47` | Substantive | `docs/local-integration-tests.md:190` | Cause: "an older `make e2e` or `make parity`". Action: "then `make e2e` or `make parity`" |
| 3 | The list of Makefile overrides leaves out the two new variables | Substantive | `test/k8s/README.md:67-72` | Add `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`, saying they take effect at `e2e-suite` / `parity-suite` |
| 4 | The Keycloak-row rewrite is claimed by no sentence of the commit message, and its symptom omits `parity-harness`, which meets the same first-pull wait | Substantive | `docs/local-integration-tests.md:191` | Add a commit-message sentence for the rewrite. Name `make parity-harness` in the symptom and the rerun |
| 5 | The `make e2e-down` remedy is not stated as run on a stand built by the old harness (low risk: it deletes the whole cluster, and the error text matches Helm's source) | Substantive | `test/k8s/README.md:47-49`, `docs/local-integration-tests.md:190` | One run from an old stand: the failing `make e2e-harness`, then `make e2e-down` and `make e2e`. Or a sentence in the description saying the remedy was not run |

This review did not run any suite or a cluster, and did not run `make lint`. It did not confirm the Helm 4 `--logs` behavior from source. It did not do a style-only pass over the prose.

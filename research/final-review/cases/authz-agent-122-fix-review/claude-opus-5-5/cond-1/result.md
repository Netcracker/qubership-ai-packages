I filled in every item of the final-review form for 17b17fc..HEAD (one commit, 5dcb6be). It finds four substantive problems and one matter of taste.

**Inputs.** I read the whole diff, the commit message and the three review comments. There was no earlier report. The change touches only a Makefile and Markdown pages, so the drift script ran but found nothing it could parse. I used the no-code analogues for items 1, 4, 5 and 6, and loaded `english-developer-style`. There is no doc-comment skill for Makefiles. I left `test-authoring` out because the change has no tests.

### Item 1: comments consistent with the code and with each other
I checked these against the new code: the comment on the new variables (`Makefile:49-50`), the new `$(4)` note on `run-suite` (`Makefile:103-104`), and the new chart README text (`helm-templates/authz-test-stand/README.md:61-70`). Each matches what the code does. The `$(4)` note ("no shorter than its suite.activeDeadlineSeconds") matches the Job's deadline in `templates/suite.yaml:25`. The comment at `Makefile:49-50` leaves out a limit; that is filed once, under item 3. Nothing describes the change in time words ("now", "no longer"). Nothing else to report.

### Item 2: claimed cases covered
The project has no automated tests for these docs and Makefile changes, so each claim below is checked against the file that makes it true, with a dry run where one is possible.

| Claimed case | Covered by |
| --- | --- |
| Comment 1 / commit: a stand built by an older harness fails the install with `invalid ownership metadata`; the docs say to run `make e2e-down` first | `test/k8s/README.md:47-49` and the troubleshooting row at `docs/local-integration-tests.md:190`. The row has a gap for parity (finding A, item 7). |
| Comment 2 / commit: `--logs` prints nothing for a Job; `kubectl logs job/<suite.name>` after `helm test` prints the log | `helm-templates/authz-test-stand/README.md:61-67`. I confirmed in the helm v3.15.2 source (`pkg/action/release_testing.go:127-130`) that Helm 3 fails with `unable to get pod logs for <hook>`: it treats every test hook as a Pod. The local `helm test --help` (v4.3.0) says `--logs` dumps "the logs from test pods". I couldn't read the Helm 4 source offline, so I'm relying on the commit's own observation for Helm 4. |
| Comment 3 / commit: `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`, both `15m`, set the `helm test` wait | `Makefile:51-52,115,163`. `make -n e2e-suite E2E_SUITE_TIMEOUT=30m` prints `test authz-test-stand --timeout 30m`. |
| Commit title: "let a suite outlast 15 minutes" | Not true as described; see finding C (item 3). |

These are the commands the change tells people to run:

- **`make e2e-down` once, then `make e2e`** (`docs/local-integration-tests.md:190`). No CI job runs this; every CI job starts from a fresh cluster. `e2e-down` deletes the whole kind cluster, so the remedy itself is reliable. The gap is that the row names only the e2e path (finding A).
- **`helm test authz-test-stand --timeout 15m` then `kubectl logs job/parity-suite`** (`helm-templates/authz-test-stand/README.md:65-66`). Nothing runs this form: the Makefile streams with `kubectl logs -f` while the Job runs.
  - After a normal finish, the log is readable. The Job is kept because of `hook-delete-policy: before-hook-creation`, and `backoffLimit: 0` keeps the failed Pod.
  - When the Job hits `activeDeadlineSeconds`, the Job controller deletes its running Pod, so `kubectl logs job/…` has no Pod to read and prints nothing. The README's own advice to keep `--timeout` at least as long as `suite.activeDeadlineSeconds` is about exactly this case. That is finding D.

Nothing in the diff changes behavior beyond what the commit message claims. The troubleshooting row reworded at `docs/local-integration-tests.md:191` (to "10-minute wait") matches `--timeout 10m` and needs no claim.

### Item 3: boundaries, partitions, and the negative control
**Leftover state.** The change does deal with the state an older harness left behind, as a documented remedy, and it covers both the e2e and the parity path in `test/k8s/README.md`. The old `parity-harness` (in `8b85515^`) created `idp`, `pip-mock`, `entitlements-mock`, the realm and pip ConfigMaps and the Secret in `authz-parity` with `kubectl apply`. So the parity path really does meet the same failure.

**Limits.** These are all the limits on the suite's work:

| Limit | Where it is set | Default |
| --- | --- | --- |
| `helm test --timeout` | `E2E_SUITE_TIMEOUT` / `PARITY_SUITE_TIMEOUT` | 15m |
| The Job's `activeDeadlineSeconds` | values | 900s |
| The Go test binary's `-test.timeout 600s` | `suite.args` in `test/k8s/test-stand-values.yaml:55-56` and `values.yaml` (parity) | 600s |
| GitHub Actions job `timeout-minutes: 30` | `.github/workflows/integration-tests.yaml:120,168` | 30m |

The limit on `kubectl wait --for=create --timeout=2m` covers one step only, so it doesn't count.

- **Finding C (substantive).** Raise the two settings the change names past 15 minutes, as `Makefile:49-50` tells you to. The Go binary still panics at 10 minutes, because `-test.timeout 600s` sits inside both limits and isn't named. Raising both settings has no effect on a suite that runs longer than 10 minutes. The commit title claims a suite can now run longer than 15 minutes; without raising `-test.timeout` as well it can't.
  - Request: name `-test.timeout` in `suite.args` in the comment at `Makefile:49-50` (and in the chart README sentence at `:69-70`), or derive one limit from another.
- **Finding E (substantive).** In CI, the 30-minute job limit also covers image builds, a harness wait of up to 10 minutes and two installs of up to 5 minutes each. Raising `E2E_SUITE_TIMEOUT` much past 15 minutes would be cut off by the job limit first.
  - Request: a sentence next to the variables saying CI's `timeout-minutes` must be raised with them, or raise it.

At the defaults the inner limit fires first (600s < 900s = 15m), which is correct. I tested no values users already pass, because no existing setting reaches a new consumer here. Nothing was replaced except `--logs`, which is finding D.

### Item 3a: level, placement, and the environment
This is a Makefile and docs change, so no unit test is owed. Each new line sits where its neighbors are: the variables next to `E2E_HELM_ARGS`, and the stale-cluster note under the Run block. I ran `make -n` on both suite targets with an override and the flags pass through correctly. I didn't run `helm lint`, because it needs the generated `files/`. Nothing to report.

### Item 4: names by content, not by position
The new text refers to things by content ("the harness objects that `kubectl apply` created", "the Job is named by `suite.name`"). Nothing to report.

### Item 5: the failure report
I used the analogue of quoting the error text exactly. Both new remedies quote the exact Helm error, so a reader can match it in their own output. Nothing to report.

### Item 6: what the writer says it verified
The commit message gives observed output for `--logs` under Helm 4.3.1 and 3.22.1. It doesn't state a run of the ownership-metadata failure on an old stand, a run of the `e2e-down` remedy, or a suite run with a raised timeout.

### Item 7: siblings of the change
- **Finding A (substantive).** The troubleshooting row at `docs/local-integration-tests.md:190` names both `make e2e-harness` and `make parity-harness` as the symptom. Its cause names only "an older `make e2e`", and its action names only `make e2e`. Someone who hit it through `make parity-harness` is told to run the wrong target. `test/k8s/README.md:47` names both.
  - Request: say "an older `make e2e` or `make parity`" in the cause, and "then `make e2e` or `make parity`" in the action.
- **Finding B (substantive).** The list of Makefile overrides at `test/k8s/README.md:66-71` names `KIND_CLUSTER`, `E2E_NAMESPACE`, `PARITY_NAMESPACE`, `E2E_ARTIFACTS`, `E2E_HELM_ARGS`, `E2E_BASE_URL` and `PARITY_AC_BASE_URL`. It doesn't mention the new `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`. No other file names two of the existing members (`git grep E2E_HELM_ARGS` outside the Makefile finds only this one).
  - Request: add both variables, with a note that they take effect at `e2e-suite` / `parity-suite`, unlike the base URLs.
- **Finding F (taste).** `test/parity/README.md:30` tells parity users to run `make parity` and has no stale-cluster note. `test/k8s/README.md` covers it, so a link or one line there is my preference, not a requirement.
- `run-suite` has two callers, and both now pass `$(4)`. Nothing else uses the `helm test … --logs` form (`git grep -- --logs`).

### Index

| Finding | Label | File and line | Item |
| --- | --- | --- | --- |
| A: the troubleshooting row names both harness targets, but its cause and action name only `make e2e` | Substantive | `docs/local-integration-tests.md:190` | 7 |
| B: the list of overrides leaves out `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` | Substantive | `test/k8s/README.md:66-71` | 7 |
| C: `-test.timeout 600s` in `suite.args` fires first, so raising the two named limits doesn't let a suite outlast 10 minutes | Substantive | `Makefile:49-50`, `test/k8s/test-stand-values.yaml:55-56` | 3 |
| D: `kubectl logs job/parity-suite` prints nothing after the Job hits its deadline (the Pod is deleted) | Substantive | `helm-templates/authz-test-stand/README.md:61-70` | 2 |
| E: CI's 30-minute job limit fires before a raised suite timeout | Substantive | `.github/workflows/integration-tests.yaml:120,168` | 3 |
| F: the parity README has no stale-cluster note | Taste | `test/parity/README.md:30` | 7 |

Three checks couldn't be done: the drift script doesn't parse Makefiles or Markdown, I couldn't read the Helm 4 source offline to check its `--logs` behavior myself, and I couldn't run `helm lint` because the chart's `files/` directory isn't generated.

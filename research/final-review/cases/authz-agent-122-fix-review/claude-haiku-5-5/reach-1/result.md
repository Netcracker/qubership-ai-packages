## Final review: `17b17fcf..HEAD` (commit `5dcb6be`)

Inputs: the diff (Makefile, `docs/local-integration-tests.md`, `helm-templates/authz-test-stand/README.md`, `test/k8s/README.md`), the commit message, and the three review comments from the task. The drift script printed nothing and exited 0. No member in the change is Go, Java, or another parsed language, so there was nothing for it to tag. The change has no code and no tests, so the form uses the analogues from §2a of the skill. I also loaded `test-authoring` and `english-developer-style` as the task asked. The sentence-level checks below apply the style skill's rules where wording makes a sentence read wrongly.

Checks I ran: `make -n e2e-suite` and `make -n parity-suite PARITY_SUITE_TIMEOUT=20m` (dry runs only), `helm test --help`, and `git log -S` over the history for the old harness's apply calls. I did not run the suite, because there is no cluster.

### Item 1: comments consistent with the code and with each other
- Two sentences in changed files are now inconsistent with what the commit itself found. The comment above `run-suite` says "`helm test` runs the suite Job… It prints the log only at the end." `helm test` prints no log for a Job, and the Makefile never passes `--logs`. The log comes from `kubectl logs -f`. See finding 1.
- The Makefile's "no shorter than its suite.activeDeadlineSeconds" is literally true at the defaults, which are equal. See finding 3 under Item 3.
- The docs row at `docs/local-integration-tests.md:190` names `make parity-harness` but tells the reader to run `make e2e`. See finding 2.
- The premise of the e2e-down remedy holds. Commit `8b85515` shows `$(E2E_KUBECTL) apply` for the e2e objects and `$(PARITY_KUBECTL) apply` in the old `parity-harness`, so "an older `make e2e` or `make parity`" is accurate.

### Item 2: claimed cases covered
Commands the change tells someone to run:

| Command (file) | Outcome | Same command that runs |
| --- | --- | --- |
| `helm test authz-test-stand --timeout 15m` (`helm-templates/authz-test-stand/README.md:65`) | Waits for the suite Job | `run-suite` via `make e2e-suite` and `parity-suite`: `helm … -n authz-e2e test authz-test-stand --timeout 15m` (checked with `make -n`). Covered. |
| `kubectl logs job/parity-suite` (README:66) | Prints the Job's log after `helm test` | `run-suite` runs `logs -f job/<name>`. The Job keeps its Pod, since the hook policy is only `before-hook-creation` (`suite.yaml:22`). The default `suite.name` is `parity-suite` (`values.yaml:90`). Covered. |
| `make e2e-down` (test/k8s/README.md:49, docs:194) | Deletes the cluster | `kind delete cluster --name authz-e2e` (Makefile:136). Covered. |

- The Helm-version claims in the commit (Helm 4.3.1 prints nothing, Helm 3.22.1 fails with `unable to get pod logs`) were not reproduced. The local helm is v4.3.0 and there is no cluster. The local `--logs` help text says "dump the logs from test pods," which supports the first point only. The documented form does not depend on Helm, because the log comes from `kubectl`.
- Hunk with no sentence claiming it: `docs/local-integration-tests.md:191`. The Keycloak row was reworded from "times out at `rollout status deploy/keycloak`" to "runs out of its 10-minute wait." The commit message does not mention it. See finding 5.
- No test claim applies.

### Item 3: boundaries, partitions, and the negative control
Limits on the suite's quantity, with where each is set:
- `helm test --timeout`: 15m, `Makefile:51-52` (variables), used at `Makefile:107`. This is the outer limit, and it is the wrapper's wait.
- Job `activeDeadlineSeconds`: 900, `helm-templates/authz-test-stand/values.yaml:99`. The test-stand values files do not override it. This is the inner limit.
- `kubectl wait --for=create --timeout=2m` and the 3-minute log poll (`Makefile:108-109`): they end only the streaming, not the suite, because `wait $helm_pid` still waits for helm. Not counted.
- CI `timeout-minutes: 30` on `kind-e2e` and `kind-parity` (`.github/workflows/integration-tests.yaml:120, 168`): counted from job start, not from suite start, so it does not meet the same-start rule. Still, the CI job includes setup, so a suite raised past about 15 minutes there is bounded by the job's 30 minutes minus setup. Noted, not a finding.
- Pre-existing state: the harness objects from an older `make e2e` or `make parity`. That is covered by the remedy in the docs, not by a run.

3a (level): no test is changed. The behavior is observable only in the expanded Make recipe. `make -n` shows `--timeout 20m` when the variable is set, so the wiring is confirmed. The outcome (the suite not failing at 15 minutes) needs a cluster and was not run.

### Item 3a: level, placement, and the environment
No test is added or changed, and the change is not in a unit that has tests. The in-process check that exists is `make -n`, and I ran it. CI does not set the new variables, so CI still uses the 15-minute default. The defaults are the same as before.

### Item 4: names by content, not by position
None. No test names are added. The README's numbered step 3 is a procedure, not a position reference.

### Item 5: the failure report
None. No assertions or failure messages are added or changed.

### Item 6: what the writer says it verified
Not stated. The commit states no dry run, no run of the install, no run of the suite, and no check of the Helm version claims. I have stated this without running the suite, which is the reviewer's rule.

### Item 7: siblings of the change
- Set member, `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`: the file that names existing members `E2E_HELM_ARGS` and `E2E_BASE_URL` is `test/k8s/README.md:66-71`. It is the only file that names both (checked by grep). It does not list the new variables. See finding 4.
- `helm test` call sites: only `run-suite`, which both `e2e-suite` and `parity-suite` pass the variable into. None elsewhere.
- Remaining `--logs` references: none, after the change.
- Parity path for the log instruction: the shared chart README covers it. `test/parity/README.md` has no log command or troubleshooting row to fix.
- Old-size counts ("both", "two"): none.

### Findings

| # | Label | File and line | Change requested |
| --- | --- | --- | --- |
| 1 | substantive | `Makefile:100` | The sentence "It prints the log only at the end" describes `helm test`, which prints no log for a Job. Reword it so the streaming is attributed to `kubectl logs -f`, which is the behavior the commit found. |
| 2 | substantive | `docs/local-integration-tests.md:190` | The row covers `make parity-harness` but says "then `make e2e`." A parity reader would run the wrong target. Name `make parity` for that path, or give each target its own remedy. |
| 3 | substantive | `Makefile:51-52`, `values.yaml:99`, `Makefile:104` | At the defaults, the helm wait (15m) and the Job deadline (900s) are equal. The Job's clock starts at or before helm's wait, so the Job deadline wins only by the controller's latency. If the report shows helm's timeout instead of `DeadlineExceeded`, the inner failure is hidden. Setting `E2E_SUITE_TIMEOUT` below 900s causes the same hiding, and nothing warns about it. Set the default wait above the deadline by a stated margin, or derive one from the other, or document the margin. |
| 4 | substantive | `test/k8s/README.md:66-71` | The override paragraph lists `E2E_HELM_ARGS`, `E2E_BASE_URL`, and `PARITY_AC_BASE_URL` but not the two new variables. Add them, and say they take effect at `e2e-suite` and `parity-suite`, not at the harness targets. |
| 5 | substantive | `docs/local-integration-tests.md:191` | The reworded Keycloak row is a hunk that no sentence of the commit message claims. Claim it in the message, or move it to its own change. |
| 6 | taste | `test/k8s/README.md:49` | "before the first run of the test-stand chart" can be read as once per chart version. I prefer "before the first `make e2e-harness` or `make parity-harness` on that cluster." |

### What the review did not check
The suite was not run, and no cluster was used. The Helm 4.3.1 and 3.22.1 behaviors in the commit message were not reproduced, and local helm is v4.3.0. The drift script ran but parsed nothing, since no code member changed.

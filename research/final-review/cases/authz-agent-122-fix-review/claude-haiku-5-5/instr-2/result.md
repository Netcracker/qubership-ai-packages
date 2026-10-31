## Final review: `17b17fc..HEAD` (commit `5dcb6be`)

Nothing was changed or committed. The change is a Makefile and Markdown edit, so the form's analogues in §2a and the drift script do not apply. The drift script printed nothing for these files, which contain no source members to parse. Items below use the §2 wording where it fits.

### Item 1: comments consistent with the code and with each other

Findings: the Makefile comment at `Makefile:100` and the timeout comments at `Makefile:49-50` and `Makefile:103-104` are inconsistent with the values and the other comments; see the table (S3, S5, S1, S2).

### Item 2: claimed cases covered

Commands with their outcomes, and the target that runs the same command:

| Command | Outcome | Counterpart in the Makefile |
| --- | --- | --- |
| `helm test authz-test-stand --timeout 15m` (`helm-templates/authz-test-stand/README.md:65`) | Waits for the suite Job | `run-suite`, `Makefile:107`. Same flags, minus the kube-context and namespace. |
| `kubectl logs job/parity-suite` (`README.md:66`) | Prints the Job's log | `Makefile:110`, the same call with `-f`. The name is a literal here, not `<suite.name>` (S8). |
| `make e2e-down`, `make e2e` | Deletes the cluster; rebuilds it | `Makefile:135`, `Makefile:61` |

The timeout claim, that `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` set the wait, holds. `make -n e2e-suite` shows `--timeout 15m`, and `make -n parity-suite PARITY_SUITE_TIMEOUT=20m` shows `--timeout 20m`.

Unverified claims: the Helm 4.3.1 and Helm 3.22.1 behaviour of `--logs` on a Job hook. The local Helm is v4.3.0 and there is no cluster. The `helm test --help` text ("dump the logs from test pods") supports the Pod-only reading.

Every hunk is claimed except one: the reworded Keycloak row (S4).

### Item 3: boundaries, partitions, and the negative control

The limits on the suite work, from inside out:

- Go test `-test.timeout 600s` in the suite args (`helm-templates/authz-test-stand/values.yaml:95-96`; `test/k8s/test-stand-values.yaml:55-56` for the runtime suite; the parity suite inherits the default).
- `suite.activeDeadlineSeconds: 900` (`values.yaml:99`).
- `helm test --timeout` at `15m` (`Makefile:51-52`). It starts before the Job is created, so it fires first at the defaults.
- The `kind-e2e` and `kind-parity` jobs at `timeout-minutes: 30` (`.github/workflows/integration-tests.yaml:120` and `:168`). They enclose the image build, the harness, and the install, so the suite's time is taken from what remains.

The change raises only the second and third limits, and the Makefile comment names only those two. The first and the fourth also bound the suite, so the change's own claim, a suite that outlasts 15 minutes, does not hold from values alone (S1, S2, S3).

The change has no run that starts from state an earlier `make e2e` left behind. The documented remedy, `make e2e-down`, is not shown run on that state. Item 6 says the same (S9).

### Item 3a: level, placement, and the environment

No test or code changed. The only check I ran is `make -n`. Nothing in the change needs a unit-level test.

### Item 4: names by content, not by position

None. The added text has no ordinals or positional references.

### Item 5: the failure report

None. The change has no assertions.

### Item 6: what the writer says it verified

Not stated. The commit records no run of the remedy on an old cluster, no run of a suite past 10 minutes, and no run of the Helm claims. I could not run any of these here (no cluster, no gh, no curl).

### Item 7: siblings of the change

- Override list: `test/k8s/README.md:66-70` lists the overrides and says the suite URLs take effect at the harness targets, "not at e2e-suite or parity-suite". The two new timeout variables are missing from that list, and they act at the suite targets (S6).
- Troubleshooting row: `docs/local-integration-tests.md:190` names only `make e2e` as the cause, while its symptom names `parity-harness` too. `test/k8s/README.md:47` says "`make e2e` or `make parity`" (S7).
- Other `helm test` calls and `--logs` mentions: none found beyond the chart README and the Makefile.

### Findings

| Finding | Label | File and line | Change requested |
| --- | --- | --- | --- |
| S1. `-test.timeout 600s` in both suite args fires before the helm wait and `activeDeadlineSeconds`. A suite past 10 minutes is killed by Go at 600s, so raising the two documented limits does nothing past 10 minutes. | substantive | `helm-templates/authz-test-stand/values.yaml:95-96`; `test/k8s/test-stand-values.yaml:55-56`; comment `Makefile:49-50` | Derive `-test.timeout` from the same variable, or name it in the comment and the chart README as a third limit to raise. |
| S2. Job `timeout-minutes: 30` encloses images, harness, install, and suite. The 15-minute suite clock starts only after the earlier steps, so raising the suite limit can hit the job cap. | substantive | `.github/workflows/integration-tests.yaml:120`, `:168` | Name the job cap in the Makefile comment, or raise `timeout-minutes` with the suite limit. |
| S3. At the defaults, `helm test --timeout` (15m) equals `activeDeadlineSeconds` (900s), and the helm clock starts first. Helm fires before the Job's own limit, the inner limit does not fire first, and the Makefile wording "no shorter than" does not prevent it. | substantive | `Makefile:51-52`, `Makefile:103-104`; `values.yaml:99`; `README.md:69-70` | Default `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` above 900s, for example `16m`. |
| S9. The `make e2e-down` remedy is not shown run on a cluster the old harness left. The commit states no run. | substantive | `test/k8s/README.md:49`; `docs/local-integration-tests.md:190` | Run: check out `17b17fc`, `make e2e`, check out `HEAD`, `make e2e-harness` (fails), `make e2e-down`, `make e2e` (passes). Repeat for `make parity`. |
| S5. The `run-suite` comment says `helm test` "prints the log only at the end". The fix established that `helm test` prints no Job log at all. | substantive | `Makefile:100` | Reword it to say the Job's log comes from `kubectl logs`, which the loop uses. |
| S6. The override list omits the two new timeout variables and says suite targets are unaffected. | substantive | `test/k8s/README.md:66-70` | Add both variables, with the note that they act at `e2e-suite` and `parity-suite`. |
| S8. The chart README runs `kubectl logs job/parity-suite`. The commit says `job/<suite.name>`, and the README says the name comes from `suite.name`. | substantive | `helm-templates/authz-test-stand/README.md:66` | Use `job/<suite.name>`, or say the example assumes the parity values. |
| S4. The reworded Keycloak troubleshooting row has no sentence in the commit message. | substantive | `docs/local-integration-tests.md:191` | Add a sentence to the commit message for it, or move it to its own change. |
| S7. The ownership row names only `make e2e` as the cause. | substantive | `docs/local-integration-tests.md:190` | Name `make parity` as well, to match `test/k8s/README.md:47`. |

### What this review did not check

- No cluster was available, so no `make` target, Helm install, `helm test`, or `kubectl logs` was run. The ownership failure and the Helm 3 and 4 behaviour are unverified.
- The Makefile lint and `markdownlint-cli2` were not run. By hand, the added Markdown lines are within the 400-character limit set in `.github/linters/.markdown-lint.yml`.
- The English-style pass covered only wording that changes meaning, as the skill directs.

## Final review: `17b17fcf..HEAD` (commit `5dcb6be`)

No previous report exists, so there is no table over earlier findings. The change has no code members and no tests: it edits a Makefile, a chart README, and two docs. The drift script ran, exited 0, and printed nothing, because it does not parse Makefiles or Markdown. For each item I used the §2a analogues. I loaded `english-developer-style` for wording and `test-authoring` for the test-level rules. `docs-page-authoring` was not in the skills folder, so I did not apply it.

### Item 1: comments consistent with the code and with each other

- **Finding 1 (substantive).** `Makefile:99-102`, the comment above `run-suite`, says "`helm test` runs the suite Job … It prints the log only at the end." This Makefile never passes `--logs`, and the stand README now says `helm test` prints no Job log. The comment describes the misreading that the README fix corrects. The log is streamed by the `kubectl logs -f` in the recipe, so the comment should say that.
- **Finding 2 (substantive).** `docs/local-integration-tests.md:190` names `make parity-harness` as a failing target, then prescribes "Run `make e2e-down` once, then `make e2e`." A parity reader can read that as the whole remedy. It needs `make parity` after the reset.
- Checked and consistent: `test/k8s/README.md:47-49` (the pre-chart Makefile at `8b85515^` applies the namespace and the Keycloak and stub objects in both `e2e-harness` and `parity-harness`); the `--timeout 10m` row in the docs; the Makefile comments at lines 49-50 and 103-104.

### Item 2: claimed cases covered (command lines)

Each command line with its outcome, and the target that runs it:

- `helm test authz-test-stand --timeout 15m` (stand README:65) matches `e2e-suite`. `make -n e2e-suite` shows `helm … test authz-test-stand --timeout 15m` with the same flags plus the kind context.
- `kubectl logs job/parity-suite` (stand README:66) matches the `parity-suite` recipe's `logs -f job/parity-suite`, which differs only by `-f` and `-n`. The Job persists after success because of `hook-delete-policy: before-hook-creation` (`suite.yaml:22`), so the form prints the log. The `helm test` line above it relies on the current namespace too, so the README is consistent. No finding.
- `make e2e-down` matches `kind delete cluster --name authz-e2e`.
- The `--logs` removal leaves no other `--logs` in the repository.
- Helm claims: `helm test --help` on the local Helm v4.3.0 says `--logs` dumps "logs from test pods", which supports "Helm 4 prints nothing for a Job". CI pins v4.3.1. The Helm 3.22.1 error text cannot be checked offline. Recorded under Item 6.

### Item 3: boundaries, the other limits, and pre-existing state

The limits on the suite's work, and where each is set:

- **L1, helm wait:** `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT`, default 15m (`Makefile:51-52`). Passed to `--timeout` at `Makefile:107`. `make -n` confirms that `PARITY_SUITE_TIMEOUT=20m` reaches `--timeout 20m`.
- **L2, Job deadline:** `suite.activeDeadlineSeconds: 900` (`helm-templates/authz-test-stand/values.yaml:99`, rendered at `suite.yaml:25`). Neither `test/k8s/test-stand-values.yaml` nor `test/k8s/parity/test-stand-values.yaml` overrides it.
- **L3, Go test timeout:** `-test.timeout 600s` in the suite `args`, at `test/k8s/test-stand-values.yaml:55-56` (runtime suite) and `helm-templates/authz-test-stand/values.yaml:95-96` (parity suite, inherited because the parity values file sets no `args`). This is not in the commit or the README.
- **L4, CI job:** `timeout-minutes: 30` at `.github/workflows/integration-tests.yaml:120` and `:168`. It wraps the image build, `make e2e-harness` (`--timeout 10m`), two installs (`--timeout 5m` each), and the suite.

Findings:

- **Finding 3 (substantive).** L3 caps both suites at 10 minutes. Raising `E2E_SUITE_TIMEOUT` and `suite.activeDeadlineSeconds` to 20m still ends the suite at 10 minutes with a Go "test timed out" panic. The commit fixes only the helm side, so its claim that a longer suite now completes is incomplete. The request: derive `-test.timeout` from the same value, or name it as the third setting in the Makefile comment and the stand README.
- **Finding 4 (substantive).** L4 caps the suite inside CI. Raising the suite past roughly 30 minutes minus setup has no effect in CI, and no document says so. The request: name the job cap in the docs, or raise the job timeouts together with the pair. The skill counts a limit as one of the others only when its expiry ends the same work. This one starts before the suite does, but its expiry does end the suite, so I count it.
- **Finding 5 (substantive).** At the defaults, L2 and L1 are equal (900 s and 15 m). The helm wait starts after the Job is created, and the Job's clock starts when its controller first syncs it. The two are within moments, so the outer helm timeout may fire first, and the report then says "timed out" and hides the Job's `DeadlineExceeded`. The README's "at least as long as" permits equality, which the skill does not. The request: make the helm default a margin above the deadline, or state that the outer limit must be strictly longer.
- **Finding 6 (substantive).** The inherited-state path has no run. The change's only proof for the old-objects case is a documented remedy, and nothing in the change runs it on a cluster that the pre-change Makefile built. CI starts each job from a fresh kind cluster, so no job reaches that state. There is no cluster here, so I could not run it. The request: run `make e2e-down` and then `make e2e-harness` on a cluster built by the pre-chart Makefile, or say in the change that the remedy is unrun.

### Item 3a: level, placement, environment

- No test is added or changed. The in-process and CI-job tests are not owed for a Makefile and docs change.
- The wiring is exercised by CI: the e2e job runs `make e2e-suite`, and the parity job runs `make parity-suite`, both through `run-suite`.
- Placement: none. The `make -n` checks above are the only local check of the timeout variables.

### Item 4: names by content

- None. No name, comment, or case id refers to a thing by position. The "first run" in the docs refers to the run, not to an ordinal.

### Item 5: failure report

- None. The change has no assertions.

### Item 6: what the writer says it verified

- **Finding 7 (substantive).** The commit states Helm behaviour as fact, "Helm 4.3.1 skips it and prints nothing, and Helm 3.22.1 … fails with 'unable to get pod logs'", and states that the remedy works. It states no run of any of them. Local Helm is v4.3.0, not the v4.3.1 that CI pins, and I could not run either version here. The request: state the run, or mark the Helm 3 text and the remedy as read from source, not run.

### Item 7: siblings

- `run-suite` has two callers, `Makefile:115` and `:163`. Both pass a timeout variable, so neither is missed.
- The `helm test` call sites are `Makefile:107` and `helm-templates/authz-test-stand/README.md:65`. No other document sets a helm timeout.
- The `-test.timeout` siblings are the two `args` blocks in Finding 3. The `activeDeadlineSeconds` siblings are `values.yaml:99` and `suite.yaml:25`, covered by Finding 5.
- The `kubectl apply` remedy sits in `test/k8s/README.md` and in the docs troubleshooting row. `test/parity/README.md` has no troubleshooting section, so it needs no note.

### Report

| Finding | Label | File and line | Change requested |
|---|---|---|---|
| 1. `helm test` "prints the log" comment is wrong for this Makefile | substantive | `Makefile:99-102` | Say that the `kubectl logs -f` in the recipe streams the Job's log. |
| 2. Parity remedy names only `make e2e` | substantive | `docs/local-integration-tests.md:190` | Add "or `make parity` for `make parity-harness`" after the reset. |
| 3. Go `-test.timeout 600s` caps both suites at 10 minutes | substantive | `test/k8s/test-stand-values.yaml:55-56`; `helm-templates/authz-test-stand/values.yaml:95-96` | Derive it from the same value as the other two limits, or name it as the third setting in the Makefile comment and the stand README. |
| 4. CI job `timeout-minutes: 30` caps the suite and is not named | substantive | `.github/workflows/integration-tests.yaml:120`, `:168` | Name the job cap in the docs, or raise the job timeouts with the pair. |
| 5. At defaults the helm timeout (15m) equals the Job deadline (900 s), so the outer limit can fire first | substantive | `Makefile:51-52`; `helm-templates/authz-test-stand/values.yaml:99`; `helm-templates/authz-test-stand/README.md:69-70` | Make the helm default a margin above the deadline, or state that the outer limit must be strictly longer. |
| 6. Inherited-state remedy has no run in the change | substantive | `test/k8s/README.md:47-49`; `docs/local-integration-tests.md:190` | Run the remedy on a cluster from the pre-chart Makefile and state the result, or say it is unrun. |
| 7. Helm behaviour and remedy stated without a run | substantive | commit message; `helm-templates/authz-test-stand/README.md:61-62` | State the run, or mark the Helm 3 text and the remedy as read from source. |

Not checked: no cluster, so no helm behaviour, no Job-deadline timing, no CI job duration, and no `e2e-down` remedy were run; the Helm 4.3.1 and 3.22.1 claims were checked only against `helm test --help` on v4.3.0. The wording pass covered only the sentences that read wrongly, not a full style pass. No file was changed and nothing was committed.

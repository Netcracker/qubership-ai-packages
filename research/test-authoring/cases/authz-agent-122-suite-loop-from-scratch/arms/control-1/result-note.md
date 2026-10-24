I added `test/scripts/test-kind-targets.sh` and a CI step that runs it. The script passes on this commit and fails on the commit before it. Each failure names the bug the change fixed. Nothing is committed, and I didn't touch the Makefile, Dockerfile or charts.

---

**Message for the author**

**Tests added: `test/scripts/test-kind-targets.sh`**

The script runs the real `make` targets with fake `kubectl`, `helm` and `sleep` first on `PATH`. No cluster is involved. The fake `kubectl` acts like version 1.30: it rejects `wait --for=create`, and the suite container starts at a chosen read of its log. The fake `sleep` returns at once and records the seconds asked for, so the three minutes of polling take no real time. It's a plain bash script with pass/fail checks, the same style as `test-chart-render.sh` beside it. This is the smallest level where the change shows: the polling only exists inside the Makefile recipe, so the only way in is `make <target>`. The kind jobs remain the test against a real cluster.

| What is checked | Why |
| --- | --- |
| `e2e-suite` streams the log and exits 0 when the container starts on read 1 or on read 90 (the first and last of the 90 polls) | Read 90 is the regression: on the old Makefile, kubectl 1.30 rejected `--for=create`, the loop was skipped, and no log was printed |
| A container that hasn't started by read 91: `make` fails, prints `The runtime-suite container did not start within 3 minutes:` and the Pod listing, streams no log, and leaves no `helm test` running | The new give-up path. On the old Makefile, the run hangs until the script's one-minute guard ends it |
| At the defaults, the polling adds up to 180 s while `helm test` gets `--timeout 15m` | Ties "3 minutes" in the message to the actual polling, and shows the three-minute stop comes before helm's own 15-minute timeout |
| With `E2E_SUITE_TIMEOUT=2m`, helm times out first: `make` fails and shows helm's error | The case where a configured limit is shorter than the three minutes |
| `parity-suite` gives up the same way, naming `parity-suite` and listing Pods in `authz-parity` | Checks that the parity target passes its own Job name and namespace |
| One run of `e2e-harness e2e-install parity-harness parity-install` with `E2E_HELM_ARGS='--set TAG=product'` and `TEST_STAND_HELM_ARGS='--set TAG=stand'` | Each test-stand install gets only `TAG=stand` and each chart install only `TAG=product`. Any wrong one shows up as a line in a diff. `test-stand-files` is skipped with `-o` because it needs docker |

**Evidence**
- **Before your change:** 9 failures, all on the old symptoms: the log line is missing, the run ends with status 124 (killed by the guard) instead of failing, and the stand install shows `TAG=product`. Two checks pass there, as expected: the helm-timeout case behaved the same before, and "no helm left running" only matters on the new path.
- **On this commit:** all pass. Five deliberate breakages of the new Makefile each fail at least one check:
  - removing the `kill`/`wait` of helm
  - polling 30 times instead of 90
  - the parity stand install taking `E2E_HELM_ARGS` again
  - a start flag that is never set
  - no `exit 1` after giving up
- shellcheck and yamllint are clean. The script takes about 50 s on macOS, almost all of it starting the fake processes. It needs `timeout` and `make`, which `ubuntu-latest` has.

**Other change:** `.github/workflows/integration-tests.yaml` now runs the script as a step in the `chart` job, and its header comment says so. That's CI wiring, not production code; drop it if you'd rather add a separate job to `ci-gate`.

**Proposed, not done**
1. **The polling loop doesn't notice when helm has already exited.** If `helm test` fails straight away (release missing, `E2E_SUITE_TIMEOUT` under 3m), the target keeps polling for three minutes. It then prints the misleading "container did not start" message and `kill: No such process`. Breaking out of the loop once helm's process is gone (a `kill -0 $$helm_pid || break` check) would fix it. My helm-timeout check only asserts that the target fails and shows helm's error, so it will still pass after that fix.
2. **The `chart-files` stage (sorted files, NUL-separated) has no test.** It only runs inside `docker build`, which I couldn't run here. One option, after `make test-stand-files` in the `chart` job: check that the users in `files/realms/parity/parity-realm.json` come in sorted file-path order. Another: run the stage on a copy of the users folder that includes a file name with a space.
3. **The SVT Keycloak 26.0 revert and the docs changes** owe no new test here. An SVT run on 26.0 is the evidence for the revert.
4. **Test-stack line.** `AGENTS.md` doesn't say how tests are written. I suggest adding: `Tests: shell checks in test/scripts are plain bash with pass/fail; a failed check is reported and the run continues; each check is named by its label.` I haven't edited `AGENTS.md`; tell me if you want the line added.

I added `test/scripts/test-k8s-make-targets.sh`, a bash script that checks the changed Makefile targets without a cluster, and a step in the `chart` job of `.github/workflows/integration-tests.yaml` that runs it. All 15 checks pass on this commit (about 35 s locally). On the parent commit, the 10 checks for the behavior this commit changed fail, and the 5 control checks pass. Nothing is committed.

---

**Message for the author of the pull request**

**Tests added: `test/scripts/test-k8s-make-targets.sh`**

These are medium tests by the skill's definition: they run the real `make` and `/bin/sh` on the local machine. The script puts fake `kubectl`, `helm` and `sleep` first on `PATH`, so the real Makefile recipes run with no cluster:

- **The fake `sleep`** returns at once and adds to a simulated clock, so the three-minute wait takes no real time.
- **The fake `kubectl`** rejects `wait --for=create`, as kubectl before 1.31 does. The suite log can be read only once the clock reaches `FAKE_SUITE_STARTS_AT`.
- **The fake `helm test`** gives up when the clock reaches its `--timeout`, and records it when it is stopped.

The script follows `test-chart-render.sh`: each check prints `ok:` or `FAIL:`, the script carries on after a failure, and each failure prints the exit status and the output.

What the checks cover, and why:

- **The suite log is streamed on an older kubectl.** The container starts 10 s after `helm test` begins and the log is streamed. This is the regression the commit fixes. On the parent commit, `wait --for=create` is rejected and the log is never streamed.
- **The edge of the 3-minute limit.**
  - A container that starts at 178 s (the 90th and last read attempt) has its log streamed.
  - One that starts at 180 s fails with "did not start within 3 minutes".
- **A container that never starts (ErrImageNeverPull), at the default `E2E_SUITE_TIMEOUT=15m`:**
  - the target fails with the message that names the Job;
  - it lists the Job's Pod;
  - it stops `helm test` after 180 s instead of waiting out helm's 15 minutes. This shows the new 3-minute limit fires before helm's timeout at the defaults.
- **`helm test`'s timeout set below the 3 minutes (`E2E_SUITE_TIMEOUT=2m`).** The target fails and helm's own timeout error reaches the user.
- **`parity-suite`.** One check for a container that never starts: the message and the Pod listing name `parity-suite` in `authz-parity`. It confirms the same recipe is wired to the parity Job and namespace.
- **The extra install arguments.**
  - `e2e-harness` and `parity-harness` pass `TEST_STAND_HELM_ARGS`, and not `E2E_HELM_ARGS`, to the test-stand install.
  - As controls in the same run, the `authz-policy-admin` and `authz-agent` installs get `E2E_HELM_ARGS` and not `TEST_STAND_HELM_ARGS`.
  - `test-stand-files` is skipped with `make -o`, because it runs docker and deletes `files/`.
- **A failed suite.** When `helm test` fails, the target fails and the suite log is still streamed. This check is a control and also passes on the parent commit.

**Red on the parent commit.** I ran the same script against the parent commit in a temporary worktree. All 10 checks for behavior this commit changed fail there, including both test-stand-install checks: the stand got `TAG=product` before this change. The 5 controls pass on both commits.

**CI:** the `chart` job now runs the script after the render assertions, and the workflow's header comment mentions it.

**Proposed, not done:**

1. **Possible defect: the wait carries on after `helm test` has ended.** With `E2E_SUITE_TIMEOUT=2m` and a container that never starts, helm gives up at 120 s, but the loop keeps polling to 180 s. It then prints "did not start within 3 minutes", and `kill` fails with `No such process`. The same happens when `helm test` fails at once, for example on a missing release. The fix would be to leave the loop once helm has exited, for example with `kill -0 $helm_pid` on each attempt. My check asserts only that the target fails and that helm's error is shown, so it will not block that fix.
2. **The chart-files stage (sorted, NUL-separated user files) has no test.** Its behavior can only be seen through `docker build --target chart-files`, which I could not run here. The test I'd propose builds that stage with two user files whose `find` order differs from their sorted order, one with a space in its name. It would assert that the merged `users` come in sorted path order and that the spaced file is included. It could run in the `chart` job, where `make test-stand-files` already builds the stage.
3. **The SVT Keycloak image is no longer pinned.** It went back to `quay.io/keycloak/keycloak:26.0` with no digest, so later 26.0 patch releases will be picked up. Only an SVT run can tell whether that matters.
4. **A stack line for the repository's instructions.** `AGENTS.md` names no test stack. I'd propose this line: `Tests: shell scripts under test/scripts with pass/fail helpers that continue after a failure and print each check's label; Go testing for Go code.` I did not edit `AGENTS.md`.

The documentation changes cannot change behavior and need no tests.

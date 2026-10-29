I added one test script, `test/scripts/test-k8s-make-targets.sh`. It passes 10 of its 11 checks; the one that stays red is a real defect in the new wait loop, not a test problem. Nothing is committed and no production file changed.

---

**Message for the author of the pull request**

**What I added.** `test/scripts/test-k8s-make-targets.sh` runs the real `make` targets with stand-ins for `kubectl`, `helm`, `docker` and `sleep` first on PATH. `sleep` returns at once and adds its argument to a fake clock, so a check can see how long a target would have taken without waiting for it. It's a local-machine test with no cluster, written in the same `pass`/`fail` style as `test-chart-render.sh`. A full run takes about 45 seconds and passes shellcheck.

| Check | What it protects | On the base commit (`HEAD~1`) |
| --- | --- | --- |
| `e2e-suite` streams the suite log on a kubectl without `wait --for=create` | The kubectl-older-than-1.31 fix | Red: the log never appears, and the target still exits 0 |
| `e2e-suite` streams the log once the container starts | That it still works on a newer kubectl | Green |
| `e2e-suite` fails with helm test's error when the suite fails | That a failed suite still fails the target | Green |
| `e2e-suite` stops helm test and lists the Pod when the container doesn't start (ErrImageNeverPull) | The new 3-minute stop | Red: helm waits out its own timeout and the Pod is never listed |
| `parity-suite`, same fault | The parity target names its own Job and namespace | Red |
| `E2E_SUITE_TIMEOUT=1m`, shorter than the 3-minute wait | helm's own timeout fires first and the user sees its error | Green |
| `e2e-harness` and `parity-harness` install the test stand with `TEST_STAND_HELM_ARGS`, not `E2E_HELM_ARGS` | The `TAG` leak into the test stand | Red: the stand got `--set TAG=product` |
| `e2e-install` and `parity-install` keep `E2E_HELM_ARGS` | That the product charts still get their arguments | Green |

**The one red check is a bug in this change.** If the Job exists but its Pod is never created (for example, the namespace's restricted Pod Security admission rejects it), each `kubectl logs job/<name>` call first waits up to 20 seconds for a Pod (`kubectl logs --help`). The loop counts 90 tries rather than watching the clock, so it gives up after 90 × (20 s + 2 s) = 1,980 s, about 33 minutes. That breaks the promised "about three minutes" and runs past helm test's 15-minute timeout. The old code behaved the same way here (2,000 s on the base commit), so it isn't a regression, but the commit message's promise doesn't hold. I left the check red because the fix belongs in the Makefile, for example:
- give the loop a deadline (`SECONDS`, or a start time compared on each pass), and
- pass `--pod-running-timeout=2s` to each try.

**Time to fail, old code against new** (from the fake clock, with each `kubectl` call counted at its own timeout):
- **Container never starts:** the old code failed after 15 minutes with only helm's timeout error. The new code fails after 180 s, prints the Pod listing, and stops helm.
- **Older kubectl:** the old code exited 0 without streaming the log. The new code streams it.
- **helm test fails before it creates the Job** (for example, the release isn't installed, or `E2E_SUITE_TIMEOUT` is short): the old code gave up after the 2-minute `wait --for=create`. The new code keeps trying `kubectl logs` for the full 3 minutes after helm has already exited, then prints "did not start within 3 minutes" and a `kill: No such process` line. Helm's real error is still shown, so the check passes. I suggest ending the loop when helm exits (`kill -0 $helm_pid || break`), or saying in the PR why not.

**Proposed, not done:**
- **Run the script in CI and list it.** Add `bash test/scripts/test-k8s-make-targets.sh` to the `chart` job in `.github/workflows/integration-tests.yaml`, and list it in `test/readme.md` next to `test-chart-render.sh`. Do this once the red check is fixed.
- **The sorted, NUL-separated `chart-files` merge in the Dockerfile has no test.** It only runs in `docker build`, which I couldn't run here. I suggest a CI step that adds a user file whose name has a space, builds `test-stand-files` twice, and checks that both `parity-realm.json` files are identical and include that user.
- **The Keycloak 26.0 revert in the SVT Compose stack** needs an SVT run as evidence. Nothing I could run covers it.
- **The documentation changes** can't change behaviour and need no tests.
- **A stack line for `AGENTS.md`**, which has none today. For example: `Tests: Go testing for Go modules; test/scripts/*.sh are bash checks whose pass/fail helpers continue past a failure and name each check.` I didn't edit `AGENTS.md`.

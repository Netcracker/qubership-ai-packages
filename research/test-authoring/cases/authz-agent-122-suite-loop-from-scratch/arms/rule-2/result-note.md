I added `test/scripts/test-k8s-targets.sh` and a CI step that runs it. It has 15 checks: all pass on this commit (about 20 s locally, and shellcheck is clean), and 9 fail on the parent commit with the symptoms this commit fixes. I changed no production code and committed nothing. Here is the message I'd leave for the author:

---

**Tests added**

`test/scripts/test-k8s-targets.sh` is a medium-level test in the style of `test-chart-render.sh` (bash, `pass`/`fail` lines, a failure count at the end). It runs the real Makefile recipes with stand-ins for `kubectl`, `helm` and `sleep` on PATH. The fake `kubectl` behaves like kubectl 1.30, which has no `wait --for=create`. The fake `sleep` returns at once and records how long it was asked to sleep, so the 3-minute wait is measured without waiting. I added it as the "Kind target checks" step in the `chart` job of `integration-tests.yaml`, and updated that file's header comment.

- **Job appears late, kubectl 1.30:** `e2e-suite` streams the suite log and exits 0. On the parent commit it fails: `wait` is rejected, the loop is skipped, and no log is streamed.
- **Suite fails:** the log is streamed and helm test's error is the outcome. This passes on both commits; it guards the `wait $helm_pid` at the end.
- **Container never starts** (`e2e-suite` and `parity-suite`): the target fails, prints "The <job> container did not start within 3 minutes:" with the Pod listing, stops helm test before helm's own timeout, and polls for about 180 s on the fake clock. On the parent commit there is no message, it polls for 0 s, and it sits in helm test until helm times out.
- **helm test's timeout is shorter than the 3-minute wait** (`E2E_SUITE_TIMEOUT=1m`): the target fails and helm's "timed out" error reaches the user.
- **Install arguments:** `e2e-harness` and `parity-harness` pass `TEST_STAND_HELM_ARGS` and not `E2E_HELM_ARGS` to the test-stand install. On the parent commit `TAG=product` reaches the stand. `e2e-install` and `parity-install` still take `E2E_HELM_ARGS`. The harness checks skip `test-stand-files` (`make -o`), because it needs Docker.

**How long each version takes to fail**

| Fault | Before this commit | After |
| --- | --- | --- |
| kubectl older than 1.31 | `error: unrecognized condition`; no log streamed; ends when the suite ends | log streamed |
| Container never starts | 3 min of polling, then helm test's timeout: 15 min, "timed out waiting for the condition" | about 3 min, the message above, the Pod listing, and helm test stopped |

**Problem found, not fixed (production code)**

- **The 3-minute limit doesn't hold when the Job exists but has no Pod.** This happens, for example, when the restricted Pod Security Standard refuses the Pod. Each `kubectl logs job/<name>` attempt then waits `--pod-running-timeout`, 20 s by default. So the loop takes about 90 × (20 s + 2 s) ≈ 33 minutes:
  - helm test gives up at 15 m;
  - the loop keeps polling;
  - it then prints "did not start within 3 minutes".

  The old mechanism took just as long on this fault, so it isn't a regression, but the new message is wrong in that case. Neither loop sets `--request-timeout`, so an API server that stops answering hangs them with no limit. I reproduced this at 1/100 scale: the stand-in helm timed out before the loop gave up.
- **Fix I propose:** pass `--pod-running-timeout=1s --request-timeout=10s` to the polling call, and stop the loop once helm test has exited (`kill -0 $helm_pid`). After that, a test with a slow `logs` stand-in can check that the target gives up within about 3 minutes. I didn't add that test, because it would fail until the fix lands.

**Not tested**

- **The `chart-files` stage** (sorted, NUL-separated user files) needs `docker build`, which I couldn't run. The test it needs: build that stage with a user file whose name has a space, plus two files in reverse order, and check the order of `users` in `parity-realm.json`. Today `make test-stand-files` in CI only shows that the stage builds.
- **Keycloak back on 26.0 in the SVT stack:** this is a version change, and only an SVT run covers it; no test from me.
- **Docs and README changes** can't change behavior, so they need no tests.

**Proposal:** `AGENTS.md` has no line saying which test tools the repo uses. I suggest adding: `Tests: Go testing for Go code; bash scripts in test/scripts with pass/fail helpers for charts and Makefile targets.` I haven't added it.

---

Files:
- `test/scripts/test-k8s-targets.sh` (new)
- `.github/workflows/integration-tests.yaml` (new step and header comment)

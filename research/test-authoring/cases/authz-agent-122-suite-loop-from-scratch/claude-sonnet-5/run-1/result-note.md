Confirmed: no commit was made, HEAD unchanged, only three new untracked test files.

---

**Message for the pull request author:**

I added three test scripts under `test/scripts/`, matching the house convention of `test-chart-render.sh`/`test-opa.sh` (plain bash, `pass`/`fail`/`failures` counter, continuing past the first failure so a run reports every mismatch) rather than introducing bats, since that's what the nearest existing tests of this kind already use.

- **`test-run-suite.sh`** — exercises the `run-suite` shell logic (`e2e-suite`/`parity-suite`) with fake `kubectl`, `helm`, and `sleep` on `PATH`, no cluster involved. Covers: a Job that starts after a couple of polls streams its log and exits 0; the same but the suite itself fails, so the failure still reports; and a Job whose container never starts, which must print the "did not start within 3 minutes" message with the Pod listing, never call `kubectl logs -f`, and kill `helm test` rather than let it run out its own timeout. I verified all three actually go red against the pre-fix Makefile (checked out `HEAD~1:Makefile` temporarily, ran the suite, restored it) — the first two fail because the log never streams (the exact "polling loop was skipped" bug), and the third hangs until my safety `timeout` kills it.
- **`test-e2e-helm-args.sh`** — uses `make -n` (no cluster, no Docker build, nothing executed) to check that `TEST_STAND_HELM_ARGS` reaches the test-stand installs in `e2e-harness`/`parity-harness` and not `E2E_HELM_ARGS`, while `e2e-install`/`parity-install` still take `E2E_HELM_ARGS` as before. Also confirmed red on `HEAD~1`.
- **`test-chart-files-merge.sh`** — runs the `find | sort -z | xargs -0 | jq --slurpfile` pipeline from the Dockerfile's `chart-files` stage directly (jq reads `$HOME/.jq` the same way the image does), with a fixture `users/` directory. Covers deterministic merge order by filename, profile defaults filled vs. kept, a filename containing a space, the existing duplicate-username check still firing, and the no-user-files case. A text guard (`grep`) ties the hardcoded pipeline to the Dockerfile's actual RUN line, so a future edit to one without the other fails loudly. I manually confirmed (not wired into the script) that the pre-fix `$(find ...)` unquoted substitution crashes on the space-named file and that its merge order follows argument order rather than being sorted.

What I did **not** add, and why:
- No test for the SVT Compose Keycloac downgrade (26.3.5 → 26.0): nothing in the repo exercises that Compose stack automatically, and reproducing it would need `docker compose`, which I was told not to run. If you want this covered, the Compose stack would need its own CI job first.
- Nothing for the doc-only changes (`README.md`, `docs/local-integration-tests.md`, the chart README, `test/k8s/README.md`, `.github/docs-for-publication-task.md`) — prose can't fail a test.

All three scripts pass against the current tree and are each individually confirmed to fail against the pre-fix Makefile/Dockerfile. No production file was changed, and nothing was committed.

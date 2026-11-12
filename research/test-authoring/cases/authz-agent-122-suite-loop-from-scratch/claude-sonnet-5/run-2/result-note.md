Both files are executable, untracked (not committed, as instructed), and the repository is otherwise unchanged. Here's the message for the PR author:

---

This commit fixed three independently-observable bugs and added no tests. I wrote the tests it owes, following `test-authoring`, as two new scripts beside the repo's existing shell-assertion tests (`test/scripts/test-chart-render.sh`-style: `pass`/`fail` helpers, no framework), since there's no Kubernetes cluster available to me and I was asked not to use kind/docker/kubectl/helm against a real cluster. Both are left uncommitted, not wired into CI, and the Makefile/Dockerfile are untouched.

**`test/scripts/test-e2e-makefile.sh`** — the `run-suite` macro and the `TEST_STAND_HELM_ARGS`/`E2E_HELM_ARGS` split, exercised through the real `make e2e-suite`/`-harness`/`-install` targets with fake `kubectl` and `helm` on `PATH` (no cluster, no Docker):
- `make -n` on each `*-harness`/`*-install` target shows `TEST_STAND_HELM_ARGS` reaching the test-stand install and `E2E_HELM_ARGS` reaching the agent/policy-admin installs, never the other way.
- A container that starts on the third poll: the suite log streams, exactly 3 polls happen, and the fake `kubectl wait` (simulating pre-1.31 kubectl) is never called — if a regression reintroduced `kubectl wait --for=create`, this fails loudly instead of silently skipping the wait as the old bug did.
- A container that never starts (`ErrImageNeverPull`): `e2e-suite` fails after ~185s (not helm's 20-minute `--timeout`, set deliberately long to prove this), prints the Pod listing, uses its full 90-poll budget, and actually kills the backgrounded `helm test`.
- I confirmed both scenarios go red on `HEAD~1`'s Makefile (wrong variable reaches the test-stand install; no poll loop, 0 attempts, straight into `kubectl wait`) before verifying green on `HEAD`.

**`test/scripts/test-parity-users-merge.sh`** — the `find | sort -z | xargs -0 | jq` pipeline in `build/authz-agent-transfer/Dockerfile`'s `chart-files` stage, extracted verbatim from the Dockerfile text (via `sed`, so the test can't drift from what the image actually runs) and run in a sandbox `$HOME` with `profile.jq` as `~/.jq`:
- A user file named `a space.json` merges correctly and in filename order — the base commit's `$(find …)` word-splits that name and errors with `jq: error: Could not open file a/space.json`, dropping that user entirely; I verified this red run.
- Merge order is alphabetical by filename regardless of the order files were created in (the bug this fixes: unsorted `find` order, varying by filesystem, moved the realm checksum and triggered spurious Keycloak restarts).
- An empty `users/` directory (the real current state of `test/parity/suite/testdata/realm/`) merges cleanly via `xargs -r`, rather than failing.
- The same input merges byte-identical twice.

What I didn't do: the Keycloak image pin back to `26.0` in `test/svt/common/compose/docker-compose.yml` is a version decision with no logic behind it, so I didn't write a test for it. I also didn't touch `.github/workflows/integration-tests.yaml` or `test/README.md`'s CI-gate list to wire the new scripts in — that felt like more than "tests," but both scripts run the same way `test-chart-render.sh` does (`bash test/scripts/<name>.sh`) and are ready to add there; the merge-pipeline one is a few seconds, the Makefile one is ~3-4 minutes because the second scenario deliberately waits out the real 3-minute poll budget the fix introduced.

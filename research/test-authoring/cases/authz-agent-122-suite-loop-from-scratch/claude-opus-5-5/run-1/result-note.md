I added two test scripts and three fake tools. Nothing is committed and no production file changed. One new check fails on HEAD, and it fails because of a real defect in the commit, not a problem in the test. The run that shows it is below.

Proposal for you (not part of the PR message): add a stack line to `AGENTS.md` saying that shell checks are plain bash scripts under `test/scripts/` using `fail`/`pass`, which report every mismatch and name each check by its label. I learned that from reading `test-chart-render.sh`. I'll only add it if you agree.

---

**Message for the author of the pull request**

**Tests added**

The repository's shell tests are plain bash scripts with `fail`/`pass`, like `test/scripts/test-chart-render.sh`, so the new ones take the same shape rather than bats.

- **`test/scripts/test-suite-targets.sh`** runs the real Makefile recipes. `test/scripts/fake-cluster/` puts a fake `kubectl`, `helm` and `sleep` first on PATH. The fake `sleep` moves a pretend clock instead of waiting, so a "3 minutes" check runs in seconds. The fake `kubectl logs job/<name>` copies kubectl 1.35: if the Job has no Pod yet, it waits `--pod-running-timeout` (20 s by default) for one, per `GetPodList` in `k8s.io/kubectl/pkg/polymorphichelpers/helpers.go`.
  - **kubectl without `wait --for=create`:** the suite log is streamed. This is the regression test; it fails on the parent commit with "no line '--- PASS: TestSuite (0.01s)'".
  - **Container starts on the 90th poll** (the last one inside 3 minutes): the log is streamed and helm test is not stopped.
  - **Container never starts (`ErrImageNeverPull`), for both `e2e-suite` and `parity-suite`:**
    - the target fails;
    - it prints the "did not start within 3 minutes:" line;
    - it lists that Job's Pod in that namespace;
    - it stops helm test;
    - it takes 180–202 s.

    On the parent commit it took 900 s and printed neither the message nor the Pod.
  - **The Job has no Pod** (for example, admission refuses it under the restricted Pod Security Standard): the target should give up within 202 s and stop helm test.
  - **`E2E_SUITE_TIMEOUT=2m`**, which is less than the 3-minute limit: helm's timeout fires first, and the target should end with it.
  - **`E2E_HELM_ARGS='--set TAG=pr-123'` with `TEST_STAND_HELM_ARGS='--set TAG=stand-7'`:** the test-stand install gets only `stand-7`, and the agent and authz-policy-admin installs get only `pr-123`. This is checked for both the e2e and parity targets. The stand reads `TAG` at `templates/suite.yaml:40`, `pip-stub.yaml:40` and `tenant-manager.yaml:34`. Both stand checks fail on the parent commit.
- **`test/scripts/test-chart-files.sh`** runs the `RUN` instruction of the `chart-files` stage, read from the Dockerfile, without docker. A fake `find` lists files in reverse order.
  - **No user files:** the realm keeps its own users.
  - **Two user files:** their users are merged in file-name order. On the parent commit they came out in reverse order.
  - **A file name with a space:** its users are merged, with the profile fields filled in. The parent commit failed with "Could not open file users/r29". A change that drops `map(profile)` makes this check fail.

**Three checks fail on HEAD, from two defects in the new wait loop**

1. **The no-Pod case does not stop at 3 minutes.** When the Job has no Pod, each `kubectl logs job/<name>` waits 20 s, so the 90 polls take 1980 s. By then helm test has already given up at 900 s. The target then prints "did not start within 3 minutes" and `kill: No such process`.
2. **The target ignores a helm timeout below 3 minutes.** With `E2E_SUITE_TIMEOUT=2m`, helm times out at 120 s, but the loop keeps polling until 180 s.

How long each fault takes to fail, measured with the fakes:

| Fault | Parent commit | HEAD |
| --- | --- | --- |
| `ErrImageNeverPull` | 900 s, helm's "timed out waiting for the condition" plus a kubectl error per poll | 180 s, the message plus the Pod listing |
| No Pod, kubectl 1.31 or later | 2000 s | 1980 s |
| No Pod, kubectl before 1.31 | 900 s | 1980 s, a misleading "3 minutes" message, and `kill: No such process` |

The poll also sets no `--request-timeout`, so a request that hangs never returns and the loop never ends.

Suggested fix, not made because production code was out of scope:
- poll with `--pod-running-timeout=2s --request-timeout=10s`;
- bound the whole wait with a deadline taken from `date +%s`;
- stop polling once `kill -0 $helm_pid` fails.

**Proposed, not done**

- **Wire both scripts into CI**, for example next to "Render assertions" in `.github/workflows/integration-tests.yaml`. As things stand, nothing runs them.
- **The SVT Keycloak revert to `26.0` has no test or run behind it.** It needs docker, which wasn't available here. The new reference is also a moving tag with no `@sha256` digest, unlike the other images.
- **The documentation-only changes owe no tests.**

---

To run them: `bash test/scripts/test-suite-targets.sh` takes about 15 s and `bash test/scripts/test-chart-files.sh` about 1 s. Both pass shellcheck.

Files are in `test/scripts`:
- `test-suite-targets.sh`
- `test-chart-files.sh`
- `fake-cluster/kubectl`
- `fake-cluster/helm`
- `fake-cluster/sleep`

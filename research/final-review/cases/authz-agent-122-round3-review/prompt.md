The skills for this task are under <skills>: `final-review/SKILL.md`, `test-authoring/SKILL.md`, and
`english-developer-style/SKILL.md`. Read `<skills>/final-review/SKILL.md` in full and follow it; where it says to load
another skill, load the copy under <skills>, and do not load any other copy of these three.

You are the fresh reviewer that final-review asks for. Review the change `<base>..HEAD` of this repository, one commit.
The commit answers a round of review comments on the pull request; they are the task statement.

Inline comments:

1. On `helm-templates/authz-test-stand/README.md`: "Helm 4 prints nothing" holds only from 4.3.0 on; v4.0.0 to v4.2.0
   fail with `unable to get pod logs` like Helm 3. Only the explanation needs the version.
2. On `test/k8s/README.md`: `E2E_SUITE_TIMEOUT` and `PARITY_SUITE_TIMEOUT` are missing from the list of overrides,
   and `docs/local-integration-tests.md` does not mention them either.
3. On `docs/local-integration-tests.md`: the row on `exists and cannot be imported` covers `make parity-harness` as
   well, but the fix sends everyone to `make e2e`. After `make e2e-down`, a parity run needs `make parity`.

General comment:

- `run-suite` uses `kubectl wait --for=create`, which needs kubectl 1.31 or later, and the prerequisites name no
  version. An older kubectl rejects the condition, `&&` skips the polling loop, and the suite log is not streamed.
- A suite Pod that never starts now holds `make e2e-suite` for 15 minutes, where the old target failed after 3. With
  `ErrImageNeverPull`, for example after a missed `kind load`, the loop polls for 3 minutes, `kubectl logs -f` fails,
  and `wait $$helm_pid` waits out the `helm test` timeout. In CI that is half of the job's `timeout-minutes: 30`.
- `build/authz-agent-transfer/Dockerfile` merges the user files in the order `find` prints them, which depends on the
  filesystem, so `checksum/realms` can change between builds. The unquoted substitution also splits a file name that
  contains a space.
- `E2E_HELM_ARGS` now reaches the test-stand install too. The stand reads `TAG` and `IMAGE_PULL_POLICY` like the
  product charts, so `--set TAG=x` makes the stand ask for images `e2e-images` does not build.
- `test/svt/common/compose/docker-compose.yml` moves Keycloak in the SVT stack from 26.0 to 26.3.5, unmentioned and
  with no SVT run.
- `README.md` still says "CI builds both" though `.github/docker-dev-config.json` now lists five components, and
  `.github/docs-for-publication-task.md` still describes "the two-entry array".

The claimed cases come from these comments and the commit message (`git log <base>..HEAD`). The drift script is at
`<skills>/final-review/scripts/comment-drift.py`.

Do not change any file and do not commit. You may run local commands such as `git`, `go`, `make -n`, `helm template`,
`helm lint`, or `kubectl` without a cluster; there is no Kubernetes cluster, and you may not use gh, a browser, or curl.
End with the report the skill describes, as your final message.

The skills for this task are under <skills>: `final-review/SKILL.md`, `test-authoring/SKILL.md`, and
`english-developer-style/SKILL.md`. Read `<skills>/final-review/SKILL.md` in full and follow it; where it says to load
another skill, load the copy under <skills>, and do not load any other copy of these three.

You are the fresh reviewer that final-review asks for. Review the change `<base>..HEAD` of this repository, one commit.
The commit answers three review comments on the pull request; they are the task statement:

1. On `Makefile`, `make e2e-harness`: on a kind cluster that an earlier `make e2e` set up, this install fails. The old
   harness created `keycloak`, `keycloak-realms`, `pip-stub`, `entitlements-mock`, `tenant-manager`, the
   `authz-agent-client-credentials` Secret, and the `runtime-suite` ServiceAccount with `kubectl apply`. Those objects
   carry no Helm ownership label or annotations, so Helm stops with `exists and cannot be imported into the current
   release: invalid ownership metadata`. `parity-harness` fails the same way. CI starts from a fresh cluster, so it
   does not see this. Either remove the old objects before the first install, or add a line to
   `docs/local-integration-tests.md` and `test/k8s/README.md` saying that a stand created before this change needs
   `make e2e-down` first.
2. On `helm-templates/authz-test-stand/README.md`: `--logs` does not print the suite log here. The suite is a Job, and
   `helm test --logs` reads logs only from test hooks that are Pods. `kubectl logs job/<suite.name>` after
   `helm test` prints the log.
3. On `Makefile`, `run-suite`: the `helm test` timeout is fixed at 15 minutes, while the Job's own limit comes from
   `suite.activeDeadlineSeconds` in the values. A suite that runs longer than 15 minutes cannot be set up through the
   values alone. A timeout variable per suite, such as `PARITY_SUITE_TIMEOUT ?= 15m` passed to `--timeout`, would let
   a later change raise both limits together.

The claimed cases come from these comments and the commit message (`git log <base>..HEAD`). The drift script is at
`<skills>/final-review/scripts/comment-drift.py`.

Do not change any file and do not commit. You may run local commands such as `git`, `go`, `make -n`, `helm template`,
or `helm lint`; there is no Kubernetes cluster, and you may not use gh, a browser, or curl. End with the report the
skill describes, as your final message.
